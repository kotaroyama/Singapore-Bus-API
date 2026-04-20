from typing import Annotated, List

from fastapi import FastAPI, Path

from schemas import BusStop, SearchedBusStop
from services import fetch_arrival_info, get_next_n_arrivals, retrieve_bus_stop_with_code, search_bus_stops_with_query
from utils import decode_arrival, get_bus_stop_desc

app = FastAPI()

@app.get("/bus/{stop_code}")
async def get_next_arrivals(
    stop_code: Annotated[str, Path(
        pattern = r"^\d{5}$",
        description="A 5-digit code for a bus stop",
        examples="05189"
    )],
    limit: int = 3
) -> BusStop:
    # Get arrival info for the next n buses for all lines
    services = await fetch_arrival_info(stop_code)
    first_n_arrivals = get_next_n_arrivals(services, limit)

    # Format arrivals
    formatted_arrivals = []
    for arrival in first_n_arrivals:
        formatted_arrivals.append(decode_arrival(arrival))
    
    # Construct return
    description = await get_bus_stop_desc(stop_code)
    bus_stop = BusStop(
        stop_code=stop_code,
        description=description,
        next_arrivals=formatted_arrivals,
    )

    return bus_stop

@app.get("/stops")
async def search_bus_stops(query: str) -> List[SearchedBusStop]:
    selected_bus_stops = await search_bus_stops_with_query(query)
    formatted_bus_stops = []
    for selected_bus_stop in selected_bus_stops:
        formatted_bus_stops.append(
            SearchedBusStop(
                stop_code=selected_bus_stop["BusStopCode"],
                description=selected_bus_stop["Description"],
                road_name=selected_bus_stop["RoadName"],
            )
        )
    return formatted_bus_stops

@app.get("/stops/{stop_code}")
async def get_bus_stop_details(
    stop_code: Annotated[str, Path(
        pattern = r"^\d{5}$",
        description="A 5-digit code for a bus stop",
        examples="05189"
    )],
) -> SearchedBusStop:
    bus_stop = await retrieve_bus_stop_with_code(stop_code)
    formatted_bus_stop = SearchedBusStop(
        stop_code=stop_code,
        description=bus_stop["Description"],
        road_name=bus_stop["RoadName"]
    )
    return formatted_bus_stop