"""
Gunicorn entrypoint (different from local debug environment with run.py)
Created by: Jean-Marie Alder on 9 november 2023
"""

from aiohttp import web

from thingy_api import main  # Import main function from api package

# Here, we don't start the server as usual, gunicorn will deal with this app object.
app = main()  # Call the main function to start your aiohttp app and MQTT client