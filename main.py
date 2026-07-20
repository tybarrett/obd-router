import signal
import sys

from data_pipeline import DataPipeline
from data_sources.obd_data_source import OBDDataSource
from data_sources.spotify_data_source import SpotifyDataSource
from data_receivers.send_data_receiver import SendDataReceiver
from switch_polling import SwitchPoller
from spotify.spotify_status_fetcher import SpotifyStatusFetcher


# TODO - uncomment when recording is desired
# from data_receivers.log_data_receiver import LogDataReceiver


# BCM-numbered GPIO pins, one per switch (indices 0-3).
SWITCH_PINS = [17, 23, 27, 22]

# BCM-numbered GPIO output pins held at constant 3.3 V to power the switches.
# Wire each output pin to one side of a switch, and the corresponding input
# pin to the other side.
SWITCH_OUTPUT_PINS = [20, 21, 19, 16]


def main():
    pipeline = DataPipeline()

    # --- Inputs (one background thread each) ---
    pipeline.register_source(OBDDataSource(rate_limit_hz=2))
    spotify_data_source = SpotifyDataSource(rate_limit_hz=0.2)
    pipeline.register_source(spotify_data_source)

    # --- Outputs ---
    pipeline.register_receiver(SendDataReceiver())
    # pipeline.register_receiver(LogDataReceiver())

    # --- Switch monitor ---
    switches = SwitchPoller(input_pins=SWITCH_PINS, output_pins=SWITCH_OUTPUT_PINS)

    switches.on_switch_up(0, lambda: spotify_data_source.spotify.change_player_state(SpotifyStatusFetcher.KICKSTART_MY_HEART_URI))
    switches.on_switch_down(0, lambda: print("Switch 0 down"))

    switches.on_switch_up(1, lambda: spotify_data_source.spotify.change_player_state(SpotifyStatusFetcher.HEARTBEAT_URI))
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
