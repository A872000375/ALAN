from RPi import GPIO as io

import time
from tools.temp_reader import TempReader
from threading import Thread
from tools.heater_controller import HeaterController
from time import sleep


# This is the GPIO Controller Class
class PiIo:

    # passthrough tkinter variables for the thread to check
    def __init__(self, tk_vars: dict):
        self.kill_thread = False
        io.setmode(io.BOARD)
        self.heat_control = HeaterController()
        self.temp_reader = TempReader()

        self.DEBUG_MODE = True
        self.pin_map = {
            'sonar_trig': 10,  # TrigPin
            'sonar_echo': 11,
            'servo': 9,
        }
        # TODO: Redo sonar pins for GPIO.BOARD configuration
        io.setup(self.pin_map['sonar_trig'], io.OUT)
        io.setup(self.pin_map['sonar_echo'], io.IN)
        self.tk_vars = tk_vars

        # Temperature management threading
        self.temp_thread = Thread(target=self.check_temperature)
        self.temp_thread.start()

    def kill_threads(self):
        self.kill_thread = True

    # This is the PID loop for the temp and heater elements.
    # If the heat is too low, the heater is turned on, and if too high, turned off
    def check_temperature(self):
        while True:
            if self.kill_thread:
                self.heat_control.heater_toggle(False)  # Turn off heater when exiting
                break
            current_temp = self.get_temp_f()
            target_temp = self.tk_vars['temp'].get()

            try:
                current_temp = float(current_temp)
            except ValueError as e:
                print('Could not convert current temp.')
                return

            try:
                target_temp = float(target_temp)
            except ValueError as e:
                print('Could not convert target temp')
                return


            print(current_temp)

            temp_needed = target_temp - current_temp
            if temp_needed > 0.5:
                # Turn on the heater
                self.heat_control.heater_toggle(True)
            elif temp_needed < -0.5:
                # Turn off the heater
                self.heat_control.heater_toggle(False)

            sleep(1)
        print('Temperature manager daemon has been terminated.')

    def get_temp_f(self):
        try:
            return self.temp_reader.read_temp()[1]
        except IndexError as e:
            return 10000  # this will trigger the heater to shut off if there is an error

    def get_temp_c(self):
        try:
            return self.temp_reader.read_temp()[1]
        except IndexError as e:
            return 10000  # this will trigger the heater to shut off if there is an error

    def get_all_temps(self):
        return self.get_temp_f(), self.get_temp_c()

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
