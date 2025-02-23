from sqlalchemy import Column, Integer, String, Float, DateTime

from infrastructure.database.base import Base, TableBase


class LocationAndTimeMixin:
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)


class IPLocation(Base, TableBase, LocationAndTimeMixin):
    __tablename__ = "ip_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String, index=True, nullable=False)


class HostnameLocation(Base, TableBase, LocationAndTimeMixin):
    __tablename__ = "url_address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String, index=True, nullable=False)
