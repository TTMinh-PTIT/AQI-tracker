CREATE TABLE stations (
    id SERIAL PRIMARY KEY,
    station_id VARCHAR(20) UNIQUE NOT NULL,  
    name VARCHAR(255) NOT NULL,
    latitude NUMERIC(9,6),
    longitude NUMERIC(9,6),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id),
    aqi INTEGER,
    pm25 NUMERIC(6,2),
    pm10 NUMERIC(6,2),
    o3 NUMERIC(6,2),
    no2 NUMERIC(6,2),
    co NUMERIC(6,2),
    recorded_at TIMESTAMPTZ NOT NULL,   
    fetched_at TIMESTAMPTZ DEFAULT now() 
);

CREATE INDEX idx_readings_station_time ON readings(station_id, recorded_at);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    station_id INTEGER NOT NULL REFERENCES stations(id),
    contact VARCHAR(255) NOT NULL,       -- email hoặc webhook URL
    threshold INTEGER NOT NULL,          -- ngưỡng AQI
    created_at TIMESTAMPTZ DEFAULT now()
);