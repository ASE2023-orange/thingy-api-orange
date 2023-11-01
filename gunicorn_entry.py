from aiohttp import web

from thingy_api import main  # Import your main function from the previous code

app = main()  # Call the main function to start your aiohttp app and MQTT client