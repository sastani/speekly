import io
import os

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

def to_sttapi(audio, smprate):

    speech_client = speech.Client()

    with io.open(audio, 'rb') as audio_file:

        audio_content = audio_file.read()

    audio_sample = speech_client.sample(
        content=audio_content,
        encoding='LINEAR16',
        sample_rate=smprate)


    print(audio_sample)

    recog_words = speech_client.speech_api.sync_recognize(audio_sample)

    print(recog_words)

    for w in recog_words:
        print(w.alternatives[0].transcript)

wav = "/Users/sinaastani/Documents/speekly/charlottes/CharlottesWeb0-5s.wav"
new_fl = get_data.convert_to_raw(wav, "wav")
print(new_fl)
