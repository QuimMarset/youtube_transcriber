# Youtube Transcription Tool

A simple tool built with OpenAI's Whisper model as the core to transcribe YouTube videos. It uses a contextual spell checker based on BERT and GPT-3.5 to enhance the transcriptions from Whisper.

Start by installing the packages specified in the `requirements.txt` file.

To execute the code, open the repository folder in your desired IDE (e.g. VisualStudioCode), run the `main.py` file and follow the instructions in the terminal. 

Even if it can enhance the transcriptions, and it is a good improvement, it will not use those models if either spaCy's core or OpenAI API's key is not installed:

* You can install the spaCY's `en_core_web_sm` by using the following command: `python -m spacy download en_core_web_sm`
* You can install OpenAI API's key following this tutorial: https://platform.openai.com/docs/quickstart?context=python

If you do not want to, you can omit the installation, and the transcription will mostly be from Whisper.

The program mostly runs by interacting with the terminal, entering URLs, and those being transcripted and saved in the `transcriptions` folder the code generates (inside this same repository folder).

The user can enter as many URLs as desired, which are processed one by one, as it only uses an instance of the different NLP models.

Both Whisper and GPT-3.5 have limitations with respect to the video size/time. Whisper can only handle files up to 25MB, and GPT-3.5 has a token limit, usually surpassed with videos longer than 5 minutes. For this reason, the program splits the audio into 5-minute chunks if required.

If you want to finish the program, you need to write "exit", and once it completes all the pending transcriptions, the program will stop.

Moreover, you can deactivate GPT-3.5, as it is the model with the highest time and resource consumption, avoiding splitting the videos if the size is not over the limit of Whisper.

A log is generated and filled with information on the transcription of the different YouTube URLs, including the errors that might occur when some video cannot be transcripted.
