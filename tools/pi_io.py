from RPi import GPIO as IO

import time
from tools.temp_reader import TempReader
from tools.sonar_reader import SonarReader
from threading import Thread
from tools.heater_controller import HeaterController
from time import sleep


# This is the GPIO Controller Class
class PiIo:

    # passthrough tkinter variables for the thread to check
    def __init__(self, tk_vars: dict):
        self.kill_thread = False
        self.previous_feeder_level = None
        IO.setmode(IO.BOARD)
        self.heat_control = HeaterController()
        self.temp_reader = TempReader()
        self.sonar_reader = SonarReader()
        self.DEBUG_MODE = True
        self.pin_map = {
            'sonar_trig': 10,  # TrigPin
            'sonar_echo': 11,
            'servo': 9,
        }
        # TODO: Redo sonar pins for GPIO.BOARD configuration
        IO.setup(self.pin_map['sonar_trig'], IO.OUT)
        IO.setup(self.pin_map['sonar_echo'], IO.IN)
        self.tk_vars = tk_vars

        # Temperature management threading
        self.temp_thread = Thread(target=self.check_temperature)
        self.temp_thread.start()

    def update_feeder_level(self):
        while True:
            if self.kill_thread:
                break

            level_formatted = self.sonar_reader.get_feed_tank_level_formatted()
            current_level_value = self.sonar_reader.get_feed_tank_level()

            # In the case that the tank is
            if current_level_value > 1.00:
                self.tk_vars['level'].set(
                    'The feeder tank is either currently open,\nor has been overfilled. Please check the feeder.')
                continue

            if self.previous_feeder_level is None:
                self.tk_vars['level'].set(level_formatted)
                self.previous_feeder_level = current_level_value
            else:
                level_delta = current_level_value - self.previous_feeder_level
                if level_delta >= 0.01:
                    self.tk_vars['level'].set(level_formatted)
                    self.previous_feeder_level = current_level_value

        print('Feeder level monitor daemon has been terminated.')

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

            temp_needed = target_temp - current_temp
            print('Current Temp:', current_temp)
            print('Target Temp:', target_temp)
            print('Temp Deltas:', temp_needed)
            if temp_needed > 0.5:
                # Turn on the heater
                self.heat_control.heater_toggle(True)
            elif temp_needed < -0.5:
                # Turn off the heater
                self.heat_control.heater_toggle(False)

            sleep(10)
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
