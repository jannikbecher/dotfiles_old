"""
Reading format. See https://cdn.sparkfun.com/assets/2/d/2/a/6/Sensirion_SPS30_Particulate_Matter_Sensor_v0.9_D1__1_.pdf
"""

import ustruct as struct
import time

class SPS30:
    """A driver for the SPS30 particulate matter sensor.
    :param i2c: The `I2C` object to use.
    """
    ADDRESS=0x69
    I2C_WRITE_DELAY_MS=20
    def __init__(self, i2c):
        self._i2c = i2c
        self._pm05_num = 0.0
        self._pm1_num = 0.0
        self._pm25_num = 0.0
        self._pm4_num = 0.0
        self._pm10_num = 0.0
        self._pm1_mass = 0.0
        self._pm25_mass = 0.0
        self._pm4_mass = 0.0
        self._pm10_mass = 0.0
        self._typical_size = 0.0
        self._packet_status = False
        self._status = ('ok', '')

    @property
    def pm_data(self):
        """Return all data bundled as dict"""
        return {
            'pm05_num': self._pm05_num,
            'pm1_num': self._pm1_num,
            'pm25_num': self._pm25_num,
            'pm4_num': self._pm4_num,
            'pm10_num': self._pm10_num,
            'pm1_mass': self._pm1_mass,
            'pm25_mass': self._pm25_mass,
            'pm4_mass': self._pm4_mass,
            'pm10_mass': self._pm10_mass,
            'typical_size': self._typical_size
        }

    @property
    def pm05_num(self):
        """Return the PM0.5 number concentration, in #/cm^3."""
        return self._pm05_num

    @property
    def pm1_num(self):
        """Return the PM1 number concentration, in #/cm^3."""
        return self._pm1_num

    @property
    def pm25_num(self):
        """Return the PM2.5 number concentration, in #/cm^3."""
        return self._pm25_num

    @property
    def pm4_num(self):
        """Return the PM4 number concentration, in #/cm^3."""
        return self._pm4_num

    @property
    def pm10_num(self):
        """Return the PM10 number concentration, in #/cm^3."""
        return self._pm10_num

    @property
    def pm1_mass(self):
        """Return the PM1 concentration, in µg/m^3."""
        return self._pm1_mass

    @property
    def pm25_mass(self):
        """Return the PM2.5 concentration, in µg/m^3."""
        return self._pm25_mass

    @property
    def pm4_mass(self):
        """Return the PM4 concentration, in µg/m^3."""
        return self._pm4_mass

    @property
    def pm10_mass(self):
        """Return the PM10 concentration, in µg/m^3."""
        return self._pm10_mass

    @property
    def typical_size(self):
        """Return the Typical Particle Size, in µg."""
        return self._typical_size

    @property
    def packet_status(self):
        """Return if there are new measured values."""
        return self._packet_status

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

    def _calc_float(self, b):
        struct_float = struct.pack('>BBBB', b[0], b[1], b[3], b[4])
        float_values = struct.unpack('>f', struct_float)
        crc1 = self._calc_crc(b[0:2])
        crc2 = self._calc_crc(b[3:5])
        if crc1 == bytes([b[2]]) and crc2 == bytes([b[5]]):
            return float_values[0]
        else:
            print('crc error: ' + str(crc1) + '=' + str(bytes([b[2]])) + ' ' + str(crc2) + '=' + str(bytes([b[5]])))
            return None

    def _calc_int(self, b):
        struct_int = struct.pack('>BBBB', b[0], b[1], b[3], b[4])
        int_values = struct.unpack('>i', struct_int)
        crc1 = self._calc_crc(b[0:2])
        crc2 = self._calc_crc(b[3:5])
        if crc1 == bytes([b[2]]) and crc2 == bytes([b[5]]):
            return int_values[0]
        else:
            print('crc error: ' + str(crc1) + '=' + str(bytes([b[2]])) + ' ' + str(crc2) + '=' + str(bytes([b[5]])))
            return None

    def _calc_from_int(self, integer):
        struct_int = struct.pack('>i', integer)
        b = struct.unpack('>BBBB', struct_int)
        return b

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
        self.write_auto_cleaning_interval(0)
        self.reset()
        self.start_measurement()
        self.read_auto_cleaning_interval()
        self.read_data_ready_flag()
        if self.packet_status == False:
            return False
        if self.status[0] == 'ok':
            return True
        else:
            return False

    def start_measurement(self):
        cmd = b'\x00\x10'
        data = b'\x03\x00'
        crc = self._calc_crc(data)
        self._write_i2c(cmd+data+crc)

    def stop_measurement(self):
        cmd = b'\x01\x04'
        self._write_i2c(cmd)

    def read_data_ready_flag(self):
        cmd = b'\x02\x02'
        data = self._read_i2c(cmd, 3)
        try:
            crc = self._calc_crc(data[0:2])
            if crc == bytes([data[2]]):
                if data[1] == 0x01:
                    self._packet_status = True
                else:
                    self._packet_status = False
            else:
                print('read data ready flag crc error ' + str(crc) + '=' + str(bytes([data[2]])))
        except:
            self._status = ('error', 'can\'nt read data ready flag')

    def read_measured_values(self):
        cmd = b'\x03\x00'
        data = self._read_i2c(cmd, 60)
        pm1_mass      = self._pm1_mass
        pm25_mass     = self._pm25_mass
        pm4_mass      = self._pm4_mass
        pm10_mass     = self._pm10_mass
        pm05_num      = self._pm05_num
        pm1_num       = self._pm1_num
        pm25_num      = self._pm25_num
        pm4_num       = self._pm4_num
        pm10_num      = self._pm10_num
        typical_size  = self._typical_size
        try:
            pm1_mass      =   self._calc_float(data[0:6])
            pm25_mass     =  self._calc_float(data[6:12])
            pm4_mass      = self._calc_float(data[12:18])
            pm10_mass     = self._calc_float(data[18:24])
            pm05_num      = self._calc_float(data[24:30])
            pm1_num       = self._calc_float(data[30:36])
            pm25_num      = self._calc_float(data[36:42])
            pm4_num       = self._calc_float(data[42:48])
            pm10_num      = self._calc_float(data[48:54])
            typical_size  = self._calc_float(data[54:60])
            self._status = ('ok', '')
        except Exception as e:
            self._status = ('error', e)

        if pm1_mass:
            self._pm1_mass = pm1_mass
        if pm25_mass:
            self._pm25_mass = pm25_mass
        if pm4_mass:
            self._pm4_mass = pm4_mass
        if pm10_mass:
            self._pm10_mass = pm10_mass
        if pm05_num:
            self._pm05_num = pm05_num
        if pm1_num:
            self._pm1_num = pm1_num
        if pm25_num:
            self._pm25_num = pm25_num
        if pm4_num:
            self._pm4_num = pm4_num
        if pm10_num:
            self._pm10_num = pm10_num
        if typical_size:
            self._typical_size = typical_size

        if self._pm1_mass < 0 or self._pm1_mass > 1000 or self._pm25_mass < 0 or self._pm25_mass > 1000 or self._pm4_mass < 0 or self._pm4_mass > 1000 or self._pm10_mass < 0 or self._pm10_mass > 1000 or self._pm05_num < 0 or self._pm05_num > 3000 or self._pm1_num < 0 or self._pm1_num > 3000 or self._pm25_num < 0 or self._pm25_num > 3000 or self._pm4_num < 0 or self._pm4_num > 3000 or self._pm10_num < 0 or self._pm10_num > 3000:
            print(self.pm1_mass)
            print(self.pm25_mass)
            print(self.pm4_mass)
            print(self.pm10_mass)
            print(self.pm05_num)
            print(self.pm1_num)
            print(self.pm25_num)
            print(self.pm4_num)
            print(self.pm10_num)
            self._status = ('error', 'PM values out of range')
        else:
            self._status = ('ok', '')

    def read_auto_cleaning_interval(self):
        cmd = b'\x80\x04'
        data = self._read_i2c(cmd, 6)
        interval = 0
        try:
            interval = self._calc_int(data)
            self._status = ('ok', '')
        except Exception as e:
            self._status = ('error', e)
        return interval

    def write_auto_cleaning_interval(self, interval):
        cmd = b'\x80\x04'
        data = self._calc_from_int(interval)
        msb = bytes(data[0:2])
        lsb = bytes(data[2:4])
        crc1 = self._calc_crc(msb)
        crc2 = self._calc_crc(lsb)
        self._write_i2c(cmd + msb + crc1 + lsb + crc2)

    def start_fan_cleaning(self):
        cmd = b'\x56\x07'
        self._write_i2c(cmd)

    def read_article_code(self):
        cmd = b'\xD0\x25'
        data = self._read_i2c(cmd, 48)
        return data

    def read_serial_number(self):
        cmd = b'\xD0\x33'
        data = self._read_i2c(cmd, 48)
        return data

    def reset(self):
        cmd = b'\xD3\x04'
        self._write_i2c(cmd)
