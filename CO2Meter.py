import sys
import fcntl
import threading
import weakref

def _co2_worker(weak_self):
    while True:
        self = weak_self()
        if self is None: break
        self._read_data()
        del self


class CO2Meter:

    _key = [0xc4, 0xc6, 0xc0, 0x92, 0x40, 0x23, 0xdc, 0x96]
    _device = ""
    _values = {}
    _file = ""

    def __init__(self, device="/dev/hidraw0"):
        self._device = device
        self._file = open(device, "a+b", 0)

        HIDIOCSFEATURE_9 = 0xC0094806
        if sys.version_info >= (3,):
            set_report = [0] + self._key
            fcntl.ioctl(self._file, HIDIOCSFEATURE_9, bytearray(set_report))
        else:
            set_report_str = "\x00" + "".join(chr(e) for e in self._key)
            fcntl.ioctl(self._file, HIDIOCSFEATURE_9, set_report_str)

        thread = threading.Thread(target = _co2_worker, args=(weakref.ref(self),))
        thread.daemon = True
        thread.start()


    def _read_data(self):
            result = self._file.read(8)
            if sys.version_info >= (3,):
                data = list(result)
            else:
                data = list(ord(e) for e in result)

            decrypted = self._decrypt(data)
            if decrypted[4] != 0x0d or (sum(decrypted[:3]) & 0xff) != decrypted[3]:
                print(self._hd(data), " => ", self._hd(decrypted), "Checksum error")
            else:
                op = decrypted[0]
                val = decrypted[1] << 8 | decrypted[2]
                self._values[op] = val


    def _decrypt(self, data):
        cstate = [0x48, 0x74, 0x65, 0x6D, 0x70, 0x39, 0x39, 0x65]
        shuffle = [2, 4, 0, 7, 1, 6, 5, 3]

        phase1 = [0] * 8
        for i, o in enumerate(shuffle):
            phase1[o] = data[i]

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


    def _hd(self, data):
        return " ".join("%02X" % e for e in data)


    def get_co2(self):
        result = {}
        if 0x50 in self._values:
            result = {'co2': self._values[0x50]}

        return result


    def get_temperature(self):
        result = {}
        if 0x42 in self._values:
            result = {'temperature': (self._values[0x42]/16.0-273.15)}

        return result


    def get_data(self):
        result = {}
        result.update(self.get_co2())
        result.update(self.get_temperature())

        return result



