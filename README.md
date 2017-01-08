# CO2Meter
Python Module to use co2meters like the 'AirCO2ntrol Mini' from TFA Dostmann with USB ID 04d9:a052. There are also other modules using the same interface.

## Attribution
Reverse Engineering of the protocol and initial code done by [Henryk Plötz](https://github.com/henryk). 

Read all about it at [hackaday](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor)

Code derived from [this article](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us)

## Usage
```python
from CO2Meter import *
sensor = CO2Meter()
sensor.get_data()
```

The device writes out one value at a time. So we need to parse some data until we have temperature and humidity. Thus the get_data() method can take between 2 and 5 seconds. Take this into account when using it in a single threaded environment.
