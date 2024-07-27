import json, dotenv, requests, os, time
#Env var loading
dotenv.load_dotenv()

TOKEN_BEARER = os.environ.get("API_TOKEN")
API_URL = os.environ.get("API_URL")
SOURCE_ZONE_INFO = os.environ.get("SOURCE_ZONE_INFO")
SOURCE_NAME = os.environ.get("SOURCE_NAME")
FORMATS = os.environ.get("PUBLISH_FORMATS")
delay_sek = float(os.environ.get("TIME_DELAY_SEK"))
publish_formats = FORMATS.split(',')

signal_names={
    "INT":"simulated_signal_int",
    "FLOAT":"simulated_signal_float",
    "TEXT":"simulated_signal_text"
}
headersList = {
 "Accept": "*/*",
 "Authorization": f"Bearer {TOKEN_BEARER}",
 "Content-Type": "application/json" 
}

def upsert_device_info(source_name:str, source_info:str, zone_info:str, signal_formats:list):
    payload = json.dumps({
    "meta_zone":zone_info,
    "meta_info":source_info,
    "unique_name":source_name
    })
    response = requests.request("POST", API_URL+'/addSource/', data=payload,  headers=headersList)
    print(response.text)

    for signal_type in signal_formats:
        if(signal_type == 'INT'):
            payload = json.dumps({
            "meta_info":"A simulated int signal",
            "unique_name":signal_names["INT"],
            "source_name":source_name
            })
            response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            print(response.text)
        elif(signal_type == 'FLOAT'):
            payload = json.dumps({
            "meta_info":"A simulated float signal",
            "unique_name":signal_names["FLOAT"],
            "source_name":source_name
            })
            response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            print(response.text)
        else:
            payload = json.dumps({
            "meta_info":"A simulated text signal",
            "unique_name":signal_names["TEXT"],
            "source_name":source_name
            })
            response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            print(response.text)

def write_value(value_type:str, value):
    if(value_type == 'INT'):
        payload = json.dumps({
        "datatype":"INT",
        "tsPoints":[
            {
            "timestamp":"2024-07-10T05:00:00+02:00",
            "value":value
            },
            {
            "timestamp":"2024-07-10T07:00:00+02:00",
            "value":value
            }
            ]
        })
        response = requests.request("PUT", API_URL+'/addSignal/', data=payload,  headers=headersList)
        print(response.text)
    elif(value_type == 'FlOAT'):
        pass
    else:
        pass
def main():
    upsert_device_info(SOURCE_NAME, f"A simulated device with the following formats: {FORMATS}.", SOURCE_ZONE_INFO, publish_formats)

if(__name__ == '__main__'):
    main()