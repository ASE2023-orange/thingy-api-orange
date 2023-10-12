from asyncio import get_event_loop

from aiohttp import web
from dotenv import load_dotenv

from thingy_api import init_app

load_dotenv()  # take environment variables from .env.

loop = get_event_loop()
loop.run_until_complete(init_app(loop))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass