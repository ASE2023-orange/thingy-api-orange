"""
API entrypoint for local debug environment.
Created by: Jean-Marie Alder on 9 november 2023
Updated by: Leyla Kandé on 9 november 2023
"""

from asyncio import get_event_loop

from aiohttp import web

from thingy_api import main

if __name__ == '__main__':
    loop = get_event_loop()
    app = main() # Also starts mqtt server, see main() function.
    loop.run_until_complete(web.run_app(app, host='0.0.0.0', port=8000))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass