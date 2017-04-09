import sys
import fcntl
import threading
import weakref

CO2METER_CO2 = 0x50
CO2METER_TEMP = 0x42
CO2METER_HUM = 0x44
HIDIOCSFEATURE_9 = 0xC0094806

def _co2_worker(weak_self):
    while True:
        self = weak_self()
        if self is None:
            break
        self._read_data()

        if not self._running:
            break
        del self


class CO2Meter:

    _key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    _device = ""
    _values = {}
    _file = ""
    _running = True
    _callback = None

    def __init__(self, device="/dev/hidraw0", callback=None):
        self._device = device
        self._callback = callback
        self._file = open(device, "a+b", 0)

        if sys.version_info >= (3,):
            set_report = [0] + self._key
            fcntl.ioctl(self._file, HIDIOCSFEATURE_9, bytearray(set_report))
        else:
            set_report_str = "\x00" + "".join(chr(e) for e in self._key)
            fcntl.ioctl(self._file, HIDIOCSFEATURE_9, set_report_str)

        thread = threading.Thread(target=_co2_worker, args=(weakref.ref(self),))
        thread.daemon = True
        thread.start()


    def _read_data(self):
        try:
            result = self._file.read(8)
            if sys.version_info >= (3,):
                data = list(result)
            else:
                data = list(ord(e) for e in result)

            decrypted = self._decrypt(data)
            if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
                print(self._hd(data), " => ", self._hd(decrypted), "Checksum error")
            else:
                operation = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                self._values[operation] = val
                if self._callback is not None:
                    if operation == CO2METER_CO2:
                        self._callback(sensor=operation, value=val)
                    elif operation == CO2METER_TEMP:
                        self._callback(sensor=operation,
                                       value=round(val / 16.0 - 273.1, 1))
                    elif operation == CO2METER_HUM:
                        self._callback(sensor=operation, value=round(val / 100.0, 1))
        except:
            self._running = False


    def _decrypt(self, data):
        cstate = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
        shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

        phase1 = [0] * 8
        for i, j in enumerate(shuffle):
            phase1[j] = data[i]

        phase2 = [0] * 8
        for i in range(8):
            phase2[i] = phase1[i] ^ self._key[i]

        phase3 = [0] * 8
        for i in range(8):
            phase3[i] = ((phase2[i] >> 3) | (phase2[(i-1+8)%8] << 5)) & 0xff

        ctmp = [0] * 8
        for i in range(8):
            ctmp[i] = ((cstate[i] >> 4) | (cstate[i]<<4)) & 0xff

        out = [0] * 8
        for i in range(8):
            out[i] = (0x100 + phase3[i] - ctmp[i]) & 0xff

        return out


    @staticmethod
    def _hd(data):
        return " ".join("%02X" % e for e in data)


    def get_co2(self):
        if not self._running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_CO2 in self._values:
            result = {'co2': self._values[CO2METER_CO2]}

        return result


    def get_temperature(self):
        if not self._running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_TEMP in self._values:
            result = {'temperature': (self._values[CO2METER_TEMP]/16.0-273.15)}

        return result


    def get_humidity(self): # not implemented by all devices
        if not self._running:
            raise IOError("worker thread couldn't read data")
        result = {}
        if CO2METER_HUM in self._values:
            result = {'humidity': (self._values[CO2METER_HUM]/100.0)}
        return result


    def get_data(self):
        result = {}
        result.update(self.get_co2())
        result.update(self.get_temperature())
        result.update(self.get_humidity())

        return result
