import io
import os
import tempfile

import get_data
from google.cloud import speech

def process_text(file):
    f = open(file, "r")
    words = []
    line = f.readline()
    while line:
        curr_words = line.split()
        for word in curr_words:
            words.append(word)
        line = f.readline()
    return words

def to_sttapi(audio):

    speech_client = speech.Client()

    with io.open(audio, 'rb') as audio_file:

        audio_content = audio_file.read()

    # audio_stream = io.open(audio, 'rb')

    #audio_stream = io.BytesIO()

    #audio_stream = tempfile.TemporaryFile()

    #audio_stream.write(audio_content)

    # print(audio_stream.read(), audio_content)

    audio_sample = speech_client.sample(content=audio_content,
        encoding='LINEAR16',
        sample_rate=16000)

    recog_words = list(audio_sample.sync_recognize())

    print(recog_words)

    for w in recog_words:
        print(w.alternatives[0].transcript)


to_sttapi("./test.raw")