from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import swisseph as swe
import pytz
import os
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Swiss Ephemeris data file
EPHE_PATH = os.path.dirname(os.path.abspath(__file__))
swe.set_ephe_path(EPHE_PATH)

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN
}

def calculate_houses(jd_ut, lat, lon):
    """Calculates Placidus house cusps and Asc/MC"""
    hsys = b'P'  # Placidus
    try:
        cusps, ascmc = swe.houses(jd_ut, lat, lon, hsys)
        houses = {}
        for i in range(12):
            houses[f"House {i+1}"] = round(cusps[i], 2)
        houses["Ascendant"] = round(ascmc[0], 2)
        houses["Midheaven"] = round(ascmc[1], 2)
        return houses
    except Exception as e:
        return {"error": str(e)}

def calculate_aspects(planet_positions):
    aspects = []
    for i, p1 in enumerate(planet_positions):
        for j, p2 in enumerate(planet_positions):
            if i >= j:
                continue
            if (
                isinstance(planet_positions[p1], (int, float))
                and isinstance(planet_positions[p2], (int, float))
            ):
                angle = abs(planet_positions[p1] - planet_positions[p2]) % 360
                for asp_angle in [0, 60, 90, 120, 180]:
                    orb = 8  # degrees of allowable difference
                    if abs(angle - asp_angle) <= orb:
                        aspects.append({
                            "between": f"{p1} and {p2}",
                            "aspect": f"{asp_angle}°",
                            "angle": round(angle, 2)
                        })
    return aspects

@app.get("/get_horary_chart")
def get_chart(
    question: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    timezone: str = Query("UTC")
):
    try:
        # Current time
        now = datetime.now(pytz.timezone(timezone))
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60 + now.second / 3600)

        # Planet positions
        planet_positions = {}
        for name, code in PLANETS.items():
            try:
                lon, lat, dist = swe.calc_ut(jd, code)[0:3]
                planet_positions[name] = round(lon, 2)
            except:
                planet_positions[name] = "Error"

        # Houses
        houses = calculate_houses(jd, latitude, longitude)

        # Aspects
        aspects = calculate_aspects(planet_positions)

        return {
            "question": question,
            "datetime": now.isoformat(),
            "location": {"latitude": latitude, "longitude": longitude},
            "planets": planet_positions,
            "houses": houses,
            "aspects": aspects
        }

    except Exception as e:
        return {"error": str(e)}
