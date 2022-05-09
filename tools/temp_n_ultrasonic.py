# from RPi import GPIO
# import time
# import os
# import glob
#
# # #GPIO Mode (BOARD / BCM)
# # GPIO.setmode(GPIO.BCM)
#
# #set GPIO Pins
# GPIO_TRIGGER = 8
# GPIO_ECHO = 11
#
# #set GPIO direction (IN / OUT)
# GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
# GPIO.setup(GPIO_ECHO, GPIO.IN)
#
# #getting temper data file
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')
# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '28*')[0]
# device_file = device_folder + '/w1_slave'
#
# #class for ultrasonic
# def distance():
#     GPIO.output(GPIO_TRIGGER, True)
#     time.sleep(0.00001)
#     GPIO.output(GPIO_TRIGGER, False)
#     StartTime = time.time()
#     StopTime = time.time()
#     while GPIO.input(GPIO_ECHO) == 0:
#         StartTime = time.time()
#     while GPIO.input(GPIO_ECHO) == 1:
#         StopTime = time.time()
#     TimeElapsed = StopTime - StartTime
#     distance = (TimeElapsed * 34300) / 2
#
#     return distance
#
# #class for temp
# def temperature():
#     #get temperature data
#     f = open(device_file, 'r')
#     lines = f.readlines()
#     f.close()
#     while lines[0].strip()[-3:] != 'YES':
#         time.sleep(0.2)
#     equals_pos = lines[1].find('t=')
#     if equals_pos != -1:
#         temp_string = lines[1][equals_pos+2:]
#         temp_c = float(temp_string) / 1000.0
#         return temp_c
#
# try:
#     while True:
#         dist = distance()
#         print ("Distance = %.1f cm" % dist)
#         temp=(temperature())
#         print (temp, 'Degree Celsius')
#         time.sleep(1)
#
# except KeyboardInterrupt:
#     print("Measurement stopped by User")
#     GPIO.cleanup()