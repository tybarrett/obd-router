"""telemetry_processing_engine.py - Requests data from the provided source and routes it to the receivers."""


import time

from obd_fetcher import ObdFetcher

# TODO - rate limit how fast TPE spins?
# TODO - abstract away the specific OBD calls
#        or, decouple it from OBD altogether?


class TelemetryProcessingEngine:
    def __init__(self, rate_limit_hz=2):
        self.data_receivers = []
        self.rate_limit_hz = rate_limit_hz
        self.is_running = True

        self.obd = ObdFetcher()

    def register_data_receiver(self, data_receiver):
        self.data_receivers.append(data_receiver)

    def spin(self):
        while self.is_running:

            start_time = time.time()

            self._get_and_process_data()

            end_time = time.time()
            elapsed_time = end_time - start_time
            if elapsed_time < 1 / self.rate_limit_hz:
                time.sleep((1 / self.rate_limit_hz) - elapsed_time)

    def _get_and_process_data(self):
        speed = self.obd.fetch_speed()
        print(speed)
        rpm = self.obd.fetch_rpm()
        print(rpm)
        gear = self.obd.fetch_gear()
        print(gear)
        throttle = self.obd.fetch_throttle()
        print(throttle)

        json_obj = {
            "speed": speed,
            "rpm": rpm,
            "gear": gear,
            "throttle": throttle
        }
        print(json_obj)

        for receiver in self.data_receivers:
            receiver.ingest(json_obj)
