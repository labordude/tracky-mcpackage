#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Customer, Package, Destination, Driver
from typing import List
import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    import ipdb

    x = 10
    ipdb.set_trace()
