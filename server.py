from aiohttp import web, WSMsgType
import asyncio

loop = asyncio.get_event_loop()
app = web.Application(loop=loop)

async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:

        if msg.type == WSMsgType.BINARY:

            # Audio processing functions go here
            # Sample rate is 2048


            value = int.from_bytes(msg.data, byteorder='little')

            print(value)

        if msg.type == WSMsgType.TEXT:

            if msg.data == 'close':
                await ws.close()

            # else:
                
            #     ws.send_str(msg.data + '/answer')

        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws

app.router.add_get('/', websocket_handler)

web.run_app(app)