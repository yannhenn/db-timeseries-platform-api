# Iot-db-timeseries-rest-api

This REST-API is mainly developed to serve timeseries data persisted in a cassandra compatible database to consumers like visualisers. Additionally it is able to insert data into the database via REST. It is not designed to be a high performant data ingestion plattform.
## Installing the dependencies

T install the dependencies, switch to the projects root dir ( the one you should be in rn) and run:
```sh
pip install -r requirements.txt --break-system-packages
```
this should install the required packages.

## Environment variables
The API needs a set of environment variables to run correctly.
Generate the environment variables by creating a .env file in the /api folder.

Populate the .env file with the following environment variables:
```.env
CASSANDRA_URLS='localhost, 127.0.0.1'
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE='IoTData'
CASSANDRA_USERNAME='YouCanLeaveThisEmpty'
CASSANDRA_PASSWORD='YouCanLeaveThisEmpty'

JWT_SECRET='generated jwt secret'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_PORT=8000
```
Replace the JWT_SECRET with a secret 32 bit long hash digest, that you generate with openssl:

``sh
openssl rand -hex 32
```
## Running the api
Before running the api, one must setup the env variables correctly. 
See therefore the section 'Environment variables'
The api uses by standard the uvicorn asgi server.
Run the api with the following command:
```sh
python3 api/api_main.py
```
This serves the application on port 8000.