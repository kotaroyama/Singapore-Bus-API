import asyncio
from datetime import datetime
import json
import os

from dotenv import load_dotenv
import httpx
import redis

load_dotenv()
api_key = os.getenv("API_KEY")
headers = {"AccountKey": api_key}

async def fetch_arrival_info(station_id: str):
    url = f"https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
    params = {"BusStopCode": station_id}
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url, 
            headers=headers,
            params=params,
        )
    r.raise_for_status()
    data = r.json()
    services = data["Services"]
    return services

def get_next_3_arrivals(services):
    first_3_arrivals = []
    for service in services:
        # If the first_3_arrivals list dosn't have any elements yet, initialize 
        # with the first three busses for the first service
        if not first_3_arrivals:
            first_3_arrivals.append((service["ServiceNo"], service["NextBus"]))
            first_3_arrivals.append((service["ServiceNo"], service["NextBus2"]))
            first_3_arrivals.append((service["ServiceNo"], service["NextBus3"]))
        else:
            next_3_busses = [service["NextBus"], service["NextBus2"], service["NextBus3"]]
            for bus in next_3_busses:
                # Skip if the estimated arrival time for the bus is empty.
                if not bus["EstimatedArrival"]:
                    break
                arrival_time = datetime.fromisoformat(bus["EstimatedArrival"])
                for index, arrival in enumerate(first_3_arrivals):
                    # Check if the item in first_3_arrivals is empty
                    if arrival[1]["EstimatedArrival"]:
                        first_arrival_time = datetime.fromisoformat(
                            arrival[1]["EstimatedArrival"]
                        )
                        if arrival_time < first_arrival_time:
                            first_3_arrivals.insert(
                                index,
                                (service["ServiceNo"], bus)
                            )
                            first_3_arrivals.pop()
                            break
                    else:
                        first_3_arrivals[index] = (service["ServiceNo"], bus)
                        break
        
    return first_3_arrivals

async def get_bus_stops():
    # Retrieve cached bus stops
    bus_stops = get_cached_bus_stops()

    # Get bus stops that are not cached and cache them
    new_bus_stops = []
    skip = len(bus_stops)

    # Get frist 5,000 bus stops concurrently if there are no cached bus stops
    #   This is assuming that the total number of bus stops in Singapore never
    #   goes below zero.
    if not skip:
        urls = []
        while skip < 5000:
            url = f"https://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip={skip}"
            urls.append(url)
            skip += 500
        try:
            async with httpx.AsyncClient() as client:
                tasks = [fetch_url(client, url) for url in urls]
                data = await asyncio.gather(*tasks)
        except httpx.HTTPStatusError as e:
            print(e)
            return None

        for item in data:
            new_bus_stops.extend(item["value"])
    
    while True:
        async with httpx.AsyncClient() as client:
            url = f"https://datamall2.mytransport.sg/ltaodataservice/BusStops?$skip={skip}"
            r = await client.get(url, headers=headers)
            r.raise_for_status()
            data = r.json()
        if not data["value"]:
            break
        new_bus_stops.extend(data["value"])
        skip += 500
    cache_bus_stops(new_bus_stops)

    # Combine all the bus stops and return them
    bus_stops.extend(new_bus_stops)
    return bus_stops

async def fetch_url(client, url):
    r = await client.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def cache_bus_stops(bus_stops):
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    for bus_stop in bus_stops:
        r.rpush("bus_stops", json.dumps(bus_stop))
    r.expire("bus_stops",  86400)

def get_cached_bus_stops():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    # Convert raw string back to dictionaries
    raw_bus_stops = r.lrange("bus_stops", 0, -1)
    bus_stops = [json.loads(bus_stop) for bus_stop in raw_bus_stops]
    return bus_stops