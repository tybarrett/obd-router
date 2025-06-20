"""obd_tester.py - attempts to fetch OBD data from the vehicle."""

import time
import random
from enum import Enum
import types


class commands(Enum):
    SPEED = 1
    RPM = 2
    THROTTLE_POS = 3


def randomize_delay(func):
    def wrapper(*args, **kwargs):
        sleep_time = random.random() * 0.2
        time.sleep(sleep_time)
        return func(*args, **kwargs)
    return wrapper


def noisify(true_value):
    random_proportion = 0.4 * random.random() + 0.8
    return true_value * random_proportion


class OBD:

    mocked_values = {
        commands.SPEED: 60,
        commands.RPM: 2000,
        commands.THROTTLE_POS: 0.2,
    }

    def __init__(self, *args, **kwargs):
        pass

    def make_resp(self, value):
        primitive_namespace = types.SimpleNamespace()
        primitive_namespace.to = lambda _: noisify(value)

        o = types.SimpleNamespace()
        o.value = primitive_namespace
        return o

    @randomize_delay
    def query(self, command):
        if command in self.mocked_values:
            return self.make_resp(self.mocked_values[command])

        else:
            return self.make_resp(f"Unexpected command: {command=}")
