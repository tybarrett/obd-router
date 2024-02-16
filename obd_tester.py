"""obd_tester.py - attempts to fetch OBD data from the vehicle."""

import obd
import time

class ObdFetcher:

    def __init__(self):
        self.conn = obd.OBD()

    def fetch_speed(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        return resp_obj.value.to("mph")

    def fetch_rpm(self):
        resp_obj = self.conn.query(obd.commands.RPM)
        return resp_obj.value

    def fetch_gear(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        return resp_obj.value / 10 # Small workaround

    def fetch_throttle(self):
        resp_obj = self.conn.query(obd.commands.THROTTLE_POS)
        return resp_obj.value



if __name__ == "__main__":
    fetcher = ObdFetcher()
    while True:
        print(fetcher.fetch_speed())

        time.sleep(0.5)
