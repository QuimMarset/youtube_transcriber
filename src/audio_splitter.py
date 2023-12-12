import os
import shutil
from pathlib import Path
from pydub import AudioSegment
from pydub.exceptions import CouldntEncodeError, CouldntDecodeError
from pydub.silence import split_on_silence



class AudioSplitterException(Exception):
    pass



class AudioSplitter:


    def __init__(self, chunk_duration_minutes, save_path, logger):
        self.chunk_duration_minutes = chunk_duration_minutes
        self.chunk_duration_ms = chunk_duration_minutes * 60 * 1000
        self.save_path = save_path
        self.logger = logger
    

    def __load_audio_file(self, audio_file_path):
        try:
            audio = AudioSegment.from_file(audio_file_path, "mp4")
            return audio
        except CouldntDecodeError as exception:
            self.logger.error(f'PyDub AudioSegment raised a CouldntDecodeError when opening' + \
                              f'{audio_file_path} with error {str(exception)}')
            raise AudioSplitterException(f'PyDub AudioSegment could not open the audio file {audio_file_path}')
        

    def __create_audio_chunks(self, audio):
        # Split on silences (i.e. < -40 dB) longer than 500ms, keeping 200ms of leading/trailing silence
        # to ensure chunks of short duration, later recombined in the desired duration
        chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40, keep_silence=200)
        if len(chunks) == 0:
            raise AudioSplitterException(f'There were no silences of 1s to split the audio in chunks')

        recombined_chunks = [chunks[0]]

        for chunk in chunks[1:]:
            if len(recombined_chunks[-1]) < self.chunk_duration_ms:
                recombined_chunks[-1] += chunk
            else:
                recombined_chunks.append(chunk)

        return recombined_chunks
    

    def __create_folder_to_save_chunks(self, audio_file_path):
        audio_file_name = Path(audio_file_path).stem
        chunks_folder_path = os.path.join(self.save_path, f'{audio_file_name}_chunks')
        os.makedirs(chunks_folder_path, exist_ok=True)
        self.logger.info(f'Created folder {chunks_folder_path} to save chunks for audio file {audio_file_path}')
        return chunks_folder_path
 

    def __save_audio_chunks(self, audio_chunks, chunks_folder_path):
        try:
            chunk_paths = []
            for i, audio_chunk in enumerate(audio_chunks):
                chunk_path = os.path.join(chunks_folder_path, f'chunk_{i}.mp4')
                audio_chunk.export(chunk_path, format='mp4', bitrate='48k')
                chunk_paths.append(chunk_path)
            self.logger.info(f'Saved {len(audio_chunks)} audio chunks as mp4 files in {chunks_folder_path}')
        except CouldntEncodeError:
            raise AudioSplitterException(f'There was an error when saving the audio chunk {i}')


    def break_down_audio_in_chunks(self, audio_file_path):
        audio = self.__load_audio_file(audio_file_path)
        audio_chunks = self.__create_audio_chunks(audio)
        chunks_folder_path = self.__create_folder_to_save_chunks(audio_file_path)
        self.__save_audio_chunks(audio_chunks, chunks_folder_path)
        return chunks_folder_path
    

    def clean_temporal_files(self, folder_path):
        num_files = len(os.listdir(folder_path))
        shutil.rmtree(folder_path)
        self.logger.info(f'Deleted folder {folder_path} containing {num_files} temporal audio chunks')
