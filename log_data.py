"""log_data.py - Saves provided json-serializable data to the filesystem"""

import datetime
import json


DATETIME_FORMAT = "%d-%m-%Y %H:%M:%s.%f"


class LogData:

    def __init__(self):
        now = datetime.datetime.strftime(datetime.now, "%d-%m-%Y_%H:%M:%s")
        self.output_fp = open(f"obd-data_{now}.log", "w")

    def record(self, data_packet):
        now = datetime.datetime.strftime(datetime.now, DATETIME_FORMAT)
        data_packet["_timestamp"] = now
        json_str = json.dumps(data_packet)
        self.output_fp.write(json_str)

    def __del__(self):
        self.output_fp.close()


def read_log(filename):
    fp = open(filename, "r")
    for line in fp.readlines():
        json_obj = json.loads(line)
        yield json_obj
    fp.close()

