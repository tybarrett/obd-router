"""multicast_sender.py - sends arbitrary data to a specified multicast group."""

import socket
import json
import time


GROUP_IP = "224.1.1.1"
DEST_PORT = 8686

TTL_LIMIT = 4


class MulticastSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, TTL_LIMIT)

    def send(self, outgoing_json):
        bytes_string = bytes(outgoing_json, "utf-8")
        self.sock.sendto(bytes_string, (GROUP_IP, DEST_PORT))


if __name__ == "__main__":
    sender = MulticastSender()
    
    i = 0
    while True:
        json_obj = {"metricName": "RPM", "value": "2500"}
        json_string = json.dumps(json_obj)
        sender.send(json_string)
        print("Sent at " + str(time.time()))

        i += 1

        time.sleep(0.5)
