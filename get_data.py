
import os
import subprocess as sp
import librosa
from pytube import YouTube
import numpy as np
import pandas as pd

'''
def parse_time_str(s):
    """
    Takes HH:MM:SS to seconds in floats.
    """

    l = [int(p) for p in s.split(':')]

    if len(l) == 3:
        hr = l[0]
        m = l[1]
        s = l[2] 
    elif len(l) == 2:
        m = l[0]
        s = l[1]

    return 3600.0 * h + 60.0 * m + s


def get_links(df):
    """
    Download videos referenced by links in the df (loaded from csv).
    Populates video_file column of the row corresponding to the Youtube link.
    """

    dl_prefix = './'

    # TODO multithread
    for l in df['link']:
        yt = YouTube(l)
        # TODO how to just always pick the lowest res? map Video objs to res strings?
        vid = yt.get(l)
        vid.download(dl_prefix)
        # how to?
        df.loc['video' == ] = dl_prefix + # TODO vid.filename?


def mp4_to_raw(mp4):
    """
    Converts mp4 file on disk, with name equal to input argument, to mp3 file.
    Populates audio_file column of df where row is mp4 
    """

    # off by one?
    outname = mp4[:-3] + '.raw'

    # wait for it to finish? default?
    sp.Popen(['ffmpeg', '-i', mp4, '-f-', 's161e', '-acodec', 'pcm_s16le', outname])
    # TODO 
    df.loc[video == mp4, 'audio_file'] = outname
'''


def words(text):
    # TODO clean off punctuation. restrict to some set of characters?
    return text.split()


def phonemes(text):
    assert False


def sentences(text):
    punctuation = {} # TODO

    # split on set?

    return text.split(punctuation)

def normalize_text(text):


# TODO general function to clean / normalize text?


# in case we want to find videos of kids speaking known texts
# and see how our pipeline works on their audio
"""
label_csv = 'ht17_links.csv'
input_df = pd.read_csv(label_csv)

'''
input_df['start'] = input_df['start'].map(lambda s: parse_time_str(s))
input_df['end'] = input_df['end'].map(lambda s: parse_time_str(s))
'''

df_pickle = 'ht17.p'
if not os.file.exists(df_pickle):
    # make a new df that also has columns for video file name and audio file name
    # TODO pickle this dataframe and load at beginning as well
    df = input_df.concat({'video_file': ,'audio_file': })

else:
    # how to load pickled df?

# go through all links
# adds video_file names to df once they download
get_links(df)

for i in range(len(df['link'])):
    mp4_to_raw(df['link'][i])


"""

template = ''

# TODO by phoneme / word / sentence ? depends on API
# robust ways to split on each of these?

# upload these raw audio files in chunks to the speech-to-text API

# receive predicted text

# see if predicted text matches template

# if it doesn't, output audio corresponding to correct pronunciation
# use text-to-speech API


# pickle df if using it
