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


#from unicast_sender import UnicastSender
#from obd_tester import ObdFetcher
#from determine_gear import *
# from obd_tester import MockObd 


#if __name__ == "__main__":
#    sender = UnicastSender()
#    obd = ObdFetcher()
#
#    while True:
#        speed = obd.fetch_speed().magnitude
#        json_obj = {"metricName": "speed", "value": int(speed)}
#        json_string = json.dumps(json_obj)
#        sender.send(json_string)
#
#        rpm = obd.fetch_rpm().magnitude
#        json_obj = {"metricName": "RPM", "value": int(rpm)}
#        json_string = json.dumps(json_obj)
#        sender.send(json_string)
#
#        gear = determine_gear(rpm, speed)
#        if gear == "N":
#            gear = str(0)
#        json_obj = {"metricName": "gear", "value": gear}
#        json_string = json.dumps(json_obj)
#        sender.send(json_string)
#
#        throttle = obd.fetch_throttle().magnitude
#        json_obj = {"metricName": "throttle", "value": throttle}
#        json_string = json.dumps(json_obj)
#        sender.send(json_string)
#
#        #time.sleep(1)
