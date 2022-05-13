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


class ServoController:

    def __init__(self, starting_angle=0):
        self.MIN_DUTY = 5
        self.MAX_DUTY = 10
        self.SERVO_PIN = 32  # GPIO 12, BOARD 32 (PWM0)
        self.OPEN_POSITION = 30
        self.CLOSE_POSITION = 0
        self.SERVO_DELAY = 1  # Controls the speed of the servo
        # wiring.wiringPiSetupGpio()
        # wiring.pinMode(self.SERVO_PIN, wiring.GPIO.PWM_OUTPUT)
        # wiring.pwmSetMode(wiring.GPIO.PWM_MODE_MS)  # Set to ms stype
        #
        # # divide down clock
        # # pulse value of 1 is fast, 75 is stop
        # wiring.pwmSetClock(384)
        # wiring.pwmSetRange(1000)
        #
        # GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        # self.servo = GPIO.PWM(self.SERVO_PIN, 50)
        # self.servo.start(0)  # Start up the servo, but don't move it yet
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)

        # self.current_angle = starting_angle
        # self.set_angle(self.current_angle)

    def test_servo(self):
        sleep(10)
        print('PWM start')
        p = GPIO.PWM(self.SERVO_PIN, 100)
        p.start(5)
        print(2.5)
        p.ChangeDutyCycle(2.5)
        sleep(5)
        print(11.5)
        p.ChangeDutyCycle(11.5)
        sleep(5)
        print(20.5)
        p.ChangeDutyCycle(20.5)
        sleep(5)
        print(11.5)
        p.ChangeDutyCycle(11.5)

    def send_pulse(self, pulse):
        wiring.pwmWrite(self.SERVO_PIN, pulse)

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
            food_amt_num = 0
            try:
                food_amt_num = int(self.food_amt)
            except ValueError:
                print('ERROR: FOOD FREQUENCY VALUE IS NOT A NUMBER')
                sleep(5)
                continue
            self.servo.operate_feeder(food_amt_num)
            print('Operating servo...')
            print(f'Next feed in {self.food_freq} hours, '
                  f'or {hours_to_seconds(self.food_freq)} seconds.')
            food_freq_num = 0
            try:
                food_freq_num = int(self.food_freq)
            except ValueError:
                print('ERROR: FOOD FREQUENCY VALUE IS NOT A NUMBER')
                sleep(5)
                continue
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
