import time
import json

from unicast_sender import UnicastSender
import datetime

try:
    sender = UnicastSender()
    while True:

        now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        msg = {"heartbeat": now_str} # value not actually used
        json_str = json.dumps(msg)
        sender.send(json_str)

        print("New heartbeat sent at " + str(time.time()))

        time.sleep(1)
except Exception as e:
    fp = open("heartbeat_error.txt", "w")
    fp.write(e)
    fp.close()
