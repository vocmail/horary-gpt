from fastapi import FastAPI
from datetime import datetime
import swisseph as swe
import pytz

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
    names = list(planet_positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            angle = abs(planet_positions[p1] - planet_positions[p2]) % 360
            for name, exact in ASPECTS.items():
                if abs(angle - exact) <= 6:
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

    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    swe.set_ephe_path(".")

    planet_positions = {}
    for name, code in PLANETS.items():
        try:
            result = swe.calc_ut(jd, code)
            if len(result) >= 1:
                planet_positions[name] = result[0]
        except:
            planet_positions[name] = "Error"

    house_cusps = swe.houses(jd, latitude, longitude)[0]
    houses = {f"House {i+1}": round(deg, 2) for i, deg in enumerate(house_cusps)}

    aspects = calculate_aspects(planet_positions)

    return {
        "question": question,
        "datetime": now.isoformat(),
        "location": {"latitude": latitude, "longitude": longitude},
        "planets": planet_positions,
        "houses": houses,
        "aspects": aspects
    }