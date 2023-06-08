#!/usr/bin/env python3
import logging
import random
from textual import on, events
from textual.app import App, ComposeResult, RenderResult
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
from rich.align import Align
from rich.box import DOUBLE
from rich.segment import Segment
from rich.panel import Panel
from rich.console import RenderableType, group
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


class Menu(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Button("Home", name="home", id="home", classes="menu")
        yield Button(
            "My Packages", name="my_packages", id="my_packages", classes="menu"
        )
        yield Button(
            "All Packages",
            name="all_packages",
            id="all_packages",
            classes="menu",
        )
        yield Button(
            "Customers",
            name="all_customers",
            id="all_customers",
            classes="menu",
        )
        yield Button(
            "Destinations",
            name="all_destinations",
            id="all_destinations",
            classes="menu",
        )
        yield Button(
            "Add customer",
            name="add_customer",
            id="add_customer",
            classes="menu",
        )
        yield Button(
            "Add destination",
            name="add_destination",
            id="add_destination",
            classes="menu",
        )
        yield Button(
            "Add package",
            name="add_package",
            id="add_package",
            classes="menu",
        )
        yield Button(
            "Exit",
            name="exit_button",
            id="exit_button",
            classes="menu",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit_button":
            app.exit()
        print(self.screen.tree)
        print(self.screen.tree)
        self.screen.query_one(
            "#content_switcher", ContentSwitcher
        ).current = event.button.id


class CurrentDriver(Widget):
    name = reactive("No")

    def __init__(self, driver):
        self.driver = driver

    def render(self) -> str:
        return f"Currently logged on: {self.name}"


MARKDOWN = """\
        # Please login to the system.
        """
EXAMPLE_MARKDOWN = """\
    # Markdown Document

    This is an example of Textual's `Markdown` widget.

    ## Features

    Markdown syntax and extensions are supported.

    - Typography *emphasis*, **strong**, `inline code` etc.
    - Headers
    - Lists (bullet and ordered)
    - Syntax highlighted code blocks
    - Tables!
    """


class Home(Widget):
    # def compose(self) -> ComposeResult:
    #     driver = session.get(Driver, current_driver)
    #     yield Static(self.tree)
    #     yield Label("Choose your login:")
    #     yield Select(
    #         options=((driver.name, driver.id) for driver in all_drivers()),
    #         id="driver_login",
    #         prompt=driver.name,
    #         value=driver.id,
    #     )

    def compose(self) -> ComposeResult:
        with Grid(classes="grid_container"):
            yield Label("Please login", classes="two center max_width")
            # yield Markdown(EXAMPLE_MARKDOWN)
            drivers = [driver for driver in all_drivers()]
            for driver in drivers:
                yield Button(
                    f"{driver.name}",
                    name=f"driver_{driver.id}",
                    id=f"driver_{driver.id}",
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        current_driver = int(event.button.id.split("_")[1])
        print(current_driver)
        self.app.query_one(ShowMyPackages.CreateTable).remove()
        self.app.query_one(ShowMyPackages).mount(ShowMyPackages.CreateTable())
        self.app.query_one(
            "#main_content", TabbedContent
        ).active = "my_packages"
        pass

    def on_select_changed(self, event: Select.Changed) -> None:
        # current_driver = session.get(
        #     Driver, self.query_one("#driver_login").value
        # )
        new_driver = self.query_one("#driver_login").value
        current_driver = session.get(Driver, new_driver)
        # self.query_one(CurrentDriver).name = current_driver.name


class CustomerInfo(Widget):
    name = reactive("name")
    address = reactive("address")
    coord_x = reactive("coord_x")
    coord_y = reactive("coord_y")

    def render(self) -> str:
        return f"Customer(name={self.name},address={self.address}, address_coordinates=Point({self.coord_x}, {self.coord_y}))"


class DisplayGrid(Widget):
    def compose(self) -> None:
        pass


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
        # new_customer(name, address, address_x, address_y)
        new_customer(
            name=self.query_one(CustomerInfo).name,
            address=self.query_one(CustomerInfo).address,
            address_x=self.query_one(CustomerInfo).coord_x,
            address_y=self.query_one(CustomerInfo).coord_y,
        )


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


class DestinationInfo(Widget):
    name = reactive("name")
    address = reactive("address")
    coord_x = reactive("coord_x")
    coord_y = reactive("coord_y")

    def render(self) -> str:
        return f"Destination(name={self.name},address={self.address}, address_coordinates=Point({self.coord_x}, {self.coord_y}))"


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
        new_destination(
            name=self.query_one(DestinationInfo).name,
            address=self.query_one(DestinationInfo).address,
            address_x=self.query_one(DestinationInfo).coord_x,
            address_y=self.query_one(DestinationInfo).coord_y,
        )


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


class ShowMyPackages(Widget):
    def compose(self) -> ComposeResult:
        yield Label(str(current_driver))
        yield self.CreateTable()

    # def on_mount(self) -> None:
    #     packages = [package for package in my_packages(current_driver)]

    #     table = self.query_one("#my_packages", DataTable)
    #     table.cursor_type = "row"
    #     table.zebra_stripes = True
    #     table.add_columns("id", "customer", "destination")
    #     for package in packages:
    #         table.add_row(
    #             package.id, package.customer.name, package.destination.name
    #         )

    class CreateTable(Widget):
        def compose(self) -> ComposeResult:
            yield DataTable(id="my_packages")

        def on_mount(self) -> None:
            packages = [package for package in my_packages(current_driver)]

            table = self.query_one("#my_packages", DataTable)
            table.cursor_type = "row"
            table.zebra_stripes = True
            table.add_columns("id", "customer", "destination")
            for package in packages:
                table.add_row(
                    package.id, package.customer.name, package.destination.name
                )

    # def key_c(self):
    #     table = self.query_one("#my_packages", DataTable)
    #     table.cursor_type = "row"


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
        table.add_columns("id", "status", "customer", "destination", "driver")
        for package in packages:
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
            else:
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
                "id", "status", "customer", "destination", "driver"
            )
            for package in packages:
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

        # print(row_data)
        # app.push_screen(self.UpdatePackage(row_data))

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     print(self.screen.tree)
    #     self.screen.query_one(
    #         "#content_switcher", ContentSwitcher
    #     ).current = event.button.id
    def update_filter(self) -> None:
        packages = [
            package
            for package in all_packages()
            if (
                self.search.upper() in package.customer.name.upper()
                or self.search.upper() in package.destination.name.upper()
            )
        ]

        table = self.query_one("#packages", DataTable)
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


# class ShowPackagesNew(Widget):
#     def compose(self) -> ComposeResult:
#         with Horizontal(id="buttons"):
#             yield Button("All", id="all_packages")
#             yield Button("In Transit", id="in_transit2")
#             yield Button("Lost", id="packages_lost")

#         with ContentSwitcher(initial="all_packages", id="package_filter"):
#             with VerticalScroll(id="all_packages"):
#                 yield DataTable(id="packages")
#             with VerticalScroll(id="in_transit2"):
#                 yield ShowPackagesInTransit()
#             with VerticalScroll(id="packages_lost"):
#                 yield ShowLostAndFound()

#     def on_mount(self) -> None:
#         packages = [package for package in all_packages()]

#         table = self.query_one("#packages", DataTable)
#         table.cursor_type = "row"
#         table.zebra_stripes = True
#         table.add_columns("id", "status", "customer", "destination")
#         for package in packages:
#             table.add_row(
#                 package.id,
#                 package.status.name,
#                 package.customer.name,
#                 package.destination.name,
#             )

#     def on_button_pressed(self, event: Button.Pressed) -> None:
#         print(self.screen.tree)
#         self.screen.query_one(
#             "#package_filter", ContentSwitcher
#         ).current = event.button.id

#     # 1	In Transit
#     # 2	Delivered
#     # 3	Waiting to be picked up
#     # 4	Lost


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


class ShowPackages(Widget):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages")

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id, package.customer.name, package.destination.name
            )

    def sort(self, id):
        return self

    async def on_input_changed(self, message: Input.Changed) -> None:
        pass

    def key_c(self):
        table = self.query_one("#packages", DataTable)
        table.cursor_type = "row"


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
        customers = [customer for customer in search_by_customer(self.search)]
        table = self.query_one("#customers", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        customers = [customer for customer in search_by_customer(self.search)]
        table = self.query_one("#customers", DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def key_c(self):
        table = self.query_one("#customers", DataTable)
        table.cursor_type = "row"


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


class TrackyMcPackage(App):
    CSS_PATH = "styles.css"
    TITLE = "Tracky McPackage"
    SUB_TITLE = "We'll get it there...eventually"
    current_driver = random.randint(1, 8)
    SCREENS = {
        "bsod": BSOD(),
    }
    BINDINGS = [("b", "push_screen('bsod')", "BSOD")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent(
            "Home",
            "My day",
            "Packages",
            "Customers",
            "Destinations",
            id="main_content",
        ):
            with TabPane("Home", id="home"):
                yield Home()
            with TabPane("My day", id="my_packages"):
                yield ShowMyPackages()
                # yield Input(placeholder="Search...", id="search_all_packages")
                # yield DataTable(id="packages", classes="clear_css")
            with TabPane("Packages"):
                with TabbedContent():
                    with TabPane("All", id="all_packages"):
                        yield ShowPackagesNew2()
                    with TabPane("In Transit", id="in_transit"):
                        yield ShowPackagesInTransit()
                    with TabPane("Lost", id="packages_lost"):
                        yield ShowLostAndFound()
                    with TabPane("Add new package", id="add_new_package"):
                        yield AddPackage()
            with TabPane("Customers", id="customers"):
                with TabbedContent():
                    with TabPane("Customers"):
                        yield ShowCustomers()
                    with TabPane("Add new customer"):
                        yield AddCustomer(classes="center")
            with TabPane("Destinations", id="destinations"):
                with TabbedContent():
                    with TabPane("Destinations"):
                        yield ShowDestinations()
                    with TabPane("Add new destination"):
                        yield AddDestination()

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
        logging.debug("Logged via TextualHandler")
        self.log(self.tree)


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        app = TrackyMcPackage()
        app.run()
