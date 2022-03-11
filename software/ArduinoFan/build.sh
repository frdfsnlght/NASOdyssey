#!/bin/sh

arduino-cli compile --fqbn Seeeduino:samd:zero ArduinoFan.ino && \
arduino-cli upload -p /dev/ttyACM0 --fqbn Seeeduino:samd:zero ArduinoFan

