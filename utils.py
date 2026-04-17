from datetime import datetime
from zoneinfo import ZoneInfo

from schemas import Arrival
from services import get_bus_stops

def decode_arrival(raw_arrival: list):
    service = raw_arrival[0]
    current_time = datetime.now(ZoneInfo("Asia/Singapore"))
    time_diff = datetime.fromisoformat(raw_arrival[1]["EstimatedArrival"]) - current_time
    minutes = int(time_diff.total_seconds() // 60)
    formatted_arrival = Arrival(
        service=service,
        minutes=minutes,
    )
    return formatted_arrival

async def get_bus_stop_desc(bus_stop_code):
    bus_stops = await get_bus_stops()
    if bus_stops:
        for bus_stop in bus_stops:
            if bus_stop_code == bus_stop["BusStopCode"]:
                return bus_stop["Description"]