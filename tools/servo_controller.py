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


class ServoController:

    def __init__(self, starting_angle=0):
        self.MIN_DUTY = 5
        self.MAX_DUTY = 10

        self.SERVO_PIN = 13  # GPIO 27

        self.OPEN_POSITION = 30
        self.CLOSE_POSITION = 0
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.servo = GPIO.pwm(self.SERVO_PIN, 50)
        self.servo.start(0)  # Start up the servo, but don't move it yet
        self.current_angle = starting_angle
        self.set_angle(self.current_angle)

        self.test_servo()

    def test_servo(self):
        while True:
            self.set_angle(0)
            sleep(3)
            self.set_angle(90)
            sleep(3)

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

    def __init__(self, servo_control: ServoController, tk_vars: dict):
        self.DEFAULT_INTERVAL = 24
        self.DEFAULT_FOOD_AMOUNT = 10
        self.tk_vars = tk_vars
        self.servo = servo_control
        self.feed_interval = self.tk_vars['freq']
        self.food_units = self.tk_vars['amt']
        self.stop_thread = False

        self.feed_thread = Thread(target=self.feed_timer)
        self.feed_thread.start()

    def feed_timer(self):
        while not self.stop_thread:
            if self.stop_thread:
                break
            self.servo.operate_feeder(self.food_units.get())
            print('Operating servo...')
            print(
                f'Next feed in {self.get_food_frequency()} hours, '
                f'or {hours_to_seconds(self.get_food_frequency())} seconds.')
            sleep(hours_to_seconds(self.feed_interval.get()))

        self.stop_thread = False

    def stop_threads(self):
        self.stop_thread = True
        print('Terminating FeederScheduler daemon.')

    def get_food_frequency(self):
        try:
            return int(self.feed_interval.get())
        except ValueError as e:
            return self.DEFAULT_INTERVAL

    def get_food_amount(self):
        try:
            return int(self.food_units.get())
        except ValueError as e:
            return self.DEFAULT_FOOD_AMOUNT
