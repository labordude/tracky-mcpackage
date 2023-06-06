#!/usr/bin/env python3
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key, Event
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
)
from itertools import cycle
from textual.reactive import reactive, Reactive
from textual.strip import Strip
from textual.screen import Screen
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
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


class Menu(Static):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("My Packages", classes="menu_item")),
            ListItem(Label("Packages", classes="menu_item")),
            ListItem(Label("Customers", classes="menu_item")),
            ListItem(Label("Destinations", classes="menu_item")),
            ListItem(Label("Search", classes="menu_item")),
        )


class Content(Widget):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield ShowDrivers()
            yield ShowPackages()
        # yield ShowCustomers()
        # yield ShowDestinations()


cursors = cycle(["column", "row", "cell"])


class ShowDrivers(Widget):
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


class ShowPackages(Widget):
    def compose(self) -> ComposeResult:
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

    def key_c(self):
        table = self.query_one("#packages", DataTable)
        table.cursor_type = next(cursors)


class ShowCustomers(Widget):
    def compose(self) -> ComposeResult:
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


class ShowDestinations(Widget):
    def compose(self) -> ComposeResult:
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

    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        CSS_PATH = "styles.css"
        TITLE = "Tracky McPackage"
        SUB_TITLE = "We'll get it there...eventually"
        current_driver = reactive(4)

        def compose(self) -> ComposeResult:
            yield Header()
            yield Footer()
            yield Menu(classes="box", id="sidebar")
            yield Content(classes="box", id="content")

        # def on_key(self, event: Key) -> None:
        #     self.exit()


if __name__ == "__main__":
    engine = create_engine("sqlite:///fpds.db")
    with Session(engine) as session:
        app = TrackyMcPackage()
        app.run()
