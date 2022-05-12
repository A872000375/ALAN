import tkinter

from RPi import GPIO as IO

import time
from tools.temp_reader import TempReader
from tools.sonar_reader import SonarReader
from threading import Thread
from tools.heater_controller import HeaterController
from time import sleep
from tools.servo_controller import FeederScheduler, ServoController
from queue import Queue
import tkinter as tk
import queue


# This is the GPIO Controller Class
class PiIo:

    # passthrough tkinter variables for the thread to check
    def __init__(self, tk_vars: dict, root: tk.Tk):
        self.tk_vars = tk_vars
        self.root = root
        self.kill_thread = False
        self.previous_feeder_level = None
        self.food_level = '0%'
        self.temp_target = tk_vars['temp'].get()
        # Init Queues
        self.food_level_q = Queue()
        self.food_amt_q = Queue()
        self.food_freq_q = Queue()
        self.temp_q = Queue()
        # Put starting values into queues
        self.food_amt_q.put(self.tk_vars['amt'].get())  # Amount
        self.food_freq_q.put(self.tk_vars['freq'].get())  # Frequency
        self.temp_q.put(self.tk_vars['temp'].get())  # Temp

        self.heat_control = HeaterController()
        self.temp_reader = TempReader()
        self.sonar_reader = SonarReader(self.food_level_q)

        self.DEBUG_MODE = True
        self.pin_map = {
            'sonar_trig': 10,  # TrigPin
            'sonar_echo': 11,
            'servo': 9,
        }
        # TODO: Redo sonar pins for GPIO.BOARD configuration
        IO.setup(self.pin_map['sonar_trig'], IO.OUT)
        IO.setup(self.pin_map['sonar_echo'], IO.IN)

        # Temperature management threading
        self.temp_thread = Thread(target=self.check_temperature)
        self.temp_thread.start()
        print('started temp thread')
        self.servo = ServoController()
        self.feeder_scheduler = FeederScheduler(self.servo, self.tk_vars, self.food_amt_q,
                                                self.food_freq_q)  # Starts on its own
        print('Started FeederScheduler')
        # self.queue_check_thread = Thread(target=self.periodic_queue_check())
        # self.queue_check_thread.start()
        self.periodic_queue_check()
        print('started periodic queue check')
        # self.root_thread = Thread(target=self.start_mainloop())
        # self.root_thread.start()
        self.start_mainloop()

        print('End of piio init')

    def start_mainloop(self):
        print('Starting mainloop')
        self.root.mainloop()

    def periodic_queue_check(self):
        print('-Starting queue check')
        # Do all of our transmission calls
        self.sonar_reader.transmit_feed_level()
        # print('Transmitted food level')
        self.food_freq_q.put(self.tk_vars['freq'].get())
        self.food_amt_q.put(self.tk_vars['amt'].get())
        # print('Transmitted food freq and amt')
        # print('Receiving...')
        # Do all of our receiving calls here
        self.feeder_scheduler.receive_food_freq()
        self.feeder_scheduler.receive_food_amt()
        self.receive_temp_target()
        self.receive_food_level()
        if self.kill_thread:
            print('Killing threads')
            return
        else:
            self.root.after(2000, self.periodic_queue_check)

    def update_feeder_level(self):
        level_formatted = self.food_level
        current_level_value = int(level_formatted[:-1]) / 100.00

        # In the case that the tank is
        if current_level_value > 1.00:
            self.tk_vars['level'].set(
                'The feeder tank is either currently open,\nor has been overfilled. \nPlease check the feeder.')
            return

        if self.previous_feeder_level is None:
            self.tk_vars['level'].set(level_formatted)
            self.previous_feeder_level = current_level_value
        else:
            level_delta = current_level_value - self.previous_feeder_level
            if abs(level_delta) >= 0.01:
                self.tk_vars['level'].set(level_formatted)
                self.previous_feeder_level = current_level_value

    def kill_threads(self):
        self.kill_thread = True
        self.feeder_scheduler.stop_threads()

    def receive_food_level(self):
        while self.food_level_q.qsize() > 0:
            try:
                self.food_level = self.food_level_q.get()
                # print('Received food level')
                self.update_feeder_level()
                # print('Updated food level')
            except queue.Empty:
                return

    def receive_temp_target(self):
        while self.temp_q.qsize() > 0:
            try:
                self.temp_target = self.temp_q.get()
                # print('Received temp target')
            except queue.Empty:
                pass

    # This is the PID loop for the temp and heater elements.
    # If the heat is too low, the heater is turned on, and if too high, turned off
    def check_temperature(self):
        while True:
            if self.kill_thread:
                self.heat_control.heater_toggle(False)  # Turn off heater when exiting
                break
            current_temp = self.get_temp_f()
            target_temp = self.temp_target

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
            return self.temp_reader.read_temp()[0]
        except IndexError as e:
            return 10000  # this will trigger the heater to shut off if there is an error

    def get_all_temps(self):
        return self.get_temp_f(), self.get_temp_c()
