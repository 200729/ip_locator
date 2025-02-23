from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Response
from loguru import logger

from api.models.models import LocationByIPRequestModel, LocationByURLRequestModel, LocationResponseModel, Location
from api.routers.dependencies import get_database, get_ip_stack_client
from infrastructure.database.connector import DatabaseConnector
from infrastructure.database.tables import IPLocation, HostnameLocation
from ipstack_client.ipstack_client import IPStackAPIClient
from utils.utils import get_hostname_of_url

router = APIRouter()


@router.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return {'message': 'OK'}


@router.post(
    "/add-location-for-ip", status_code=status.HTTP_201_CREATED, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}}
)
async def add_location_for_ip(
    request: LocationByIPRequestModel,
    database: Annotated[DatabaseConnector, Depends(get_database)],
    ip_stack_client: Annotated[IPStackAPIClient, Depends(get_ip_stack_client)],
):
    timestamp = datetime.now(timezone.utc)

    try:
        location_data = ip_stack_client.get_location(request.ip)
    except Exception as error:
        logger.error(f'Error while retrieving ip {request.ip} location from ipstack: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while retrieving location from ipstack'
        )

    ip_location = IPLocation(
        ip=request.ip, latitude=location_data.latitude, longitude=location_data.longitude, timestamp=timestamp
    )

    try:
        await database.insert(ip_location)
    except Exception as error:
        logger.error(f'Error while inserting ip {ip_location} location in database: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while inserting ip location in database'
        )

    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    "/add-location-for-url", status_code=status.HTTP_201_CREATED, responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}}
)
async def add_location_for_url(
    request: LocationByURLRequestModel,
    database: Annotated[DatabaseConnector, Depends(get_database)],
    ip_stack_client: Annotated[IPStackAPIClient, Depends(get_ip_stack_client)],
):
    timestamp = datetime.now(timezone.utc)

    try:
        hostname = get_hostname_of_url(request.url)
    except Exception as error:
        logger.error(f'Error while retrieving hostname from url {request.url} error: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while retrieving hostname from url'
        )
    try:
        location_data = ip_stack_client.get_location(hostname)
    except Exception as error:
        logger.error(f'Error while retrieving url location {request.url} from ipstack: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while retrieving location from ipstack'
        )

    hostname_location = HostnameLocation(
        hostname=hostname, latitude=location_data.latitude, longitude=location_data.longitude, timestamp=timestamp
    )

    try:
        await database.insert(hostname_location)
    except Exception as error:
        logger.error(f'Error while inserting hostname {hostname} location in database: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while inserting url location in database'
        )

    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "/delete-location-for-ip",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}},
)
async def delete_location_for_ip(ip: str, database: Annotated[DatabaseConnector, Depends(get_database)]):
    try:
        await database.delete_location_by_ip(ip)
    except Exception as error:
        logger.error(f'Error while deleting ip {ip} location in database: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while deleting ip location in database'
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/delete-location-for-url",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}},
)
async def delete_location_for_url(url: str, database: Annotated[DatabaseConnector, Depends(get_database)]):
    try:
        hostname = get_hostname_of_url(url)
    except Exception as error:
        logger.error(f'Error while retrieving hostname from url {url} error: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while retrieving hostname from url'
        )

    try:
        await database.delete_location_by_hostname(hostname)
    except Exception as error:
        logger.error(f'Error while deleting hostname {hostname} location in database: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error while deleting hostname location in database',
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/get-location-for-ip", responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}})
async def get_location_for_ip(
    ip: str, database: Annotated[DatabaseConnector, Depends(get_database)]
) -> LocationResponseModel:
    try:
        results = await database.select_by_ip(ip)
    except Exception as error:
        logger.error(f'Database error: {error}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Database error')

    locations = LocationResponseModel(
        locations=[
            Location(latitude=result.latitude, longitude=result.longitude, timestamp=result.timestamp)
            for result in results
        ]
    )

    return locations


@router.get("/get-location-for-url", responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {}})
async def get_location_for_url(
    url: str, database: Annotated[DatabaseConnector, Depends(get_database)]
) -> LocationResponseModel:
    try:
        hostname = get_hostname_of_url(url)
    except Exception as error:
        logger.error(f'Error while retrieving hostname from url {url} error: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error while retrieving hostname from url'
        )

    try:
        results = await database.select_by_hostname(hostname)
    except Exception as error:
        logger.error(f'Database error: {error}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Database error')

    locations = LocationResponseModel(
        locations=[
            Location(latitude=result.latitude, longitude=result.longitude, timestamp=result.timestamp)
            for result in results
        ]
    )

    return locations
