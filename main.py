from fastapi import FastAPI, Query
from datetime import datetime
from skyfield.api import load, Topos
import pytz

app = FastAPI()

@app.get("/get_horary_chart")
def get_chart(
    question: str,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
):
    # Get current time in given timezone
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    # Load ephemeris and observer location
    eph = load('de421.bsp')
    ts = load.timescale()
    t = ts.from_datetime(now)

    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)

    # Get planet positions
    planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn']
    positions = {}

    for planet in planets:
        ast_obj = eph[planet]
        ast = eph['earth'] + observer
        ast_pos = ast.at(t).observe(ast_obj).apparent()
        alt, az, distance = ast_pos.altaz()
        ra, dec, _ = ast_pos.radec()
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