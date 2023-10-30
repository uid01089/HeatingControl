#! /bin/bash
cd /home/pi/homeautomation/ZigMqtt2Mqtt
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 ZigMqtt2Mqtt.py > /home/pi/homeautomation/ZigMqtt2Mqtt/ZigMqtt2Mqtt.log
