"""
Access layer function for users.
Created by: Jean-Marie Alder on 10 november 2023
"""
from os import getenv

import psycopg2


def get_all_users():
    """Get all users from database."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
        cursor = conn.cursor()

        query = 'SELECT * FROM keycloak.user_entity'

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

            return dict_data
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"message": "error when retrieving users."}


def get_user(user_id):
    """Get one user by id."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
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
            return {"message": "error when retrieving user."}


def get_user_dev():
    """Get the first user of the database (dev)."""
    # Establish a connection to your PostgreSQL database
    with psycopg2.connect(
        dbname="thingy_db",
        user=getenv('DB_USER'),
        password=getenv('DB_PASSWORD'),
        host=getenv('DB_URL'),
        port=getenv('DB_PORT')
    ) as conn:
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
            return {"message": "error when retrieving user."}