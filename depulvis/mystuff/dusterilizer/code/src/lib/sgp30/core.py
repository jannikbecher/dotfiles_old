"""
Reading format. See https://www.rutronik.com/fileadmin/Rutronik/Supplier/Sensirion/September/Sensirion_Gas_Sensors_SGP_Preliminary_Datasheet_EN.pdf
"""

import ustruct as struct
import time

class SGP30:
    """A driver for the SHTC1 humidity and temerature sensor.
    :param i2c: The `I2C` object to use.
    """
    ADDRESS=0x58
    I2C_WRITE_DELAY_MS=20
    def __init__(self, i2c):
        self._i2c = i2c
        self._tvoc = 0.0
        self._baseline_tvoc = 0.0
        self._eco2 = 0.0
        self._baseline_eco2 = 0.0
        self._status = ('ok', '')

    @property
    def tvoc(self):
        """Returns Total Volatile Organic Compound in parts per billion."""
        return self._tvoc

    @property
    def baseline_tvoc(self):
        """Returns Total Volatile Organic Compound baseline value."""
        return self._temperature

    @property
    def eco2(self):
        """Returns Carbon Dioxide Equivalent in parts per million."""
        return self._eco2

    @property
    def baseline_eco2(self):
        """Returns Carbon Dioxide Equivalent baseline value."""
        return self._baseline_eco2

    @property
    def status(self):
        """Returns true if everything is ok."""
        return self._status

    def _write_i2c(self, data):
        try:
            self._i2c.writeto(self.ADDRESS, data)
            time.sleep_ms(self.I2C_WRITE_DELAY_MS)
            self._status = ('ok', '')
        except:
            self._status = ('error', 'can\'t write to i2c')

    def _read_i2c(self, cmd, num):
        try:
            self._i2c.writeto(self.ADDRESS, cmd)
            time.sleep_ms(self.I2C_WRITE_DELAY_MS)
            self._status = ('ok', '')
            return self._i2c.readfrom(self.ADDRESS, num)
        except:
            self._status = ('error', 'can\'t write to i2c')
            return None

    def _calc_int(self, b):
        struct_int = struct.pack('>BB', b[0], b[1])
        int_values = struct.unpack('>H', struct_int)
        crc = self._calc_crc(b[0:2])
        if crc == bytes([b[2]]):
            return int_values[0]
        else:
            print('crc error: ' + str(crc) + '=' + str(bytes([b[2]])))
            return None

    def _calc_crc(self, data):
        crc = 0xFF
        for i in range(2):
            crc = (crc ^ data[i]) & 0xFF
            for bit in range(8, 0, -1):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = ((crc << 1)) & 0xFF
        return bytes([crc])

    def init(self):
        self.init_air_quality()
        return True

    def read_measured_values(self):
        self.init_air_quality()
        self.measure_air_quality()

    def init_air_quality(self):
        cmd = b'\x20\x03'
        self._write_i2c(cmd)

    def measure_air_quality(self):
        cmd = b'\x20\x08'
        data = self._read_i2c(cmd, 6)
        eco2 = self._eco2
        tvoc = self._tvoc
        try:
            eco2 = self._calc_int(data[0:3])
            tvoc = self._calc_int(data[3:6])
            self._status = ('ok', '')
        except Exception as e:
            self._status = ('error', e)

        if eco2:
            self._eco2 = eco2
        if tvoc:
            self._tvoc = tvoc
        if self._eco2 < 400 or self._eco2 > 60000 or self._tvoc < 0 or self._tvoc > 60000:
            self._status = ('error', 'eco2/tvoc is out of range')
        else:
            self._status = ('ok', '')

    def get_baseline(self):
        cmd = b'\x20\x15'
        self._read_i2c(cmd, 6)

    def set_baseline(self, baseline):
        cmd = b'\x20\x1e'
        self._write_i2c(cmd + baseline)

    def measure_test(self):
        cmd = b'\x20\x32'
        data = self._read_i2c(cmd, 3)

    def get_feature_set_version(self):
        cmd = b'\x20\x2f'
        data = self._read_i2c(cmd, 3)

    def measure_signals(self):
        cmd = b'\x20\x50'
        data = self._read_i2c(cmd, 6)

    def get_serial_id(self):
        cmd = b'\x36\x82'
        data = self._read_i2c(cmd, 9)
