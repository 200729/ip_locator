import pytest
from infrastructure.database.tables import IPLocation


@pytest.mark.asyncio
async def test_insert_to_empty_database(mock_database, fixed_timestamp_with_timezone):
    entity = IPLocation(
        ip='127.0.0.1',
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )

    db_id = await mock_database.insert(entity)

    assert db_id == 1


@pytest.mark.asyncio
async def test_select_by_id(mock_database, fixed_timestamp_with_timezone):
    entity = IPLocation(
        ip='127.0.0.1',
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )
    db_id = await mock_database.insert(entity)

    selected_entity = await mock_database.select_by_id(IPLocation, db_id)

    assert selected_entity.to_content_dict() == entity.to_content_dict()


@pytest.mark.asyncio
async def test_select_by_id_when_id_not_found(mock_database):
    db_id = 99

    selected_entity = await mock_database.select_by_id(IPLocation, db_id)

    assert selected_entity is None


@pytest.mark.asyncio
async def test_delete_by_id(mock_database, fixed_timestamp_with_timezone):
    entity = IPLocation(
        ip='127.0.0.1',
        latitude=1.1,
        longitude=2.2,
        timestamp=fixed_timestamp_with_timezone,
    )
    db_id_1 = await mock_database.insert(entity)
    db_id_2 = await mock_database.insert(entity)
    entities = await mock_database.select_all(IPLocation)
    assert len(entities) == 2

    await mock_database.delete_by_id(IPLocation, db_id_1)

    entities = await mock_database.select_all(IPLocation)
    assert len(entities) == 1
