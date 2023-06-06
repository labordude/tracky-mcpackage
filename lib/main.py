#!/usr/bin/env python3
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Input,
    Label,
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
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


class Menu(Static):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("My Packages", classes="menu_item")),
            ListItem(Label("", classes="menu_item")),
            ListItem(Label("Packages", classes="menu_item")),
            ListItem(Label("Customers", classes="menu_item")),
            ListItem(Label("Destinations", classes="menu_item")),
            ListItem(Label("", classes="menu_item")),
            ListItem(Label("Search", classes="menu_item")),
        )


class Content(Widget):
    def compose(self) -> ComposeResult:
        yield Static("hello")

    pass


class TrackyMcPackage(App):
    CSS_PATH = "styles.css"
    TITLE = "Tracky McPackage"
    SUB_TITLE = "We'll get it there...eventually"
    current_driver = reactive(4)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Menu(classes="box", id="sidebar")

        yield Content(classes="box", id="content")

    def on_key(self, event: Key) -> None:
        self.exit()


if __name__ == "__main__":
    app = TrackyMcPackage()
    app.run()
    # drivers = all_drivers()
    # for driver in drivers:
    #     print(driver.name)
