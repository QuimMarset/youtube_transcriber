# Youtube Transcription Tool

Simple tool built with OpenAI's Whisper model together with a contextual spell checker based on BERT, and GPT-3.5 to enhance the transcriptions from Whisper.

Start by executing the packages you can find in the `requirements.txt` file.

To execute the code, open the folder in your desired IDE (e.g. VisualStudioCode), and simply run the `main.py` file and follow the instructions. 

Even if it can enhance the transcriptions, and it is a good improvement, it will not use those models if either spaCy's core or OpenAI API's key are not installed:

* You can install the spaCY's `en_core_web_sm` by using the following command: `python -m spacy download en_core_web_sm`
* You can install OpenAI API's key following this tutorial: https://platform.openai.com/docs/quickstart?context=python

If you do not want, you can omit the installation, and the transcription will mostly be the one provided by Whisper.

The program mostly runs by interacting with the terminal, entering URLs, and those being transcripted and saved in the `transcriptions` folder the code generates (inside this same repository folder).

It can handle as many URLs as desired, and those are processed one by one, as it only uses an instance of the different NLP models.

Both Whisper and GPT-3.5 have limitations with respect to the video size/time. Whisper can only handle files up to 25MB, and GPT-3.5 has a token limit, which is usually surpassed with videos longer than 5 minutes. For this reason, the program splits the audios in 5-minute chunks if required.

If you want to finish, you simply need to write "exit", and once it finishes all the pending transcriptions the program will stop.

Moreover, you can deactivate GPT-3.5, as it is the model with the highest time and resource consumption, avoiding the splitting of the videos if the size is not over the limit of Whisper.

A log is generated and filled with the information of the transcription process of the different Youtube URLs, including the different errors that might occurr when some video cannot be transcripted.