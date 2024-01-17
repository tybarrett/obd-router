"""unicast_sender.py - sends arbitrary data to a specified ip and port."""

import socket
import json
import time

TARGET_IP = "192.168.1.151"
DEST_PORT = 8686

TTL_LIMIT = 4


class MulticastSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, outgoing_json):
        json_bytes = bytes(outgoing_json, "utf-8")
        self.sock.sendto(json_bytes, (TARGET_IP, DEST_PORT))


if __name__ == "__main__":
    sender = MulticastSender()

    i = 0
    while True:
        json_obj = {"metricName": "speed", "value": str(i)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "RPM", "value": str(i * 100)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "gear", "value": str((i % 6) + 1)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "throttle", "value": str((i * 4) % 100)}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        time.sleep(0.5)
