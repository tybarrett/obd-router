
import json
import time

from unicast_sender import UnicastSender
from obd_tester import ObdFetcher
from obd_tester import MockObd 


if __name__ == "__main__":
    sender = UnicastSender()
    obd = ObdFetcher()

    while True:
        speed = obd.fetch_speed().magnitude
        json_obj = {"metricName": "speed", "value": int(speed)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        rpm = obd.fetch_rpm().magnitude
        json_obj = {"metricName": "RPM", "value": int(rpm)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        gear = obd.fetch_gear().magnitude
        json_obj = {"metricName": "gear", "value": int(gear)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        throttle = obd.fetch_throttle().magnitude
        json_obj = {"metricName": "throttle", "value": throttle}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)
