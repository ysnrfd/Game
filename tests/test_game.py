from rpg.game import Game
from rpg.world import create_world


def test_basic_movement_and_look():
    game = Game("Tester")
    text = game.process_command("look")
    assert "Town Square" in text
    moved = game.process_command("go north")
    assert "Old Forest" in moved


def test_take_equip_and_status():
    game = Game("Tester")
    game.process_command("go east")
    game.process_command("take Leather Armor")
    equip = game.process_command("equip Leather Armor")
    assert "Equipped" in equip
    status = game.process_command("status")
    assert "Leather Armor" in status


def test_save_and_load(tmp_path):
    save = tmp_path / "save.json"
    game = Game("Tester")
    game.process_command("go north")
    game.process_command(f"save {save}")

    other = Game("Other")
    other.process_command(f"load {save}")
    assert other.player.location == "old_forest"


def test_plugin_command_loads():
    game = Game("Tester")
    result = game.load_plugins("plugins")
    assert "campfire_plugin" in result
    out = game.process_command("rest")
    assert "recover" in out


def test_quest_kill_requirements_are_possible_from_world_spawns():
    world = create_world()

    enemy_counts: dict[str, int] = {}
    for location in world.values():
        for enemy in location.enemies:
            enemy_counts[enemy.name] = enemy_counts.get(enemy.name, 0) + 1

    for location in world.values():
        for quest in location.quests:
            available = enemy_counts.get(quest.target_enemy, 0)
            assert available >= quest.required_kills
