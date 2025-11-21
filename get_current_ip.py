import os
import re

def get_current_ip():
    return os.popen("ifconfig wlan0 | grep 'inet ' | cut -d \" \" -f 10").read()

if __name__ == "__main__":
    print(get_current_ip())
        
