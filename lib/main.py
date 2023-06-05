#!/usr/bin/env python3
from models import Driver, Destination, Customer, Package, Status
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

import dataclasses
from helpers import (
    all_packages,
    show_all_packages_by_status,
    packages_by_driver,
    update_package_status,
    new_customer,
    new_destination,
    new_package,
    packages_by_customer,
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


if __name__ == "__main__":
    # all_packages()
    # packages_by_driver(6)
    # show_all_packages_by_status()
    # update_package_status(14, 3)
    # packages_by_customer(8)
