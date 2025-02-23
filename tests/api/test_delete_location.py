import pytest
from fastapi import status

from infrastructure.database.tables import IPLocation, HostnameLocation


@pytest.mark.asyncio
async def test_delete_location_for_url(api_client, mock_database, fixed_timestamp_with_timezone):
    hostname = 'www.somehost.com'
    url = f'https://{hostname}/and/path?query=value'
    entity = HostnameLocation(
        hostname=hostname,
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )
    await mock_database.insert(entity)
    await mock_database.insert(entity)
    assert len(await mock_database.select_all(HostnameLocation)) == 2

    response = api_client.delete('/api/v1/public/delete-location-for-url', params={'url': url})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    hostname_locations = await mock_database.select_all(HostnameLocation)
    assert hostname_locations == []


@pytest.mark.asyncio
async def test_delete_location_for_ip(api_client, mock_database, fixed_timestamp_with_timezone):
    ip = '133.1.1.0'
    entity = IPLocation(
        ip=ip,
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )
    await mock_database.insert(entity)
    assert len(await mock_database.select_all(IPLocation)) == 1

    response = api_client.delete('/api/v1/public/delete-location-for-ip', params={'ip': ip})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    ip_locations = await mock_database.select_all(IPLocation)
    assert ip_locations == []


@pytest.mark.asyncio
async def test_delete_location_twice(api_client, mock_database, fixed_timestamp_with_timezone):
    ip = '133.1.1.0'
    entity = IPLocation(
        ip=ip,
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )
    await mock_database.insert(entity)
    assert len(await mock_database.select_all(IPLocation)) == 1

    for _ in range(2):
        response = api_client.delete('/api/v1/public/delete-location-for-ip', params={'ip': ip})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        ip_locations = await mock_database.select_all(IPLocation)
        assert ip_locations == []
