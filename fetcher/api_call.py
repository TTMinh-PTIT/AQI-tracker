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
    
def safe_number(value):
    if value is None or value == "-":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_reading(raw_data: dict) -> dict:
    d = raw_data["data"]
    iaqi = d.get("iaqi", {})
    geo = d.get("city", {}).get("geo", [None, None])
    return {
        "station_id": d.get("idx"),
        "station_name": d.get("city", {}).get("name"),
        "lat": geo[0],
        "lon": geo[1],
        "aqi": safe_number(d.get("aqi")),
        "pm25": safe_number(iaqi.get("pm25", {}).get("v")),
        "pm10": safe_number(iaqi.get("pm10", {}).get("v")),
        "o3": safe_number(iaqi.get("o3", {}).get("v")),
        "no2": safe_number(iaqi.get("no2", {}).get("v")),
        "co": safe_number(iaqi.get("co", {}).get("v")),
        "timestamp": d.get("time", {}).get("iso"),
    }

