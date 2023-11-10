import psycopg2.pool
from dotenv import load_dotenv
from os import getenv

# take environment variables from api.env
load_dotenv(dotenv_path='environments/api.env')

# Create a connection pool
db_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dbname="thingy_db",
    user=getenv('DB_USER'),
    password=getenv('DB_PASSWORD'),
    host=getenv('DB_URL'),
    port=getenv('DB_PORT')
)