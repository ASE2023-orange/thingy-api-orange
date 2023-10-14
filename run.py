from asyncio import get_event_loop

from aiohttp import web

from thingy_api import init_app

loop = get_event_loop()
# init_app() is the entry point of the api
loop.run_until_complete(init_app(loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass