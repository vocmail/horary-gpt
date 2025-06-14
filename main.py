from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz
import swisseph as swe
import os
import math

app = FastAPI()

# Allow all origins (for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set ephemeris path (assumes sepl_18.se1 is in the same folder)
EPHE_PATH = os.path.abspath(".")
swe.set_ephe_path(EPHE_PATH)

# Planet codes
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}

# Common aspects in degrees
ASPECTS = {
    "Conjunction": 0,
    "Opposition": 180,
    "Trine": 120,
    "Square": 90,
    "Sextile": 60,
}

def calculate_aspects(positions, orb=8):
    aspects_found = []
    names = list(positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            if isinstance(positions[p1], (int, float)) and isinstance(positions[p2], (int, float)):
                angle = abs(positions[p1] - positions[p2]) % 360
                angle = 360 - angle if angle > 180 else angle
                for name, exact in ASPECTS.items():
                    if abs(angle - exact) <= orb:
                        aspects_found.append({"between": f"{p1} - {p2}", "aspect": name, "angle": round(angle, 2)})
    return aspects_found

@app.get("/get_horary_chart")
def get_chart(
    question: str = Query(...),
    latitude: float = Query(...),
    longitude: float = Query(...),
    timezone: str = Query("UTC")
):
    # Current time in UTC
    now_utc = datetime.utcnow()

    # Localize datetime to user's timezone
    try:
        tz = pytz.timezone(timezone)
        local_dt = pytz.utc.localize(now_utc).astimezone(tz)
    except Exception as e:
        print(f"[ERROR] Timezone issue: {e}")
        return {"error": "Invalid timezone provided."}

    year, month, day = local_dt.year, local_dt.month, local_dt.day
    hour = local_dt.hour + local_dt.minute / 60.0 + local_dt.second / 3600.0

    # Julian Day
    jd = swe.julday(year, month, day, hour)

    # Planet positions
    planet_positions = {}
    for name, code in PLANETS.items():
        try:
            result = swe.calc_ut(jd, code)
            if result and len(result[0]) >= 1:
                lon = result[0][0]
                planet_positions[name] = round(lon, 2)
            else:
                planet_positions[name] = "Unavailable"
        except Exception as e:
            print(f"[ERROR] Could not calculate {name}: {e}")
            planet_positions[name] = "Unavailable"

    # Houses (Placidus)
    try:
        cusps, ascmc = swe.houses(jd, latitude, longitude.encode() if isinstance(longitude, str) else longitude)
        houses = {f"House {i+1}": round(deg, 2) for i, deg in enumerate(cusps)}
        houses["Ascendant"] = round(ascmc[0], 2)
        houses["Midheaven"] = round(ascmc[1], 2)
    except Exception as e:
        print(f"[ERROR] House calculation failed: {e}")
        houses = {"error": "House calculation failed"}

    aspects = calculate_aspects(planet_positions)

    return {
        "question": question,
        "datetime": local_dt.isoformat(),
        "location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "planets": planet_positions,
        "houses": houses,
        "aspects": aspects
    }
