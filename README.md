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
import time
sensor = CO2Meter("/dev/hidraw0")
while True:
    time.sleep(2)
    sensor.get_data()
```

The device writes out one value at a time. So we need to parse some data until we have co2 and temperature. Thus the get_data() method will initially return none or only on value (whichever comes first). 
When you just need one measurement you should wait some seconds or iterate until you get a full reading. If you just need co2 a call to `get_co2` might speed things up.

### Callback
You can pass a callback to the constructor. It will be called when any of the values is updated. The parameters passed are `sensor` and `value`. `sensor` contains one of these constants:

```python
CO2METER_CO2 = 0x50
CO2METER_TEMP = 0x42
CO2METER_HUM = 0x44
```


### Error handling
In Case the device can't be read anymore (e.g. it was unplugged) the worker thread will end in the background. Afterwards calls to any of the `get_*` functions will throw an `IOError`. You will need to handle any resetup, making sure that the device is there etc yourself.
