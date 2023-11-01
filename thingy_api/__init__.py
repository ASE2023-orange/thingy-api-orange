import logging
from logging.handlers import RotatingFileHandler
from os import getenv

import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv

from thingy_api.influx import get_test_points, write_test_point
from thingy_api.middleware import keycloak_middleware
from thingy_api.thingy_mqtt import get_thingy_data

# take environment variables from api.env
load_dotenv(dotenv_path='api.env')

# Retrieve environment variables
IP = getenv('API_IP', 'localhost')
PORT = getenv('API_PORT', '8000')

# setup logs
logging.basicConfig(
    level=logging.INFO,  # Set the logging level as needed (e.g., INFO, DEBUG, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api.log',  # Set the filename for your log file
    filemode='a'  # 'a' appends to the log file, 'w' overwrites it
)
# Configure log rotation (log file management, max 1Mb)
# Changes log file when reaching 1MB, keeping 3 backup files.
log_handler = RotatingFileHandler(
    'logs/api.log', maxBytes=1024*1024, backupCount=3
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)

async def init_app(loop):

    # Create app, also including credential checker middleware
    app = web.Application(loop=loop, middlewares=[keycloak_middleware])

    # Configure default CORS settings.
    # TODO: modify according to the frontend url (if it should not be accessed somewhere else)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*",
            )
    })

    # TODO: add all routes here
    cors.add(app.router.add_get('/api/test', test_route, name='test'))
    cors.add(app.router.add_get('/api/test/influx', test_influx_write, name='test_influx_write'))
    cors.add(app.router.add_get('/api/test/influx/get', test_influx_get, name='test_influx_get'))
    cors.add(app.router.add_get('/api/thingy', thingy_data_get, name='thingy_get'))

    logging.info("Starting server at %s:%s", IP, PORT)
    srv = await loop.create_server(app.make_handler(), IP, PORT)
    return srv


async def test_route(request):
    """Hello world route, to make sure that api is working"""
    return web.json_response({"message": "Hello world!"})


async def test_influx_write(request):
    """Route to test influx db"""
    value = write_test_point()
    return web.json_response({'value': value})

async def test_influx_get(request):
    """Route to test influx db, get test points"""
    result = get_test_points()
    return web.json_response({'value': result})

# get request without automatic update in FE 
async def thingy_data_get(request):
    """Route to get thingy data"""
    result = get_thingy_data()
    return web.json_response(result)