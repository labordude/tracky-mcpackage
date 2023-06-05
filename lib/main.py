#!/usr/bin/env python3
from models import Driver, Destination, Customer, Package
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        statement = select(Driver).where(Driver.driver_id < 10)

        result = session.scalars(statement)

        for driver in result:
            print(driver.name())
