
import logging
from os import getenv

import aiohttp_cors
from aiohttp import web
from aiohttp.web import Response
from dotenv import load_dotenv

from thingy_api.middleware import keycloak_middleware


# take environment variables from api.env
load_dotenv(dotenv_path='api.env')

# Retrieve environment variables
IP = getenv('API_IP', 'localhost')
PORT = getenv('API_PORT', '8080')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    cors.add(app.router.add_get('/test', test_route, name='test'))
    cors.add(app.router.add_get('/test/influx', test_influx, name='test_influx'))

    logger.info("Starting server at %s:%s", IP, PORT)
    srv = await loop.create_server(app.make_handler(), IP, PORT)
    return srv


async def test_route(request):
    """Hello world route, to make sure that api is working"""
    return web.json_response({"message": "Hello world!"})


async def test_influx(request):
    """Route to test influx db"""
    return web.json_response({'message': 'Not implemented'})