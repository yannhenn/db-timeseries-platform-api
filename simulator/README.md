# REST Device Simulator

This simulator simulates an edge device, that writes timeseries data
via the REST api to the database.

## Configuration

Configure the device simulator by creating a .env file in this repository with the 
following variables or setting them as environment variables:

```.env
API_URL='https://iot-db-api.globalshipyard.net'
API_TOKEN='tokenFromAPI'

SOURCE_NAME='A103_Climate'
SIGNAL_NAME='-9,8,12'

PUBLISH_FORMATS='INT,FLOAT,TEXT'
TIME_DELAY_SEK='4'
```
You can fetch the API_TOKEN by running the api and requesting a token from the 
getT0ken endpoint. One can do this via curl.
Replace the localhost & port with your address and the username(here cassandra) and password(here cassandra) with your db username and password:

```sh
curl -X 'GET' \
  'http://localhost:8000/getToken?username=cassandra&password=cassandra' \
  -H 'accept: application/json'
```
This will return a secure token that you can use to access the api from now on.

## Running the simulator
Before running, one must setup the env variables correctly. 
See therefore the section 'Configuration'
Run  with the following command:
```sh
python3 api/api_main.py
```