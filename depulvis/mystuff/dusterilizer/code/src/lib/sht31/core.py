"""
Reading format. See https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Humidity/Sensirion_Humidity_Sensors_SHT3x_Datasheet_digital.pdf
"""

import ustruct as struct
import time

class SHT31:
    """A driver for the SHT31 humidity and temerature sensor.
    :param i2c: The `I2C` object to use.
    """
    ADDRESS=0x44
    I2C_WRITE_DELAY_MS=20
    def __init__(self, i2c):
        self._i2c = i2c
        self._humidity = 0.0
        self._temperature = 0.0
        self._status = ('ok', '')

    @property
    def humidity(self):
        """Return the Humidity, in %RH."""
        return self._humidity

    @property
    def temperature(self):
        """Return the Temperature, in °C."""
        return self._temperature

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

        self.read_measured_values()
        return self._humidity > 0

    def set_high_repeatability_no_stretching(self):
        cmd = b'\x24\x00'

    def read_measured_values(self):
        cmd = b'\x5c\x24'
        data = self._read_i2c(cmd, 6)
        humidity = self._humidity
        temperature = self._temperature
        try:
            humidity = self._calc_int(data[0:3])
            temperature = self._calc_int(data[3:6])
            self._status = ('ok', '')
        except Exception as e:
            self._status = ('error', e)

        if humidity:
            self._humidity = 100 * humidity / (65535.0)
        if temperature:
            self._temperature = -45 + 175 * temperature / (65535.0)
        if self._temperature < -30 or self._temperature > 100 or self._humidity < 0 or self._humidity > 100:
            self._status = ('error', 'Temperature/Humidity is out of range')
        else:
            self._status = ('ok', '')

    def read_id_register(self):
        cmd = b'\xef\xc8'
        data = self._read_i2c(cmd, 3)
        try:
            self._status = ('ok', '')
            if self._calc_crc(data) == bytes([data[2]]):
                return data[0:2]
        except Exception as e:
            self._status = ('error', e)

    def reset(self):
        cmd = b'\x80\x5d'
        self._write_i2c(cmd)
