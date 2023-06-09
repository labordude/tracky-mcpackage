#!/usr/bin/env python3
import six
import sys

sys.modules["sklearn.externals.six"] = six
import mlrose
import numpy as np
import logging
import random
import datetime
from dateutil import tz
from dateutil.relativedelta import *
from textual import on, events
from textual.app import App, ComposeResult, RenderResult
from textual.binding import Binding
from textual.color import Color
from textual.events import Key, Event
from textual.logging import TextualHandler
from textual.message import Message
from textual.containers import (
    Container,
    Grid,
    Vertical,
    Horizontal,
    ScrollableContainer,
    VerticalScroll,
)
from terminaltables import AsciiTable
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Input,
    Label,
    DataTable,
    ContentSwitcher,
    Markdown,
    TabbedContent,
    TabPane,
    Select,
)
from itertools import cycle
from textual.reactive import reactive, Reactive
from textual.strip import Strip
from textual.screen import Screen, ModalScreen
from rich import box
from rich.align import Align
from rich.box import DOUBLE, Box
from rich.segment import Segment
from rich.panel import Panel
from rich.console import RenderableType, group, Console
from rich.style import Style
from rich.table import Table
from rich.text import Text
from textual.widget import Widget
from models import Driver, Destination, Customer, Package, Status
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

import dataclasses
from helpers import (
    all_packages,
    show_all_packages_by_status,
    packages_by_driver,
    new_customer,
    new_destination,
    new_package,
    packages_by_customer,
    packages_by_destination,
    all_drivers,
    all_customers,
    all_destinations,
    my_packages,
    packages_by_status,
    search_by_customer,
    search_by_destination,
    search_packages,
    single_package,
    all_statuses,
    update_package,
    single_customer,
    single_destination,
    update_customer,
    update_destination,
    get_my_packages,
)

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


current_driver = random.randint(1, 8)


# BSOD easter egg
class BSOD(Screen):
    ERROR_TEXT = """
An error has occurred. To continue:

Press Enter to return to Windows, or

Press CTRL+ALT+DEL to restart your computer. If you do this,
you will lose any unsaved information in all open applications.

Error: 0E : 016F : BFF9B3D4
"""
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Static(" Windows ", id="title")
        yield Static(self.ERROR_TEXT)
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


class CurrentDriver(Widget):
    name = reactive("No")

    def __init__(self, driver):
        self.driver = driver

    def render(self) -> str:
        return f"Currently logged on: {self.name}"


# CUSTOMER FUNCTIONS
class CustomerInfo(Widget):
    name = reactive("name")
    address = reactive("address")
    coord_x = reactive("coord_x")
    coord_y = reactive("coord_y")

    def render(self) -> str:
        return f"Customer(name={self.name},address={self.address}, address_coordinates=Point({self.coord_x}, {self.coord_y}))"


class ShowCustomers(Widget):
    search = ""

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Search for a customer",
            id="search_customer",
            classes="search_bar",
        )

        yield DataTable(id="customers")

    def on_mount(self) -> None:
        customers = [customer for customer in all_customers()]

        table = self.query_one("#customers", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    def update_filter(self) -> None:
        try:
            customers = [
                customer for customer in search_by_customer(self.search)
            ]
            table = self.query_one("#customers", DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "name", "address")
            for customer in customers:
                table.add_row(customer.id, customer.name, customer.address)
        except Exception:
            print("Whoops")

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     customers = [customer for customer in search_by_customer(self.search)]
    #     table = self.query_one("#customers", DataTable)
    #     table.clear(columns=True)
    #     table.cursor_type = "row"
    #     table.zebra_stripes = True
    #     table.add_columns("id", "name", "address")
    #     for customer in customers:
    #         table.add_row(customer.id, customer.name, customer.address)

    def key_c(self):
        table = self.query_one("#customers", DataTable)
        table.cursor_type = "row"

    class UpdateCustomer(Widget):
        BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
        """update a package from this screen"""

        def __init__(self, row: list) -> None:
            super().__init__()
            self.customer_id = row[0]
            self.customer_name = row[1]
            self.customer_address = row[2]
            self.row = row

        def compose(self) -> ComposeResult:
            customer = single_customer(self.customer_id).one()

            with Horizontal():
                yield Label(
                    f"Customer: {customer.name}",
                    classes="package_labels",
                )

                yield Input(
                    id="update_customer_name",
                    placeholder=customer.name,
                    classes="update_package_select",
                    value=customer.name,
                )
            with Horizontal():
                yield Label(
                    f"Customer: {customer.address}",
                    classes="package_labels",
                )
                yield Input(
                    id="update_customer_address",
                    classes="update_package_select",
                    placeholder=customer.address,
                    value=customer.address,
                )

            with Horizontal():
                yield Button(
                    "Update",
                    classes="half_screen",
                    variant="primary",
                    id="submit_update",
                )
                yield Button(
                    "Quit",
                    classes="half_screen",
                    variant="default",
                    id="quit_update",
                )

        def on_input_changed(self, event: Input.Changed) -> None:
            self.customer_name = self.query_one("#update_customer_name").value
            self.customer_address = self.query_one(
                "#update_customer_address"
            ).value

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "submit_update":
                self.customer_name = self.query_one(
                    "#update_customer_name"
                ).value
                self.customer_address = self.query_one(
                    "#update_customer_address"
                ).value
                print(
                    f"{self.customer_id}, {self.customer_name}, {self.customer_address}"
                )
                # new_destination(name, address, address_x, address_y)
                update_customer(
                    customer_id=self.customer_id,
                    customer_name=self.customer_name,
                    customer_address=self.customer_address,
                )

            self.parent.mount(self.parent.CreateCustomerTable())
            self.remove()

    class CreateCustomerTable(Widget):
        def compose(self) -> ComposeResult:
            yield DataTable(id="customers")

        def on_mount(self) -> None:
            customers = [customer for customer in all_customers()]
            table = self.query_one("#customers", DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "name", "address")
            for customer in customers:
                table.add_row(customer.id, customer.name, customer.address)

        def on_data_table_row_selected(
            self, event: DataTable.RowSelected
        ) -> None:
            table = self.query_one("#customers", DataTable)
            row_data = table.get_row(row_key=event.row_key)
            self.parent.mount(self.parent.UpdateCustomer(row_data))
            self.remove()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#customers", DataTable)
        row_data = table.get_row(row_key=event.row_key)
        self.mount(self.UpdateCustomer(row_data))
        table.remove()


class AddCustomer(Widget):
    def compose(self) -> ComposeResult:
        with Grid(classes="grid_container"):
            yield Label("Enter the new customer's information", classes="two")

            yield Input(
                placeholder="Enter a customer name",
                id="new_customer_name",
                classes="two",
            )
            yield Input(
                placeholder="Enter a customer address",
                id="new_customer_address",
                classes="two",
            )

            yield Input(
                placeholder="Enter customer x coordinates",
                id="new_customer_coordinates_x",
                classes="half_screen",
            )
            yield Input(
                placeholder="Enter customer y coordinates",
                id="new_customer_coordinates_y",
                classes="half_screen",
            )
            # with Horizontal(classes="btn_container"):
            yield Button(
                "Submit Customer",
                id="btn_submit_customer",
                classes="half_screen",
            )
            yield Button("Quit", id="btn_quit_customer", classes="half_screen")
            yield CustomerInfo(id="customer_info", classes="two")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(CustomerInfo).name = self.query_one(
            "#new_customer_name"
        ).value
        self.query_one(CustomerInfo).address = self.query_one(
            "#new_customer_address"
        ).value
        self.query_one(CustomerInfo).coord_x = self.query_one(
            "#new_customer_coordinates_x"
        ).value
        self.query_one(CustomerInfo).coord_y = self.query_one(
            "#new_customer_coordinates_y"
        ).value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # new_destination(name, address, address_x, address_y)
        self.app.query_one(ShowCustomers).remove()
        if event.button.id == "btn_submit_customer":
            new_customer(
                name=self.query_one(CustomerInfo).name,
                address=self.query_one(CustomerInfo).address,
                address_x=self.query_one(CustomerInfo).coord_x,
                address_y=self.query_one(CustomerInfo).coord_y,
            )
        self.query_one("#new_customer_name").value = ""
        self.query_one("#new_customer_address").value = ""
        self.query_one("#new_customer_coordinates_x").value = ""
        self.query_one("#new_customer_coordinates_y").value = ""

        self.parent.parent.query_one("#all_customers").mount(ShowCustomers())
        self.app.query_one(
            "#customers_content", TabbedContent
        ).active = "all_customers"
        pass


# DESTINATION FUNCTIONS
class DestinationInfo(Widget):
    name = reactive("name")
    address = reactive("address")
    coord_x = reactive("coord_x")
    coord_y = reactive("coord_y")

    def render(self) -> str:
        return f"Destination(name={self.name},address={self.address}, address_coordinates=Point({self.coord_x}, {self.coord_y}))"


class ShowDestinations(Widget):
    search = ""

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Search for a destination",
            id="search_destination",
        )

        yield DataTable(id="destinations")

    def on_mount(self) -> None:
        destinations = [destination for destination in all_destinations()]

        table = self.query_one("#destinations", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for destination in destinations:
            table.add_row(
                destination.id, destination.name, destination.address
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    def update_filter(self) -> None:
        try:
            destinations = [
                destination
                for destination in search_by_destination(self.search)
            ]
            table = self.query_one("#destinations", DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "name", "address")
            for destination in destinations:
                table.add_row(
                    destination.id, destination.name, destination.address
                )
        except Exception:
            print("destinations_update_filter went boom")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        destinations = [
            destination for destination in search_by_destination(self.search)
        ]
        table = self.query_one("#destinations", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for destination in destinations:
            table.add_row(
                destination.id, destination.name, destination.address
            )

    def key_c(self):
        table = self.query_one("#destinations", DataTable)
        table.cursor_type = "row"

    class UpdateDestination(Widget):
        BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
        """update a package from this screen"""

        def __init__(self, row: list) -> None:
            super().__init__()
            self.destination_id = row[0]
            self.destination_name = row[1]
            self.destination_address = row[2]
            self.row = row

        def compose(self) -> ComposeResult:
            destination = single_destination(self.destination_id).one()

            with Horizontal():
                yield Label(
                    f"Destination: {destination.name}",
                    classes="package_labels",
                )

                yield Input(
                    id="update_destination_name",
                    placeholder=destination.name,
                    classes="update_package_select",
                    value=destination.name,
                )
            with Horizontal():
                yield Label(
                    f"Destination: {destination.address}",
                    classes="package_labels",
                )
                yield Input(
                    id="update_destination_address",
                    classes="update_package_select",
                    placeholder=destination.address,
                    value=destination.address,
                )

            with Horizontal():
                yield Button(
                    "Update",
                    classes="half_screen",
                    variant="primary",
                    id="submit_update",
                )
                yield Button(
                    "Quit",
                    classes="half_screen",
                    variant="default",
                    id="quit_update",
                )

        def on_input_changed(self, event: Input.Changed) -> None:
            self.destination_name = self.query_one(
                "#update_destination_name"
            ).value
            self.destination_address = self.query_one(
                "#update_destination_address"
            ).value

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "submit_update":
                self.destination_name = self.query_one(
                    "#update_destination_name"
                ).value
                self.destination_address = self.query_one(
                    "#update_destination_address"
                ).value
                print(
                    f"{self.destination_id}, {self.destination_name}, {self.destination_address}"
                )
                # new_destination(name, address, address_x, address_y)
                update_destination(
                    destination_id=self.destination_id,
                    destination_name=self.destination_name,
                    destination_address=self.destination_address,
                )

            self.parent.mount(self.parent.CreateDestinationTable())
            self.remove()

    class CreateDestinationTable(Widget):
        def compose(self) -> ComposeResult:
            yield DataTable(id="destinations")

        def on_mount(self) -> None:
            destinations = [destination for destination in all_destinations()]
            table = self.query_one("#destinations", DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "name", "address")
            for destination in destinations:
                table.add_row(
                    destination.id, destination.name, destination.address
                )

        def on_data_table_row_selected(
            self, event: DataTable.RowSelected
        ) -> None:
            table = self.query_one("#destinations", DataTable)
            row_data = table.get_row(row_key=event.row_key)
            self.parent.mount(self.parent.UpdateDestination(row_data))
            self.remove()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#destinations", DataTable)
        row_data = table.get_row(row_key=event.row_key)
        self.mount(self.UpdateDestination(row_data))
        table.remove()


class AddDestination(Widget):
    def compose(self) -> ComposeResult:
        with Grid(classes="grid_container"):
            yield Label(
                "Enter the new destination's information", classes="two"
            )

            yield Input(
                placeholder="Enter a destination name",
                id="new_destination_name",
                classes="two",
            )
            yield Input(
                placeholder="Enter a destination address",
                id="new_destination_address",
                classes="two",
            )

            yield Input(
                placeholder="Enter destination x coordinates",
                id="new_destination_coordinates_x",
                classes="half_screen",
            )
            yield Input(
                placeholder="Enter destination y coordinates",
                id="new_destination_coordinates_y",
                classes="half_screen",
            )
            # with Horizontal(classes="btn_container"):
            yield Button(
                "Submit destination",
                id="btn_submit_destination",
                classes="half_screen",
            )
            yield Button(
                "Quit", id="btn_quit_destination", classes="half_screen"
            )
            yield DestinationInfo(id="destination_info", classes="two")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(DestinationInfo).name = self.query_one(
            "#new_destination_name"
        ).value
        self.query_one(DestinationInfo).address = self.query_one(
            "#new_destination_address"
        ).value
        self.query_one(DestinationInfo).coord_x = self.query_one(
            "#new_destination_coordinates_x"
        ).value
        self.query_one(DestinationInfo).coord_y = self.query_one(
            "#new_destination_coordinates_y"
        ).value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # new_destination(name, address, address_x, address_y)
        self.app.query_one(ShowDestinations).remove()
        self.log(self.parent.parent.tree)
        if event.button.id == "btn_submit_destination":
            new_destination(
                name=self.query_one(DestinationInfo).name,
                address=self.query_one(DestinationInfo).address,
                address_x=self.query_one(DestinationInfo).coord_x,
                address_y=self.query_one(DestinationInfo).coord_y,
            )
        self.query_one("#new_destination_name").value = ""
        self.query_one("#new_destination_address").value = ""
        self.query_one("#new_destination_coordinates_x").value = ""
        self.query_one("#new_destination_coordinates_y").value = ""
        self.parent.parent.query_one("#all_destinations").mount(
            ShowDestinations()
        )
        self.app.query_one(
            "#destinations_content", TabbedContent
        ).active = "all_destinations"
        pass


# DRIVER FUNCTIONS
class ShowDrivers(Widget):
    def compose(self) -> ComposeResult:
        yield DataTable(id="drivers")

    def on_mount(self) -> None:
        drivers = [driver for driver in all_drivers()]

        table = self.query_one("#drivers", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name")
        for driver in drivers:
            table.add_row(driver.id, driver.name)


# PACKAGE FUNCTIONS
class PackageInfo(Widget):
    customer = reactive("Customer")
    destination = reactive("Destination")
    driver = reactive("Driver")

    def render(self) -> str:
        return f"{self.customer}\n{self.destination}\n{self.driver}"


class AddPackage(Widget):
    def compose(self) -> ComposeResult:
        yield Label(
            "Select the customer, destination, and driver of the new package"
        )
        # with Horizontal():
        yield Select(
            options=(
                (customer.name, customer) for customer in all_customers()
            ),
            id="select_customer",
            prompt="Select a customer",
            classes="half_screen",
        )
        yield Select(
            options=(
                (destination.address, destination)
                for destination in all_destinations()
            ),
            id="select_destination",
            prompt="Select a destination",
            classes="half_screen",
        )
        yield Select(
            options=((driver.name, driver) for driver in all_drivers()),
            id="select_driver",
            prompt="Select a driver",
            classes="half_screen",
        )
        yield Button("Submit Package", id="submit_package")
        yield PackageInfo(id="package_info")

    def on_select_changed(self, event: Select.Changed) -> None:
        self.query_one(PackageInfo).customer = self.query_one(
            "#select_customer"
        ).value
        self.query_one(PackageInfo).destination = self.query_one(
            "#select_destination"
        ).value
        self.query_one(PackageInfo).driver = self.query_one(
            "#select_driver"
        ).value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        new_package(
            status_id=1,
            customer_id=self.query_one(PackageInfo).customer.id,
            destination_id=self.query_one(PackageInfo).destination.id,
            driver_id=self.query_one(PackageInfo).driver.id,
        )
        self.query_one("#select_customer").value = ""
        self.query_one("#select_destination").value = ""
        self.query_one("#select_driver").value = ""
        self.app.query_one(
            "#package_content", TabbedContent
        ).active = "all_packages"
        pass


class UpdatePackageLabel(Widget):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    """update a package from this screen"""

    # def __init__(self, row: list) -> None:
    #     super().__init__()
    #     self.package_id = row[0]
    #     self.package_status = row[1]
    #     self.package_customer = row[2]
    #     self.package_destination = row[3]
    #     self.package_driver = row[4]
    #     self.row = row

    def compose(self) -> ComposeResult:
        yield Label("This is where you update a package")
        # package = single_package(self.package_id).one()

        # with Horizontal():
        #     yield Label(
        #         f"Status: {package.status.name}",
        #         classes="package_labels",
        #     )
        #     yield Select(
        #         options=(
        #             (status.name, status.id) for status in all_statuses()
        #         ),
        #         id="update_status",
        #         prompt=package.status.name,
        #         classes="update_package_select",
        #         value=package.status.id,
        #     )
        # with Horizontal():
        #     yield Label(
        #         f"Customer: {package.customer.name}",
        #         classes="package_labels",
        #     )

        #     yield Select(
        #         options=(
        #             (
        #                 f"{customer.name} @ {customer.address}",
        #                 customer.id,
        #             )
        #             for customer in all_customers()
        #         ),
        #         id="update_customer",
        #         prompt=package.customer.name,
        #         classes="update_package_select",
        #         value=package.customer.id,
        #     )
        # with Horizontal():
        #     yield Label(
        #         f"Destination: {package.destination.name}",
        #         classes="package_labels",
        #     )
        #     yield Select(
        #         options=(
        #             (destination.name, destination.id)
        #             for destination in all_destinations()
        #         ),
        #         id="update_destination",
        #         classes="update_package_select",
        #         prompt=package.destination.name,
        #         value=package.destination.id,
        #     )

        # with Horizontal():
        #     yield Label(
        #         f"Driver: {package.driver.name}",
        #         classes="package_labels",
        #     )
        #     yield Select(
        #         options=(
        #             (driver.name, driver.id) for driver in all_drivers()
        #         ),
        #         id="update_driver",
        #         classes="update_package_select",
        #         prompt=package.driver.name,
        #         value=package.driver.id,
        #     )
        # with Horizontal():
        #     yield Button(
        #         "Update",
        #         classes="half_screen",
        #         variant="primary",
        #         id="submit_update",
        #     )
        #     yield Button(
        #         "Quit",
        #         classes="half_screen",
        #         variant="default",
        #         id="quit_update",
        #     )

    # def on_select_changed(self, event: Select.Changed) -> None:
    #     self.package_customer = self.query_one("#update_customer").value
    #     self.package_destination = self.query_one(
    #         "#update_destination"
    #     ).value
    #     self.package_driver = self.query_one("#update_driver").value
    #     self.package_status = self.query_one("#update_status").value

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     if event.button.id == "submit_update":
    #         self.package_customer = self.query_one(
    #             "#update_customer"
    #         ).value
    #         self.package_destination = self.query_one(
    #             "#update_destination"
    #         ).value
    #         self.package_driver = self.query_one("#update_driver").value
    #         self.package_status = self.query_one("#update_status").value
    #         print(
    #             f"{self.package_id}, {self.package_customer}, {self.package_destination}, {self.package_driver}, {self.package_status}"
    #         )
    #         # new_destination(name, address, address_x, address_y)
    #         update_package(
    #             package_id=self.package_id,
    #             status_id=self.package_status,
    #             customer_id=self.package_customer,
    #             destination_id=self.package_destination,
    #             driver_id=self.package_driver,
    #         )
    #     else:
    #         self.remove()


class ShowPackagesNew2(Widget):
    search = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages")

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns(
            "id",
            "status",
            "customer",
            "destination",
            "driver",
            "delivery_time",
        )
        for package in packages:
            if package.delivery_time is not None:
                delta = relativedelta(hours=-5)
                corrected_time = (package.delivery_time + delta).strftime(
                    "%x %X"
                )
                table.add_row(
                    package.id,
                    package.status.name,
                    package.customer.name,
                    package.destination.name,
                    package.driver.name,
                    corrected_time,
                )
            else:
                table.add_row(
                    package.id,
                    package.status.name,
                    package.customer.name,
                    package.destination.name,
                    package.driver.name,
                )

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type("#package_filter", TabbedContent).active = tab

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    class UpdatePackage(Widget):
        BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
        """update a package from this screen"""

        def __init__(self, row: list) -> None:
            super().__init__()
            self.package_id = row[0]
            self.package_status = row[1]
            self.package_customer = row[2]
            self.package_destination = row[3]
            self.package_driver = row[4]
            self.package_delivery_time = row[5]
            self.row = row

        def compose(self) -> ComposeResult:
            package = single_package(self.package_id).one()

            with Horizontal():
                yield Label(
                    f"Status: {package.status.name}",
                    classes="package_labels",
                )
                yield Select(
                    options=(
                        (status.name, status.id) for status in all_statuses()
                    ),
                    id="update_status",
                    prompt=package.status.name,
                    classes="update_package_select",
                    value=package.status.id,
                )
            with Horizontal():
                yield Label(
                    f"Customer: {package.customer.name}",
                    classes="package_labels",
                )

                yield Select(
                    options=(
                        (
                            f"{customer.name} @ {customer.address}",
                            customer.id,
                        )
                        for customer in all_customers()
                    ),
                    id="update_customer",
                    prompt=package.customer.name,
                    classes="update_package_select",
                    value=package.customer.id,
                )
            with Horizontal():
                yield Label(
                    f"Destination: {package.destination.name}",
                    classes="package_labels",
                )
                yield Select(
                    options=(
                        (destination.name, destination.id)
                        for destination in all_destinations()
                    ),
                    id="update_destination",
                    classes="update_package_select",
                    prompt=package.destination.name,
                    value=package.destination.id,
                )

            with Horizontal():
                yield Label(
                    f"Driver: {package.driver.name}",
                    classes="package_labels",
                )
                yield Select(
                    options=(
                        (driver.name, driver.id) for driver in all_drivers()
                    ),
                    id="update_driver",
                    classes="update_package_select",
                    prompt=package.driver.name,
                    value=package.driver.id,
                )
            with Horizontal():
                yield Button(
                    "Update",
                    classes="half_screen",
                    variant="primary",
                    id="submit_update",
                )
                yield Button(
                    "Quit",
                    classes="half_screen",
                    variant="default",
                    id="quit_update",
                )

        def on_select_changed(self, event: Select.Changed) -> None:
            self.package_customer = self.query_one("#update_customer").value
            self.package_destination = self.query_one(
                "#update_destination"
            ).value
            self.package_driver = self.query_one("#update_driver").value
            self.package_status = self.query_one("#update_status").value

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "submit_update":
                self.package_customer = self.query_one(
                    "#update_customer"
                ).value
                self.package_destination = self.query_one(
                    "#update_destination"
                ).value
                self.package_driver = self.query_one("#update_driver").value
                self.package_status = self.query_one("#update_status").value
                print(
                    f"{self.package_id}, {self.package_customer}, {self.package_destination}, {self.package_driver}, {self.package_status}"
                )
                # new_destination(name, address, address_x, address_y)
                update_package(
                    package_id=self.package_id,
                    status_id=self.package_status,
                    customer_id=self.package_customer,
                    destination_id=self.package_destination,
                    driver_id=self.package_driver,
                )

            self.parent.mount(self.parent.CreatePackageTable())
            self.remove()

    class CreatePackageTable(Widget):
        def compose(self) -> ComposeResult:
            yield DataTable(id="packages")

        def on_mount(self) -> None:
            packages = [package for package in all_packages()]

            table = self.query_one("#packages", DataTable)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns(
                "id",
                "status",
                "customer",
                "destination",
                "driver",
                "delivery_time",
            )
            for package in packages:
                if package.delivery_time is not None:
                    delta = relativedelta(hours=-5)
                    corrected_time = (package.delivery_time + delta).strftime(
                        "%x %X"
                    )
                    table.add_row(
                        package.id,
                        package.status.name,
                        package.customer.name,
                        package.destination.name,
                        package.driver.name,
                        corrected_time,
                    )
                else:
                    table.add_row(
                        package.id,
                        package.status.name,
                        package.customer.name,
                        package.destination.name,
                        package.driver.name,
                    )

        def on_data_table_row_selected(
            self, event: DataTable.RowSelected
        ) -> None:
            table = self.query_one("#packages", DataTable)
            row_data = table.get_row(row_key=event.row_key)
            self.parent.mount(self.parent.UpdatePackage(row_data))
            self.remove()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#packages", DataTable)
        row_data = table.get_row(row_key=event.row_key)
        self.mount(self.UpdatePackage(row_data))
        table.remove()

    def update_filter(self) -> None:
        try:
            packages = [
                package
                for package in all_packages()
                if (
                    self.search.upper() in package.destination.name.upper()
                    or self.search.upper() in package.driver.name.upper()
                    or self.search.upper() in package.customer.name.upper()
                )
            ]
            table = self.query_one("#packages", DataTable)
            table.clear(columns=True)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns(
                "id",
                "status",
                "customer",
                "destination",
                "driver",
                "delivery_time",
            )
            for package in packages:
                if package.delivery_time is not None:
                    delta = relativedelta(hours=-5)
                    corrected_time = (package.delivery_time + delta).strftime(
                        "%x %X"
                    )
                    table.add_row(
                        package.id,
                        package.status.name,
                        package.customer.name,
                        package.destination.name,
                        package.driver.name,
                        corrected_time,
                    )
                else:
                    table.add_row(
                        package.id,
                        package.status.name,
                        package.customer.name,
                        package.destination.name,
                        package.driver.name,
                    )
        except Exception as err:
            self.log(self.parent.tree)
            print("package_filter_goes_BOOM", err)


class ShowLostAndFound(Widget):
    search = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages_lost")

    def on_mount(self) -> None:
        packages = [package for package in packages_by_status(4)]

        table = self.query_one("#packages_lost", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination", "driver")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
                package.driver.name,
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    def update_filter(self) -> None:
        packages = [
            package
            for package in packages_by_status(4)
            if (
                self.search.upper() in package.customer.name.upper()
                or self.search.upper() in package.destination.name.upper()
            )
        ]

        table = self.query_one("#packages_lost", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination", "driver")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
                package.driver.name,
            )

    def key_c(self):
        table = self.query_one("#packages_lost", DataTable)
        table.cursor_type = "row"


class ShowPackagesInTransit(Widget):
    search = ""

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Search...", id="search_packages", classes="search"
        )
        yield DataTable(id="packages_in_transit")

    def on_mount(self) -> None:
        packages = [package for package in packages_by_status(1)]

        table = self.query_one("#packages_in_transit", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination", "driver")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
                package.driver.name,
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    def update_filter(self) -> None:
        packages = [
            package
            for package in packages_by_status(1)
            if (
                self.search.upper() in package.customer.name.upper()
                or self.search.upper() in package.destination.name.upper()
            )
        ]

        table = self.query_one("#packages_in_transit", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination", "driver")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
                package.driver.name,
            )

    def key_c(self):
        table = self.query_one("#packages_in_transit", DataTable)
        table.cursor_type = "row"


class AddField(Widget):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter a customer name", id="new_customer_name"
        )
        yield Input(
            placeholder="Enter a customer address", id="new_customer_address"
        )
        yield Input(
            placeholder="Enter customer coordinates", id="new_customer_coords"
        )
        yield Button("Submit Customer", id="submit_customer")

        yield Label("", id="below_customer_submit")

        yield Input(
            placeholder="Enter a destination name", id="new_destination_name"
        )
        yield Input(
            placeholder="Enter a destination address",
            id="new_destination_address",
        )
        yield Input(
            placeholder="Enter destination coordinates",
            id="new_destination_coords",
        )
        yield Button("Submit Destination", id="submit_destination")


# class ShowMyPackages(Widget):
#     def compose(self) -> ComposeResult:
#         yield Label(str(current_driver))
#         yield self.CreateTable()

#     def on_mount(self) -> None:
#         packages = [package for package in my_packages(current_driver)]

#         table = self.query_one("#my_packages", DataTable)
#         table.cursor_type = "row"
#         table.zebra_stripes = True
#         table.add_columns("id", "customer", "destination")
#         for package in packages:
#             table.add_row(
#                 package.id, package.customer.name, package.destination.name
#             )

#     class CreateTable(Widget):
#         def compose(self) -> ComposeResult:
#             yield DataTable(id="my_packages")

#         def on_mount(self) -> None:
#             packages = [package for package in my_packages(current_driver)]

#             table = self.query_one("#my_packages", DataTable)
#             table.cursor_type = "row"
#             table.zebra_stripes = True
#             table.add_columns("id", "customer", "destination")
#             for package in packages:
#                 table.add_row(
#                     package.id, package.customer.name, package.destination.name
#                 )

#     # def key_c(self):
#     #     table = self.query_one("#my_packages", DataTable)
#     #     table.cursor_type = "row"


# class ShowPackages(Widget):
#     def compose(self) -> ComposeResult:
#         yield Input(placeholder="Search...", id="search_packages")
#         yield DataTable(id="packages")

#     def on_mount(self) -> None:
#         packages = [package for package in all_packages()]

#         table = self.query_one("#packages", DataTable)
#         table.cursor_type = "row"
#         table.zebra_stripes = True
#         table.add_columns("id", "customer", "destination")
#         for package in packages:
#             table.add_row(
#                 package.id, package.customer.name, package.destination.name
#             )

#     def sort(self, id):
#         return self

#     async def on_input_changed(self, message: Input.Changed) -> None:
#         pass

#     def key_c(self):
#         table = self.query_one("#packages", DataTable)
#         table.cursor_type = "row"


# get package delivery points
class BestPath(Widget):
    deliveries = []

    def compose(self) -> ComposeResult:
        yield Button("Calculate best path", id="btn_best_path")
        yield DataTable(id="destination_stops")

    def on_mount(self) -> None:
        packages = [package for package in get_my_packages(3)]
        packages = packages[0:10]

        for i in range(10):
            self.deliveries.append(
                [
                    packages[i].destination.address_coordinates.x,
                    packages[i].destination.address_coordinates.y,
                ]
            )
        table = self.query_one("#destination_stops", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "coordinate")
        for package in packages:
            table.add_row(
                package.id,
                (
                    package.destination.address_coordinates.x,
                    package.destination.address_coordinates.y,
                ),
            )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        fitness_destinations = mlrose.TravellingSales(coords=self.deliveries)

        # optimization definition
        problem_fit = mlrose.TSPOpt(
            length=len(self.deliveries),
            fitness_fn=fitness_destinations,
            maximize=False,
        )
        # generic geneTic algorithm
        best_state_1, best_fitness_1 = mlrose.genetic_alg(
            problem_fit, random_state=2
        )

        # potentially optimized genetic algorithm
        best_state_2, best_fitness_2 = mlrose.genetic_alg(
            problem_fit, mutation_prob=0.2, max_attempts=100, random_state=2
        )
        await self.mount(
            Label(f"the best order for deliveries is {best_state_1}")
        )


# home function
class Home(Widget):
    def compose(self) -> ComposeResult:
        new_driver = self.app.current_driver

        current_driver = app.current_driver
        driver = session.get(Driver, current_driver)

        yield Label("Welcome to work. Remember you're here forever.")
        yield Label("Choose your login")
        yield Select(
            options=((driver.name, driver.id) for driver in all_drivers()),
            id="driver_login",
            prompt=driver.name,
            value=driver.id,
        )
        # try:
        #     self.query_one("#package_widget").remove()
        # except Exception:
        #     print("No Matches")

        # self.mount(self.ShowMyPackages(id="package_widget"))

    # def compose(self) -> ComposeResult:
    #     with Grid(classes="grid_container"):
    #         yield Label("Please login", classes="two center max_width")
    #         # yield Markdown(EXAMPLE_MARKDOWN)
    #         drivers = [driver for driver in all_drivers()]
    #         for driver in drivers:
    #             yield Button(
    #                 f"{driver.name}",
    #                 name=f"driver_{driver.id}",
    #                 id=f"driver_{driver.id}",
    #             )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        current_driver = int(event.button.id.split("_")[1])
        print(current_driver)
        self.app.query_one(self.ShowMyPackages.CreateTable).remove()
        self.app.query_one(self.ShowMyPackages).mount(
            ShowMyPackages.CreateTable()
        )
        self.app.query_one(
            "#main_content", TabbedContent
        ).active = "my_packages"
        pass

    def on_select_changed(self, event: Select.Changed) -> None:
        # current_driver = session.get(
        #     Driver, self.query_one("#driver_login").value
        # )
        self.new_driver = self.query_one("#driver_login").value
        current_driver = session.get(Driver, self.new_driver)
        try:
            self.query_one("#package_widget").remove()
        except Exception:
            print("No Matches")
        self.mount(self.ShowMyPackages(id="package_widget"))
        # self.query_one(CurrentDriver).name = current_driver.name

    class ShowMyPackages(Widget):
        def compose(self) -> ComposeResult:
            yield Label(str(self.parent.new_driver))
            yield DataTable(id="my_packages")

        def on_mount(self) -> None:
            packages = [
                package for package in my_packages(self.parent.new_driver)
            ]

            table = self.query_one("#my_packages", DataTable)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "status", "customer", "destination")
            for package in packages:
                table.add_row(
                    package.id,
                    package.status.name,
                    package.customer.name,
                    package.destination.name,
                )

        # class CreateTable(Widget):
        #     def compose(self) -> ComposeResult:
        #         yield DataTable(id="my_packages")

        #     def on_mount(self) -> None:
        #         packages = [package for package in my_packages(current_driver)]

        #         table = self.query_one("#my_packages", DataTable)
        #         table.cursor_type = "row"
        #         table.zebra_stripes = True
        #         table.add_columns("id", "customer", "destination")
        #         for package in packages:
        #             table.add_row(
        #                 package.id,
        #                 package.customer.name,
        #                 package.destination.name,
        #             )

        # def key_c(self):
        #     table = self.query_one("#my_packages", DataTable)
        #     table.cursor_type = "row"


class Footer(Widget):
    def compose(self) -> ComposeResult:
        yield Button("Logout", id="btn_logout")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        app.exit()


class Welcome(Screen[int]):
    WELCOME_TEXT = """


# TRACKYMCPACKAGE - WE'LL GET IT THERE...EVENTUALLY

"""
    # drivers_list = [(driver.name, driver.id) for driver in all_drivers()]
    # drivers_list.insert(0, ("Select your name", 0))

    def compose(self) -> ComposeResult:
        yield Static("TrackyMcPackage ", id="title")
        yield Markdown(self.WELCOME_TEXT)
        yield Button("Let's party", classes="btn_welcome")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


# main app class
class TrackyMcPackage(App):
    CSS_PATH = "styles.css"
    TITLE = "Tracky McPackage"
    SUB_TITLE = "We'll get it there...eventually"
    current_driver = reactive(2)
    SCREENS = {"bsod": BSOD(), "welcome": Welcome()}

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", show=False, priority=True),
        Binding("tab", "focus_next", "Focus Next", show=False),
        Binding("shift+tab", "focus_previous", "Focus Previous", show=False),
        Binding("b", "push_screen('bsod')", "egg"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent(
            "Home",
            # "My day",
            "Packages",
            "Customers",
            "Destinations",
            # "Best Path",
            id="main_content",
        ):
            with TabPane("Home", id="home"):
                yield Home()
            # with TabPane("My day", id="my_packages"):
            #     yield ShowMyPackages()
            # yield Input(placeholder="Search...", id="search_all_packages")
            # yield DataTable(id="packages", classes="clear_css")
            with TabPane("Packages"):
                with TabbedContent(id="package_content"):
                    with TabPane("All", id="all_packages"):
                        yield ShowPackagesNew2()
                    with TabPane("In Transit", id="in_transit"):
                        yield ShowPackagesInTransit()
                    with TabPane("Lost", id="packages_lost"):
                        yield ShowLostAndFound()
                    with TabPane("Add new package", id="add_new_package"):
                        yield AddPackage()
            with TabPane("Customers"):
                with TabbedContent(id="customers_content"):
                    with TabPane("Customers", id="all_customers"):
                        yield ShowCustomers()
                    with TabPane("Add new customer"):
                        yield AddCustomer(classes="center")
            with TabPane("Destinations"):
                with TabbedContent(id="destinations_content"):
                    with TabPane("Destinations", id="all_destinations"):
                        yield ShowDestinations()
                    with TabPane("Add new destination"):
                        yield AddDestination()
            with TabPane("BestPath", id="best_path"):
                # yield Label("Coming Soon")
                yield BestPath()
        # with Vertical(id="menu"):
        #     yield Menu(classes="box", id="sidebar")
        # with ContentSwitcher(
        #     initial="home", id="content_switcher", classes="content"
        # ):
        #     yield Home(id="home")
        #     with VerticalScroll(id="my_packages"):
        #         yield ShowMyPackages()
        #     with VerticalScroll(id="all_packages"):
        #         yield ShowPackagesNew2()
        #     with VerticalScroll(id="in_transit"):
        #         yield ShowPackagesInTransit()
        #     with VerticalScroll(id="lost_and_found"):
        #         yield ShowLostAndFound()
        #     with VerticalScroll(id="all_customers"):
        #         yield ShowCustomers()
        #     with VerticalScroll(id="all_destinations"):
        #         yield ShowDestinations()
        #     with VerticalScroll(id="add_customer"):
        #         yield AddCustomer()
        #     with VerticalScroll(id="add_destination"):
        #         yield AddDestination()
        #     with VerticalScroll(id="add_package"):
        #         yield AddPackage()
        #     yield Button("Exit", id="exit_button")

    def on_mount(self) -> None:
        def check_driver_login(driver) -> None:
            print(driver)
            if driver:
                self.current_driver = driver
                print(self.current_driver)

        self.push_screen(Welcome(), check_driver_login)
        logging.debug("Logged via TextualHandler")
        self.log(self.tree)


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        app = TrackyMcPackage()
        app.run()
