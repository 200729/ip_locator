import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from starlette.testclient import TestClient

from infrastructure.database.connector import DatabaseConnector, DatabaseSingleton
from ipstack_client.ipstack_client import LocationResponse, IPStackAPIClientSingleton, IPStackAPIClient
from main import app


@pytest.fixture
def fixed_timestamp_with_timezone():
    return datetime(2022, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def fixed_timestamp():
    return datetime(2022, 1, 1, 12, 0, 0)


@pytest.fixture
def tmp_sqlite_file(tmp_path):
    return tmp_path / 'test.db'


@pytest.fixture
def tmp_sqlite_uri(tmp_sqlite_file):
    return f'sqlite+aiosqlite:///{tmp_sqlite_file}'


@pytest.fixture
def mock_database(tmp_sqlite_uri):
    database = DatabaseConnector(tmp_sqlite_uri)
    asyncio.run(database.create_tables())
    DatabaseSingleton.get_instance = Mock(return_value=database)
    return database


@pytest.fixture
def mock_error_database(tmp_sqlite_uri):
    database = None
    DatabaseSingleton.get_instance = Mock(return_value=database)
    return database


@pytest.fixture
def location():
    return LocationResponse(latitude=1.1, longitude=2.2)


@pytest.fixture
def mock_ip_stack_client(location):
    ip_stack_client = Mock(spec=IPStackAPIClient)
    ip_stack_client.get_location.return_value = location
    IPStackAPIClientSingleton.get_instance = Mock(return_value=ip_stack_client)
    return ip_stack_client


@pytest.fixture
def mock_error_ip_stack_client():
    ip_stack_client = None
    IPStackAPIClientSingleton.get_instance = Mock(return_value=ip_stack_client)
    return ip_stack_client


@pytest.fixture
def api_client():
    client = TestClient(app)
    return client
