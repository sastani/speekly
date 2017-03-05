from aiohttp import web, WSMsgType
import asyncio
import io
import copy

from google.cloud import speech

loop = asyncio.get_event_loop()
app = web.Application(loop=loop)

async def handle_audio(speech_client, audio):

    try:
        stt_stream = speech_client.sample(content=audio,
        encoding='LINEAR16',
        sample_rate=44100)

        results = list(stt_stream.sync_recognize())

        for w in results:
            print(w.alternatives[0].transcript)

    except Exception as ValueError:
        pass

async def websocket_handler(request):
    # Special notes: we are keeping two copies of the audio at once
    # so that we can send a staggered output to make sure
    # no words are cutoff in the short capture frame

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Initialize API speech client
    speech_client = speech.Client()

    # Initlize audio accumulator variables and a counter
    accum1 = b''
    accum2 = b''
    i = 0

    async for msg in ws:

        if msg.type == WSMsgType.BINARY:

            # Add to the accumulator variables and the counter
            accum1 += msg.data
            i += 1

            #  cutoff
            if i == 10:
                audio = copy.deepcopy(accum1)
                accum1 = b''
                i = 0
                coro = handle_audio(speech_client, audio)
                future = asyncio.ensure_future(coro)

        if msg.type == WSMsgType.TEXT:

            if msg.data == 'close':
                await ws.close()

            # ws.send_str(msg.data + '/answer')

        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


app.router.add_get('/', websocket_handler)

web.run_app(app)