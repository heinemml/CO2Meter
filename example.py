#!/bin/env python
from CO2Meter import *
from datetime import datetime
import time

Meter = CO2Meter("/dev/hidraw0")
while True:
    measurement = Meter.get_data()
    measurement.update({'timestamp': datetime.now()})
    print(measurement)
    time.sleep(5)
