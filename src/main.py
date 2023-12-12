import os
import logging
import aioconsole
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from youtube_video_downloader import YoutubeVideoDownloader, YVDException
from whisper_model import AudioTranscriptionModel, ATMException
from audio_splitter import AudioSplitter, AudioSplitterException
from transcription_enhancer import TranscriptionEnhancer



class YoutubeVideoTranscription:


    def __init__(self):
        self.__create_folders()
        self.__create_logger()
        self.logger.info('==== Starting a new session of transcriptions ===')
        self.transcription_model = AudioTranscriptionModel(self.logger)
        self.video_downloader = YoutubeVideoDownloader(self.logger, self.audios_path)
        self.transcription_enhancer = TranscriptionEnhancer(self.logger)
        self.audio_splitter = AudioSplitter(5, self.audios_path, self.logger)
        self.still_entering_urls = True


    def __create_folders(self):
        base_path = './'
        self.transcriptions_path = os.path.join(base_path, 'transcriptions')
        self.audios_path = os.path.join(base_path, 'audios')
        os.makedirs(self.transcriptions_path, exist_ok=True)
        os.makedirs(self.audios_path, exist_ok=True)


    def __create_logger(self):
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        date_format = '%d/%m/%Y %I:%M:%S %p'
        self.logger = logging.getLogger('youtube_video_transcriber')
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('./youtube_video_transcription.log')
        formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


    def __save_transcription(self, transcription, audio_file_path):
        audio_file_name = Path(audio_file_path).stem
        transcription_path = os.path.join(self.transcriptions_path, f'{audio_file_name}_transcriptions.txt')
        with open(transcription_path, 'w') as file:
            file.write(transcription)
        self.logger.info(f'The transcription of {audio_file_path} was saved on {transcription_path}')
        return transcription_path
    

    def __audio_requires_splitting(self, audio_path):
        return (self.transcription_model.audio_requires_splitting(audio_path) or
            self.transcription_enhancer.audio_requires_splitting())
    

    def __transcribe_audio_chunks(self, chunks_folder_path):
        transcriptions = []
        chunk_file_names = sorted(os.listdir(chunks_folder_path), 
                                  key=lambda x: int(x.split('.')[0].split('_')[1]))
        
        for chunk_name in chunk_file_names:
            chunk_path = os.path.join(chunks_folder_path, chunk_name)
            transcription = self.transcription_model.transcribe_audio(chunk_path)
            transcription = self.transcription_enhancer.enhance_transcription(transcription)
            transcriptions.append(transcription)
        
        return ' '.join(transcriptions)
    

    def __transcribe_audio_file(self, audio_path):
        if self.__audio_requires_splitting(audio_path):
            self.logger.info(f'The audio file {audio_path} will be splitted in 5-minutes chunks')
            chunks_folder_path = self.audio_splitter.break_down_audio_in_chunks(audio_path)
            transcription = self.__transcribe_audio_chunks(chunks_folder_path)
            self.audio_splitter.clean_temporal_files(chunks_folder_path)

        else:
            transcription = self.transcription_model.transcribe_audio(audio_path)
            transcription = self.transcription_enhancer.enhance_transcription(transcription)
        
        return transcription
            

    def __transcribe_video_url(self, video_url):
        try:
            self.logger.info(f'Starting the transcription of the Youtube video {video_url}')
            audio_path = self.video_downloader.download_video_audio(video_url)
            transcription = self.__transcribe_audio_file(audio_path)
            transcription_path = self.__save_transcription(transcription, audio_path)
            self.video_downloader.delete_stored_video_audio(audio_path)
            self.logger.info(f'Completed the transcription of the Youtube video {video_url}')
            print_message = f'The transcription for the Youtube video {video_url} was saved on {transcription_path}'
        
        except YVDException as ydb_exception:
            self.logger.exception(ydb_exception, exc_info=False)
            print_message = f'The Youtube video {video_url} was not transcripted because it could not be downloaded: ' + \
                  f'{str(ydb_exception)}. Please, fix the URL if it is incorrect, or try a different one'
        
        except (AudioSplitterException, ATMException) as exception:
            self.logger.exception(exception, exc_info=False)
            print_message = f'The Youtube video {video_url} was not transcripted because there was an error in the ' + \
                  'transcription process. Please, try again'
            
        return print_message


    async def __process_queue(self, thread_pool, task_queue):
        while True:
            # Waits until a URL is available
            video_url = await task_queue.get()
            loop = asyncio.get_running_loop()
            # Sets the transcription process to be handled by a different thread inside the execution loop
            # Most transcription process cannot be done asynchronous, so it needs a different thread to avoid blocking the I/O
            print_message = await loop.run_in_executor(thread_pool, self.__transcribe_video_url, video_url)
            print(print_message)
            if self.still_entering_urls:
                # Avoid confusing the user when printing messages and entering URLs at the same time
                print('Enter a Youtube video URL to transcribe (or "exit" to quit) and press ENTER:')
            task_queue.task_done()


    def __set_gpt_usage(self):
        if self.transcription_enhancer.is_gpt_available():
            use_gpt = input('Enter "yes" if you want to disable GPT-3.5 when enhancing transcriptions ' + \
                            '(will result in faster, but worse transcriptions):\n')
            if use_gpt == 'yes':
                self.transcription_enhancer.disable_gpt()
            

    async def main(self):
        # A pool of threads is created to handle the transcription process in different threads
        # than the main one that handles the I/O
        with ThreadPoolExecutor() as pool:
            # The queue is used to store the URLs to be processed asynchronously, together with the I/O
            task_queue = asyncio.Queue()
            asyncio.create_task(self.__process_queue(pool, task_queue))

            print('Youtube transcription tool with Whisper')

            self.__set_gpt_usage()

            while True:
                # ainput allows to have an asynchronous input function
                user_input = await aioconsole.ainput('Enter a Youtube video URL to transcribe ' + \
                                                     '(or "exit" to quit) and press ENTER:\n')

                if user_input.lower() == 'exit':
                    self.still_entering_urls = False
                    break
                
                await task_queue.put(user_input)

            # It waits until all the pending transcriptions finish
            await task_queue.join()



if __name__ == '__main__':
    asyncio.run(YoutubeVideoTranscription().main())
