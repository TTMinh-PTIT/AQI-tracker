from fastapi import FastAPI, HTTPException
from db import get_connection, get_latest_reading, get_history, list_stations, get_triggered_alerts, insert_alerts
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from datetime import timedelta, datetime
from decimal import Decimal
import json

app = FastAPI()

class Create_Alert(BaseModel):
    station_id: str
    contact: str
    threshold: int

def tojson_filter(value):
    def default(o):
        if isinstance(o,datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Type {type(o)} not serializable")
    return json.dumps(value, default=default)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.filters["tojson"] = tojson_filter
                            
@app.get("/health", tags=["health"])
async def liveness() -> dict:
    """Always returns 200 if the process is running."""
    return {"status": "ok"}

@app.get("/stations")
def read_stations():
    conn = get_connection()
    try:
        return list_stations(conn)
    finally:
        conn.close()

@app.get("/aqi/current/{station_id}")
def read_current(station_id: str):
    conn = get_connection()
    try:
        result = get_latest_reading(conn, station_id)
        if not result:
            raise HTTPException(status_code=404, detail="Station not found or no data")
        return result
    finally:
        conn.close()

@app.get("/aqi/history/{station_id}")
def read_history(station_id: str, start: str, end: str):
    conn = get_connection()
    try:
        return get_history(conn, station_id, start, end)
    finally:
        conn.close()

@app.get("/alerts")
def get_alerts():
    conn = get_connection()
    try:
        return get_triggered_alerts(conn)
    finally:
        conn.close()

@app.post("/alerts")
def create_new_alert(alert: Create_Alert):
    conn = get_connection()
    try:
        result = insert_alerts(conn, alert.station_id, alert.contact, alert.threshold)
        if result is None:
            raise HTTPException(status_code=404, detail="Station not found")
        return result
    finally:
        conn.close()

@app.get("/dashboard")
def dashboard(request: Request):
    conn = get_connection()
    try:
        stations = list_stations(conn)
        return templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={"stations": stations}
        )
    finally:
        conn.close()

@app.get("/dashboard/{station_id}")
def dashboard_detail(request: Request, station_id: str):
    conn = get_connection()
    try:
        current = get_latest_reading(conn, station_id)
        if current is None:
            raise HTTPException(status_code=404, detail="Station not found")
        end = datetime.now()
        start = end - timedelta(days=7)
        history = get_history(conn, station_id, start, end)
        return templates.TemplateResponse(
            request=request,
            name="station_details.html",
            context={"current": current, "history": history}
        )
    finally:
        conn.close()