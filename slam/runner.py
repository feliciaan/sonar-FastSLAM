import time


def run(hardware, state):
    while not state.started():
        time.sleep(.1)

    try:
        for update in hardware.updates():
            state.update(update)

    except KeyboardInterrupt:
        pass
