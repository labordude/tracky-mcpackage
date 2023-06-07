#!/usr/bin/env python3
import logging
import random
from textual import on
from textual.app import App, ComposeResult, RenderResult
from textual.color import Color
from textual.events import Key, Event
from textual.logging import TextualHandler
from textual.message import Message
from textual.containers import (
    Container,
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
)
from textual.reactive import reactive
from textual.strip import Strip
from textual.screen import Screen
from rich.segment import Segment
from rich.style import Style
from textual.widget import Widget
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
    packages_by_destination,
    all_drivers,
    all_customers,
    all_destinations,
    my_packages,
)

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


current_driver = 4


class MenuButton(Button):
    """A color button."""

    class Clicked(Message):
        """Color selected message."""

        def __init__(self, goal: str) -> None:
            self.goal = goal
            super().__init__()

    def __init__(self, goal: str) -> None:
        self.goal = goal
        super().__init__()

    def on_mount(self) -> None:
        self.styles.margin = (1, 2)
        self.styles.content_align = ("center", "middle")
        self.styles.background = Color.parse("#ffffff33")

    def on_click(self) -> None:
        # The post_message method sends an event to be handled in the DOM
        self.post_message(self.Clicked(self.text))

    def render(self) -> str:
        return str(self.text)


class Menu(VerticalScroll):
    def compose(self) -> ComposeResult:
        # yield ListView(
        #     ListItem(
        #         Label("My Packages"), classes="menu_item", id="my_packages"
        #     ),
        #     ListItem(
        #         Label("Packages"),
        #         classes="menu_item",
        #         name="all_packages",
        #         id="all_packages",
        #     ),
        #     ListItem(
        #         Label("Customers"),
        #         classes="menu_item",
        #         name="all_customers",
        #         id="all_customers",
        #     ),
        #     ListItem(Label("Destinations", classes="menu_item")),
        #     ListItem(
        #         Label(
        #             "Search",
        #             classes="menu_item",
        #             name="all_destinations",
        #             id="all_destinations",
        #         )
        #     ),
        # )
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

    # def on_list_item_clicked(self, event: ListView.Selected) -> None:
    #     print(self.item.id)
    #     self.screen.query_one(
    #         "#content_switcher", ContentSwitcher
    #     ).current = event.item.id

    def on_button_pressed(self, event: Button.Pressed) -> None:
        print(self.screen.tree)
        self.screen.query_one(
            "#content_switcher", ContentSwitcher
        ).current = event.button.id


class Home(Static):
    def compose(self) -> ComposeResult:
        driver = session.get(Driver, current_driver)
        yield Label(f"Hello, {driver.name}")

        pass


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


# class Content(Widget):
#     def compose(self) -> ComposeResult:
#         yield MenuButton("My Packages", goal="MyPackages.Display")
#         yield MenuButton("2", goal="menu2")
#         yield MenuButton("3", goal="menu3")
#         yield MenuButton("4", goal="menu4")
#         pass

#     def on_menu_button_clicked(s, message: MenuButton.Clicked) -> None:
#         for widget in screen.query():
#             print(widget)

# def on_my_packages_pressed(self,event:)
# yield ShowDrivers()
# yield ShowMyPackages()
# yield ShowCustomers()
# yield ShowDestinations()


cursors = cycle(["column", "row", "cell"])


class ShowDrivers(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield DataTable(id="drivers")

    def on_mount(self) -> None:
        drivers = [driver for driver in all_drivers()]

        table = self.query_one("#drivers", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name")
        for driver in drivers:
            table.add_row(driver.id, driver.name)

    def key_c(self):
        table = self.query_one("#drivers", DataTable)
        table.cursor_type = next(cursors)


class ShowMyPackages(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield DataTable(id="my_packages")

    def on_mount(self) -> None:
        packages = [package for package in my_packages(current_driver)]

        table = self.query_one("#my_packages", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id, package.customer.name, package.destination.name
            )

    def key_c(self):
        table = self.query_one("#my_packages", DataTable)
        table.cursor_type = next(cursors)


class ShowPackagesNew(Widget):
    def compose(self) -> ComposeResult:
        with Horizontal(id="buttons"):
            yield Button("All", id="filter_all_packages")
            yield Button("In Transit", id="filter_in_transit")
            yield Button("Waiting", id="filter_to_be_picked_up")

        with ContentSwitcher(initial="packages"):
            with VerticalScroll(id="all_packages"):
                yield DataTable(id="packages")
            with VerticalScroll(id="all_customers"):
                yield ShowCustomers()
            with VerticalScroll(id="all_destinations"):
                yield ShowDestinations()

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id, package.customer.name, package.destination.name
            )


class ShowPackages(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages")

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = next(cursors)
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
        table.cursor_type = next(cursors)


class ShowCustomers(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a customer", id="search_customer")
        yield DataTable(id="customers")

    def on_mount(self) -> None:
        customers = [customer for customer in all_customers()]

        table = self.query_one("#customers", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def key_c(self):
        table = self.query_one("#customers", DataTable)
        table.cursor_type = next(cursors)


class ShowDestinations(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_destination")
        yield DataTable(id="destinations")

    def on_mount(self) -> None:
        destinations = [destination for destination in all_destinations()]

        table = self.query_one("#destinations", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for destination in destinations:
            table.add_row(
                destination.id, destination.name, destination.address
            )

    def key_c(self):
        table = self.query_one("#destinations", DataTable)
        table.cursor_type = next(cursors)


class TrackyMcPackage(App):
    # async def on_load(self) -> None:
    #     await self.bind("ctrl+c", "quit", "Quit")

    # engine = create_engine("sqlite:///fpds.db")
    # with Session(engine) as session:
    CSS_PATH = "styles.css"
    TITLE = "Tracky McPackage"
    SUB_TITLE = "We'll get it there...eventually"
    current_driver = 4
    # display = reactive(Content(classes="box", id="content"))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal(id="menu"):
            yield Menu(classes="box", id="sidebar")
        with ContentSwitcher(
            initial="home", id="content_switcher", classes="content"
        ):
            yield Home(id="home")
            with VerticalScroll(id="my_packages"):
                yield ShowMyPackages()
            with VerticalScroll(id="all_packages"):
                yield ShowPackages()
            with VerticalScroll(id="all_customers"):
                yield ShowCustomers()
            with VerticalScroll(id="all_destinations"):
                yield ShowDestinations()
            with VerticalScroll(id="add_customer"):
                yield AddField()
            # yield Content(classes="box", id="content")

    def remove_content(self) -> None:
        packages = self.query("ShowPackages")
        if packages:
            packages.remove()
        drivers = self.query("ShowDrivers")
        if drivers:
            drivers.remove()

    def add_packages(self) -> None:
        packages = ShowPackages()
        # alternatives = self.query("#drivers")
        # if alternatives:
        #     alternatives.last().remove()
        # self.query_one("#content").mount(packages)
        customers = self.query("ShowCustomers")
        if customers:
            customers.last().remove()
            drivers = self.display.query("ShowDrivers")
        if drivers:
            drivers.last().remove()
        self.query_one("#content_switcher").mount(packages)
        self.display.scroll_visible()

    def add_drivers(self) -> None:
        drivers = ShowDrivers()
        # alternatives = self.query("#packages")
        # if alternatives:
        #     alternatives.last().remove()
        # self.query_one("#content").mount(drivers)
        packages = self.query("ShowPackages")
        if packages:
            packages.last().remove()
        customers = self.query("ShowCustomers")
        if customers:
            customers.last().remove()
        self.query_one("#content_switcher").mount(drivers)

    def add_customers(self) -> None:
        customers = ShowCustomers()
        packages = self.query("ShowPackages")
        if packages:
            packages.last().remove()
        drivers = self.display.query("ShowDrivers")
        if drivers:
            drivers.last().remove()
        self.query_one("#content_switcher").mount(customers)

    def add(self):
        packages = self.query("ShowPackages")
        if packages:
            packages.last().remove()
        drivers = self.display.query("ShowDrivers")
        if drivers:
            drivers.last().remove()
        customers = self.query("ShowCustomers")
        if customers:
            customers.last().remove()
        self.query_one("#content_switcher").mount(AddField())

    @on(Button.Pressed)
    def handle_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "packages_button":
            self.add_packages()
        if event.button.id == "clear_button":
            self.remove_content()
        if event.button.id == "drivers_button":
            self.add_drivers()
        if event.button.id == "customers_button":
            self.add_customers()
        if event.button.id == "add_button":
            self.add()
        if event.button.id == "exit_button":
            self.exit()
        if event.button.id == "submit_customer":
            customer = Customer(
                name=self.query_one("#new_customer_name").value,
                address=self.query_one("#new_customer_address").value,
                address_coordinates=Point(
                    random.randint(1, 50), random.randint(1, 50)
                ),
            )
            # session.add(customer)
            # session.commit()
            self.query_one("#new_customer_name").value = ""
            self.query_one("#new_customer_address").value = ""
            self.query_one("#new_customer_coords").value = ""
            self.query_one("AddField").mount(
                Label(
                    f"{customer.name}, {customer.address}, {customer.address_coordinates}"
                )
            )

        if event.button.id == "submit_destination":
            destination = Destination(
                name=self.query_one("#new_destination_name").value,
                address=self.query_one("#new_destination_address").value,
                address_coordinates=Point(
                    random.randint(1, 50), random.randint(1, 50)
                ),
            )
            self.query_one("#new_destination_name").value = ""
            self.query_one("#new_destination_address").value = ""
            self.query_one("#new_destination_coords").value = ""
            self.query_one("AddField").mount(
                Label(
                    f"{destination.name}, {destination.address}, {destination.address_coordinates}"
                )
            )

        # @on(Input.Submitted)
        # def customer_name_submitted(self, event: Input.Submitted) -> None:
        #     if event.input.id == "new_customer_name":
        #         new_customer_name = event.value
        #         event.input.value = ""
        #         print(f"{new_customer_name}")

    def on_load(self):
        self.log("In the log handler", pi=3.141529)

    def on_mount(self) -> None:
        logging.debug("Logged via TextualHandler")
        self.log(self.tree)

    # def on_key(self, event: Key) -> None:
    #     self.exit()


if __name__ == "__main__":
    app = TrackyMcPackage()
    app.run()
    # drivers = all_drivers()
    # for driver in drivers:
    #     print(driver.name)
