from typing import Annotated

from fastapi import FastAPI, Path

from schemas import BusStop
from services import fetch_arrival_info, get_next_3_arrivals
from utils import decode_arrival, get_bus_stop_desc

app = FastAPI()

@app.get("/bus/{stop_code}")
async def get_next_arrivals(
    stop_code: Annotated[str, Path(
        pattern = r"^\d{5}$",
        description="A 5-digit code for a bus stop",
        example="05189"
    )],
) -> BusStop:
    # Get arrival info for the next 3 buses for all lines
    services = await fetch_arrival_info(stop_code)
    first_3_arrivals = get_next_3_arrivals(services)

    # Format arrivals
    arrivals = []
    for arrival in first_3_arrivals:
        arrivals.append(decode_arrival(arrival))
    
    # Construct return
    description = await get_bus_stop_desc(stop_code)
    bus_stop = BusStop(
        stop_code=stop_code,
        description=description,
        next_arrivals=arrivals,
    )

    return bus_stop