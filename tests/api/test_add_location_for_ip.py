import pytest
from fastapi import status
from freezegun import freeze_time

from api.models.models import LocationByIPRequestModel
from infrastructure.database.tables import IPLocation


@pytest.mark.asyncio
async def test_add_location_for_ip(
    api_client, mock_database, fixed_timestamp_with_timezone, mock_ip_stack_client, location
):
    request = LocationByIPRequestModel(ip='120.1.1.1')
    expected_ip_location = IPLocation(
        id=1,
        ip=request.ip,
        latitude=location.latitude,
        longitude=location.longitude,
        timestamp=fixed_timestamp_with_timezone,
    )

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-ip', json=request.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    ip_locations = await mock_database.select_all(IPLocation)
    assert [ip_location.to_dict() for ip_location in ip_locations] == [expected_ip_location.to_dict()]


@pytest.mark.asyncio
async def test_add_location_for_ip_database_error(
    api_client, mock_error_database, fixed_timestamp_with_timezone, mock_ip_stack_client, location
):
    request = LocationByIPRequestModel(ip='120.1.1.1')

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-ip', json=request.model_dump())

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_add_location_for_ip_ipstack_error(
    api_client, mock_database, fixed_timestamp_with_timezone, mock_error_ip_stack_client, location
):
    request = LocationByIPRequestModel(ip='120.1.1.1')

    with freeze_time(fixed_timestamp_with_timezone):
        response = api_client.post('/api/v1/public/add-location-for-ip', json=request.model_dump())

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
