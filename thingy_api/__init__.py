"""
Main file to start mqtt and api servers.
Created by: Jean-Marie Alder on 9 november 2023
Updated by: Leyla Kandé on 9 november 2023
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from os import getenv

import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv

from thingy_api.influx import get_test_points, write_test_point
from thingy_api.middleware import keycloak_middleware
import thingy_api.dal.plant as plant_dal
import thingy_api.dal.user as user_dal
from thingy_api.thingy_mqtt import start_mqtt
from thingy_api.thingy_mqtt import get_thingy_data
from thingy_api.thingy_mqtt import start_mqtt, get_thingy_data, get_thingy_id_data

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')

# Retrieve environment variables
IP = getenv('API_IP', 'localhost')
PORT = getenv('API_PORT', '8000')

# setup logs
logging.basicConfig(
    level=logging.INFO,  # Set the logging level as needed (e.g., INFO, DEBUG, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/api.log',  # Set the filename for your log file
    filemode='a'  # 'a' appends to the log file, 'w' overwrites it
)
# Configure log rotation (log file management, max 1Mb)
# Changes log file when reaching 1MB, keeping 3 backup files.
log_handler = RotatingFileHandler(
    'logs/api.log', maxBytes=1024*1024, backupCount=3
)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(log_handler)


async def main():
    # Start the MQTT client
    start_mqtt()

    # Initialize the aiohttp app
    return init_app()


def init_app():

    # Create app, also including credential checker middleware
    app = web.Application(middlewares=[keycloak_middleware])

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
    cors.add(app.router.add_get('/api/thingy/{id}', thingy_data_by_id_get, name='thingy_by_id_get'))

    cors.add(app.router.add_post('/api/plants/create', create_plant, name='create_plant'))
    cors.add(app.router.add_get('/api/plants/create/dev', create_plant_dev, name='create_plant_dev'))
    cors.add(app.router.add_get('/api/plants', get_all_plants, name='get_all_plants'))
    cors.add(app.router.add_get('/api/plants/{id}', get_plant, name='get_plant'))
    cors.add(app.router.add_delete('/api/plants/{id}', delete_plant, name='delete_plant'))
    cors.add(app.router.add_patch('/api/plants/{id}', update_plant, name='update_plant'))

    cors.add(app.router.add_get('/api/users', get_all_users, name='get_all_users'))

    return app


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
    serialized_result = json.dumps(result)
    return web.json_response(serialized_result)

async def thingy_data_by_id_get(request):
    """Route to get thingy data for ID"""
    thingy_id = request.match_info.get('id')
    result = get_thingy_id_data(thingy_id)

    if result is not None:
        serialized_result = json.dumps(result)
        return web.json_response(serialized_result)
    else:
        # Case in which requested ID does not exist
        return web.Response(status=404, text="Thingy not found")
    return web.json_response(serialized_result)


########################################
# PLANTS ROUTES


async def create_plant(request):
    data = await request.json()
    result = plant_dal.create_plant(data)
    return web.json_response(result)


async def create_plant_dev(request):
    """Create a new plant in the database"""
    plant_data_1 = {
        'friendly_name': 'Bundeshaus Energie',
        'thingy_id': 'orange-1',
        'locality': 'Bern',
        'npa': '3001',
        'lat': 46.947050,
        'lng': 7.444104,
        'max_power': 2500,
        'nr_panels': 200,
        'contact_person': user_dal.get_user_dev()["id"]
    }
    plant_data_2 = {
        'friendly_name': 'Romande Energie',
        'thingy_id': 'orange-2',
        'locality': 'Echichens',
        'npa': '1112',
        'lat': 46.526240,
        'lng': 6.498429,
        'max_power': 1000,
        'nr_panels': 50,
        'contact_person': user_dal.get_user_dev()["id"]
    }
    plant_dal.create_plant(plant_data_1)
    result = plant_dal.create_plant(plant_data_2)
    return web.json_response(result)


async def get_all_plants(request):
    return web.json_response(plant_dal.get_all_plants())


async def get_plant(request):
    id = str(request.match_info['id'])
    result = plant_dal.get_plant(id)
    return web.json_response(result)


async def update_plant(request):
    id = str(request.match_info['id'])
    data = await request.json()
    result = plant_dal.update_plant(id, data)
    return web.json_response(result)


async def delete_plant(request):
    id = str(request.match_info['id'])
    result = plant_dal.delete_plant(id)
    return web.json_response(result)


###########################################
# USERS ROUTES

async def get_all_users(request):
    result = user_dal.get_all_users()
    return web.json_response(result)
