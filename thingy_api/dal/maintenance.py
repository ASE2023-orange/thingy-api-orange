"""
Access layer function for plant objects
Created by: LK on 20.12.2023
Updated by: -
"""

# take environment variables from api.env
import logging
from os import getenv
from dotenv import load_dotenv
import psycopg2

from thingy_api.dal.plant import transform_data


load_dotenv(dotenv_path='environments/api.env')

def get_maintenance_status(thingy_id):
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

        query = f'SELECT maintenance_status FROM public."Maintenance" WHERE thingy_id=\'{thingy_id}\''

        try:
            # Execute the SELECT query
            cursor.execute(query)
            maintenance_status = cursor.fetchone()

            if maintenance_status is not None:
                # Extract the maintenance status from the result
                return {"maintenance_status": maintenance_status[0]}
            else:
                return {"message": "Plant not found."}
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving plant maintenance status."}  
        

def reset_maintenance_status():
    """Update the inMaintenance field for all plants."""
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
                UPDATE public."Maintenance" 
                SET
                    maintenance_status = False,
                    updated_at = NOW(),
                    maintenance_end = ARRAY_APPEND(maintenance_end, NOW())
                WHERE 
                    maintenance_status = '{True}'
            """
        try:
            # Execute the UPDATE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"maintenance_status field reset successfully for all plants")
            return 
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when resetting maintenance_status field for all plants."}
        

def set_maintenance_end(thingy_id):
    """Set maintenance end"""
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
                UPDATE public."Maintenance" 
                SET
                    maintenance_status = False,
                    updated_at = NOW(),
                    maintenance_end = ARRAY_APPEND(maintenance_end, NOW())
                WHERE 
                    thingy_id=\'{thingy_id}\'
            """
        try:
            # Execute the UPDATE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"maintenance_status stop set for thingy_id: {thingy_id}")
            return 
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when setting maintenance_status stop"}
        
def set_maintenance_start(thingy_id):
    """Set maintenance end"""
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
                UPDATE public."Maintenance" 
                SET
                    maintenance_status = True,
                    updated_at = NOW(),
                    maintenance_start = ARRAY_APPEND(maintenance_start, NOW())
                WHERE 
                    thingy_id=\'{thingy_id}\'
            """
        try:
            # Execute the UPDATE query
            cursor.execute(query)
            conn.commit()
            logging.info(f"maintenance_status start set for thingy_id: {thingy_id}")
            return 
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when setting maintenance_status stop"}

def get_maintenance_history(thingy_id):
    """Get maintenacne data for plant by thingy_id from database."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = f'SELECT * FROM public."Maintenance" WHERE thingy_id=\'{thingy_id}\''

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
            result = {col_name: value for col_name, value in zip(column_names, modified_data)}
            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving maintenance history ."}
        

def get_all_maintenance_thingies():
    """Get all thingy ids"""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = 'SELECT thingy_id FROM public."Maintenance"'

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
                dict_data.append(row_dict)

            # Only return thingy_id names.
            result = []
            for row in dict_data:
                result.append(row["thingy_id"])

            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving thingy_ids."}

def add_new_thingy_id(thingy_id):
    """Create new thingy_ids."""
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
            INSERT INTO public."Maintenance" (thingy_id)
            VALUES ('{thingy_id}')
        """

        try:
            # Execute the INSERT query
            cursor.execute(query)
            conn.commit()
            logging.info(f"thingy_id added successfully. {thingy_id}")
            return
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when inserting a new thingy id."}
        
