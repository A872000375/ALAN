import RPi.GPIO as GPIO
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import math


def convert(self, status):
    if status == 1:
        return 'HIGH'
    else:
        return 'LOW'


class Control:

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # Heater setup
        self.HEATER_PIN = 36
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.HEATER_PIN, GPIO.OUT)

        # Temperature Sensor setup
        self.ads = ADS.ADS1115(self.i2c)
        # do I add this? : self.ads.mode = Mode.CONTINUOUS (where to import Mode?)
        self.temp_sensor = AnalogIn(self.ads, ADS.P0)

    def heater_toggle(self, status: bool):
        previous = self.get_heater_status_readable()
        if status is True:
            GPIO.output(self.HEATER_PIN, GPIO.HIGH)
        else:
            GPIO.output(self.HEATER_PIN, GPIO.LOW)

        print(f'Heater was changed from {previous} to {self.get_heater_status_readable()}')

    def get_heater_status_readable(self):
        return convert(GPIO.input(self.HEATER_PIN))

    def get_raw_heater_status(self):
        return GPIO.input(self.HEATER_PIN)

    def get_raw_temp_value(self):
        return self.chan.value

    def convert_temp_value_to_fahrenheit(self, value=None):
        if value is None:
            value = self.chan.value

        # https://www.instructables.com/16-bit-I2C-Temperature-Monitor-Using-Arduino/
        # ref_current = 0.0001
        # therm_25 = 10000
        #
        # voltage = value * (5.0 / 65535)
        #
        # resistance = voltage / ref_current
        #
        # log_of_ratio = math.log10(resistance / therm_25)

        # TODO: program sensor (trial and error, probably)
