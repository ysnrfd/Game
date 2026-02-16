# Legends of the Open Realm (Text RPG)

A fully featured, text-based, open-world RPG written in Python.

## Features

- Open-world map with many connected regions.
- Turn-based combat with scaling enemies.
- Leveling system with stat growth.
- Inventory, consumables, weapons, armor, and equipment bonuses.
- Quest system with kill objectives and rewards.
- Save/load support (JSON).
- Plugin system for custom commands and gameplay extensions.
- Modular codebase suitable for expansion.

## Run

```bash
python3 main.py
```

## Commands

- `look`
- `go <direction>`
- `fight <enemy>`
- `take <item>`
- `use <item>`
- `equip <item>`
- `quest <name>`
- `status`
- `save [file]`
- `load [file]`
- `map`
- `help`
- `quit`

## Plugin support

Plugins are Python files in `plugins/` that expose:

```python
def register(game):
    ...
```

Within `register(game)`, you can call:

- `game.add_command("name", handler)` to add commands.

See `plugins/campfire_plugin.py` for an example.

## Tests

```bash
python3 -m pytest -q
```
