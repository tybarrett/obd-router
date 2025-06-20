"""send_data_receiver.py - Receives incoming obd data, processes it, and sends it out."""

import json
import time

from unicast_sender import UnicastSender


class SendDataReceiver:
    def __init__(self):
        self.sender = UnicastSender()

    def ingest(self, data):
        json_objs = [
            {"metricName": key, "value": value}
            for key, value in data.items()
        ]

        for obj in json_objs:
            print(obj)
            self.sender.send(json.dumps(obj))

            # Rate-limit outgoing traffic bc of bandwidth concerns
            time.sleep(0.1)
