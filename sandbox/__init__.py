"""A tiny falling-sand sandbox game built with pygame-ce.

The package is split by responsibility:

- ``config``     window/grid constants and panel colours
- ``materials``  material ids, colours, and movement rules
- ``world``      the particle grid and the simulation step
- ``renderer``   drawing the grid to the screen
- ``input``      mapping keyboard/mouse events to world edits
- ``settings``   input-method preference, persisted as JSON
- ``panel``      the settings overlay
- ``app``        pygame setup and the main loop
"""

from .app import Game
from .world import World

__all__ = ["Game", "World"]
