from rpg.game import Game


def run() -> None:
    print("=== Legends of the Open Realm ===")
    name = input("Enter your hero name: ").strip() or "Wanderer"
    game = Game(name)
    print(game.load_plugins("plugins"))
    print(game.describe_location())
    print("Type 'help' for commands.\n")

    while game.running:
        try:
            cmd = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting game.")
            break
        print(game.process_command(cmd))


if __name__ == "__main__":
    run()
