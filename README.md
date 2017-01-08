# CO2Meter
Python Module to use co2meters like the 'AirCO2ntrol Mini' from TFA Dostmann with USB ID 04d9:a052. There are also other modules using the same interface.

This module supports Python 2.7 and 3.x.

## Attribution
Reverse Engineering of the protocol and initial code done by [Henryk Plötz](https://github.com/henryk). 

Read all about it at [hackaday](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor)

Code derived from [this article](https://hackaday.io/project/5301-reverse-engineering-a-low-cost-usb-co-monitor/log/17909-all-your-base-are-belong-to-us)

## Install

With pip:
```bash
pip install git+https://github.com/heinemml/CO2Meter
```

Without pip:
```bash
python setup.py install
```
Remark: you don't need to install, you can also just copy the CO2Meter.py into your project.

If you don't want to run your script as root make sure you have sufficient rights to access the device file.

This udev rule can be used to set permissions.
```
ACTION=="remove", GOTO="co2mini_end"

SUBSYSTEMS=="usb", KERNEL=="hidraw*", ATTRS{idVendor}=="04d9", ATTRS{idProduct}=="a052", GROUP="plugdev", MODE="0660", SYMLINK+="co2mini%n", GOTO="co2mini_end"

LABEL="co2mini_end"
```
save it as `/etc/udev/rules.d/90-co2mini.rules` and add the script user to the group `plugdev`.

This rules make the device also available as co2mini0 (increase trailing number for each additional device).

## Usage
```python
from CO2Meter import *
sensor = CO2Meter("/dev/hidraw0")
sensor.get_data()
```

The device writes out one value at a time. So we need to parse some data until we have co2 and temperature. Thus the get_data() method can take between 2 and 5 seconds. Take this into account when using it in a single threaded environment.
