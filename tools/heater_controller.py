import RPi.GPIO as GPIO


def convert(status):
    if status == 1:
        return 'HIGH'
    else:
        return 'LOW'


class HeaterController:

    def __init__(self):

        # Heater setup
        self.HEATER_PIN = 36
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.HEATER_PIN, GPIO.OUT)

    # Desc: Sets the heater to on (True) or off (False)
    def heater_toggle(self, status: bool):
        previous = self.get_heater_status_readable()
        if status is True:
            GPIO.output(self.HEATER_PIN, GPIO.HIGH)
        else:
            GPIO.output(self.HEATER_PIN, GPIO.LOW)

        # print(f'Heater was changed from {previous} to {self.get_heater_status_readable()}')

    def get_heater_status_readable(self):
        status = self.get_raw_heater_status()
        # print(status)
        return convert(status)

    def get_raw_heater_status(self):
        # GPIO.setmode(GPIO.BOARD)
        value = GPIO.input(self.HEATER_PIN)
        return value
