import gpio as io
import time
from temp_reader

class PiIo:

    def __init__(self):
        self.DEBUG_MODE = True
        self.pin_map = {
            'sonar_trig': 10,  # TrigPin
            'sonar_echo': 11,
            'servo': 9,
            'temp': 5r
        }
        io.setmode(io.BCM)
        io.setup(self.pin_map['sonar_trig'], io.OUT)
        io.setup(self.pin_map['sonar_echo'], io.IN)

        self.temp_reader =

    def read_sonar_ping(self):
        io.output(self.pin_map['sonar_trig'], io.LOW)
        time.sleep(2)
        io.output(self.pin_map['sonar_trig'], io.HIGH)
        time.sleep(0.00001)
        io.output(self.pin_map['sonar_trig'], io.LOW)

        start_time = None
        end_time = None

        while io.input(self.pin_map['sonar_echo']) == 0:
            # While input reads on
            start_time = time.time()

        while io.input(self.pin_map['sonar_echo']) == 1:
            end_time = time.time()

        duration = end_time - start_time

        distance = round(duration * 17150, 2)  # will be centimeters
        if self.DEBUG_MODE:
            print('Food Distance:', distance)

        return distance
