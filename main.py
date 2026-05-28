import signal
import sys

from data_pipeline import DataPipeline
from data_sources.obd_data_source import OBDDataSource
from data_sources.spotify_data_source import SpotifyDataSource
from data_receivers.send_data_receiver import SendDataReceiver
from switch_monitor import SwitchMonitor


# TODO - uncomment when recording is desired
# from data_receivers.log_data_receiver import LogDataReceiver


# BCM-numbered GPIO pins, one per switch (indices 0-3).
SWITCH_PINS = [17, 18, 27, 22]


def main():
    pipeline = DataPipeline()

    # --- Inputs (one background thread each) ---
    pipeline.register_source(OBDDataSource(rate_limit_hz=2))
    pipeline.register_source(SpotifyDataSource(rate_limit_hz=0.2))

    # --- Outputs ---
    pipeline.register_receiver(SendDataReceiver())
    # pipeline.register_receiver(LogDataReceiver())

    # --- Switch monitor ---
    switches = SwitchMonitor(pins=SWITCH_PINS)

    switches.on_switch_up(0, lambda: print("Switch 0 up"))
    switches.on_switch_down(0, lambda: print("Switch 0 down"))

    switches.on_switch_up(1, lambda: print("Switch 1 up"))
    switches.on_switch_down(1, lambda: print("Switch 1 down"))

    switches.on_switch_up(2, lambda: print("Switch 2 up"))
    switches.on_switch_down(2, lambda: print("Switch 2 down"))

    switches.on_switch_up(3, lambda: print("Switch 3 up"))
    switches.on_switch_down(3, lambda: print("Switch 3 down"))

    switches.start()

    # Ensure GPIO is cleaned up on Ctrl-C or SIGTERM.
    def _shutdown(sig, frame):
        switches.stop()
        pipeline.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    pipeline.spin()


if __name__ == "__main__":
    main()
