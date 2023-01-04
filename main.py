from bfrl import game_loop, startup


def main() -> None:
    startup.init()
    startup.new()
    game_loop.main()


if __name__ == "__main__":
    main()
