from fastapi import FastAPI, Query
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.const import PLACIDUS
from datetime import datetime
import pytz

app = FastAPI()

@app.get("/get_horary_chart")
def get_chart(
    question: str,
    latitude: float,
    longitude: float,
    timezone: str = "UTC"
):
    now = datetime.now(pytz.timezone(timezone))
    dt_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')

    dt = Datetime(dt_str, time_str, now.strftime('%z'))
    pos = GeoPos(str(latitude), str(longitude))
    chart = Chart(dt, pos, hsys=PLACIDUS)

    result = {
        "ASC": str(chart.get("ASC")),
        "Moon": str(chart.get("MOON")),
        "Sun": str(chart.get("SUN")),
        "Question": question,
        "Time": now.isoformat(),
        "Location": {"lat": latitude, "lon": longitude},
        "Planets": {obj: str(chart.get(obj)) for obj in chart.objects}
    }

    return result