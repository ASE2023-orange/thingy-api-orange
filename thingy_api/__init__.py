"""
Main file to start mqtt and api servers.
Created by: Jean-Marie Alder on 9 november 2023
Updated by: LK on 20 dec 2023
"""

import asyncio
import logging
from logging.handlers import RotatingFileHandler
from os import getenv

import aiohttp_cors
from aiohttp import web
from dotenv import load_dotenv

from thingy_api.influx import get_plant_simple_history
from thingy_api.middleware import keycloak_middleware
import thingy_api.dal.plant as plant_dal
import thingy_api.dal.user as user_dal
import thingy_api.dal.thingy_id as thingy_id_dal
import thingy_api.dal.maintenance as maintenance_dal
from thingy_api.thingy_mqtt import start_mqtt
from thingy_api.thingy_mqtt import get_thingy_data
from thingy_api.thingy_mqtt import start_mqtt, get_thingy_data, get_thingy_id_data
from thingy_api.weather import add_light_quality_to_plants, get_current_light_quality, refresh_weather_info, get_current_station_weather

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
    # Reset maintenance status
    maintenance_dal.reset_maintenance_status()

    # Get initial light quality 
    await refresh_weather_info()
    # Schedule get_light_quality() every 2 minutes
    asyncio.create_task(schedule_task(refresh_weather_info, interval_seconds=120))

    # Initialize the aiohttp app
    return init_app()


async def schedule_task(task_function, interval_seconds):
    """Custom method to run scheduled tasks."""
    while True:
        await asyncio.sleep(interval_seconds)
        await task_function()


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

    # Historical data actions
    cors.add(app.router.add_get('/api/influx/{id}/{range}', influx_get_for, name='influx_get_for'))

    # currrent data actions
    cors.add(app.router.add_get('/api/thingy', thingy_data_get, name='thingy_get'))
    cors.add(app.router.add_get('/api/thingy/{id}', thingy_data_by_id_get, name='thingy_by_id_get'))

    # thingy actions
    cors.add(app.router.add_get('/api/thingy_id', get_all_thingy_ids, name='get_all_thingy_ids'))

    # plant actions 
    cors.add(app.router.add_post('/api/plants/create', create_plant, name='create_plant'))
    cors.add(app.router.add_get('/api/plants/create/dev', create_plant_dev, name='create_plant_dev'))
    cors.add(app.router.add_get('/api/plants', get_all_plants, name='get_all_plants'))
    cors.add(app.router.add_get('/api/plants/{id}', get_plant, name='get_plant'))
    cors.add(app.router.add_delete('/api/plants/{id}', delete_plant, name='delete_plant'))
    cors.add(app.router.add_patch('/api/plants/{id}', update_plant, name='update_plant'))
    cors.add(app.router.add_get('/api/map/plants', get_all_plants_map, name='get_all_plants_map'))

    cors.add(app.router.add_get('/api/plants/light/{id}', get_plant_light_quality, name='get_plant_light_quality'))
    cors.add(app.router.add_get('/api/weather/plants/{id}', get_weather_plant, name='get_weather_plant'))

    # maintenance actions
    cors.add(app.router.add_get('/api/maintenance/status/{id}', get_plant_maintenance, name='get_plant_maintenance'))
    cors.add(app.router.add_get('/api/maintenance/history/{id}', get_maintenance_history, name='get_maintenance_history'))

    # user actions
    cors.add(app.router.add_get('/api/users', get_all_users, name='get_all_users'))

    return app


async def test_route(request):
    """Hello world route, to make sure that api is working"""
    return web.json_response({"message": "Hello world!"})

########################################
# INFLUX ROUTES

async def influx_get_for(request):
    """Route to get influx data for thingy ID"""
    thingy_id = request.match_info.get('id')
    range = request.match_info.get('range')
    # Check if range is in accepted format
    if range not in ["30d", "15d", "7d", "1d", "1h"]: 
        return web.Response(status=404, text="Time range not allowed")
    result = get_plant_simple_history(thingy_id, range)
    if result is not None:
        return web.json_response(result)
    else:
        # Case in which requested ID does not exist
        return web.Response(status=404, text="Thingy not found")

########################################
# THINGY ROUTES

# get request without automatic update in FE 
async def thingy_data_get(request):
    """Route to get thingy data"""
    result = get_thingy_data()
    return web.json_response(result)

async def thingy_data_by_id_get(request):
    """Route to get thingy data for ID"""
    thingy_id = request.match_info.get('id')
    result = get_thingy_id_data(thingy_id)

    if result is not None:
        return web.json_response(result)
    else:
        # Case in which requested ID does not exist
        return web.Response(status=404, text="Thingy not found")


async def get_all_thingy_ids(request):
    """Route to get thingy Ids only"""
    result = thingy_id_dal.get_all_thingy_ids()
    return web.json_response(result)

########################################
# PLANTS ROUTES


async def create_plant(request):
    """Route to create a new plant. Takes a json object as request 
       with all plant details."""
    data = await request.json()
    result = plant_dal.create_plant(data)
    return web.json_response(result)


async def create_plant_dev(request):
    """DEV function: Creates two placeholder plants for tests."""
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
        'thingy_id': 'orange-3',
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
    """Route to get all plants."""
    return web.json_response(plant_dal.get_all_plants())


async def get_plant(request):
    """Route to get one plant by id."""
    id = str(request.match_info['id'])
    result = plant_dal.get_plant(id)
    return web.json_response(result)


async def update_plant(request):
    """Route to update a plant by id"""
    id = str(request.match_info['id'])
    data = await request.json()
    result = plant_dal.update_plant(id, data)
    return web.json_response(result)


async def delete_plant(request):
    """Route to delete a plant by id"""
    id = str(request.match_info['id'])
    result = plant_dal.delete_plant(id)
    return web.json_response(result)


async def get_all_plants_map(request):
    """Route to get information to print on a map. 
    It adds cloud cover information to show on plant popups."""
    plants = plant_dal.get_all_plants()
    plants_final = add_light_quality_to_plants(plants)
    return web.json_response(plants_final)


async def get_plant_light_quality(request):
    """Route to get light quality category (not % cloud cover) of a plant by id."""
    id = str(request.match_info['id'])
    result = get_current_light_quality(id)
    return web.json_response({"light_quality": result})


async def get_weather_plant(request):
    """Route to get weather information of a plant by id."""
    id = str(request.match_info['id'])
    result = get_current_station_weather(id)
    return web.json_response(result)

###########################################
# MAINTENANCE ROUTES

async def get_plant_maintenance(request):
    """Route to get the status of a plant maintenance by id."""
    id = str(request.match_info['id'])
    result = maintenance_dal.get_maintenance_status(id)
    return web.json_response(result)

async def get_maintenance_history(request):
    """Route to get history of plant maintenances by plant id."""
    id = str(request.match_info['id'])
    result = maintenance_dal.get_maintenance_history(id)
    return web.json_response(result)

###########################################
# USERS ROUTES

async def get_all_users(request):
    """Route to get all users from Keycloak database table."""
    result = user_dal.get_all_users()
    return web.json_response(result)
