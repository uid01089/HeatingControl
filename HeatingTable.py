import re
import logging
from datetime import datetime


logger = logging.getLogger('HeatingTable')


timePattern = re.compile("(\\d+):(\\d+)")


class TimeEntry:
    def __init__(self, day: str, entry: dict) -> None:
        self.time = entry['time']
        self.temperature = entry['temperature']
        self.day = day

        match = timePattern.match(self.time)
        self.timeMinutes = int(match.group(1)) * 60 + int(match.group(2))

    def getTime(self) -> datetime:
        return self.time

    def getTimeMinutes(self) -> int:
        return self.timeMinutes

    def getTemperature(self) -> int:
        return self.temperature

    def markAsPredecessor(self) -> None:
        self.timeMinutes = 0 - self.timeMinutes

    def markAsSuccessor(self) -> None:
        self.timeMinutes = 24 * 60 + self.timeMinutes


class HeatingTable:
    def __init__(self) -> None:
        self.config = {}

    def setConfig(self, config: dict) -> None:
        self.config = config

    def getTargetTemperature(self, date: datetime) -> float:

        targetTemp = 0

        # See https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        day = int(date.strftime("%w"))
        time = int(date.strftime("%H")) * 60 + int(date.strftime("%M"))

        dayString = self.__dayOfWeekAsString(day)
        dayStringPredecessor = self.__dayOfWeekAsString(day - 1 + 7)
        dayStringSuccessor = self.__dayOfWeekAsString(day + 1)

        dayConfig = self.config.get(dayString)
        dayConfigPredecessor = self.config.get(dayStringPredecessor)
        dayConfigSuccessor = self.config.get(dayStringSuccessor)

        if not (dayConfig and dayConfigPredecessor and dayConfigSuccessor):
            raise ValueError("Config is corrupt")

        lastTimeConfigOfPredecessor = dayConfigPredecessor[-1]
        fistTimeConfigOfSuccessor = dayConfigSuccessor[0]

        alignedTimeConfig = []

        # First add last time from predecessor als time 0
        predecessor = TimeEntry(dayStringPredecessor, lastTimeConfigOfPredecessor)
        predecessor.markAsPredecessor()
        alignedTimeConfig.append(predecessor)

        # Add all other time entries for this day
        for entry in dayConfig:
            alignedTimeConfig.append(TimeEntry(dayString, entry))

        # Add First time from successor
        predecessor = TimeEntry(dayStringSuccessor, fistTimeConfigOfSuccessor)
        predecessor.markAsSuccessor()
        alignedTimeConfig.append(predecessor)

        # Running from front to back
        runningElement = 0
        while runningElement <= len(alignedTimeConfig) and alignedTimeConfig[runningElement].getTimeMinutes() < time:
            targetTemp = alignedTimeConfig[runningElement].getTemperature()
            runningElement = runningElement + 1

        return targetTemp

    def __dayOfWeekAsString(self, dayIndex: int) -> str:
        return ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][(dayIndex % 7)]
