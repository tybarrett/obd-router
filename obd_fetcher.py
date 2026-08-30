"""obd_fetcher.py - attempts to fetch OBD data from the vehicle."""

import logging
import time
import os
from determine_gear import determine_gear

if "MOCK_OBD" in os.environ:
    print("Importing our obd mock module")
    import mock_obd as obd
else:
    print("Starting to import obd at " + str(time.time()))
    t_start = time.time()
    import obd
    # obd.logger.setLevel(obd.logging.DEBUG)
    print("Time to import obd: " + str(time.time() - t_start))


class ObdFetcher:

    def __init__(self):
        self.rpm = 100
        self.speed = 1

        self.conn = obd.OBD(portstr="/dev/ttyUSB0", baudrate=115200, protocol="6")

    def fetch_speed(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        if resp_obj.value is None:
            logging.warning("Unable to capture vehicle speed.")
            return None

        self.speed = float(resp_obj.value.to("mph").magnitude)
        return self.speed

    def fetch_rpm(self):
        resp_obj = self.conn.query(obd.commands.RPM)
        if not resp_obj.value:
            logging.warning("Unable to capture RPM.")
            return None

        self.rpm = float(resp_obj.value.to("rpm").magnitude)
        return self.rpm

    def fetch_gear(self):
        return determine_gear(self.rpm, self.speed)

    def fetch_throttle(self):
        resp_obj = self.conn.query(obd.commands.THROTTLE_POS)
        if not resp_obj.value:
            logging.warning("Unable to determine throttle.")
            return None

        return resp_obj.value.to("").magnitude


if __name__ == "__main__":
    fetcher = ObdFetcher()
    while True:
        print(fetcher.fetch_speed())
        time.sleep(0.5)
