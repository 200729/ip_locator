import pytest
from fastapi import status

from api.models.models import LocationResponseModel, Location
from infrastructure.database.tables import HostnameLocation, IPLocation


@pytest.mark.asyncio
async def test_get_location_for_url(api_client, mock_database, fixed_timestamp):
    hostname = 'www.somehost.com'
    url = f'https://{hostname}/and/path?query=value'
    entity = HostnameLocation(
        hostname=hostname,
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp,
    )
    await mock_database.insert(entity)
    await mock_database.insert(entity)
    assert len(await mock_database.select_all(HostnameLocation)) == 2
    location = Location(latitude=1.1, longitude=2.2, timestamp=fixed_timestamp)
    expected_response = LocationResponseModel(locations=[location, location])

    response = api_client.get('/api/v1/public/get-location-for-url', params={'url': url})

    parsed_response = LocationResponseModel.model_validate(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert parsed_response == expected_response


@pytest.mark.asyncio
async def test_get_location_for_ip(api_client, mock_database, fixed_timestamp):
    ip = '133.1.1.0'
    entity = IPLocation(
        ip=ip,
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp,
    )
    await mock_database.insert(entity)
    await mock_database.insert(entity)
    assert len(await mock_database.select_all(IPLocation)) == 2
    location = Location(latitude=1.1, longitude=2.2, timestamp=fixed_timestamp)
    expected_response = LocationResponseModel(locations=[location, location])

    response = api_client.get('/api/v1/public/get-location-for-ip', params={'ip': ip})

    parsed_response = LocationResponseModel.model_validate(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert parsed_response == expected_response
