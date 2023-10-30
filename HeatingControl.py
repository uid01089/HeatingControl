import logging
import time
from datetime import datetime
from pathlib import PurePath
from PythonLib.DateUtil import DateTimeUtilities


import pathlib


import paho.mqtt.client as pahoMqtt
from PythonLib.Mqtt import Mqtt
from PythonLib.Scheduler import Scheduler
from PythonLib.SchmittTrigger import SchmittTrigger

from HeatingTable import HeatingTable

logger = logging.getLogger('HeatingControl')


class HeatingControl:

    def __init__(self, roomName: str, timeTableFile: pathlib.PurePath, mqttClient: Mqtt, scheduler: Scheduler, schmittTrigger: SchmittTrigger) -> None:
        self.roomName = roomName
        self.timeTableFile = timeTableFile
        self.mqttClient = mqttClient
        self.scheduler = scheduler
        self.schmittTrigger = schmittTrigger

    def setup(self) -> None:

        self.mqttClient.subscribeIndependentTopic(f'/house/rooms/{self.roomName}/Temperature', self.receiveData)
        self.scheduler.scheduleEach(self.__keepAlive, 10000)

    def receiveData(self, payload: str) -> None:

        try:
            temperature = float(payload)
            heatingTable = HeatingTable(self.timeTableFile)
            targetTemperature = heatingTable.getTargetTemperature(datetime.now())
            heating = not self.schmittTrigger.setValue(temperature, targetTemperature)

            self.mqttClient.publishOnChange(f'{self.roomName}/TargetTemperature', str(targetTemperature))
            self.mqttClient.publishOnChange(f'{self.roomName}/heating', str(heating))
        except Exception as e:
            logger.error("Exception occurs: " + str(e))

    def __keepAlive(self) -> None:
        self.mqttClient.publishIndependentTopic('/house/agents/HeatingControl/heartbeat', DateTimeUtilities.getCurrentDateString())


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('HeatingControl').setLevel(logging.DEBUG)

    scheduler = Scheduler()

    mqttClient = Mqtt("koserver.iot", "/house/rooms", pahoMqtt.Client("HeatingControl"))
    scheduler.scheduleEach(mqttClient.loop, 500)

    HeatingControl('KonniZimmer', PurePath('KonniZimmer.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('Bad', PurePath('Bad.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('SamiZimmer', PurePath('SamiZimmer.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('SebiZimmer', PurePath('SebiZimmer.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('SilviaZimmer', PurePath('SilviaZimmer.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('Wohnzimmer', PurePath('Wohnzimmer.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('WcOben', PurePath('WcOben.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()
    HeatingControl('WcUnten', PurePath('WcUnten.json'), mqttClient, scheduler, SchmittTrigger(0.5)).setup()

    while (True):
        scheduler.loop()
        time.sleep(0.25)


if __name__ == '__main__':
    main()
