"""obd-tester.py - attempts to fetch OBD data from the vehicle."""

import obd
import time

class ObdFetcher:

    def __init__(self):
        self.conn = obd.OBD()

    def fetch_speed(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        return resp_obj.value.to("mph")

if __name__ == "__main__":
    fetcher = ObdFetcher()
    while True:
        print(fetcher.fetch_speed())

        time.sleep(0.5)
