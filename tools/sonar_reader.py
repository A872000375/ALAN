from RPi import GPIO as IO
import time


class SonarReader:

    def __init__(self):
        # Sonar reader cables from LEFT to RIGHT (in the module itself):purple, blue, green, yellow
        self.DEBUG_MODE = True
        IO.setmode(IO.BOARD)
        self.EMPTY_DISTANCE = 6.25
        self.FULL_DISTANCE = 1
        self.pin_map = {
            'sonar_trig': 10,  # RED CABLE
            'sonar_echo': 11,   # ORANGE CABLE
        }
        # TODO: Redo sonar pins for GPIO.BOARD configuration
        IO.setup(self.pin_map['sonar_trig'], IO.OUT)
        IO.setup(self.pin_map['sonar_echo'], IO.IN)

    def read_sonar_ping(self):
        IO.output(self.pin_map['sonar_trig'], IO.LOW)
        time.sleep(2)
        IO.output(self.pin_map['sonar_trig'], IO.HIGH)
        time.sleep(0.00001)
        IO.output(self.pin_map['sonar_trig'], IO.LOW)

        start_time = None
        end_time = None

        while IO.input(self.pin_map['sonar_echo']) == 0:
            # While input reads on
            start_time = time.time()

        while IO.input(self.pin_map['sonar_echo']) == 1:
            end_time = time.time()

        duration = end_time - start_time

        distance = round(duration * 17150, 2)  # will be centimeters
        if self.DEBUG_MODE:
            print('Food Distance:', distance)

        return distance  # centimeters

    def is_empty(self):
        return self.read_sonar_ping() <= self.EMPTY_DISTANCE

    def is_full(self):
        return self.read_sonar_ping() >= self.FULL_DISTANCE

    def get_feed_tank_level(self):
        return self.read_sonar_ping() / self.EMPTY_DISTANCE

    def get_feed_tank_level_formatted(self):
        feed_level = self.get_feed_tank_level() * 100
        return f'{feed_level:0.0f}%'
