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

def to_sttapi(audio, smprate):

    speech_client = speech.Client()

    with io.open(audio, 'rb') as audio_file:

        audio_content = audio_file.read()

        audio_sample = speech_client.sample(
        content=audio_content,
        encoding='LINEAR16',
        sample_rate=smprate)

    # print(audio_stream.read(), audio_content)

    audio_sample = speech_client.sample(content=audio_content,
        encoding='LINEAR16',
        sample_rate=16000)

    recog_words = list(audio_sample.sync_recognize())

    print(recog_words)

    for w in recog_words:
        print(w.alternatives[0].transcript)

def map_homophones(file):
    related_words = {}
    f = open(file, "r")
    line = f.readline()
    key_value = line.split(",")
    related_words[key_value[0]] = key_value[1]
    return related_words

def clean_homophones(file):
    f = open(file, "r")
    fout = open(file.split(".")[0]+"-clean.txt", "w")
    line = f.readline()
    while line:
        new_line = line.split()
        out = new_line[1] + "," + new_line[2]
        fout.write(out)
        fout.write("\n")
        line = f.readline()

wav = "/Users/sinaastani/Documents/speekly/charlottes/CharlottesWeb0-5s.wav"
new_fl = get_data.convert_to_raw(wav, "wav")
print(new_fl)