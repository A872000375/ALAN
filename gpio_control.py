import RPi.GPIO as GPIO


def convert(self, status):
    if status == 1:
        return 'HIGH'
    else:
        return 'LOW'

class Control:

    def __init__(self):
        self.HEATER_PIN = 36
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.HEATER_PIN, GPIO.OUT)

    def heater_toggle(self, status: bool):
        previous = GPIO.input(self.HEATER_PIN)
        if status is True:
            GPIO.output(self.HEATER_PIN, GPIO.HIGH)
        else:
            GPIO.output(self.HEATER_PIN, GPIO.LOW)

        print(f'Heater was changed from {convert(previous)} to {convert(status)}')



