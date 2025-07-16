import time
import json

from unicast_sender import UnicastSender

try:
    sender = UnicastSender()
    while True:

        msg = {"metricName": "heartbeat"}
        json_str = json.dumps(msg)
        sender.send(json_str)

        print("New heartbeat sent at " + str(time.time()))

        time.sleep(1)
except Exception as e:
    fp = open("heartbeat_error.txt", "w")
    fp.write(e)
    fp.close()
