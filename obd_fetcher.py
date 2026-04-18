"""obd_tester.py - attempts to fetch OBD data from the vehicle."""

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
    print("Time to import obd: " + str(time.time() - t_start))


class ObdFetcher:

    self.rpm = 100
    self.speed = 1

    def __init__(self):
#        while not os.path.exists("/dev/rfcomm0"):
#            print("rfcomm0 does not exist yet.")
#            time.sleep(0.5)
        self.conn = obd.OBD()

    def fetch_speed(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        self.speed = float(resp_obj.value.to("mph").magnitude)
        return self.speed

    def fetch_rpm(self):
        resp_obj = self.conn.query(obd.commands.RPM)
        self.rpm = float(resp_obj.value.to("rpm").magnitude)
        return self.rpm

    def fetch_gear(self):
        return determine_gear(self.rpm, self.speed)

    def fetch_throttle(self):
        resp_obj = self.conn.query(obd.commands.THROTTLE_POS)
        return resp_obj.value.to("").magnitude



if __name__ == "__main__":
    fetcher = ObdFetcher()
    while True:
        print(fetcher.fetch_speed())

        time.sleep(0.5)
