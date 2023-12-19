"""
Access layer function for plant objects
Created by: Jean-Marie Alder on 9 november 2023
Updated by: LK on 19.12.2023
"""
from datetime import datetime
from decimal import Decimal
import logging
from os import getenv
import uuid

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

from thingy_api.dal.user import get_user

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')


def get_all_plants():
    """Get all plants from database."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = 'SELECT * FROM public."Plant"'

        try:
            # Execute the SELECT query
            cursor.execute(query)
            data = cursor.fetchall()
            # Get column names from cursor.description
            column_names = [desc[0] for desc in cursor.description]

            # Transform the data to replace Decimal and datetime values
            modified_data = transform_data(data)

            # Match data values to column names and put into a python dict
            dict_data = []
            for row in modified_data:
                row_dict = {col_name: value for col_name, value in zip(column_names, row)}
                row_dict["contact_person"] = get_user(row_dict["contact_person"]) # Adds user info
                dict_data.append(row_dict)

            return dict_data
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving plants."}
        

def get_plant(plant_id):
    """Get one plant by id from database."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f'SELECT * FROM public."Plant" WHERE id=\'{plant_id}\''

        try:
            # Execute the SELECT query
            cursor.execute(query)
            data = cursor.fetchone()
            # Get column names from cursor.description
            column_names = [desc[0] for desc in cursor.description]

            # Transform the data to replace Decimal and datetime values
            # Node that transform_data takes an array as param. But one result is present.
            modified_data = transform_data([data])[0]

            # Match data values to column names and put into a python dict
            dict_data = []
            result = {col_name: value for col_name, value in zip(column_names, modified_data)}
            result["contact_person"] = get_user(result["contact_person"]) # Adds user info
            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving plant."}


def create_plant(values):
    """Create a new plant row on database.
    :param value: dict containing all plant values."""
    #Generate ID
    values["id"]= str(uuid.uuid4())

    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = sql.SQL("""
            INSERT INTO public."Plant" (id, friendly_name, thingy_id, locality, npa, lat, lng, max_power, nr_panels, contact_person)
            VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {})
        """).format(
            sql.Literal(values['id']),
            sql.Literal(values['friendly_name']),
            sql.Literal(values['thingy_id']),
            sql.Literal(values['locality']),
            sql.Literal(values['npa']),
            sql.Literal(values['lat']),
            sql.Literal(values['lng']),
            sql.Literal(values['max_power']),
            sql.Literal(values['nr_panels']),
            sql.Literal(values['contact_person'])
        )

        try:
            # Execute the INSERT query
            cursor.execute(query)
            conn.commit()
            logging.info(f"Plant added successfully. {values['friendly_name'], values['id']}")
            return get_plant(values['id'])
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when inserting a new plant."}
        

def update_plant(plant_id, values):
    """Update a plant by id."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f"""
            UPDATE public."Plant"
            SET
                friendly_name = '{values['friendly_name']}',
                thingy_id = '{values['thingy_id']}',
                locality = '{values['locality']}',
                npa = '{values['npa']}',
                lat = {values['lat']},
                lng = {values['lng']},
                max_power = {values['max_power']},
                nr_panels = {values['nr_panels']},
                contact_person = '{values['contact_person']}',
                updated_at = NOW()
            WHERE
                id = '{plant_id}'
        """

        try:
            # Execute the INSERT query
            cursor.execute(query)
            conn.commit()
            logging.info(f"Plant modified successfully. {values['friendly_name'], values['id']}")
            return get_plant(plant_id)
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when updating a plant."}
        
def toggle_maintenance(thingy_id):
    """Update the inMaintenance field for a plant by thingy_id."""

     # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f"""
                UPDATE public."Plant"
                SET
                    in_maintenance = NOT in_maintenance,
                    updated_at = NOW()
                WHERE
                    thingy_id = '{thingy_id}'
            """
        try:
            # Execute the UPDATE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"in_maintenance field updated successfully for plants with thingy_id: {thingy_id}")
            return get_all_plants
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when updating in_maintenance field for plants."}
        
def reset_maintenance():
    """Update the inMaintenance field for a plant by thingy_id."""

     # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f"""
                UPDATE public."Plant"
                SET
                    in_maintenance = False,
                    updated_at = NOW()
            """
        try:
            # Execute the UPDATE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"in_maintenance field reset successfully for all plants")
            return get_all_plants
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when resetting in_maintenance field for all plants."}


def delete_plant(plant_id):
    """Delete a plant by id."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f'DELETE FROM public."Plant" WHERE id=\'{plant_id}\''

        try:
            # Execute the DELETE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"Plant deleted successfully. {plant_id}")
            return get_all_plants()
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when deleting a plant."}


def transform_data(data):
    """Converts all decimals and datetime objects to json serializable types.
    Includes Decimal to float and datetime to timestamp."""
    transformed_data = []
    for row in data:
        modified_row = list(row)
        for i, value in enumerate(row):
            if isinstance(value, Decimal):
                modified_row[i] = float(value)
            elif isinstance(value, datetime):
                modified_row[i] = value.timestamp()
        transformed_data.append(modified_row)
    return transformed_data