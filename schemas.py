from typing import Annotated, List

from pydantic import BaseModel, Field


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

class SingaporeLocation(BaseModel):
    lat: Annotated[float, Field(ge=1.13, le=1.48)]
    lon: Annotated[float, Field(ge=103.59, le=104.05)]