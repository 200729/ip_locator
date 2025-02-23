import os
import threading
import urllib

import requests
from pydantic import BaseModel, ValidationError


class IPStackAPIClientSingleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'IPStackAPIClient':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = IPStackAPIClient(
                        baseurl='http://api.ipstack.com/', access_key=os.getenv('IPSTACK_KEY')
                    )
        return cls._instance


class LocationResponse(BaseModel):
    latitude: float
    longitude: float


class IPStackAPIClientError(Exception):
    pass


class IPStackAPIClient:
    def __init__(self, baseurl: str, access_key: str) -> None:
        self._baseurl = baseurl.rstrip('/') + '/'
        self._access_key = access_key
        self._session = requests.Session()

    def get_location(self, host: str) -> LocationResponse:
        url = self._baseurl + urllib.parse.quote(host)
        try:
            response = self._session.get(
                url,
                params={
                    'access_key': self._access_key,
                    'fields': 'latitude,longitude',
                },
            )
            response.raise_for_status()
            json_data = response.json()
            location_parsed = LocationResponse.model_validate(json_data)
        except requests.RequestException as error:
            raise IPStackAPIClientError(f"Request Error: {error}")
        except ValidationError as error:
            raise IPStackAPIClientError(f"Validation Error: {error}")

        return location_parsed
