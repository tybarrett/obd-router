"""log_data_receiver.py - Saves provided json-serializable data to the filesystem"""

import datetime
import json
import os


LOG_FOLDER = "obd_logs"
DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S.%f"


class LogDataReceiver:

    def __init__(self):
        now = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self.output_fp = open(
            os.path.join(LOG_FOLDER, f"obd-data_{now}.log"),
            "w",
        )

    def ingest(self, data_packet):
        now = datetime.datetime.now().strftime(DATETIME_FORMAT)
        data_packet["_timestamp"] = now
        json_str = json.dumps(data_packet)
        print(json_str)
        self.output_fp.write(json_str + "\n")
        self.output_fp.flush()

    def __del__(self):
        if hasattr(self, "output_fp"):
            self.output_fp.close()


def read_log(filename):
    fp = open(filename, "r")
    for line in fp.readlines():
        json_obj = json.loads(line)
        json_obj["_timestamp"] = datetime.datetime.strptime(json_obj["_timestamp"], DATETIME_FORMAT)
        yield json_obj
    fp.close()


if __name__ == "__main__":
    for log_entry in read_log(r""):
        print(f"{type(log_entry)=} - {log_entry}")
