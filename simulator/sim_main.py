import json, dotenv, requests, os, time, random
import numpy as np
import http.client
from datetime import datetime
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
    conn = http.client.HTTPSConnection(API_URL, 443)
    payload = json.dumps({
    "meta_zone":zone_info,
    "meta_info":source_info,
    "unique_name":source_name
    })
    conn.request("POST", "/addSource/", payload, headersList)
    response = conn.getresponse()
    result = response.read()
    print(result.decode("utf-8"))
    #response = requests.request("POST", API_URL+'/addSource/', data=payload,  headers=headersList)
    #print(response.text)

    for signal_type in signal_formats:
        if(signal_type == 'INT'):
            payload = json.dumps({
            "meta_info":"UNIT: counts, MSG: A simulated int signal",
            "unique_name":signal_names["INT"],
            "source_name":source_name
            })
            conn.request("POST", "/addSignal/", payload, headersList)
            response = conn.getresponse()
            result = response.read()
            print(result.decode("utf-8"))
            #response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            #print(response.text)
        elif(signal_type == 'FLOAT'):
            payload = json.dumps({
            "meta_info":"UNIT: C, MSG: A simulated float signal",
            "unique_name":signal_names["FLOAT"],
            "source_name":source_name
            })
            conn.request("POST", "/addSignal/", payload, headersList)
            response = conn.getresponse()
            result = response.read()
            print(result.decode("utf-8"))
            #response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            #print(response.text)
        else:
            payload = json.dumps({
            "meta_info":"UNIT: text, MSG: A simulated text signal",
            "unique_name":signal_names["TEXT"],
            "source_name":source_name
            })
            conn.request("POST", "/addSignal/", payload, headersList)
            response = conn.getresponse()
            result = response.read()
            print(result.decode("utf-8"))
            #response = requests.request("POST", API_URL+'/addSignal/', data=payload,  headers=headersList)
            #print(response.text)
    conn.close()

def write_value(value_type:str, source_name:str, value, timestamp:datetime, conn:http.client.HTTPSConnection):
    # INT
    if(value_type == 'INT'):
        payload = json.dumps({
        "datatype":"INT",
        "tsPoints":[
            {
            "timestamp":timestamp.isoformat(),
            "value":int(value)
            }
            ]
        })
        conn.request("PUT", f"/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", payload, headersList)
        response = conn.getresponse()
        result = response.read()
        print(result.decode("utf-8"))
        #response = requests.request("PUT", f"{API_URL}/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", data=payload,  headers=headersList)
        #print(response.text)
    #FLOAT
    elif(value_type == 'FLOAT'):
        payload = json.dumps({
        "datatype":"FLOAT",
        "tsPoints":[
            {
            "timestamp":timestamp.isoformat(),
            "value":float(value)
            }
            ]
        })
        conn.request("PUT", f"/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", payload, headersList)
        response = conn.getresponse()
        result = response.read()
        print(result.decode("utf-8"))
        #response = requests.request("PUT", f"{API_URL}/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", data=payload,  headers=headersList)
        #print(response.text)
    #TEXT
    else:
        payload = json.dumps({
        "datatype":"STRING",
        "tsPoints":[
            {
            "timestamp":timestamp.isoformat(),
            "value":str(value)
            }
            ]
        })
        conn.request("PUT", f"/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", payload, headersList)
        response = conn.getresponse()
        result = response.read()
        print(result.decode("utf-8"))
        #response = requests.request("PUT", f"{API_URL}/writeTimeseriesData/{source_name}/{signal_names[value_type]}/", data=payload,  headers=headersList)
        #print(response.text)
def main():
    upsert_device_info(SOURCE_NAME, f"A simulated device with the following formats: {FORMATS}.", SOURCE_ZONE_INFO, publish_formats)
    generated_int_range = (np.random.randint(-50, 10),np.random.randint(11,100))
    generated_float_range = (float(np.random.randint(-10,10)),float(np.random.randint(10,40)))

    last_int = np.random.randint(generated_int_range[0], generated_int_range[1]) #will be the latest int value written
    spread_range_int = abs(generated_int_range[1]-generated_int_range[0])
    mean_range_int = generated_int_range[0]+(spread_range_int/2)

    last_float = random.uniform(generated_float_range[0], generated_float_range[1]) #will be the latest float value
    spread_range_float = abs(generated_float_range[1]-generated_float_range[0])
    mean_range_float = generated_float_range[0]+(spread_range_float/2)
    
    trend_int = 0
    trend_float = 0.0

    conn = http.client.HTTPSConnection(API_URL, 443)
    while(True):
        # First set some trend values
        trend_int = trend_int + ((-random.random()*(float(last_int)-float(mean_range_int))* spread_range_int) / spread_range_int)*0.5
        trend_float = trend_float + ((-random.random()*(float(last_float)-float(mean_range_float))* spread_range_float) / spread_range_float)*0.5
        # Simulate data
        for format in publish_formats:
            if(format == 'INT'):
                write_value(format, SOURCE_NAME, int(last_int+trend_int), datetime.now(), conn)
                last_int = int(last_int+trend_int)
            elif(format =='FLOAT'):
                write_value(format, SOURCE_NAME, last_float + trend_float, datetime.now(), conn)
                last_float = last_float + trend_float            
            else:
                message = f"Calculated following values: INT: {last_int} FLOAT: {last_float}"
                write_value(format, SOURCE_NAME, message, datetime.now(), conn)
        print(f"Calculated following values: INT: {last_int} FLOAT: {last_float}")
        print("◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤◢◤")
        time.sleep(delay_sek)
if(__name__ == '__main__'):
    main()