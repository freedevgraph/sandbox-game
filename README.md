# Falling Sand Sandbox

A tiny falling-sand game built with [pygame-ce](https://pyga.me/).

## Run

```sh
pip install -r requirements.txt
python game.py
python benchmark.py   # occasional performance check: startup + frame timing
```

## Controls

Press **Tab** to open settings; the world pauses while they are open. The
settings panel switches between two input methods (click an option or press
**M** / **K**):

- **Mouse buttons** – left drops sand, right pours water, middle places stone
- **Number keys** – **1** sand, **2** water, **3** stone, then hold left mouse to
  paint the selected material

The selected material is also shown as a swatch next to the hint line. Choices
are saved to `settings.json` when the game exits, so they are remembered next
time.

Hold a button to keep painting. Sand piles up, water flows around obstacles,
and stone stays put — build dams, funnels, and towers.

## Layout

```
game.py              entry point
benchmark.py         startup + per-frame timing, run occasionally
sandbox/
  config.py          grid/window constants, colours, hint text
  materials.py       material ids, colours, and movement rules
  world.py           particle grid: painting and the simulation step
  renderer.py        grid-to-screen drawing
  input.py           keyboard/mouse events -> world edits
  settings.py        input method + selected material, saved as JSON
  panel.py           the settings overlay
  app.py             pygame setup and the main loop
```

Adding a material means adding an id and a `MaterialSpec` in
`sandbox/materials.py` (plus a target function if it should move), then a
button binding in `sandbox/input.py`. Number-key order follows the material ids,
so new materials are pickable automatically.
