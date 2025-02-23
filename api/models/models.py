from datetime import datetime

from pydantic import BaseModel


class LocationByIPRequestModel(BaseModel):
    ip: str


class LocationByURLRequestModel(BaseModel):
    url: str


class Location(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime


class LocationResponseModel(BaseModel):
    locations: list[Location]
