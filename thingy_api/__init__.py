
import logging
from os import getenv

import aiohttp_cors
from aiohttp import web
from aiohttp.web import Response

IP = getenv('TODO_IP', 'localhost')
PORT = getenv('TODO_PORT', '8080')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_app(loop):

    app = web.Application(loop=loop)

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
    cors.add(app.router.add_get('/live/', None, name='all_todos'))
    cors.add(app.router.add_get('/live/{plant_id}', None, name='create_todo'))

    logger.info("Starting server at %s:%s", IP, PORT)
    srv = await loop.create_server(app.make_handler(), IP, PORT)
    return srv
