"""obd_tester.py - attempts to fetch OBD data from the vehicle."""

import time
import os

if "MOCK_OBD" in os.environ:
    print("Importing our obd mock module")
    import mock_obd as obd
else:
    print("Starting to import obd at " + str(time.time()))
    t_start = time.time()
    import obd
    print("Time to import obd: " + str(time.time() - t_start))


class ObdFetcher:

    def __init__(self):
        # while not os.path.exists("/dev/rfcomm0"):
        #     print("rfcomm0 does not exist yet.")
        #     time.sleep(0.5)
        self.conn = obd.OBD(portstr="/dev/rfcomm0", baudrate=115200)

    def fetch_speed(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        return resp_obj.value.to("mph")

    def fetch_rpm(self):
        resp_obj = self.conn.query(obd.commands.RPM)
        return resp_obj.value.to("rpm")

    def fetch_gear(self):
        resp_obj = self.conn.query(obd.commands.SPEED)
        if resp_obj.value:
            return int(resp_obj.value.to("mph") / 10) # Small workaround
        else:
            return None

    def fetch_throttle(self):
        resp_obj = self.conn.query(obd.commands.THROTTLE_POS)
        return resp_obj.value.to("")



if __name__ == "__main__":
    fetcher = ObdFetcher()
    while True:
        print(fetcher.fetch_speed())

        time.sleep(0.5)
