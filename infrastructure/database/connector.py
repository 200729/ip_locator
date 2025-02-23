import copy
import os
import threading

from sqlalchemy import Engine, event, select, delete
from sqlalchemy.dialects.sqlite.aiosqlite import AsyncAdapt_aiosqlite_connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from infrastructure.database.base import Base
from infrastructure.database.tables import HostnameLocation, IPLocation


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, AsyncAdapt_aiosqlite_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class DatabaseSingleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> 'DatabaseConnector':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = DatabaseConnector(os.getenv('DATABASE_URI'))
        return cls._instance


class DatabaseConnector:
    def __init__(self, uri: str):
        self.engine = create_async_engine(uri)
        self.AsyncSession = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_tables(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def insert(self, entity) -> int:
        entity = copy.deepcopy(entity)
        async with self.AsyncSession() as session:
            try:
                session.add(entity)
                await session.commit()
                return entity.id
            except Exception as error:
                await session.rollback()
                raise error

    async def select_all(self, table):
        async with self.AsyncSession() as session:
            statement = select(table)
            rows = await session.execute(statement)
            result = rows.scalars().all()
            return result

    async def select_by_id(self, table, db_id: int):
        async with self.AsyncSession() as session:
            statement = select(table).where(table.id == db_id)
            rows = await session.execute(statement)
            result = rows.unique().scalar_one_or_none()
            return result

    async def select_by_hostname(self, hostname: str):
        async with self.AsyncSession() as session:
            statement = select(HostnameLocation).where(HostnameLocation.hostname == hostname)
            rows = await session.execute(statement)
            result = rows.scalars().all()
            return result

    async def select_by_ip(self, ip: str):
        async with self.AsyncSession() as session:
            statement = select(IPLocation).where(IPLocation.ip == ip)
            rows = await session.execute(statement)
            result = rows.scalars().all()
            return result

    async def delete_by_id(self, table, db_id: int):
        async with self.AsyncSession() as session:
            try:
                statement = delete(table).where(table.id == db_id)
                await session.execute(statement)
                await session.commit()
            except Exception as error:
                await session.rollback()
                raise error

    async def delete_location_by_hostname(self, hostname: str):
        async with self.AsyncSession() as session:
            try:
                statement = delete(HostnameLocation).where(HostnameLocation.hostname == hostname)
                await session.execute(statement)
                await session.commit()
            except Exception as error:
                await session.rollback()
                raise error

    async def delete_location_by_ip(self, ip: str):
        async with self.AsyncSession() as session:
            try:
                statement = delete(IPLocation).where(IPLocation.ip == ip)
                await session.execute(statement)
                await session.commit()
            except Exception as error:
                await session.rollback()
                raise error
