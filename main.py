from fastapi import FastAPI
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
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    eph = load("de421.bsp")
    ts = load.timescale()
    t = ts.from_datetime(now)

    observer = Topos(latitude_degrees=latitude, longitude_degrees=longitude)
    positions = {}

    # Only use planets known to exist in your de421.bsp
    safe_planets = ['sun', 'moon', 'mercury', 'venus', 'mars']

    for planet in safe_planets:
        try:
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
        except KeyError:
            positions[planet.capitalize()] = "Not found in ephemeris"

    return {
        "question": question,
        "datetime": now.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude},
        "positions": positions
    }
