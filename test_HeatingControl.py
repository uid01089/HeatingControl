from pathlib import PurePath
from HeatingTable import HeatingTable
from datetime import datetime


def test1() -> None:

    date = datetime(2023, 10, 30, 14, 8)  # mon 14:08

    heatingTable = HeatingTable(PurePath('KonniZimmer.json'))
    targetTemperature = heatingTable.getTargetTemperature(date)
    assert targetTemperature == 21


def test2() -> None:

    date = datetime(2023, 10, 30, 3, 8)  # mon 03:08

    heatingTable = HeatingTable(PurePath('KonniZimmer.json'))
    targetTemperature = heatingTable.getTargetTemperature(date)
    assert targetTemperature == 18


def test3() -> None:

    date = datetime(2023, 10, 29, 3, 8)  # sun 03:08

    heatingTable = HeatingTable(PurePath('KonniZimmer.json'))
    targetTemperature = heatingTable.getTargetTemperature(date)
    assert targetTemperature == 18
