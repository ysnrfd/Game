from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path
from typing import Callable

from rpg.models import Enemy, Item, Player, Quest
from rpg.world import create_world


class Game:
    def __init__(self, player_name: str):
        self.world = create_world()
        self.player = Player(name=player_name)
        self.running = True
        self.custom_commands: dict[str, Callable[[list[str]], str]] = {}
        self.message_log: list[str] = []

    def log(self, text: str) -> str:
        self.message_log.append(text)
        return text

    @property
    def location(self):
        return self.world[self.player.location]

    def describe_location(self) -> str:
        loc = self.location
        parts = [f"\n== {loc.name} ==", loc.description]
        if loc.enemies:
            parts.append("Enemies: " + ", ".join(enemy.name for enemy in loc.enemies))
        if loc.items:
            parts.append("Items: " + ", ".join(item.name for item in loc.items))
        if loc.quests:
            parts.append("Quests available: " + ", ".join(q.name for q in loc.quests if not q.completed))
        parts.append("Exits: " + ", ".join(loc.exits.keys()))
        return self.log("\n".join(parts))

    def move(self, direction: str) -> str:
        loc = self.location
        if direction not in loc.exits:
            return self.log("You cannot go that way.")
        self.player.location = loc.exits[direction]
        return self.describe_location()

    def take_item(self, item_name: str) -> str:
        loc = self.location
        for i, item in enumerate(loc.items):
            if item.name.lower() == item_name.lower():
                self.player.inventory.append(item)
                del loc.items[i]
                return self.log(f"You picked up {item.name}.")
        return self.log("No such item here.")

    def use_item(self, item_name: str) -> str:
        for i, item in enumerate(self.player.inventory):
            if item.name.lower() == item_name.lower():
                if item.heal_amount <= 0:
                    return self.log("That item cannot be used directly.")
                self.player.hp = min(self.player.max_hp, self.player.hp + item.heal_amount)
                del self.player.inventory[i]
                return self.log(f"You use {item.name} and restore {item.heal_amount} HP.")
        return self.log("Item not in inventory.")

    def equip_item(self, item_name: str) -> str:
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                if item.attack_bonus > 0:
                    self.player.equipped_weapon = item.name
                    return self.log(f"Equipped {item.name} as weapon.")
                if item.defense_bonus > 0:
                    self.player.equipped_armor = item.name
                    return self.log(f"Equipped {item.name} as armor.")
                return self.log("That item cannot be equipped.")
        return self.log("Item not in inventory.")

    def accept_quest(self, quest_name: str) -> str:
        for quest in self.location.quests:
            if quest.name.lower() == quest_name.lower() and not quest.completed:
                if any(q.id == quest.id for q in self.player.active_quests):
                    return self.log("You already accepted that quest.")
                self.player.active_quests.append(
                    Quest(**{k: v for k, v in quest.__dict__.items()})
                )
                return self.log(f"Quest accepted: {quest.name}")
        return self.log("Quest not found.")

    def _progress_quests(self, enemy_name: str) -> list[str]:
        completed_msgs = []
        self.player.kill_log[enemy_name] = self.player.kill_log.get(enemy_name, 0) + 1
        for quest in self.player.active_quests:
            if quest.completed:
                continue
            if quest.target_enemy == enemy_name:
                kills = self.player.kill_log.get(enemy_name, 0)
                if kills >= quest.required_kills:
                    quest.completed = True
                    self.player.gold += quest.reward_gold
                    self.player.xp += quest.reward_xp
                    completed_msgs.append(
                        f"Quest complete: {quest.name} (+{quest.reward_gold} gold, +{quest.reward_xp} XP)"
                    )
        return completed_msgs

    def fight(self, enemy_name: str) -> str:
        loc = self.location
        target_idx = -1
        for i, enemy in enumerate(loc.enemies):
            if enemy.name.lower() == enemy_name.lower():
                target_idx = i
                break
        if target_idx < 0:
            return self.log("No such enemy here.")

        enemy = Enemy(**{k: v for k, v in loc.enemies[target_idx].__dict__.items()})
        combat_log = [f"Combat started against {enemy.name}!"]

        while enemy.hp > 0 and self.player.hp > 0:
            player_damage = max(1, self.player.effective_attack() - enemy.defense + random.randint(-2, 3))
            enemy.hp -= player_damage
            combat_log.append(f"You hit {enemy.name} for {player_damage}. ({max(0, enemy.hp)} hp left)")

            if enemy.hp <= 0:
                break

            enemy_damage = max(1, enemy.attack - self.player.effective_defense() + random.randint(-2, 2))
            self.player.hp -= enemy_damage
            combat_log.append(f"{enemy.name} hits you for {enemy_damage}. ({max(0, self.player.hp)} hp left)")

        if self.player.hp <= 0:
            self.player.hp = self.player.max_hp
            self.player.location = "town_square"
            self.player.gold = max(0, self.player.gold - 15)
            combat_log.append("You were defeated! You wake up in Town Square and lose 15 gold.")
        else:
            del loc.enemies[target_idx]
            self.player.xp += enemy.xp_reward
            self.player.gold += enemy.gold_reward
            combat_log.append(f"You defeated {enemy.name}! +{enemy.xp_reward} XP, +{enemy.gold_reward} gold.")
            combat_log.extend(self._progress_quests(enemy.name))
            self._check_level_up(combat_log)

        return self.log("\n".join(combat_log))

    def _check_level_up(self, combat_log: list[str]) -> None:
        while self.player.xp >= self.player.level * 100:
            self.player.level += 1
            self.player.max_hp += 15
            self.player.hp = self.player.max_hp
            self.player.attack += 3
            self.player.defense += 2
            combat_log.append(f"LEVEL UP! You are now level {self.player.level}.")

    def player_status(self) -> str:
        inv = ", ".join(i.name for i in self.player.inventory) or "(empty)"
        quests = ", ".join(
            f"{q.name} ({'done' if q.completed else 'active'})" for q in self.player.active_quests
        ) or "(none)"
        return self.log(
            "\n".join(
                [
                    f"{self.player.name} - Lv {self.player.level}",
                    f"HP: {self.player.hp}/{self.player.max_hp}",
                    f"ATK/DEF: {self.player.effective_attack()}/{self.player.effective_defense()}",
                    f"XP: {self.player.xp}   Gold: {self.player.gold}",
                    f"Equipped: weapon={self.player.equipped_weapon or '-'} armor={self.player.equipped_armor or '-'}",
                    f"Inventory: {inv}",
                    f"Quests: {quests}",
                ]
            )
        )

    def save(self, file_path: str = "savegame.json") -> str:
        payload = {
            "player": {
                **self.player.__dict__,
                "inventory": [item.__dict__ for item in self.player.inventory],
                "active_quests": [quest.__dict__ for quest in self.player.active_quests],
            },
            "world": {
                key: {
                    "items": [item.__dict__ for item in loc.items],
                    "enemies": [enemy.__dict__ for enemy in loc.enemies],
                    "quests": [quest.__dict__ for quest in loc.quests],
                }
                for key, loc in self.world.items()
            },
        }
        Path(file_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return self.log(f"Game saved to {file_path}.")

    def load(self, file_path: str = "savegame.json") -> str:
        path = Path(file_path)
        if not path.exists():
            return self.log("Save file does not exist.")
        payload = json.loads(path.read_text(encoding="utf-8"))

        p = payload["player"]
        self.player = Player(
            **{
                **p,
                "inventory": [Item(**it) for it in p["inventory"]],
                "active_quests": [Quest(**q) for q in p["active_quests"]],
            }
        )

        for key, state in payload["world"].items():
            loc = self.world[key]
            loc.items = [Item(**it) for it in state["items"]]
            loc.enemies = [Enemy(**e) for e in state["enemies"]]
            loc.quests = [Quest(**q) for q in state["quests"]]

        return self.log(f"Game loaded from {file_path}.")

    def help_text(self) -> str:
        builtins = [
            "look",
            "go <direction>",
            "fight <enemy>",
            "take <item>",
            "use <item>",
            "equip <item>",
            "quest <name>",
            "status",
            "save [file]",
            "load [file]",
            "map",
            "help",
            "quit",
        ]
        custom = sorted(self.custom_commands.keys())
        text = "Commands:\n- " + "\n- ".join(builtins)
        if custom:
            text += "\nPlugin commands:\n- " + "\n- ".join(custom)
        return self.log(text)

    def world_map(self) -> str:
        rows = []
        for loc in self.world.values():
            rows.append(f"{loc.name}: " + ", ".join(f"{d}->{self.world[k].name}" for d, k in loc.exits.items()))
        return self.log("\n".join(rows))

    def add_command(self, name: str, handler: Callable[[list[str]], str]) -> None:
        self.custom_commands[name] = handler

    def load_plugins(self, plugins_dir: str = "plugins") -> str:
        path = Path(plugins_dir)
        if not path.exists():
            return self.log("No plugins directory found; continuing without plugins.")

        loaded = []
        for plugin_file in sorted(path.glob("*.py")):
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            register = getattr(module, "register", None)
            if callable(register):
                register(self)
                loaded.append(plugin_file.stem)

        if loaded:
            return self.log(f"Loaded plugins: {', '.join(loaded)}")
        return self.log("No valid plugins found.")

    def process_command(self, raw: str) -> str:
        raw = raw.strip()
        if not raw:
            return self.log("Enter a command. Type 'help' for options.")

        parts = raw.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in self.custom_commands:
            return self.log(self.custom_commands[cmd](args))

        if cmd == "look":
            return self.describe_location()
        if cmd == "go" and args:
            return self.move(args[0].lower())
        if cmd == "fight" and args:
            return self.fight(" ".join(args))
        if cmd == "take" and args:
            return self.take_item(" ".join(args))
        if cmd == "use" and args:
            return self.use_item(" ".join(args))
        if cmd == "equip" and args:
            return self.equip_item(" ".join(args))
        if cmd == "quest" and args:
            return self.accept_quest(" ".join(args))
        if cmd == "status":
            return self.player_status()
        if cmd == "save":
            return self.save(args[0] if args else "savegame.json")
        if cmd == "load":
            return self.load(args[0] if args else "savegame.json")
        if cmd == "help":
            return self.help_text()
        if cmd == "map":
            return self.world_map()
        if cmd == "quit":
            self.running = False
            return self.log("Farewell, adventurer.")

        return self.log("Unknown command. Type 'help'.")
