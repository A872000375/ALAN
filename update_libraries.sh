
pip install Adafruit-ADS1x15==1.0.2, Adafruit-Blinka==7.2.2, adafruit-circuitpython-ads1x15==2.2.13, adafruit-circuitpython-busdevice==5.1.8, adafruit-circuitpython-motor==3.4.0, adafruit-circuitpython-neopixel==6.3.0, adafruit-circuitpython-pca9685==3.4.1, adafruit-circuitpython-pixelbuf==1.1.3, adafruit-circuitpython-register==1.9.8, adafruit-circuitpython-servokit==1.3.8, adafruit-circuitpython-typing==1.6.0, Adafruit-GPIO==1.0.3, Adafruit-PlatformDetect==3.22.1, Adafruit-PureIO==1.1.9
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
