#!/usr/bin/env python3
from models import Driver, Destination, Customer, Package, Status
from sqlalchemy import create_engine, select, update, or_
from sqlalchemy.orm import Session
import itertools
import dataclasses


@dataclasses.dataclass
class Point:
    x: int
    y: int


engine = create_engine("sqlite:///fpds.db", echo=False)
with Session(engine) as session:
    # [X] see a list of all packages in the system

    def menu():
        print(
            """
        Select a function:
        1. Show all packages.
        2. Show packages sorted by status.
        3. Show all drivers.
        4. Show packages by selected driver.
        5. Add a new customer.
        6. Add a new destination.
        7. Add a new package.
        8. Update a package's status.
        9. Show packages by customer.
        10. Show packages by destination.

        """
        )
        pass

    def all_drivers():
        return session.scalars(select(Driver))

    def all_packages():
        return session.scalars(select(Package))

    def single_package(search):
        return session.scalars(select(Package).where(Package.id == search))

    def all_customers():
        return session.scalars(select(Customer))

    def single_customer(search):
        return session.scalars(select(Customer).where(Customer.id == search))

    def all_statuses():
        return session.scalars(select(Status))

    def all_destinations():
        return session.scalars(select(Destination))

    def single_destination(search):
        return session.scalars(
            select(Destination).where(Destination.id == search)
        )

    def search_by_customer(search):
        return session.scalars(
            select(Customer).where(
                or_(
                    Customer.name.contains(search),
                    Customer.address.contains(search),
                )
            )
        )

    def search_by_destination(search):
        return session.scalars(
            select(Destination).where(
                or_(
                    Destination.name.contains(search),
                    Destination.address.contains(search),
                )
            )
        )

    def search_packages(search):
        return session.scalars(
            select(Package)
            .join(Package.customer)
            .join(Package.destination)
            .join(Package.driver)
            .where(
                or_(
                    Package.customer.name.contains(search),
                    Package.destination.name.contains(search),
                    Package.driver.name.contains(search),
                )
            )
        )

    # [X] see a list of all packages by status
    def packages_by_status(status_id):
        return session.scalars(
            select(Package, Status)
            .join(Package.status)
            .where(Status.id == status_id)
        )

    def show_all_packages_by_status():
        stmt = select(Package, Status).join(Package.status).order_by(Status.id)
        result = session.execute(stmt)
        for k, g in itertools.groupby(result, lambda x: x[1]):
            print("---------------")
            print(k.name)
            print("---------------")
            for item in list(g):
                print(
                    f"{item[0].id}|\t{item[0].destination.name}|\t{item[0].destination.address}"
                )
            pass
        # for row in session.execute(stmt):
        #     print(f"{row.Status.name} {row.Package.id}")

    # [X] see a list of all packages assigned to them for delivery
    def my_packages(driver_id):
        driver = session.get(Driver, driver_id)
        return driver.driver_packages

    def packages_by_driver(driver_id):
        driver = session.get(Driver, driver_id)
        for package in driver.driver_packages:
            print(
                f"{package.id} | {package.destination.name}, {package.destination.address}"
            )

    # [X] change the status on a package
    def update_package(
        package_id, status_id, customer_id, destination_id, driver_id
    ):
        statement = (
            update(Package)
            .where(Package.id == package_id)
            .values(
                {
                    Package.status_id: status_id,
                    Package.customer_id: customer_id,
                    Package.destination_id: destination_id,
                    Package.driver_id: driver_id,
                }
            )
            .returning(Package)
        )
        result = session.execute(statement).first()
        for row in result:
            print(row.status_id)
        # you have to commit the updates...
        session.commit()

    # [X] create a new customer in the system
    def new_customer(name, address, address_x, address_y):
        new_customer = Customer(
            name=name,
            address=address,
            address_coordinates=Point(address_x, address_y),
        )
        session.add(new_customer)
        session.commit()

    def update_customer(customer_id, customer_name, customer_address):
        statement = (
            update(Customer)
            .where(Customer.id == customer_id)
            .values(
                {
                    Customer.name: customer_name,
                    Customer.address: customer_address,
                }
            )
            .returning(Customer)
        )
        result = session.execute(statement).first()
        # you have to commit the updates...
        session.commit()

    # [ ] create a new destination in the system
    def new_destination(name, address, address_x, address_y):
        new_destination = Destination(
            name=name,
            address=address,
            address_coordinates=Point(address_x, address_y),
        )
        session.add(new_destination)
        session.commit()

    def update_destination(
        destination_id, destination_name, destination_address
    ):
        statement = (
            update(Destination)
            .where(Destination.id == destination_id)
            .values(
                {
                    Destination.name: destination_name,
                    Destination.address: destination_address,
                }
            )
            .returning(Destination)
        )

        # you have to commit the updates...
        session.commit()

    # [X] create a new package to be delivered
    def new_package(status_id, customer_id, destination_id, driver_id):
        new_package = Package(
            status_id=status_id,
            customer_id=customer_id,
            destination_id=destination_id,
            driver_id=driver_id,
        )
        session.add(new_package)
        session.commit()

    # [X] view a list of packages by customer or destination with sorting/filtering by status
    def packages_by_customer(customer_id):
        customer = session.get(Customer, customer_id)
        for package in customer.customer_packages:
            print(
                f"{package.id} | {package.destination.name}, {package.destination.address}"
            )

    # [X] view a list of packages by customer or destination with sorting/filtering by status
    def packages_by_destination(destination_id):
        destination = session.get(Destination, destination_id)
        for package in destination.destination_packages:
            print(f"{package.id} | {package.customer.name}")
