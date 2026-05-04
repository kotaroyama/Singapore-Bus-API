from datetime import datetime
from zoneinfo import ZoneInfo

from geopy.distance import geodesic

from schemas import Arrival, SearchedBusStop
from services import get_bus_stops

def format_arrivals(first_n_arrivals) -> list:
    formatted_arrivals = []
    for arrival in first_n_arrivals:
        formatted_arrivals.append(decode_arrival(arrival))
    return formatted_arrivals

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

def get_bus_stop_list(bus_stops):
    formatted_bus_stops = []
    for bus_stop in bus_stops:
        formatted_bus_stops.append(
            SearchedBusStop(
                stop_code=bus_stop["BusStopCode"],
                description=bus_stop["Description"],
                road_name=bus_stop["RoadName"],
            )
        )
    return formatted_bus_stops

async def get_bus_stop_desc(bus_stop_code):
    bus_stops = await get_bus_stops()
    if bus_stops:
        for bus_stop in bus_stops:
            if bus_stop_code == bus_stop["BusStopCode"]:
                return bus_stop["Description"]

def get_lat_long_range(start_point, radius):
    # Find the North and South bounds
    north = geodesic(meters=radius).destination(start_point, 0).latitude
    south = geodesic(meters=radius).destination(start_point, 180).latitude

    # Find the East and West bounds
    east = geodesic(meters=radius).destination(start_point, 90).longitude
    west = geodesic(meters=radius).destination(start_point, -90).longitude

    result = {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
    }
    return result