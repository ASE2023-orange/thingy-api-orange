from asyncio import get_event_loop

from aiohttp import web

from thingy_api import main

from thingy_api.thingy_mqtt import start_mqtt

if __name__ == '__main__':
    loop = get_event_loop()
    app = main()
    loop.run_until_complete(web.run_app(app, host='0.0.0.0', port=8000))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass