# Thingy Project Orange - Monitoring System for Solar Power Plants
This project is being developped for the "Advanced Software Engineering" course at University of Fribourg, Switzerland. 
## Setup API locally with debug
_Note: follow this section when running the api for the first time. For later use, once the setup has been done, follow [below section](#run-api-locally-with-debug)_
### Requirements
- Please note that if "python" is not recognized by your machine, try other aliases, like py, python3. Make sure that Python is installed on your system. Docker and Docker compose should be installed as well.
- Make sure that no service is running on mentionned ports (5432, 8888, 8086).
### Docker setup
- Open "docker-compose-local.yml" file and have a look at it to know more about its services. Default parameters should do, but they can be updated if needed. Here is an overview of deployied services:
  - postgres: a simple Postgresql database containing keycloak users and configurations as well as plants metadata.
  - keycloak: authentication server using OpenID Connect and OAuth2.0. Admin can create and manage accounts and clients here.
  - influxdb: Influxdb2 timeseries database to store historical data.
- To run all services, run ```docker compose -f docker-compose-local.yml up -d``` on the project root folder.
  - Note that older docker versions may use ```docker-compose``` (with hyphen).
  - If changes have been made to the docker compose file, make sure to rerun all services running ```docker compose -f docker-compose-local.yml up -d --build --force-recreate```
- To make sure that all services are running, use ```docker ps -a```, and check that all services are on "Running" state.

### Keycloak local setup
In order to test the API, a test user is required. It can be created on the keycloak administration console.
- Have a look at the docker-compose-local.yml file and adapt if needed. Defalut should work in local environments.
- Make sure that keycloak and postgres docker services are running.
- Open the keycloak admin dashboard, e.g., http://localhost:8888
- Login with default admin credentials (have a look at docker-compose file to find them).
- Create a new realm called "thingy-orange"
- Create a test user. Once created, create a credential (password) for the new user
- Create two clients:
  - Frontend: add a client ID and make sure that "Client authentication" is **disabled**.
  - Backend: Same as frontend, but "OAuth 2.0 Device Authorization Grant" must be **enabled** and client authentication set to **enabled**.
- On the frontend client settings, go to "Login Theme" and set "thingy".

### Setup environment variables
- Copy "environments/api.env.example" to "environments/api.env" at the root of the project and adapt if needed. Default values will do for a local environment (localhost:8000 for api).

### Setup Python API with virtual environment
- Create a virtual environment: ```python -m venv venv``` (or similar, e.g., ```python3 -m venv venv```).
- Enter the virtual environment:
  - Mac and Linux: ```source ./venv/bin/activate```
  - Windows: ```.\venv\Scripts\activate.bat``` or ```.\venv\Scripts\Activate.ps1``` for Powershell.
- Inside virtual environment, install all dependencies: ```pip install -r requirements.txt```.

### Run the app
- Once all requirements are installed, run the application using: 
```
python3 run.py
```
- To stop the local server, use ctrl+c
- Finally, read carefully next section to know more about database. Normally, it should be plug and play and no more action is required (unless configurations in .env have been modified)



## Run API locally with debug
_Note: Follow this section if you have already setup the api before_
- Start all Docker container with ```docker compose -f docker-compose-local.yml up -d``` on project root folder.
- Start the API with ```python3 run.py```



## Test local API with Postman
To test the api without the client, Postman can be used and configured to test secured endpoints. 
To setup authentication, follow the following steps on the "Authorization" tab and make sure to adapt urls, ids and secrets :
- Type: "OAuth 2.0"
- Add authorization data to: "Request header"
- Header Prefix: "Bearer"
- Grant Type: "Authorization Code"
- Callback URL: "http://localhost:8888/"
- Auth URL: "http://localhost:8888/realms/thingy-orange/protocol/openid-connect/auth"
- Access Token URL: "http://localhost:8888/realms/thingy-orange/protocol/openid-connect/token"
- Client ID: "backend"
- Client Secret: "YourSecretHere"
- Client Authentication: "Send as Basic Auth header"
Once configured, click on "Get New Access Token". A login prompt will appear. Enter your test user credentials (keycloak admin won't work). If redirected successfully, the token should be available. Click "Use Token" to automatically add it to each request.



## Production Setup
This section briefly describes steps to host the application on a production server. This guide is an example and should be adapted. Some seconary steps are only mentionned and the organization is responsible for it's setup.

### Requirements
- A server, or VPS, with min. 4Go RAM and two processor cores.
- A URL, e.g., myproject.ch.
- The URL should have these subdomains setup on a DNS server:
  - myproject.ch
  - auth.myproject.ch
  - timeseries.myproject.ch
  - api.myproject.ch
- Docker should be installed.
### Procedure
- On the server, setup a reverse proxy, e.g., Traefik, that will monitor the "web" Docker network. There is an example setup inside labels of the docker-compose-prod.yml file.
- Create a folder for the project, e.g., "thingy_orange", inside "/srv".
- Clone both repositories (api, client) inside this root folder.
- Adapt environment variables of both backend (environments folder) and frontend (.env).
- Adapt docker-compose-prod file to match your needs.
- Copy and paste the docker-compose-prod.yml file to the root folder of the entire project (here, "thingy_orange"). Rename it to "docker-compose.yml"
- To start all services, run ```docker compose up -d --build --force-recreate```. Use this command everytime you need to update the platform.
- **Important**: The "init_db.sql" script should be run manually on the postgres instance. Please use any way to connect and run the script "init_db.sql" inside the "thingy_db" database. This will require a restart of all docker containers (especially Keycloak). Use the same docker compose command as mentionned above.
- For debugging, have a look at docker container logs and the api logs inside "thingy-api-orange/logs/api.log".

To know more about how it works. Please have a look at the following files: "docker-compose-prod.yml", "Dockerfile", and also the Dockerfile from the frontend.

