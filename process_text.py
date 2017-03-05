import io
import os
import tempfile

import get_data
from google.cloud import speech
import re

def process(ls, homo_dic):
    for w in ls:
        w = process_string(w)
    return ls

def process_text(in_file, homo_dic):
    f = open(in_file, "r")
    words = []
    line = f.readline()
    while line:
        curr_words = line.split()
        for word in curr_words:
            word = process_string(word, homo_dic)
            words.append(word)
        line = f.readline()
    return words

def process_string(word, homo_dic):
    word = re.sub(r'[^a-zA-Z]', '', word)
    word = word.lower()
    if word in homo_dic:
        word = homo_dic[word]
    return word


def to_sttapi(audio, smprate):

    speech_client = speech.Client()

    with io.open(audio, 'rb') as audio_file:

        audio_content = audio_file.read()

        audio_sample = speech_client.sample(
        content=audio_content,
        encoding='LINEAR16',
        sample_rate=smprate)

    recog_words = list(audio_sample.sync_recognize())

    print(recog_words)

    for w in recog_words:
        print(w.alternatives[0].transcript)

def map_homophones(in_file):
    related_words = {}
    f = open(in_file, "r")
    line = f.readline()
    key_value = line.split(",")
    related_words[key_value[0]] = key_value[1]
    return related_words

def clean_homophones(in_file):
    f = open(in_file, "r")
    fout = open(in_file.split(".")[0]+"-clean.txt", "w")
    line = f.readline()
    while line:
        new_line = line.split()
        out = new_line[1] + "," + new_line[2]
        fout.write(out)
        fout.write("\n")
        line = f.readline()

#wav = "/Users/sinaastani/Documents/speekly/charlottes/CharlottesWeb0-5s.wav"
#new_fl = get_data.convert_to_raw("./test_recording.m4a", "m4a")
#to_sttapi(new_fl[0], new_fl[1])

homos = map_homophones("./homophones-clean.txt")
words = process_text("/Users/sinaastani/Documents/speekly/charlottes/Charlottes0-16.txt", homos)
print(words)