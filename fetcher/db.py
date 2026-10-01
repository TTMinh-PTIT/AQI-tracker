import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASS"),
        dbname = os.getenv("DB_NAME"),
        port = os.getenv("DB_PORT")
    )
def upsert_stations(conn, station_id: str, name: str, lat, lon) -> int:
    cur = conn.cursor()
    try:
        cur.execute(
        """INSERT INTO stations(station_id, name, latitude, longitude)
        VALUES(%s,%s,%s,%s)
        ON CONFLICT (station_id) DO UPDATE SET name = EXCLUDED.name
        RETURNING id""",
        (station_id,name,lat,lon)
        )
        res = cur.fetchone()
        conn.commit()
        return res[0]
    except Exception as e:
        conn.rollback()
        print(f"error at {e}")
        raise
    finally:
        cur.close()
def insert_readings(conn, station_fk: int, reading: dict):
    cur = conn.cursor()
    try:
        cur.execute(
        """INSERT INTO readings(station_id, aqi, pm25, pm10, o3, no2, co, recorded_at)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
        (station_fk,reading["aqi"],reading["pm25"],reading["pm10"],reading["o3"],reading["no2"],reading["co"],reading["timestamp"])
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"error at {e}")
        raise
    finally:
        cur.close()
def get_latest_reading(conn, station_id: str) -> dict | None:
    cur = conn.cursor()
    try:
        cur.execute("""
        SELECT r.*, s.name, s.station_id 
        FROM readings r
        INNER JOIN stations s ON r.station_id = s.id
        WHERE s.station_id = %s
        ORDER BY recorded_at DESC LIMIT 1""",
        (station_id,))
        row = cur.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns,row))
    except Exception as e:
        conn.rollback()
        print(f"error at {e}")
        raise
    finally:
        cur.close()

def get_history(conn, station_id: str, start, end) -> list[dict]:
    cur = conn.cursor()
    try:
        cur.execute("""
        SELECT r.*, s.name, s.station_id FROM readings r
        INNER JOIN stations s ON r.station_id = s.id
        WHERE s.station_id = %s AND recorded_at BETWEEN %s AND %s
        ORDER BY recorded_at ASC
        """,(station_id,start,end))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns,row)) for row in rows]

    except Exception as e:
        conn.rollback()
        print(f"error at {e}")
        raise
    finally:
        cur.close()

def list_stations(conn) -> list[dict]:
    # SELECT * FROM stations
    cur = conn.cursor()
    try:
        cur.execute("""
        SELECT s.*, latest.aqi, latest.recorded_at
        FROM stations s
        LEFT JOIN (
            SELECT DISTINCT ON (station_id)*
            FROM readings
            ORDER BY station_id, recorded_at DESC
            ) latest ON latest.station_id = s.id"""
        )
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns,row)) for row in rows]
    except Exception as e:
        conn.rollback()
        print(f"error as {e}")
        raise
    finally:
        cur.close()

def get_triggered_alerts(conn) -> list[dict]:
    cur = conn.cursor()
    try:
        cur.execute("""
        SELECT a.id, a.contact, a.threshold, s.station_id, s.name, latest.aqi
        FROM alerts a
        INNER JOIN stations s ON a.station_id = s.id
        INNER JOIN(
            SELECT DISTINCT ON (station_id) *
            FROM readings
            ORDER BY station_id, recorded_at DESC
            ) latest ON latest.station_id = s.id
        WHERE latest.aqi >= a.threshold""")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns,row)) for row in rows]
    except Exception as e:
        conn.rollback()
        print(f"Error at {e}")
        raise
    finally:
        cur.close()

def insert_alerts(conn,station_id: str,contact: str, threshold: int) -> dict:
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO alerts (station_id, contact, threshold)
            SELECT id, %s, %s FROM stations WHERE station_id = %s
            RETURNING id, station_id, contact, threshold""",(contact, threshold, station_id)
            )
        row = cur.fetchone()
        if row is None:
            return None
        conn.commit()
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns,row))
    except Exception as e:
        conn.rollback()
        print(f"error at {e}")
        raise
    finally:
        cur.close()