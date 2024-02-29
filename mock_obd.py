"""obd_tester.py - attempts to fetch OBD data from the vehicle."""

import time

class MockObd:

    def __init__(self):
        # self.conn = obd.OBD()
        pass

    def fetch_speed(self):
        # resp_obj = self.conn.query(obd.commands.SPEED)
        return 1

    def fetch_rpm(self):
        # resp_obj = self.conn.query(obd.commands.RPM)
        return 2000

    def fetch_gear(self):
        # resp_obj = self.conn.query(obd.commands.SPEED)
        return 3

    def fetch_throttle(self):
        # resp_obj = self.conn.query(obd.commands.THROTTLE_POS)
        return 0.5



if __name__ == "__main__":
    fetcher = MockObd()
    while True:
        print(fetcher.fetch_speed())

        time.sleep(0.5)
