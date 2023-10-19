from asyncio import get_event_loop

from aiohttp import web

from thingy_api import init_app

from thingy_mqtt import start_mqtt

if __name__ == "__main__":
    loop = get_event_loop()
    # init_app() is the entry point of the api
    loop.run_until_complete(init_app(loop))

    start_mqtt()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass