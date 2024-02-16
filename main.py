
import json
import time

from unicast_sender import UnicastSender
from obd_tester import ObdFetcher


if __name__ == "__main__":
    sender = UnicastSender()
    obd = ObdFetcher()

    while True:
        speed = obd.fetch_speed()
        json_obj = {"metricName": "speed", "value": str(speed)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        rpm = obd.fetch_rpm()
        json_obj = {"metricName": "RPM", "value": str(rpm)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        gear = obd.fetch_gear()
        json_obj = {"metricName": "gear", "value": str(rpm)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)

        throttle = obd.fetch_throttle()
        json_obj = {"metricName": "throttle", "value": str(rpm)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)

        time.sleep(0.25)