import random
import time
from os import getenv

import influxdb_client
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# take environment variables from api.env
load_dotenv(dotenv_path='api.env')

token = getenv("INFLUXDB_TOKEN")
org = getenv("INFLUXDB_ORG")
url = getenv("INFLUXDB_URL")
bucket = getenv("INFLUXDB_BUCKET")


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
    

def write_light_points(value, thingy_id):
    """Specific method to deal with light data."""
    labels = ['RED', 'GREEN', 'BLUE', 'INFRARED']
    values = value.split(' ')

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


def write_test_point():
    """Adds a random point to the test measurement in influxdb.
    Value is between 0 and 10."""
    value = int(random.random() * 10)
    write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    point = (
        Point("test")
        .tag("environment", "development")
        .field("field1", value)
    )
    write_api.write(bucket=bucket, org="thingy-orange", record=point)
    return value


def get_test_points():
    """Returns the test points of the previous 10 minutes"""
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    query = f"""from(bucket: "{bucket}")
    |> range(start: -10m)
    |> filter(fn: (r) => r._measurement == "test")"""
    tables = query_api.query(query, org=org)

    result = ""
    for table in tables:
        for record in table.records:
            print(record)
            result = result + str(record)

    return result