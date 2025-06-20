from data_receivers.send_data_receiver import SendDataReceiver
from telemetry_processing_engine import TelemetryProcessingEngine
from data_receivers.log_data_receiver import LogDataReceiver


def main():
    tpe = TelemetryProcessingEngine()
    tpe.register_data_receiver(
        SendDataReceiver()
    )

    tpe.register_data_receiver(
        LogDataReceiver()
    )

    tpe.spin()


if __name__ == "__main__":
    main()
