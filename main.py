from fastapi import FastAPI
from datetime import datetime
from skyfield.api import load, Topos
import pytz
import os

app = FastAPI()

@app.get("/get_horary_chart")
def get_chart(
    question: str,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    ephemeris_path = "de421.bsp"
    eph = load(ephemeris_path)
    ts = load.timescale()
    t = ts.from_datetime(now)
    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    positions = {}
    for planet in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']:
        ast_obj = eph[planet]
        obs = eph['earth'] + observer
        ast = obs.at(t).observe(ast_obj).apparent()
        alt, az, distance = ast.altaz()
        ra, dec, _ = ast.radec()
        positions[planet.capitalize()] = {
            'RA': ra.hours,
            'Dec': dec.degrees,
            'Altitude': alt.degrees,
            'Azimuth': az.degrees
        }

    return {
        "question": question,
        "datetime": now.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude},
        "positions": positions
    }
