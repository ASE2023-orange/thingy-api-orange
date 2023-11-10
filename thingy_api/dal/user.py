"""
Access layer function for users.
Created by: Jean-Marie Alder on 10 november 2023
"""
from os import getenv

import psycopg2

from . import db_pool


def get_user(user_id):
    """Get one user by id."""
    # Establish a connection to your PostgreSQL database
    with db_pool.getconn() as conn:
        cursor = conn.cursor()

        query = f"SELECT * FROM keycloak.user_entity WHERE id='{user_id}'"

        try:
            # Execute the SELECT query
            cursor.execute(query)
            data = cursor.fetchone()
            # Get column names from cursor.description
            column_names = [desc[0] for desc in cursor.description]

            # Match data values to column names and put into a python dict
            result = {col_name: value for col_name, value in zip(column_names, data)}
            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving plant."}


def get_user_dev():
    """Get the first user of the database (dev)."""
    # Establish a connection to your PostgreSQL database
    with db_pool.getconn() as conn:
        cursor = conn.cursor()

        query = 'SELECT * FROM keycloak.user_entity LIMIT 1'

        try:
            # Execute the SELECT query
            cursor.execute(query)
            data = cursor.fetchone()
            # Get column names from cursor.description
            column_names = [desc[0] for desc in cursor.description]

            # Match data values to column names and put into a python dict
            result = {col_name: value for col_name, value in zip(column_names, data)}
            return result
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving plant."}