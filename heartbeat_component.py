import time
import json

from unicast_sender import UnicastSender


sender = UnicastSender()
while True:

    msg = {"metricName": "heartbeat"}
    json_str = json.dumps(msg)
    sender.send(json_str)

    print("New heartbeat sent at " + str(time.time()))

    time.sleep(1)

