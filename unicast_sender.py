"""unicast_sender.py - sends arbitrary data to a specified ip and port."""

import socket
import json
import time

from get_current_ip import get_current_ip

current_ip = get_current_ip()
while not current_ip:
    print("IP has not been assigned yet...")
    time.sleep(0.5)
    current_ip = get_current_ip()
subnet_octets = current_ip.split(".")[:-1]
subnet_octets.append("26")

TARGET_IP = ".".join(subnet_octets)
print(TARGET_IP)
DEST_PORT = 8686

TTL_LIMIT = 4


class UnicastSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def send(self, outgoing_json):
        json_bytes = bytes(outgoing_json, "utf-8")
        try:
            self.sock.sendto(json_bytes, (TARGET_IP, DEST_PORT))
        except:
            pass
        time.sleep(0.1)


if __name__ == "__main__":
    sender = UnicastSender()

    i = 0
    while True:
        json_obj = {"metricName": "speed", "value": i}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "RPM", "value": i * 100}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "gear", "value": (i % 6) + 1}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        json_obj = {"metricName": "throttle", "value": (i * 4) % 100}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print(f"Sent {json_obj} at {str(time.time())}")

        i = (i + 1) % 100

        time.sleep(0.5)
