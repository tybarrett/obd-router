import os
import re

def get_current_ip():
    output = os.popen("ifconfig").read()
    all_ip_matches = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", output, flags=0)
    for ip in all_ip_matches:
        if ip.startswith("10.241"):
            return ip

if __name__ == "__main__":
    print(get_current_ip())
        
