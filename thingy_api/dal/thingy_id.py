"""
Access layer function for thingy_id objects
Created by: Jean-Marie Alder on 10 november 2023
"""

from os import getenv

import psycopg2

from . import db_pool

def get_all_thingy_ids():
    """Get all thingy_ids."""
    # Establish a connection to your PostgreSQL database
    with db_pool.getconn() as conn:
        cursor = conn.cursor()

        query = f"SELECT * FROM public.thingy_id"

        try:
            # Execute the SELECT query
            cursor.execute(query)
            data = cursor.fetchall()
            # Get column names from cursor.description
            column_names = [desc[0] for desc in cursor.description]

            # Match data values to column names and put into a python dict
            dict_data = []
            for row in data:
                row_dict = {col_name: value for col_name, value in zip(column_names, row)}
                dict_data.append(row_dict)

            # Only return thingy_id names.
            result = []
            for row in dict_data:
                result.append(row["name"])

            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving thingy ids."}
        

def add_new_id(thingy_id):
    """Create new thingy_ids."""
    # Establish a connection to your PostgreSQL database
    with db_pool.getconn() as conn:
        cursor = conn.cursor()

        query = f"""
            INSERT INTO public.thingy_id (name)
            VALUES ('{thingy_id}')
        """

        try:
            # Execute the INSERT query
            cursor.execute(query)
            conn.commit()
            print("thingy_id added successfully.")
            return get_all_thingy_ids()
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when inserting a new thingy id."}
        

def update_id(thingy_id):
    """update thingy_id timestamp. Keeps track of wether the thingy
       is active or not."""
    # Establish a connection to your PostgreSQL database
    with db_pool.getconn() as conn:
        cursor = conn.cursor()

        query = f"""
            UPDATE public.thingy_id
            SET updated_at = NOW()
            WHERE
                name = '{thingy_id}'
        """

        try:
            # Execute the INSERT query
            cursor.execute(query)
            conn.commit()
            return get_all_thingy_ids()
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when updating a thingy id."}