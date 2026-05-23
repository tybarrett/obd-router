from data_pipeline import DataPipeline
from data_sources.obd_data_source import OBDDataSource
from data_sources.spotify_data_source import SpotifyDataSource
from data_receivers.send_data_receiver import SendDataReceiver

# TODO - uncomment when recording is desired
# from data_receivers.log_data_receiver import LogDataReceiver


def main():
    pipeline = DataPipeline()

    # --- Inputs (one background thread each) ---
    pipeline.register_source(OBDDataSource(rate_limit_hz=2))
    pipeline.register_source(SpotifyDataSource(rate_limit_hz=0.2))

    # --- Outputs ---
    pipeline.register_receiver(SendDataReceiver())
    # pipeline.register_receiver(LogDataReceiver())

    pipeline.spin()


if __name__ == "__main__":
    main()
