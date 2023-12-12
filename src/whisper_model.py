import whisper
import os
from torch.cuda import is_available



class ATMException(Exception):
    pass



class AudioTranscriptionModel:


    def __init__(self, logger):
        self.logger = logger
        self.model = whisper.load_model('small')
    

    def audio_requires_splitting(self, audio_path):
        bytes_size = os.path.getsize(audio_path)
        return (bytes_size // 1e6) > 25


    def transcribe_audio(self, audio_path):
        try:
            # Cannot use float16 with CPU
            result = self.model.transcribe(audio_path, fp16=is_available())
            transcription = result['text'].strip()
            if transcription == '':
                raise ATMException(f'The transcription for {audio_path} is empty')
            self.logger.info(f'Transcription generated for audio file {audio_path}')
            return transcription
        except Exception as exception:
            # The exceptions are not that easily localized, so we catch a general one
            raise ATMException(f'There was an error transcribing the audio in {audio_path}: {str(exception)}')
