#!/bin/env python
import time
from datetime import datetime

from CO2Meter import *

Meter = CO2Meter("/dev/hidraw0")
while True:
    measurement = Meter.get_data()
    measurement.update({'timestamp': datetime.now()})
    print(measurement)
    time.sleep(5)
