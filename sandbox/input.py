"""Mapping keyboard and mouse input to world edits.

Mouse-button mode binds a material to each button; number-key mode binds a
material to each digit and paints it with the left button. Which mode is active
lives in :class:`sandbox.settings.Settings`.
"""

import pygame

from .config import CELL
from .materials import Material
from .settings import InputMode, Settings, material_for_number
from .world import World

# Mouse buttons that place a material on click, in mouse-button mode.
BUTTON_MATERIALS = {
    pygame.BUTTON_LEFT: Material.SAND,
    pygame.BUTTON_RIGHT: Material.WATER,
    pygame.BUTTON_MIDDLE: Material.STONE,
}

# Held buttons in mouse-button mode: index in pygame.mouse.get_pressed() -> material.
HELD_MATERIALS = {
    0: Material.SAND,    # left
    1: Material.STONE,   # middle
    2: Material.WATER,   # right
}

# Number keys (and keypad equivalents) that pick a material in number-key mode.
NUMBER_KEYS = {
    pygame.K_1: 1,
    pygame.K_2: 2,
    pygame.K_3: 3,
    pygame.K_KP1: 1,
    pygame.K_KP2: 2,
    pygame.K_KP3: 3,
}


def number_from_key(key: int) -> int | None:
    """The 1-based number bound to a key, or None for any other key."""
    return NUMBER_KEYS.get(key)


def cell_at(pos: tuple[int, int]) -> tuple[int, int]:
    """Convert window pixel coordinates to grid cell coordinates."""
    return pos[0] // CELL, pos[1] // CELL


def material_for_click(button: int, settings: Settings) -> Material | None:
    """Which material a mouse button places under the current input mode."""
    if settings.input_mode is InputMode.MOUSE:
        return BUTTON_MATERIALS.get(button)
    if button == pygame.BUTTON_LEFT:
        return settings.selected
    return None


def handle_event(event: pygame.event.Event, world: World, settings: Settings) -> None:
    """Apply one gameplay event (window events such as QUIT are the loop's job)."""
    if event.type == pygame.KEYDOWN and settings.input_mode is InputMode.KEYBOARD:
        material = material_for_number(number_from_key(event.key))
        if material is not None:
            settings.selected = material
    elif event.type == pygame.MOUSEBUTTONDOWN:
        material = material_for_click(event.button, settings)
        if material is not None:
            gx, gy = cell_at(event.pos)
            world.paint(gx, gy, material)


def paint_from_held_buttons(
    world: World, pressed: tuple[bool, ...], settings: Settings
) -> None:
    """Paint under the cursor while a mouse button is held down."""
    if settings.input_mode is InputMode.KEYBOARD:
        if pressed[0]:
            gx, gy = cell_at(pygame.mouse.get_pos())
            world.paint(gx, gy, settings.selected)
        return

    for button, material in HELD_MATERIALS.items():
        if pressed[button]:
            gx, gy = cell_at(pygame.mouse.get_pos())
            world.paint(gx, gy, material)
            break
