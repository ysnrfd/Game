from __future__ import annotations

from rpg.models import Enemy, Item, Location, Quest


def create_world() -> dict[str, Location]:
    town_square = Location(
        key="town_square",
        name="Town Square",
        description="Merchants shout over each other while adventurers gather around the fountain.",
        exits={"north": "old_forest", "east": "market", "west": "guild_hall", "south": "farmlands"},
        items=[Item("Bread", "A simple loaf restoring 15 HP.", value=3, heal_amount=15)],
    )

    old_forest = Location(
        key="old_forest",
        name="Old Forest",
        description="Tall trees block the sun and strange tracks cut through the mud.",
        exits={"south": "town_square", "north": "ruined_watchtower"},
        enemies=[
            Enemy("Wolf", 30, 8, 2, 20, 12, "A hungry gray wolf."),
            Enemy("Boar", 40, 9, 3, 24, 15, "A massive tusked boar."),
        ],
        items=[Item("Herb", "A medicinal herb restoring 20 HP.", value=5, heal_amount=20)],
        quests=[
            Quest(
                id="q_wolf_hunt",
                name="Wolf Hunt",
                description="Thin out the wolf pack threatening caravans.",
                target_enemy="Wolf",
                required_kills=3,
                reward_gold=40,
                reward_xp=60,
            )
        ],
    )

    ruined_watchtower = Location(
        key="ruined_watchtower",
        name="Ruined Watchtower",
        description="A collapsed tower crawling with bandits and old treasures.",
        exits={"south": "old_forest", "east": "mountain_pass"},
        enemies=[Enemy("Bandit", 55, 12, 4, 35, 30, "A ruthless scavenger.")],
        items=[Item("Iron Sword", "Reliable steel blade.", value=25, attack_bonus=4)],
    )

    market = Location(
        key="market",
        name="Grand Market",
        description="Colorful stalls sell food, potions, and worn gear.",
        exits={"west": "town_square", "east": "harbor"},
        items=[
            Item("Health Potion", "Restores 45 HP.", value=15, heal_amount=45),
            Item("Leather Armor", "Light armor for travelers.", value=18, defense_bonus=3),
        ],
    )

    guild_hall = Location(
        key="guild_hall",
        name="Adventurer Guild",
        description="Quest boards line the walls and veterans trade stories.",
        exits={"east": "town_square", "north": "catacombs"},
        quests=[
            Quest(
                id="q_bandit_leader",
                name="End the Bandits",
                description="Defeat two bandits near the watchtower.",
                target_enemy="Bandit",
                required_kills=2,
                reward_gold=70,
                reward_xp=90,
            )
        ],
    )

    catacombs = Location(
        key="catacombs",
        name="Ancient Catacombs",
        description="Dark corridors echo with undead whispers.",
        exits={"south": "guild_hall", "north": "underground_lake"},
        enemies=[Enemy("Skeleton", 65, 14, 5, 45, 34, "Bones held by cursed magic.")],
        items=[Item("Bone Shield", "A reinforced shield.", value=30, defense_bonus=5)],
    )

    underground_lake = Location(
        key="underground_lake",
        name="Underground Lake",
        description="Bioluminescent water glows beneath vaulted stone.",
        exits={"south": "catacombs"},
        enemies=[Enemy("Cave Serpent", 80, 17, 6, 60, 50, "A venomous giant serpent.")],
    )

    farmlands = Location(
        key="farmlands",
        name="Farmlands",
        description="Wind sweeps over fields where scarecrows keep watch.",
        exits={"north": "town_square", "south": "marsh"},
        enemies=[Enemy("Rogue Scarecrow", 35, 9, 2, 22, 14, "Animated by dark rites.")],
    )

    marsh = Location(
        key="marsh",
        name="Black Marsh",
        description="Mist hovers over pools filled with lurking eyes.",
        exits={"north": "farmlands", "east": "mountain_pass"},
        enemies=[Enemy("Swamp Wraith", 70, 16, 5, 50, 40, "A spirit born from sorrow.")],
    )

    mountain_pass = Location(
        key="mountain_pass",
        name="Mountain Pass",
        description="Narrow cliffs lead to the frozen highlands.",
        exits={"west": "marsh", "south": "ruined_watchtower", "north": "dragon_peak"},
        enemies=[Enemy("Ice Raider", 90, 19, 7, 75, 60, "A mercenary of the cold.")],
        items=[Item("War Axe", "A heavy axe favored by raiders.", value=40, attack_bonus=7)],
    )

    dragon_peak = Location(
        key="dragon_peak",
        name="Dragon Peak",
        description="The summit crackles with ancient fire and thunder.",
        exits={"south": "mountain_pass"},
        enemies=[Enemy("Ancient Drake", 140, 24, 10, 140, 160, "A legendary apex predator.")],
    )

    harbor = Location(
        key="harbor",
        name="Harbor",
        description="Ships from distant islands dock near weathered piers.",
        exits={"west": "market"},
        items=[Item("Sailor's Jacket", "Salt-stained but protective.", value=22, defense_bonus=4)],
    )

    return {
        loc.key: loc
        for loc in [
            town_square,
            old_forest,
            ruined_watchtower,
            market,
            guild_hall,
            catacombs,
            underground_lake,
            farmlands,
            marsh,
            mountain_pass,
            dragon_peak,
            harbor,
        ]
    }
