"""multicast_receive.py - receives and prints multicast messages (for testing)"""

import socket
import struct

MULTICAST_GROUP = "224.1.1.1"
RECEIVE_PORT = 8687

class MulticastReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("localhost", RECEIVE_PORT))

        self.mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)

    def wait_and_receive(self):
        return self.sock.recv(10240)

   
if __name__ == "__main__":
    receiver = MulticastReceiver()
    while True:
        print(receiver.wait_and_receive())
