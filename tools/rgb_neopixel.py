import board
from neopixel import NeoPixel
from time import sleep
class RGBController:


    def __init__(self):
        self.MAX_PIXEL_RANGE = 59 # there are only 60 pixels

        self.pixels = NeoPixel()
        for x in range(255):
            self.pixels.fill((x, 0, x))
            sleep(0.1)

        self.pixels.fill((0, 0, 0))

    def fill(self, color: tuple):
        self.pixels.fill(color)

    def set_pixel(self, position: int, color: tuple):
        if position > self.MAX_PIXEL_RANGE:
            position = self.MAX_PIXEL_RANGE

        self.pixels[position] = color


