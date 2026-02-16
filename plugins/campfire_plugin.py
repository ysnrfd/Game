"""Example plugin that adds a rest command."""


def register(game):
    def rest(_args):
        healed = max(10, game.player.max_hp // 5)
        game.player.hp = min(game.player.max_hp, game.player.hp + healed)
        return f"You rest at a campfire and recover {healed} HP."

    game.add_command("rest", rest)
