import os
import openai
import tiktoken
import spacy
import contextualSpellCheck



class TranscriptionEnhancer:


    def __init__(self, logger):
        self.logger = logger
        self.__load_contextual_spell_checker()
        self.__load_gpt_3_5()
        self.use_gpt = self.gpt_client is not None


    def __load_contextual_spell_checker(self):
        try:
            self.spacy_spell_checker = spacy.load('en_core_web_sm')
            contextualSpellCheck.add_to_pipe(self.spacy_spell_checker)
        except OSError:
            self.spacy_spell_checker = None
            self.logger.warning('spaCy cannot found the model and will not be used to enhance transcriptions. ' + \
                            'You can install it with the following command: python -m spacy download en_core_web_sm')


    def __load_gpt_3_5(self):
        if os.environ.get("OPENAI_API_KEY"):
            self.logger.info('OpenAI API Key is available and GPT-3.5 will be used to enhance transcriptions')
            self.gpt_client = openai.OpenAI()
        else:
            self.logger.warning('OpenAI API Key is not available and GPT-3.5 will not be used to enhance transcriptions')
            self.gpt_client = None


    def is_gpt_available(self):
        return self.gpt_client is not None


    def disable_gpt(self):
        self.use_gpt = False
        self.logger.warning('Disabled GPT-3.5 to enhance transcriptions')


    def audio_requires_splitting(self):
        return self.use_gpt


    def __remove_non_ascii_characters(self, transcription):
        return ''.join(character for character in transcription if ord(character) < 128)


    def __fix_spell_errors(self, transcription):
        doc = self.spacy_spell_checker(transcription)
        if doc._.performed_spellCheck:
            self.logger.info('The contextual spell checker enhanced the current transcription')
            return doc._.outcome_spellCheck
        self.logger.warning('The contextual spell checker did not enhance the current transcription')
        return transcription
    

    def __fix_grammatical_errors(self, transcription):
        system_message = """
            You are a helpful assistant that corrects spelling and grammatical errors in text without 
            removing any content. Also, try to make different paragraphs when strictly needed.
            Return the corrected text
        """

        response = self.gpt_client.chat.completions.create(model='gpt-3.5-turbo', temperature=0,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": transcription},
            ],
        )
        return response.choices[0].message.content
    

    def __is_over_the_gpt_token_limit(self, transcription):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(transcription)) >= 2048


    def enhance_transcription(self, transcription):
        transcription = self.__remove_non_ascii_characters(transcription)

        if self.spacy_spell_checker:
            transcription = self.__fix_spell_errors(transcription)
        
        if self.use_gpt and not self.__is_over_the_gpt_token_limit(transcription):
            transcription = self.__fix_grammatical_errors(transcription)
            self.logger.info('GPT-3.5 enhanced the current transcription')
        
        elif self.use_gpt:
            self.logger.warning('GPT-3.5 did not enhance the current transcription because ' + \
                                'the text was over the token limit')
        
        return transcription