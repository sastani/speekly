from aiohttp import web, WSMsgType
import asyncio
import io
import copy
import process
import json

# from google.cloud import speech


import google.auth
import google.auth.transport.grpc
import google.auth.transport.requests
from google.cloud.proto.speech.v1beta1 import cloud_speech_pb2
from google.rpc import code_pb2
import grpc

loop = asyncio.get_event_loop()
app = web.Application(loop=loop)

SPEECH_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'


def make_channel(host, port):
    """Creates a secure channel with auth credentials from the environment."""
    # Grab application default credentials from the environment
    credentials, _ = google.auth.default(scopes=[SPEECH_SCOPE])

    # Create a secure channel using the credentials.
    http_request = google.auth.transport.requests.Request()
    target = '{}:{}'.format(host, port)

    return google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, target)

async def handle_audio(speech_client, audio, progress_manager, ws):

    try:
        # The method and parameters can be inferred from the proto from which the
        # grpc client lib was generated. See:
        # https://github.com/googleapis/googleapis/blob/master/google/cloud/speech/v1beta1/cloud_speech.proto
        response = speech_client.SyncRecognize(cloud_speech_pb2.SyncRecognizeRequest(
            config=cloud_speech_pb2.RecognitionConfig(
                # There are a bunch of config options you can specify. See
                # https://goo.gl/KPZn97 for the full list.
                encoding='LINEAR16',  # one of LINEAR16, FLAC, MULAW, AMR, AMR_WB
                sample_rate=44100,  # the rate in hertz
                # See https://g.co/cloud/speech/docs/languages for a list of
                # supported languages.
                #language_code=language_code,  # a BCP-47 language tag
            ),
            audio=cloud_speech_pb2.RecognitionAudio(
                content=audio,
            )
        ), 120)

        to_update = []

        for result in response.results:
            for alt in result.alternatives:
                to_update.append((alt.transcript.split(' '), alt.confidence))

        print(to_update)

        output = progress_manager.update(to_update)

        print(output)

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

    service = cloud_speech_pb2.SpeechStub(
        make_channel('speech.googleapis.com', 443))

    # Initlize audio accumulator variables and a counter
    accum1 = b''
    accum2 = b''
    i = 0

    progress_manager = None

    async for msg in ws:

        if msg.type == WSMsgType.BINARY:

            if progress_manager == None:
                continue

            # Add to the accumulator variables and the counter
            accum1 += msg.data
            i += 1

            #  cutoff
            if i == 10:
                audio = copy.deepcopy(accum1)
                accum1 = b''
                i = 0
                coro = handle_audio(service, audio, progress_manager, ws)
                future = asyncio.ensure_future(coro)

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