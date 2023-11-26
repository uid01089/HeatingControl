from __future__ import annotations

import logging
from pathlib import Path
import time
from datetime import datetime
import paho.mqtt.client as pahoMqtt
from PythonLib.JsonUtil import JsonUtil
from PythonLib.Mqtt import Mqtt

from AtLeastOneActive import AtLeastOneActive

from PythonLib.DateUtil import DateTimeUtilities
from PythonLib.MqttConfigContainer import MqttConfigContainer
from PythonLib.Scheduler import Scheduler
from PythonLib.SchmittTrigger import SchmittTrigger

from HeatingTable import HeatingTable

logger = logging.getLogger('HeatingControl')


class Module:
    def __init__(self) -> None:
        self.scheduler = Scheduler()
        self.mqttClient = Mqtt("koserver.iot", "/house/rooms", pahoMqtt.Client("HeatingControl"))
        self.atLeastOneActive = AtLeastOneActive(self.mqttClient, '/house/agents/HeatingControl/values/allOverHeating')

    def getAtLeastOneActive(self) -> AtLeastOneActive:
        return self.atLeastOneActive

    def getScheduler(self) -> Scheduler:
        return self.scheduler

    def getMqttClient(self) -> Mqtt:
        return self.mqttClient

    def setup(self) -> None:
        self.scheduler.scheduleEach(self.mqttClient.loop, 500)

    def loop(self) -> None:
        self.scheduler.loop()


class SpecificModule:
    def __init__(self, roomName: str, module: Module) -> None:
        self.roomName = roomName
        self.module = module
        self.config = MqttConfigContainer(module.getMqttClient(), f"/house/agents/HeatingControl/{self.roomName}/config", Path(self.roomName + ".json"), {"Sun": []})
        self.schmittTrigger = SchmittTrigger(0.5)
        self.heatingTable = HeatingTable()

    def getHeatingTable(self) -> str:
        return self.heatingTable

    def getRoomName(self) -> str:
        return self.roomName

    def getSchmittTrigger(self) -> SchmittTrigger:
        return self.schmittTrigger

    def getConfig(self) -> MqttConfigContainer:
        return self.config

    def getScheduler(self) -> Scheduler:
        return self.module.getScheduler()

    def getMqttClient(self) -> Mqtt:
        return self.module.getMqttClient()

    def getAtLeastOneActive(self) -> AtLeastOneActive:
        return self.module.getAtLeastOneActive()

    def setup(self) -> SpecificModule:
        self.module.getScheduler().scheduleEach(self.config.loop, 60000)
        return self


class HeatingControl:

    def __init__(self, module: SpecificModule) -> None:
        self.roomName = module.getRoomName()
        self.config = module.getConfig()
        self.mqttClient = module.getMqttClient()
        self.scheduler = module.getScheduler()
        self.schmittTrigger = module.getSchmittTrigger()
        self.heatingTable = module.getHeatingTable()
        self.atLeastOneActive = module.getAtLeastOneActive()

    def setup(self) -> None:

        self.config.setup()
        self.config.subscribeToConfigChange(self.__updateHeatingTable)

        self.mqttClient.subscribeIndependentTopic(f'/house/rooms/{self.roomName}/Temperature', self.receiveData)
        self.scheduler.scheduleEach(self.__keepAlive, 10000)

    def receiveData(self, payload: str) -> None:

        try:
            temperature = float(payload)
            targetTemperature = self.heatingTable.getTargetTemperature(datetime.now())
            heating = not self.schmittTrigger.setValue(temperature, targetTemperature)

            self.mqttClient.publishIndependentTopic(f'/house/agents/HeatingControl/{self.roomName}/values/CurrentTemperature', str(temperature))
            self.mqttClient.publishIndependentTopic(f'/house/agents/HeatingControl/{self.roomName}/values/TargetTemperature', str(targetTemperature))
            self.mqttClient.publishIndependentTopic(f'/house/agents/HeatingControl/{self.roomName}/values/doHeating', heating)

            self.atLeastOneActive.trigger(f'{self.roomName}/heating', heating)

        except BaseException:
            logging.exception('')

    def __updateHeatingTable(self, config: dict) -> None:
        self.heatingTable.setConfig(config)

    def __keepAlive(self) -> None:
        self.mqttClient.publishIndependentTopic(f'/house/agents/HeatingControl/{self.roomName}/heartbeat', DateTimeUtilities.getCurrentDateString())
        self.mqttClient.publishIndependentTopic(f'/house/agents/HeatingControl/{self.roomName}/subscriptions', JsonUtil.obj2Json(self.mqttClient.getSubscriptionCatalog()))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('HeatingControl').setLevel(logging.DEBUG)

    module = Module()
    module.setup()

    HeatingControl(SpecificModule('KonniZimmer', module).setup()).setup()
    HeatingControl(SpecificModule('Bad', module).setup()).setup()
    HeatingControl(SpecificModule('SamiZimmer', module).setup()).setup()
    HeatingControl(SpecificModule('SebiZimmer', module).setup()).setup()
    HeatingControl(SpecificModule('SilviaZimmer', module).setup()).setup()
    HeatingControl(SpecificModule('Wohnzimmer', module).setup()).setup()
    HeatingControl(SpecificModule('WcOben', module).setup()).setup()
    HeatingControl(SpecificModule('WcUnten', module).setup()).setup()

    print("HeatingControl is running!")

    while (True):
        module.loop()
        time.sleep(0.25)


if __name__ == '__main__':
    main()
