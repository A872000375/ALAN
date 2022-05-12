from adafruit_servokit import ServoKit
from time import sleep
from datetime import datetime
from threading import Thread
from board import SCL, SDA
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685
from adafruit_motor.servo import Servo
import RPi.GPIO as GPIO
from queue import Queue
import queue


class ServoController:

    def __init__(self, starting_angle=0):
        self.MIN_DUTY = 5
        self.MAX_DUTY = 10

        self.SERVO_PIN = 13  # GPIO 27

        self.OPEN_POSITION = 30
        self.CLOSE_POSITION = 0
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.servo = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo.start(0)  # Start up the servo, but don't move it yet
        self.current_angle = starting_angle
        self.set_angle(self.current_angle)

    def test_servo(self):
        while True:
            print('Testing servo')
            self.open_feeder()
            sleep(3)
            self.close_feeder()
            sleep(3)
            print('Testing feeder operation')
            self.operate_feeder()

    def set_angle(self, degree):
        if degree > 180 or degree < 0:
            print('Invalid servo degree.')
            return
        self.servo.ChangeDutyCycle(self.deg_to_duty(degree))
        self.current_angle = degree

    def deg_to_duty(self, deg):
        return (deg - 0) * (self.MAX_DUTY - self.MIN_DUTY) / 180 + self.MIN_DUTY

    def operate_feeder(self, units_of_food: int):
        # Each unit of food corresponds to 0.1 second of food dispensing
        operation_time_sec = units_of_food * 0.1
        self.open_feeder()
        sleep(operation_time_sec)
        self.close_feeder()

    def open_feeder(self):
        self.set_angle(self.OPEN_POSITION)

    def close_feeder(self):
        self.set_angle(self.CLOSE_POSITION)

    def get_current_angle(self):
        return self.current_angle


def hours_to_seconds(num_hours):
    return num_hours * 3600


class FeederScheduler:

    def __init__(self, servo: ServoController, tk_vars: dict, food_amt_q: Queue, food_freq_q: Queue):
        self.food_amt_q = food_amt_q
        self.food_freq_q = food_freq_q
        self.food_amt = 1
        self.food_freq = 24
        self.DEFAULT_INTERVAL = 24
        self.DEFAULT_FOOD_AMOUNT = 10
        self.tk_vars = tk_vars
        self.servo = servo

        self.stop_thread = False

        self.feed_thread = Thread(target=self.feed_timer)
        self.feed_thread.start()

    def feed_timer(self):
        while not self.stop_thread:
            if self.stop_thread:
                break
            self.servo.operate_feeder(self.food_amt)
            print('Operating servo...')
            print(f'Next feed in {self.food_freq} hours, '
                  f'or {hours_to_seconds(self.food_freq)} seconds.')
            sleep(hours_to_seconds(self.food_freq))

        self.stop_thread = False

    def stop_threads(self):
        self.stop_thread = True
        print('Terminating FeederScheduler daemon.')

    def receive_food_freq(self):
        while self.food_freq_q.qsize():
            try:
                self.food_freq = self.food_freq_q.get()
                # print('Received food freq')
            except queue.Empty:
                pass

    def receive_food_amt(self):
        while self.food_amt_q.qsize() > 0:
            try:
                self.food_amt = self.food_amt_q.get()
                # print('Received food amt')
            except queue.Empty:
                pass
