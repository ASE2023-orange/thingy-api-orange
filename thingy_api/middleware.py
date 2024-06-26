"""
Middleware for authentication with Keycloak.
This is an aiohttp middleware, make sure to add it
to the app object when creating the api.
Created by: Jean-Marie Alder on 9 november 2023
"""

import logging
from os import getenv

import keycloak
from aiohttp import web
from dotenv import load_dotenv

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')

server_url = getenv('KEYCLOAK_URL')
client_id = getenv('KEYCLOAK_CLIENT_ID')
realm_name = getenv('KEYCLOAK_REALM_NAME')
client_secret_key = getenv('KEYCLOAK_SECRET_KEY')

# Configure client
keycloak_openid = keycloak.KeycloakOpenID(server_url=server_url,
                                 client_id=client_id,
                                 realm_name=realm_name,
                                 client_secret_key=client_secret_key)

@web.middleware
async def keycloak_middleware(request: web.Request, handler):
    """Middleware for authentication. Required on all routes.
       Checks user token with Keycloak server."""
    # Get the access token from the request headers
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        # Validate the access token with Keycloak
        # Decode Token
        KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
        token_info = keycloak_openid.decode_token(access_token, key=KEYCLOAK_PUBLIC_KEY, options=options)

        # If token validation and role checks pass, proceed with the request
        return await handler(request)
    
    except keycloak.exceptions.KeycloakGetError as e:
        # Handle token validation errors
        logging.error(e)
        return web.Response(text="Access forbidden: Token validation failed", status=403)
    
    except Exception as e:
        # Handle other exceptions
        logging.error(e)
        return web.Response(text="Internal server error", status=500)