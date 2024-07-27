# REST Device Simulator

This simulator simulates an edge device, that writes timeseries data
via the REST api to the database.

## Configuration

Configure the device simulator by creating a .env file in this repository with the 
following variables or setting them as environment variables:

```.env
API_URL='localhost'
API_TOKEN='jwt_token_from_api'
API_PORT=8000

SOURCE_NAME='Source1'
SIGNAL_ZONE_INFO='SIGNAL1'

PUBLISH_INT='True'
PUBLISH_FLOAT='True'
PUBLISH_STRING='True'
```