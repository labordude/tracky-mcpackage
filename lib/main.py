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
    packages_by_status,
    search_by_customer,
    search_by_destination,
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
            "In_Transit",
            name="in_transit",
            id="in_transit",
            classes="menu",
        )
        yield Button(
            "Lost_and_Found",
            name="lost_and_found",
            id="lost_and_found",
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

        # yield ShowCustomers()
        # yield ShowDestinations()


class Submit(Button):
    clicked: Reactive[RenderableType] = Reactive(False)

    def on_click(self) -> None:
        self.clicked = True


class CustomerInfo(Widget):
    name = reactive("name")
    address = reactive("address")
    coord_x = reactive("coord_x")
    coord_y = reactive("coord_y")

    def render(self) -> str:
        return f"Customer(name={self.name},address={self.address}, address_coordinates=Point({self.coord_x}, {self.coord_y}))"


class AddCustomer(Widget):
    def compose(self) -> ComposeResult:
        yield Label("Enter the new customer's information")

        yield Input(
            placeholder="Enter a customer name", id="new_customer_name"
        )
        yield Input(
            placeholder="Enter a customer address", id="new_customer_address"
        )
        with Horizontal():
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

        yield Button("Submit Customer", id="submit_customer")
        yield CustomerInfo(id="customer_info")

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
        yield Label("Enter the new destination's information")

        yield Input(
            placeholder="Enter a destination name", id="new_destination_name"
        )
        yield Input(
            placeholder="Enter a destination address",
            id="new_destination_address",
        )
        with Horizontal():
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

        yield Button("Submit destination", id="submit_destination")
        yield DestinationInfo(id="destination_info")

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


class UpdatePackage(ModalScreen):
    """update a package from this screen"""

    def __init__(self):
        # self.package_id = package_id
        # self.customer = package_customer
        # self.destination = package_dest
        # self.status = package_status
        pass

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Hello!"),
            # Label(str(self.package_id), id="question"),
            # Label(str(self.customer)),
            # Label(str(self.destination)),
            # Label(str(self.status)),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()


class ShowPackagesNew2(Widget):
    def compose(self) -> ComposeResult:
        with TabbedContent("All", "In Transit", "Lost", id="package_filter"):
            yield DataTable(id="packages")
            yield ShowPackagesInTransit()
            yield ShowLostAndFound()

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
            )

    def action_show_tab(self, tab: str) -> None:
        """Switch to a new tab."""
        self.get_child_by_type("#package_filter", TabbedContent).active = tab

    # def on_tabs_tab_activated(self, event: Tabs.Clicked):
    #     pass

    # def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    #     self.app.push_screen("UpdatePackage")

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     print(self.screen.tree)
    #     self.screen.query_one(
    #         "#package_filter", ContentSwitcher
    #     ).current = event.button.id

    # 1	In Transit
    # 2	Delivered
    # 3	Waiting to be picked up
    # 4	Lost


class ShowPackagesNew(Widget):
    SCREENS = {"UpdatePackage": UpdatePackage()}

    def compose(self) -> ComposeResult:
        with Horizontal(id="buttons"):
            yield Button("All", id="all_packages")
            yield Button("In Transit", id="in_transit2")
            yield Button("Lost", id="packages_lost")

        with ContentSwitcher(initial="all_packages", id="package_filter"):
            with VerticalScroll(id="all_packages"):
                yield DataTable(id="packages")
            with VerticalScroll(id="in_transit2"):
                yield ShowPackagesInTransit()
            with VerticalScroll(id="packages_lost"):
                yield ShowLostAndFound()

    def on_mount(self) -> None:
        packages = [package for package in all_packages()]

        table = self.query_one("#packages", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.app.push_screen("UpdatePackage")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        print(self.screen.tree)
        self.screen.query_one(
            "#package_filter", ContentSwitcher
        ).current = event.button.id

    # 1	In Transit
    # 2	Delivered
    # 3	Waiting to be picked up
    # 4	Lost


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


class ShowLostAndFound(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages_lost")

    def on_mount(self) -> None:
        packages = [package for package in packages_by_status(4)]

        table = self.query_one("#packages_lost", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
            )

    def sort(self, id):
        return self

    async def on_input_changed(self, message: Input.Changed) -> None:
        pass

    def key_c(self):
        table = self.query_one("#packages_lost", DataTable)
        table.cursor_type = next(cursors)


class ShowPackagesInTransit(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search...", id="search_packages")
        yield DataTable(id="packages_in_transit")

    def on_mount(self) -> None:
        packages = [package for package in packages_by_status(1)]

        table = self.query_one("#packages_in_transit", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "status", "customer", "destination")
        for package in packages:
            table.add_row(
                package.id,
                package.status.name,
                package.customer.name,
                package.destination.name,
            )

    def sort(self, id):
        return self

    async def on_input_changed(self, message: Input.Changed) -> None:
        pass

    def key_c(self):
        table = self.query_one("#packages_in_transit", DataTable)
        table.cursor_type = next(cursors)


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
    search = ""

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            with Horizontal(classes="search"):
                yield Input(
                    placeholder="Search for a customer", id="search_customer"
                )
                yield Button("Search", id="submit_search_customer")
            yield DataTable(id="customers")

    def on_mount(self) -> None:
        customers = [customer for customer in all_customers()]

        table = self.query_one("#customers", DataTable)
        table.cursor_type = next(cursors)
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
        table.clear()
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        customers = [customer for customer in search_by_customer(self.search)]
        table = self.query_one("#customers", DataTable)
        table.clear()
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name", "address")
        for customer in customers:
            table.add_row(customer.id, customer.name, customer.address)

    def key_c(self):
        table = self.query_one("#customers", DataTable)
        table.cursor_type = next(cursors)


class ShowDestinations(VerticalScroll):
    search = ""

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="search"):
                yield Input(
                    placeholder="Search for a destination",
                    id="search_destination",
                )
                yield Button("Search", id="submit_search_destination")
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

    def on_input_changed(self, event: Input.Changed) -> None:
        self.search = event.value
        self.update_filter()

    def update_filter(self) -> None:
        destinations = [
            destination for destination in search_by_destination(self.search)
        ]
        table = self.query_one("#destinations", DataTable)
        table.clear()
        table.cursor_type = next(cursors)
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
        table.clear()
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
    SCREENS = {"bsod": BSOD(), "UpdatePackage": UpdatePackage()}
    BINDINGS = [("b", "push_screen('bsod')", "BSOD")]
    # display = reactive(Content(classes="box", id="content"))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Horizontal():
            with Vertical(id="menu"):
                yield Menu(classes="box", id="sidebar")
            with ContentSwitcher(
                initial="home", id="content_switcher", classes="content"
            ):
                yield Home(id="home")
                with VerticalScroll(id="my_packages"):
                    yield ShowMyPackages()
                with VerticalScroll(id="all_packages"):
                    yield ShowPackagesNew2()
                with VerticalScroll(id="in_transit"):
                    yield ShowPackagesInTransit()
                with VerticalScroll(id="lost_and_found"):
                    yield ShowLostAndFound()
                with VerticalScroll(id="all_customers"):
                    yield ShowCustomers()
                with VerticalScroll(id="all_destinations"):
                    yield ShowDestinations()
                with VerticalScroll(id="add_customer"):
                    # yield AddField()
                    yield AddCustomer()
                with VerticalScroll(id="add_destination"):
                    yield AddDestination()
            # yield Content(classes="box", id="content")

    # def remove_content(self) -> None:
    #     packages = self.query("ShowPackages")
    #     if packages:
    #         packages.remove()
    #     drivers = self.query("ShowDrivers")
    #     if drivers:
    #         drivers.remove()

    # def add_packages(self) -> None:
    #     packages = ShowPackages()
    #     # alternatives = self.query("#drivers")
    #     # if alternatives:
    #     #     alternatives.last().remove()
    #     # self.query_one("#content").mount(packages)
    #     customers = self.query("ShowCustomers")
    #     if customers:
    #         customers.last().remove()
    #         drivers = self.display.query("ShowDrivers")
    #     if drivers:
    #         drivers.last().remove()
    #     self.query_one("#content_switcher").mount(packages)
    #     self.display.scroll_visible()

    # def add_drivers(self) -> None:
    #     drivers = ShowDrivers()
    #     # alternatives = self.query("#packages")
    #     # if alternatives:
    #     #     alternatives.last().remove()
    #     # self.query_one("#content").mount(drivers)
    #     packages = self.query("ShowPackages")
    #     if packages:
    #         packages.last().remove()
    #     customers = self.query("ShowCustomers")
    #     if customers:
    #         customers.last().remove()
    #     self.query_one("#content_switcher").mount(drivers)

    # def add_customers(self) -> None:
    #     customers = ShowCustomers()
    #     packages = self.query("ShowPackages")
    #     if packages:
    #         packages.last().remove()
    #     drivers = self.display.query("ShowDrivers")
    #     if drivers:
    #         drivers.last().remove()
    #     self.query_one("#content_switcher").mount(customers)

    # def add(self):
    #     packages = self.query("ShowPackages")
    #     if packages:
    #         packages.last().remove()
    #     drivers = self.display.query("ShowDrivers")
    #     if drivers:
    #         drivers.last().remove()
    #     customers = self.query("ShowCustomers")
    #     if customers:
    #         customers.last().remove()
    #     self.query_one("#content_switcher").mount(AddField())

    # @on(Button.Pressed)
    # def handle_button_pressed(self, event: Button.Pressed) -> None:
    #     if event.button.id == "packages_button":
    #         self.add_packages()
    #     if event.button.id == "clear_button":
    #         self.remove_content()
    #     if event.button.id == "drivers_button":
    #         self.add_drivers()
    #     if event.button.id == "customers_button":
    #         self.add_customers()
    #     if event.button.id == "add_button":
    #         self.add()
    #     if event.button.id == "exit_button":
    #         self.exit()
    #     if event.button.id == "submit_customer":
    #         customer = Customer(
    #             name=self.query_one("#new_customer_name").value,
    #             address=self.query_one("#new_customer_address").value,
    #             address_coordinates=Point(
    #                 random.randint(1, 50), random.randint(1, 50)
    #             ),
    #         )
    #         # session.add(customer)
    #         # session.commit()
    #         self.query_one("#new_customer_name").value = ""
    #         self.query_one("#new_customer_address").value = ""
    #         self.query_one("#new_customer_coords").value = ""
    #         self.query_one("AddField").mount(
    #             Label(
    #                 f"{customer.name}, {customer.address}, {customer.address_coordinates}"
    #             )
    #         )

    #     if event.button.id == "submit_destination":
    #         destination = Destination(
    #             name=self.query_one("#new_destination_name").value,
    #             address=self.query_one("#new_destination_address").value,
    #             address_coordinates=Point(
    #                 random.randint(1, 50), random.randint(1, 50)
    #             ),
    #         )
    #         self.query_one("#new_destination_name").value = ""
    #         self.query_one("#new_destination_address").value = ""
    #         self.query_one("#new_destination_coords").value = ""
    #         self.query_one("AddField").mount(
    #             Label(
    #                 f"{destination.name}, {destination.address}, {destination.address_coordinates}"
    #             )
    #         )

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
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        app = TrackyMcPackage()
        app.run()
