from __future__ import annotations

from typing import Any

from textual.app import ComposeResult
from textual.timer import Timer
from textual.widgets import Static

from vibe.cli.textual_ui.widgets.braille_renderer import render_braille

WIDTH = 22
HEIGHT = 12
# Honeycomb hive structure with hexagonal cells
STARTING_DOTS = [
    set[int](),
    {5, 6, 7, 8, 15, 16, 17, 18},
    {4, 9, 14, 19},
    {3, 4, 8, 9, 13, 14, 18, 19},
    {3, 9, 13, 19},
    {2, 3, 4, 8, 9, 10, 12, 13, 14, 18, 19, 20},
    {2, 10, 12, 20},
    {2, 3, 4, 8, 9, 10, 12, 13, 14, 18, 19, 20},
    {3, 9, 13, 19},
    {3, 4, 8, 9, 13, 14, 18, 19},
    {4, 9, 14, 19},
    set[int](),
]

# Bee flying around the hive - position 1
BEE_POS_1 = {
    "remove": set[int](),
    "add": {1j + 11, 1j + 12, 2j + 10, 2j + 13}
}
BEE_CLEAR_1 = {
    "remove": {1j + 11, 1j + 12, 2j + 10, 2j + 13},
    "add": set[int]()
}

# Bee flying - position 2
BEE_POS_2 = {
    "remove": set[int](),
    "add": {2j + 21, 3j + 20, 3j + 21}
}
BEE_CLEAR_2 = {
    "remove": {2j + 21, 3j + 20, 3j + 21},
    "add": set[int]()
}

# Bee flying - position 3
BEE_POS_3 = {
    "remove": set[int](),
    "add": {8j + 1, 8j + 2, 9j + 0, 9j + 3}
}
BEE_CLEAR_3 = {
    "remove": {8j + 1, 8j + 2, 9j + 0, 9j + 3},
    "add": set[int]()
}

# Bee flying - position 4
BEE_POS_4 = {
    "remove": set[int](),
    "add": {9j + 21, 10j + 20, 10j + 21}
}
BEE_CLEAR_4 = {
    "remove": {9j + 21, 10j + 20, 10j + 21},
    "add": set[int]()
}

# Honeycomb cell pulse animation
CELL_PULSE_1 = {
    "remove": {5j + 5, 5j + 6, 5j + 7},
    "add": {4j + 5, 4j + 6, 4j + 7, 6j + 5, 6j + 6, 6j + 7}
}
CELL_PULSE_1_BACK = {
    "remove": {4j + 5, 4j + 6, 4j + 7, 6j + 5, 6j + 6, 6j + 7},
    "add": {5j + 5, 5j + 6, 5j + 7}
}

CELL_PULSE_2 = {
    "remove": {5j + 15, 5j + 16, 5j + 17},
    "add": {4j + 15, 4j + 16, 4j + 17, 6j + 15, 6j + 16, 6j + 17}
}
CELL_PULSE_2_BACK = {
    "remove": {4j + 15, 4j + 16, 4j + 17, 6j + 15, 6j + 16, 6j + 17},
    "add": {5j + 15, 5j + 16, 5j + 17}
}

WAIT = {"remove": set[int](), "add": set[int]()}

TRANSITIONS = [
    BEE_POS_1,
    WAIT,
    CELL_PULSE_1,
    WAIT,
    BEE_POS_2,
    WAIT,
    CELL_PULSE_1_BACK,
    BEE_CLEAR_1,
    WAIT,
    CELL_PULSE_2,
    BEE_POS_3,
    WAIT,
    BEE_CLEAR_2,
    CELL_PULSE_2_BACK,
    WAIT,
    BEE_POS_4,
    WAIT,
    BEE_CLEAR_3,
    CELL_PULSE_1,
    WAIT,
    BEE_CLEAR_4,
    CELL_PULSE_1_BACK,
    WAIT,
]
# cf render_braille() docstring for coordinates convention


class PetitChat(Static):
    """Animated hive with bees flying around - HiveTerminal branding."""
    def __init__(self, animate: bool = True, **kwargs: Any) -> None:
        super().__init__(**kwargs, classes="banner-chat")
        self._dots = {1j * y + x for y, row in enumerate(STARTING_DOTS) for x in row}
        self._transition_index = 0
        self._do_animate = animate
        self._freeze_requested = False
        self._timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static(render_braille(self._dots, WIDTH, HEIGHT), classes="petit-chat")

    def on_mount(self) -> None:
        self._inner = self.query_one(".petit-chat", Static)
        if self._do_animate:
            self._timer = self.set_interval(0.16, self._apply_next_transition)

    def freeze_animation(self) -> None:
        self._freeze_requested = True

    def _apply_next_transition(self) -> None:
        if self._freeze_requested and self._transition_index == 0:
            if self._timer:
                self._timer.stop()
            self._timer = None
            return

        transition = TRANSITIONS[self._transition_index]
        self._dots -= transition["remove"]
        self._dots |= transition["add"]
        self._transition_index = (self._transition_index + 1) % len(TRANSITIONS)
        self._inner.update(render_braille(self._dots, WIDTH, HEIGHT))
