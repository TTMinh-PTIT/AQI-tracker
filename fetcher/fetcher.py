from apscheduler.schedulers.blocking import BlockingScheduler
from api_call import get_data, parse_reading
from db import get_connection, upsert_stations, insert_readings,insert_alerts,get_triggered_alerts
from notifier import send_email_alert

def job():
    conn = get_connection()
    try:
        station_ids = ["A112819", "A476341", "A477292","@13251","@8688","@13026","A1791037"]
        for sid in station_ids:
            data = get_data(sid)
            if data and data["status"] == "ok":
                reading = parse_reading(data)
                station_pk = upsert_stations(conn, reading["station_id"],reading["station_name"],reading["lat"],reading["lon"])
                insert_readings(conn, station_pk, reading)
            else:
                print(f"Failed to fetch {sid}")
        alerts = get_triggered_alerts(conn)
        for a in alerts:
            subject = f"[AQI alert] {a} vượt ngưỡng"
            body = f"Trạm {a['name']} {a['station_id']} có mức AQI hiện tại là: {a['aqi']} -> (vượt ngưỡng {a['threshold']})"
            send_email_alert(a['contact'],subject,body)
    finally:
        conn.close()

if __name__ == '__main__':
    schedule = BlockingScheduler()
    schedule.add_job(job,'interval',minutes = 30)
    job()
    schedule.start()