# This class is for running and testing the SmartFishTank Project while in windows

BOARD = 'setup as Board.'
BCM = 'setup as BCM.'
OUT = 'set as Output.'
IN = 'set as Input.'
HIGH = 'HIGH'
LOW = 'LOW'

def setmode(a):
   print(a)
def setup(a, b):
   print(a, b)
def output(a, b):
   print(a, b)
def input(a):
   return LOW;
def cleanup():
   print('cleaned up.')
def setwarnings(flag):
   print('warnings set.')