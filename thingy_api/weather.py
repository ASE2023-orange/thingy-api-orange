"""
Weather utility file (light quailty, current weather, forecast)
Created by: JMA on 8 dec 2023
Updated by: JMA on 19 dec 2023
"""

import logging
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from thingy_api.dal.plant import get_all_plants, get_plant
from thingy_api.thingy_mqtt import publish_led_color


load_dotenv(dotenv_path='environments/api.env')
api_key = os.getenv('WEATHER_API_KEY', "default")
api_url = "https://api.openweathermap.org/data/2.5/"

current_weather = {} # Stores api request. Key= plant_id, Obj= api response.
current_light_quality = {} # Keeps track of the light quality category (0-4)


async def refresh_weather_info():
    """Sets weather info to current situation using api call."""
    global current_weather
    plants = get_all_plants()
    for plant in plants:
        try:
            # Get weather data at the plant location
            weather_url = f"{api_url}weather?lat={plant['lat']}&lon={plant['lng']}&units=metric&appid={api_key}" # type: ignore
            async with ClientSession() as session:
                async with session.get(weather_url) as response:
                    if response.status == 200:
                        weather_data = await response.json()
                        current_weather[plant['id']] = weather_data # type: ignore
                    else:
                        logging.error(f"Error fetching weather data for plant {plant['id']}. Status code: {response.status}") # type: ignore
        except Exception as e:
            logging.error("Error when fetching weather data.")
    
    set_light_quality()


def set_light_quality():
    """
    Set light quality and publish mqtt to change led color.
    # 5 levels of light quality, 0 = best, 4 = worst
    # Level 0: Bright Green (e.g., #00FF00)
    # Level 1: Light Green (e.g., #7FFF00)
    # Level 2: Yellow (e.g., #FFFF00)
    # Level 3: Orange (e.g., #FFA500)
    # Level 4: Red (e.g., #FF0000)
    """
   
    global current_weather
    global current_light_quality

    # Set all current plant light quality and color for thingy led.
    for plant_id, weather_info in current_weather.items():
        cloud_cover = weather_info["clouds"]["all"]
        light_quality = 2
        color = 'FFFF00'
        if cloud_cover >= 81:
            light_quality = 4
            color = 'FF0000'
        elif cloud_cover >= 61:
            light_quality = 3
            color = 'FFA500'
        elif cloud_cover >= 41:
            light_quality = 2
            color = 'FFFF00'
        elif cloud_cover >= 21:
            light_quality = 1
            color = '7FFF00'
        else:
            light_quality = 0
            color = '00FF00'

        # update light only if status has changed since last time
        if plant_id not in current_light_quality or light_quality != current_light_quality[plant_id]:
            current_light_quality[plant_id] = light_quality

            thingy_id = get_plant(plant_id)['thingy_id']
            # Publish mqtt to change color of current thingy
            logging.info(f"Changing light quality status color for {thingy_id}, plant {plant_id}")
            publish_led_color(thingy_id, color)


def get_current_light_quality(plant_id):
    """Getter for current light quality
    :param: plant_id"""
    try:
        return current_light_quality[plant_id]
    except Exception as e:
        logging.error(f"Error on get_current_light_quality for plant {plant_id}")
        return 2
    

def get_current_station_weather(plant_id):
    """Returns plant current weather (all informations).
    :param: plant_id"""
    try:
        return current_weather[plant_id]
    except Exception as e:
        logging.error(f"get current weather failed. {plant_id}" )
        return {"message": "error"}


def add_light_quality_to_plants(plants):
    """Takes all plants and adds light quality from weather api to each of them.
    :param: plants {}"""
    for plant in plants:
        plant["light_quality"] = current_light_quality[plant["id"]]
    return plants