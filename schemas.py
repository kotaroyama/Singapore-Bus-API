from typing import List

from pydantic import BaseModel


class Arrival(BaseModel):
    service: str
    minutes: int

class Services(BaseModel):
    services: List[str]

class BusStop(BaseModel):
    stop_code: str
    description: str
    next_arrivals: List[Arrival]

class SearchedBusStop(BaseModel):
    stop_code: str
    description: str
    road_name: str