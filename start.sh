#! /bin/bash
cd /home/pi/homeautomation/HeatingControl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 HeatingControl.py > /home/pi/homeautomation/HeatingControl/HeatingControl.log
