from itertools import cycle

from textual.widgets import Button
from textual.widget import Widget
from textual.reactive import Reactive
from textual.views import GridView
from textual.message import Message

from rich.panel import Panel


class GridBox(Widget):
    """Each individual box"""

    mouse_over = Reactive(False)
    is_destination = Reactive(False)
    driver_location = Reactive(False)
    color = ""
    disable = False

    def __init__(self, board, name=None):
        super().__init__(name=name)
        self.board = board

    def render(self) -> Panel:
        if not self.is_selected:
            if self.mouse_over:
                self.color = self.board.current_turn.color
            else:
                self.color = "grey35"
        else:
            if self.winner:
                self.color = "bright_white"

        r = Button("", style=f"on {self.color}")
        return r

    # def toggle_disable(self):
    #     """Used to disable tiles on game over"""
    #     self.disable = not self.disable
    #     self.log(f"toggling myslef {self}")

    def reset_gridbox(self) -> None:
        """Resets tiles"""
        self.toggle_disable()
        self.is_destination = False
        self.driver_location = False
        self.mouse_over = False

    def on_enter(self) -> None:
        if not self.disable:
            self.mouse_over = True

    def on_leave(self) -> None:
        if not self.disable:
            self.mouse_over = False

    def on_click(self) -> None:
        if not self.disable:
            if not self.is_selected:
                self.is_selected = True
                self.board.react_box_click()


class GridBoard(GridView):
    """Grid widget"""

    # set of possoble states after a click is received
    # OPEN = 0
    # WIN = 1
    # TIE = 2

    rows = 50
    columns = 50
    show_end_panel = Reactive(False)

    def __init__(self, destinations: list, driver):
        super().__init__()
        self.destinations = destinations
        self.driver = driver

    # TODO: test speed if made async
    def on_mount(self) -> None:
        self.grid.set_align("center", "top")
        self.grid.set_gap(2, 1)
        self.grid.set_gutter(column=3, row=1)

        # add rows and columns with repeat arg
        self.grid.add_column(name="col", min_size=2, max_size=10, repeat=50)
        self.grid.add_row(name="row", min_size=2, max_size=5, repeat=50)

        self.board = [GridBox(self) for _ in range(self.rows * self.columns)]

        self.grid.place(*self.board)

    def board_access(self, r, c, n):
        """ "Helper function, calculates position in 1D array of board tiles"""
        return self.board[((r * n) + c)]

    def reset_game(self):
        """Resets the game board"""
        for box in self.board:
            box.reset_gridbox()

    def toggle_disable(self):
        """Toggle board interactability"""
        for tile in self.board:
            tile.toggle_disable()

    # def react_box_click(self):
    #     """Handle a TTTBoxClick"""
    #     # TODO: this could possbly be replaced by watchers, action, and compute functions
    #     status, indexes = self.is_winner()
    #     if status is self.WIN:
    #         self.current_turn.add_win()
    #         self.emit_no_wait(GameStatusNote(self, self.current_turn))
    #         self.display_win(indexes)
    #         self.toggle_disable()
    #         # TODO: Show win Panel
    #     elif status is self.TIE:
    #         self.emit_no_wait(GameStatusNote(self))
    #         self.toggle_disable()
    #         # self.display_tie()
    #         # TODO: Show win Panel
    #     else:
    #         self.switch_turns()
