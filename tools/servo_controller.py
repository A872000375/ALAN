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
import wiringpi as wiring


def ms_to_duty(ms: float):
    period = 20  # 20ms period for this servo
    return (ms / period) * 100


def hours_to_seconds(num_hours):
    return num_hours * 3600


class ServoController:

    def __init__(self, starting_angle=0):
        self.MIN_DUTY = 5
        self.MAX_DUTY = 10
        self.SERVO_PIN = 18  # GPIO 18, BOARD 12 # PCM_CLK
        self.OPEN_POSITION = 30
        self.CLOSE_POSITION = 0
        self.SERVO_DELAY = 1  # Controls the speed of the servo
        self.CCW_DUTY = 1
        self.STOP_DUTY = 0
        self.CW_DUTY = 2
        self.SECONDS_PER_UNIT_FOOD = 1
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        self.p = GPIO.PWM(self.SERVO_PIN, 50)
        self.p.start(0)

    def operate_feeder(self, units_of_food):
        if units_of_food < 1:
            print('Must specify at least 1 unit of food.')
        print('Operating servo...')
        duty = ms_to_duty(self.CCW_DUTY)
        self.p.ChangeDutyCycle(duty)
        sleep(units_of_food * self.SECONDS_PER_UNIT_FOOD)
        self.p.ChangeDutyCycle(0)


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
            food_amt_num = 0
            try:
                food_amt_num = int(self.food_amt)
            except ValueError:
                print('ERROR: FOOD AMOUNT VALUE IS NOT A NUMBER')
                sleep(5)
                continue
            self.servo.operate_feeder(food_amt_num)
            print('Operating servo...')

            food_freq_num = 0
            try:
                food_freq_num = float(self.food_freq)
            except ValueError:
                print('ERROR: FOOD FREQUENCY VALUE IS NOT A NUMBER')
                sleep(5)
                continue
            print(f'Next feed in {food_freq_num} hours, '
                  f'or {hours_to_seconds(food_freq_num)} seconds.')
            sleep(hours_to_seconds(food_freq_num))

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
