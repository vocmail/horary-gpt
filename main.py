from fastapi import FastAPI
from datetime import datetime
import swisseph as swe
import pytz
import math

app = FastAPI()

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN
}

ASPECTS = {
    'Conjunction': 0,
    'Sextile': 60,
    'Square': 90,
    'Trine': 120,
    'Opposition': 180
}

def calculate_aspects(planet_positions):
    results = []
    planet_names = list(planet_positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planet_names[i]
            p2 = planet_names[j]
            angle = abs(planet_positions[p1] - planet_positions[p2]) % 360
            for name, exact in ASPECTS.items():
                orb = 6
                if abs(angle - exact) <= orb:
                    results.append({
                        "between": f"{p1} and {p2}",
                        "aspect": name,
                        "angle": round(angle, 2)
                    })
    return results

@app.get("/get_horary_chart")
def get_chart(question: str, latitude: float, longitude: float, timezone: str = "UTC"):
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60)
    swe.set_topo(longitude, latitude, 0)

    planet_positions = {}
    for name, code in PLANETS.items():
        lon, lat, dist = swe.calc_ut(jd, code)[0:3]
        planet_positions[name] = lon

    houses = swe.houses(jd, latitude, longitude)[0]
    house_data = {f"House {i+1}": round(houses[i], 2) for i in range(12)}

    aspects = calculate_aspects(planet_positions)

    return {
        "question": question,
        "datetime": now.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude},
        "planets": planet_positions,
        "houses": house_data,
        "aspects": aspects
    }