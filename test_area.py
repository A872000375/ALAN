from tools.sonar_reader import SonarReader
from queue import Queue
from time import sleep
myqueue = Queue
sonar = SonarReader(myqueue)


while True:
    print(sonar.read_sonar_ping())
    sleep(1)
