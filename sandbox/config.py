"""Tunable constants: grid size, window size, and presentation settings."""

GRID_W, GRID_H = 100, 75        # world size, in cells
CELL = 8                        # pixels per cell -> 800x600 window
WIDTH, HEIGHT = GRID_W * CELL, GRID_H * CELL
FPS = 60

BRUSH_RADIUS = 1                # cells painted around the click

CAPTION = "Falling Sand Sandbox"
BG = (18, 18, 28)               # near-black background
HINT_COLOR = (200, 200, 210)
HINT_MARGIN = (8, 24)           # left inset, height above the bottom edge

# Settings overlay
PANEL_WIDTH, PANEL_HEIGHT = 440, 258
PANEL_BG = (32, 32, 46)
PANEL_BORDER = (84, 84, 110)
PANEL_TEXT = (230, 230, 240)
PANEL_MUTED = (155, 155, 175)
PANEL_ACCENT = (232, 196, 96)   # highlight for the active option
