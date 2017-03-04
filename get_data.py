
import os
import subprocess as sp
import librosa
from pytube import YouTube
import numpy as np
import pandas as pd
from ntlk.tokenize import word_tokenize

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
