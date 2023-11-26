from PythonLib.Mqtt import Mqtt


class AtLeastOneActive:
    def __init__(self, mqttClient: Mqtt, topic: str) -> None:
        self.mqttClient = mqttClient
        self.topic = topic
        self.inputs = {}

    def trigger(self, topic: str, value: bool) -> None:

        allOverValue = False

        self.inputs[topic] = value
        for value in self.inputs.values():
            allOverValue = allOverValue or value

        self.mqttClient.publishIndependentTopic(self.topic, str(allOverValue))
