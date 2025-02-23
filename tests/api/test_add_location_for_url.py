from datetime import timedelta

import pytest
from fastapi import status
from freezegun import freeze_time

from api.models.models import LocationByURLRequestModel
from infrastructure.database.tables import HostnameLocation


@pytest.mark.asyncio
async def test_add_location_for_url(
    api_client, mock_database, fixed_timestamp_with_timezone, mock_ip_stack_client, location
):
    hostname = 'www.somehost.com'
    request = LocationByURLRequestModel(url=f'https://{hostname}/and/path?query=value')
    expected_ip_location = HostnameLocation(
        id=1,
        hostname=hostname,
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=fixed_timestamp_with_timezone,
    )

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-url', json=request.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    ip_locations = await mock_database.select_all(HostnameLocation)
    assert [ip_location.to_dict() for ip_location in ip_locations] == [expected_ip_location.to_dict()]


@pytest.mark.asyncio
async def test_add_location_for_url_twice(api_client, mock_database, fixed_timestamp, mock_ip_stack_client, location):
    hostname = 'www.somehost.com'
    request = LocationByURLRequestModel(url=f'https://{hostname}/and/path?query=value')
    sending_time = [fixed_timestamp, fixed_timestamp + timedelta(seconds=1)]
    expected_ip_locations = [
        HostnameLocation(
            id=1,
            hostname=hostname,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=sending_time[0],
        ),
        HostnameLocation(
            id=2,
            hostname=hostname,
            latitude=location.latitude,
            longitude=location.longitude,
            timestamp=sending_time[1],
        ),
    ]

    for i, current_time in zip(range(2), sending_time):
        with freeze_time(current_time):
            response = api_client.post('/api/v1/public/add-location-for-url', json=request.model_dump())
        assert response.status_code == status.HTTP_201_CREATED

    ip_locations = await mock_database.select_all(HostnameLocation)
    assert [ip_location.to_dict() for ip_location in ip_locations] == [
        expected_ip_location.to_dict() for expected_ip_location in expected_ip_locations
    ]


@pytest.mark.asyncio
async def test_add_location_for_url_database_error(
    api_client, mock_error_database, fixed_timestamp_with_timezone, mock_ip_stack_client, location
):
    hostname = 'www.somehost.com'
    request = LocationByURLRequestModel(url=f'https://{hostname}/and/path?query=value')

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-url', json=request.model_dump())

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_add_location_for_ip_ipstack_error(
    api_client, mock_database, fixed_timestamp_with_timezone, mock_error_ip_stack_client, location
):
    hostname = 'www.somehost.com'
    request = LocationByURLRequestModel(url=f'https://{hostname}/and/path?query=value')

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-url', json=request.model_dump())

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
