import RPi.GPIO as GPIO


def convert(self, status):
    if status == 1:
        return 'HIGH'
    else:
        return 'LOW'


class HeaterController:

    def __init__(self):

        # Heater setup
        self.HEATER_PIN = 36
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.HEATER_PIN, GPIO.OUT)

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
