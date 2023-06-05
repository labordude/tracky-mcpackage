#!/usr/bin/env python3
import ipdb
from faker import Faker
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Customer, Driver, Destination, Package, Status

import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        session.query(Package).delete()
        session.query(Destination).delete()
        session.query(Customer).delete()
        session.query(Driver).delete()
        session.query(Status).delete()
        fake = Faker("en_US")

        status_list = [
            "In Transit",
            "Delivered",
            "Waiting to be picked up",
            "Lost",
        ]
        statuses = []
        for i in range(4):
            status = Status(name=status_list[i], description="")
            session.add(status)
            session.commit()
            statuses.append(status)

        customer_names_list = [
            "Walmart",
            "Target",
            "Amazon",
            "Best Buy",
            "Sony",
            "Apple",
            "Etsy",
        ]
        customers = []
        for i in range(50):
            customer = Customer(
                name=random.choice(customer_names_list),
                address=f"{fake.street_address()} {fake.city()}, TX {fake.zipcode_in_state('TX')} ",
                address_coordinates=Point(
                    random.randint(1, 50), random.randint(1, 50)
                ),
            )
            session.add(customer)
            session.commit()
            customers.append(customer)

        drivers = []
        for i in range(10):
            driver = Driver(
                name=fake.unique.name(),
                start_location=Point(
                    random.randint(1, 50), random.randint(1, 50)
                ),
            )
            session.add(driver)
            session.commit()
            drivers.append(driver)

        destinations = []
        for i in range(50):
            destination = Destination(
                name=fake.unique.name(),
                address=f"{fake.street_address()} {fake.city()}, TX {fake.zipcode_in_state('TX')} ",
                address_coordinates=Point(
                    random.randint(1, 50), random.randint(1, 50)
                ),
            )
            session.add(destination)
            session.commit()
            destinations.append(destination)

        packages = []
        for i in range(500):
            package = Package(
                status_id=random.randint(1, 4),
                customer_id=random.randint(1, 50),
                destination_id=random.randint(1, 50),
                driver_id=random.randint(1, 10),
            )
            session.add(package)
            session.commit()
            packages.append(package)
        session.commit()
        ipdb.set_trace()
        session.close()
