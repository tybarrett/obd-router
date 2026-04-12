"""send_data_receiver.py - Receives incoming obd data, processes it, and sends it out."""

import json
import time

from unicast_sender import UnicastSender


class SendDataReceiver:
    def __init__(self):
        self.sender = UnicastSender()

    def ingest(self, data):
        self.sender.send(json.dumps(data))
