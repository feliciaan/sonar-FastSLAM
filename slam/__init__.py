from state import State
from hardware import Hardware
import runner


def main():
    hardware = Hardware()
    state = State()
    runner.run(hardware, state)


if __name__ == "__main__":
    main()
