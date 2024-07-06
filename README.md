# Iot-db-timeseries-rest-api

This REST-API is mainly developed to serve timeseries data persisted in a cassandra compatible database to consumers like visualisers. Additionally it is able to insert data into the database via REST. It is not designed to be a high performant data ingestion plattform.
## Installing the dependencies

T install the dependencies, switch to the projects root dir ( the one you should be in rn) and run:
```sh
pip install -r requirements.txt --break-system-packages
```
this should install the required packages.
## Running the api
The api uses by standard the uvicorn asgi server.
Run the api with the following command:
```sh
python3 api/api_main.py
```
This serves the application on port 8000.