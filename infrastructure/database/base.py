from abc import abstractmethod

from loguru import logger
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class TableBase:
    @abstractmethod
    def to_dict(self) -> dict:
        return self._to_dict()

    @abstractmethod
    def to_content_dict(self) -> dict:
        table_dict = self._to_dict()
        table_dict.pop('id', None)
        return table_dict

    def _to_dict(self):
        table_dict = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime) and value.tzinfo is None:
                logger.warning('No timezone info found in database. Assuming UTC.')
                value = value.replace(tzinfo=timezone.utc)
            table_dict[column.name] = value
        return table_dict
