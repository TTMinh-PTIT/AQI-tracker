import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()
token=os.getenv("token")

def get_data(station_id: str):
    url = f"https://api.waqi.info/feed/{station_id}/?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error: ",response.status_code)
        return None
def parse_reading(raw_data: dict) -> dict:
    d = raw_data["data"]
    iaqi = d.get("iaqi", {})
    geo = d.get("city", {}).get("geo", [None, None]) 
    return {
        "station_id": d.get("idx"),
        "station_name": d.get("city", {}).get("name"),
        "lon":geo[0],
        "lat":geo[1],
        "aqi": d.get("aqi"),
        "pm25": iaqi.get("pm25", {}).get("v"),  
        "pm10": iaqi.get("pm10", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "co": iaqi.get("co", {}).get("v"),
        "timestamp": d.get("time", {}).get("iso"),
    }
# if __name__ == '__main__':
#     station_ids=["A112819","A476341","A477292"]
#     for sid in station_ids:
#         data = get_data(sid)
#         if data and data["status"] == "ok":
#             print(parse_reading(data))
#         elif data:
#             print(f"Error for {sid}: ",data["data"])
#         else:
#             print(f"Failed to fetch data for {sid}")
