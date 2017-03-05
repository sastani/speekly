from aiohttp import web, WSMsgType
import asyncio
import io
import copy
import process
import json

from google.cloud import speech

from google.cloud.proto.speech.v1beta1 import cloud_speech_pb2

import signal

import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
from google.cloud.proto.speech.v1beta1 import cloud_speech_pb2
from google.rpc import code_pb2
import grpc
import pyaudio
from six.moves import queue

loop = asyncio.get_event_loop()
app = web.Application(loop=loop)
SPEECH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'
RATE = 44100

def make_channel(host, port):
    """Creates a secure channel with auth credentials from the environment."""
    # Grab application default credentials from the environment
    credentials, _ = google.auth.default(scopes=[SPEECH_SCOPE])

    # Create a secure channel using the credentials.
    http_request = google.auth.transport.requests.Request()
    target = '{}:{}'.format(host, port)

    return google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, target)

def request_stream(data_stream, rate, interim_results=True):
    """Yields `StreamingRecognizeRequest`s constructed from a recording audio
    stream.
    Args:
        data_stream: A generator that yields raw audio data to send.
        rate: The sampling rate in hertz.
        interim_results: Whether to return intermediate results, before the
            transcription is finalized.
    """
    # The initial request must contain metadata about the stream, so the
    # server knows how to interpret it.
    recognition_config = cloud_speech_pb2.RecognitionConfig(
        # There are a bunch of config options you can specify. See
        # https://goo.gl/KPZn97 for the full list.
        encoding='LINEAR16',  # raw 16-bit signed LE samples
        sample_rate=rate,  # the rate in hertz
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code='en-US',  # a BCP-47 language tag
    )

    streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(
        interim_results=interim_results,
        config=recognition_config,
    )

    yield cloud_speech_pb2.StreamingRecognizeRequest(
        streaming_config=streaming_config)

    for data in data_stream:
        # Subsequent requests can all just have the content
        yield cloud_speech_pb2.StreamingRecognizeRequest(audio_content=data)

async def handle_audio(speech_client, audio, progress_manager, ws):

    try:
        stt_stream = speech_client.sample(content=audio,
        encoding='LINEAR16',
        sample_rate=44100)

        results = list(stt_stream.sync_recognize())

        to_update = []

        for w in results:
            to_update.append((w.alternatives[0].transcript.split(' '), w.alternatives[0].confidence))

        output = progress_manager.update(to_update)

        ws.send_str(json.dumps(output))

    except Exception as e:
        print(e)

        pass

async def websocket_handler(request):
    # Special notes: we are keeping two copies of the audio at once
    # so that we can send a staggered output to make sure
    # no words are cutoff in the short capture frame

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Initialize API speech client
    # speech_client = speech.Client()

    # Initlize audio accumulator variables and a counter
    # accum1 = b''
    # accum2 = b''
    # i = 0

    progress_manager = None

    service = cloud_speech_pb2.SpeechStub(
        make_channel('speech.googleapis.com', 443))

    audio_stream = asyncio.StreamReader()

    requests = request_stream(audio_stream, RATE)

    recognize_stream = service.StreamingRecognize(
            requests, 60*3+5)

    signal.signal(signal.SIGINT, lambda *_: recognize_stream.cancel())

    async for results in recognize_stream:
        print(results)


    async for msg in ws:

        if msg.type == WSMsgType.BINARY:

            if progress_manager == None:
                continue

            audio_stream.feed_data(msg.data)

            # # Add to the accumulator variables and the counter
            # accum1 += msg.data
            # i += 1

            # #  cutoff
            # if i == 5:
            #     audio = copy.deepcopy(accum1)
            #     accum1 = b''
            #     i = 0
            #     coro = handle_audio(speech_client, audio, progress_manager, ws)
            #     future = asyncio.ensure_future(coro)

        if msg.type == WSMsgType.TEXT:

            if msg.data == 'close':
                await ws.close()

            progress_manager = process.TextProgress(msg.data)

        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


app.router.add_get('/', websocket_handler)

web.run_app(app)