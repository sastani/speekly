import io
import os
import pytube

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
        audio_sample = speech_client.sample(
            audio_content,
            source_uri=None,
            encoding='LINEAR16',
            sample_rate=16000)
    recog_words = speech_client.speech_api.sync_recognize(audio_sample)
    for w in recog_words:
        print(w.transcript())


to_sttapi("/Users/sinaastani/Documents/speekly/charlottes/CharlottesWeb0-5s.wav")