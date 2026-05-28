"""obd_data_source.py - DataSource adapter for the OBD vehicle interface."""

from data_sources.data_source import DataSource
from obd_fetcher import ObdFetcher


class OBDDataSource(DataSource):
    """
    Wraps ObdFetcher and exposes it as a DataSource.

    Fetches speed, RPM, gear, and throttle in a single cycle and packages
    them into a dict for downstream receivers.
    """

    def __init__(self, rate_limit_hz: float = 2.0):
        super().__init__(rate_limit_hz)
        self.obd = ObdFetcher()

    def fetch(self) -> dict | None:
        speed = self.obd.fetch_speed()
        rpm = self.obd.fetch_rpm()
        gear = self.obd.fetch_gear()
        throttle = self.obd.fetch_throttle()

        return {
            "__TYPE": "telemetry",
            "speed": speed,
            "rpm": rpm,
            "gear": gear,
            "throttle": throttle,
        }
