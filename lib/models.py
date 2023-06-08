from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    composite,
    relationship,
)
from typing import List
import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


# declarative base class
class Base(DeclarativeBase):
    pass


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    driver_packages: Mapped[List["Package"]] = relationship(
        back_populates="driver"
    )
    start_location: Mapped[Point] = composite(
        mapped_column("address_x"), mapped_column("address_y")
    )

    def __repr__(self):
        return f"Driver(id={self.id}, name={self.name}, location={self.start_location})"

    pass


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True)
    status_id = mapped_column(ForeignKey("statuses.id"))
    status: Mapped["Status"] = relationship(back_populates="package_statuses")
    customer_id = mapped_column(ForeignKey("customers.id"))
    customer: Mapped["Customer"] = relationship(
        back_populates="customer_packages"
    )
    destination_id = mapped_column(ForeignKey("destinations.id"))
    destination: Mapped["Destination"] = relationship(
        back_populates="destination_packages"
    )
    driver_id = mapped_column(ForeignKey("drivers.id"))
    driver: Mapped["Driver"] = relationship(back_populates="driver_packages")


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    address_coordinates: Mapped[Point] = composite(
        mapped_column("address_x"), mapped_column("address_y")
    )
    destination_packages: Mapped[List["Package"]] = relationship(
        back_populates="destination"
    )

    def __repr__(self):
        return f"Destination(id={self.id},name={self.name}, address={self.address}, coords={self.address_coordinates})"


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    address_coordinates: Mapped[Point] = composite(
        mapped_column("address_x"), mapped_column("address_y")
    )
    customer_packages: Mapped[List["Package"]] = relationship(
        back_populates="customer"
    )

    def __repr__(self):
        return f"Customer(id={self.id},name={self.name} address={self.address}, coords={self.address_coordinates})"

    pass


class Status(Base):
    __tablename__ = "statuses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column()
    package_statuses: Mapped[List["Package"]] = relationship(
        back_populates="status"
    )

    def __repr__(self):
        return f"Status(id={self.id}, name={self.name}, description={self.description})"
