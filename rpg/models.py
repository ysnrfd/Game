from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Item:
    name: str
    description: str
    value: int = 0
    attack_bonus: int = 0
    defense_bonus: int = 0
    heal_amount: int = 0


@dataclass
class Enemy:
    name: str
    hp: int
    attack: int
    defense: int
    xp_reward: int
    gold_reward: int
    description: str = ""


@dataclass
class Quest:
    id: str
    name: str
    description: str
    target_enemy: str
    required_kills: int
    reward_gold: int
    reward_xp: int
    completed: bool = False


@dataclass
class Location:
    key: str
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)
    enemies: List[Enemy] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    quests: List[Quest] = field(default_factory=list)


@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    gold: int = 20
    xp: int = 0
    level: int = 1
    location: str = "town_square"
    inventory: List[Item] = field(default_factory=list)
    equipped_weapon: str = ""
    equipped_armor: str = ""
    kill_log: Dict[str, int] = field(default_factory=dict)
    active_quests: List[Quest] = field(default_factory=list)

    def effective_attack(self) -> int:
        base = self.attack
        for item in self.inventory:
            if item.name == self.equipped_weapon:
                base += item.attack_bonus
        return base

    def effective_defense(self) -> int:
        base = self.defense
        for item in self.inventory:
            if item.name == self.equipped_armor:
                base += item.defense_bonus
        return base
