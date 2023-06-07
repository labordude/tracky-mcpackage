#!/usr/bin/env python3
import random
from textual.app import App, ComposeResult, RenderResult
from textual.events import Key
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    Header,
    Footer,
    Static,
    ListView,
    ListItem,
    Input,
    Label,
    DataTable
)
from textual import events, on
from textual.reactive import reactive
from textual.strip import Strip
from textual.screen import Screen
from rich.segment import Segment
from rich.style import Style
from textual.widget import Widget
from models import Driver, Destination, Customer, Package, Status
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from itertools import cycle

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
    all_customers
)


@dataclasses.dataclass
class Point:
    x: int
    y: int


class Menu(Static):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("My Packages", classes="menu_item", id="my_packages")),
            ListItem(Label("", classes="menu_item")),
            ListItem(Button("Packages", id = "packages_button", classes="menu_item")),
            ListItem(Button("Customers", id = "customers_button", classes="menu_item")),
            ListItem(Button("Drivers", classes="menu_item", id = "drivers_button")),
            ListItem(Label("Destinations", classes="menu_item")),
            ListItem(Button("Clear Contents", id= "clear_button", classes="menu_item")),
            ListItem(Button("Add", id = "add_button", classes="menu_item")),
            ListItem(Button("exit", id = "exit_button", classes = "button"))
        )
    

    

class Content(Widget):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield ShowDrivers()
            yield ShowPackages()
            
    # def on_click(self) -> ComposeResult:
    #     yield Static("clicked")
    pass

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

class ShowCustomers(Widget):
    def compose(self) -> ComposeResult:
        yield DataTable(id="customers")
        

    def on_mount(self) -> None:
        customers = [customer for customer in all_customers()]

        table = self.query_one("#customers", DataTable)
        table.cursor_type = next(cursors)
        table.zebra_stripes = True
        table.add_columns("id", "name")
        for customer in customers:
            table.add_row(customer.id, customer.name)

    def key_c(self):
        table = self.query_one("#customers", DataTable)
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
    
class AddField(Widget):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter a customer name", id = "new_customer_name"
        )
        yield Input(
            placeholder="Enter a customer address", id = "new_customer_address"
        )
        yield Input(
            placeholder="Enter customer coordinates", id = "new_customer_coords"
        )
        yield Button("Submit Customer", id = "submit_customer")

        yield Label("", id = "below_customer_submit")

        yield Input(
            placeholder="Enter a destination name", id = "new_destination_name"
        )
        yield Input(
            placeholder="Enter a destination address", id = "new_destination_address"
        )
        yield Input(
            placeholder="Enter destination coordinates", id = "new_destination_coords"
        )
        yield Button("Submit Destination", id = "submit_destination")





class TrackyMcPackage(App):
    CSS_PATH = "styles.css"
    TITLE = "Tracky McPackage"
    SUB_TITLE = "We'll get it there...eventually"
    current_driver = reactive(4)
    display = reactive(Content(classes = "box", id = "content"))

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
        self.query_one("#content").mount(packages)
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
        self.query_one("#content").mount(drivers)
        

    def add_customers(self) -> None:
        customers = ShowCustomers()
        packages = self.query("ShowPackages")
        if packages:
            packages.last().remove()
        drivers = self.display.query("ShowDrivers")
        if drivers:
            drivers.last().remove()
        self.query_one("#content").mount(customers)


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
        self.query_one("#content").mount(AddField())

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
            self.query_one("AddField").mount(Label(f"{customer.name}, {customer.address}, {customer.address_coordinates}"))
        if event.button.id == "submit_destination":
            destination = Destination(name=self.query_one("#new_destination_name").value,
                address=self.query_one("#new_destination_address").value,
                address_coordinates=Point(
                    random.randint(1, 50), random.randint(1, 50)))
            self.query_one("#new_destination_name").value = ""
            self.query_one("#new_destination_address").value = ""
            self.query_one("#new_destination_coords").value = ""
            self.query_one("AddField").mount(Label(f"{destination.name}, {destination.address}, {destination.address_coordinates}"))
    
    # @on(Input.Submitted)
    # def customer_name_submitted(self, event: Input.Submitted) -> None:
    #     if event.input.id == "new_customer_name":
    #         new_customer_name = event.value
    #         event.input.value = ""
    #         print(f"{new_customer_name}")
    
        
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Menu(classes="box", id="sidebar")
        yield self.display
        # yield Content(classes = "box", id = "content")
        
    
    

    

        



if __name__ == "__main__":
    app = TrackyMcPackage()
    app.run()
    # drivers = all_drivers()
    # for driver in drivers:
    #     print(driver.name)
