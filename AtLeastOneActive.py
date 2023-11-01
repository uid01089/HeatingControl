class AtLeastOneActive:
    def __init__(self) -> None:
        self.inputs = {}

    def trigger(self, topic: str, value: bool) -> bool:

        allOverValue = False

        self.inputs[topic] = value
        for value in self.inputs.values():
            allOverValue = allOverValue or value

        return value
