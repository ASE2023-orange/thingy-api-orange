"""
Influx utils file.
Created by: Jean-Marie Alder on 9 november 2023
Updated by: Jean-Marie Alder on 6 dec 2023
"""

from datetime import datetime
import logging
import random
from os import getenv

import influxdb_client
from dotenv import load_dotenv
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')

token = getenv("INFLUXDB_TOKEN", "default")
org = getenv("INFLUXDB_ORG", "default")
url = getenv("INFLUXDB_URL", "localhost")
bucket = getenv("INFLUXDB_BUCKET", "default")

# CONSTANTS
RANGE_MAP = {
    "30d": "2h",
    "15d": "1h",
    "7d": "30m",
    "1d": "10m",
    "1h": "1m",
}
UNIT_MAP = {
    "TEMP": "Temperature °C",
    "HUMID": "Humidity %",
    "AIR_PRESS": "Air pressure (hPa/10)",
    "AIR_QUAL": "Air pollution",
    "BLUE": "Blue",
    "GREEN": "Green",
    "INFRARED": "Infrared",
    "RED": "Red",
    "RSRP": "RSRP"
}
COLOR_MAP = {
    "TEMP": "rgba(255, 0, 0, 1)",
    "HUMID": "rgba(0, 255, 0, 1)",
    "AIR_PRESS": "rgba(0, 0, 255, 1)",
    "AIR_QUAL": "rgba(255, 165, 0, 1)",    # Orange
    "BLUE": "rgba(0, 0, 128, 1)",         # Dark Blue
    "GREEN": "rgba(0, 128, 0, 1)",        # Green
    "INFRARED": "rgba(128, 0, 0, 1)",     # Dark Red
    "RED": "rgba(255, 0, 255, 1)",        # Magenta
    "RSRP": "rgba(128, 128, 128, 1)"      # Gray
}


def write_point(value, measurement, thingy_id):
    """Writes a point with specific label, thingy id and value.

    Inputs:
    value: actual numeric data
    measurement: label of data
    thingy_id: e.g., orange-2
    """
    if measurement == 'LIGHT':
        # light measurement must be treated separately
        write_light_points(value, thingy_id)
    else:
        try:
            # Write to Influxdb using InfluxDBClient
            write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
            write_api = write_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point(measurement)
                .tag("location", thingy_id)
                .field("value", float(value))
            )
            write_api.write(bucket=bucket, org="thingy-orange", record=point)
            return value
        except Exception as e:
            logging.error(e)
            return value
    

def write_light_points(value, thingy_id):
    """Specific method to deal with light data."""
    labels = ['RED', 'GREEN', 'BLUE', 'INFRARED']
    values = value.split(' ')

    try:
        # Write to influx all 4 values, only creating influxdb client once.
        write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)
        for i in range(len(values)):
            point = (
                Point(labels[i])
                .tag("location", thingy_id)
                .field("value", float(values[i]))
            )
            write_api.write(bucket=bucket, org="thingy-orange", record=point)
    except Exception as e:
        logging.error(e)
        return value


def get_plant_simple_history(thingy_id, range):
    """Returns the air pressure, temperature and humidity of the 
    previous 24 hours for a specific plant.
    :param thingy_id: id of the plant's thingy."""

    # Start by chosing relevant aggregation window according to range
    window = None
    try:
        window = RANGE_MAP[range]
    except:
        window = "1h" # Takes least data if error happens to limit crashes

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    query = f'''
        from(bucket: "{bucket}")
            |> range(start: -{range})
            |> filter(fn: (r) => r["_measurement"] == "TEMP" 
                or r["_measurement"] == "HUMID" 
                or r["_measurement"] == "AIR_PRESS"
                or r["_measurement"] == "AIR_QUAL"
                or r["_measurement"] == "BLUE"
                or r["_measurement"] == "GREEN"
                or r["_measurement"] == "INFRARED"
                or r["_measurement"] == "RED"
                or r["_measurement"] == "RSRP"
                )
            |> filter(fn: (r) => r["location"] == "{thingy_id}")
            |> aggregateWindow(every: {window}, fn: mean, createEmpty: false)
    '''
    # Execute the query
    result = query_api.query(org=org, query=query)

    # Process the result into the desired format
    data = {"labels": [], "datasets": []}
    for table in result:
        for record in table.records:
            timestamp = datetime.timestamp(record["_time"])

            if timestamp not in data["labels"]:
                data["labels"].append(timestamp)

            measurement = record["_measurement"]
            measurement_label = generate_label(measurement)
            measurement_color = generate_colors(measurement)
            value = record["_value"]

            # Find or create dataset for the measurement
            dataset = next((d for d in data["datasets"] if d["label"] == measurement_label), None)
            if not dataset:
                dataset = {
                    "label": measurement_label,
                    "data": [],
                    "borderColor": measurement_color,
                    "fill": False,
                }
                data["datasets"].append(dataset)

            # Append data point to the dataset
            dataset["data"].append(value)
    
    return data


def generate_label(measurement):
    """Generate graph labels for all thingy measurement using a hash map.
        :param: raw measurement label"""

    try:
        return UNIT_MAP[measurement]
    except Exception as e:
        logging.info(f"Measurement {measurement} not found when generating label.")
        return "Undef"
    

def generate_colors(measurement):
    """Generate graph colors for all thingy measurement using a hash map.
        :param: raw measurement label"""

    try:
        return COLOR_MAP[measurement]
    except Exception as e:
        logging.info(f"Measurement {measurement} not found when generating graph colors.")
