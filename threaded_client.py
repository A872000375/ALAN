import tkinter as tk
from queue import Queue
import queue
from tools.pi_io import PiIo

'''
Current plan:

1. Pass through queues to PiIo class
2. Create functions to update values for other threads via a receive() function similar to receive_feed_level
2a. Feed amt, feed freq, and target temp are receive methods needed
3. Create function to transmit the current feed level to the GuiPart
4. Better way to organize this?


'''


class GuiPart:

    def __init__(self, root: tk.Tk, feed_level_q: Queue, food_amt_q: Queue, food_freq_q: Queue, tk_vars: dict, elements: dict):
        self.root = root
        self.feed_level_q = feed_level_q
        self.food_amt_q = food_amt_q
        self.food_freq_q = food_freq_q
        self.tk_vars = tk_vars
        self.elements = elements

    def receive_feed_level(self):
        while self.feed_level_q.qsize():
            try:
                feed_level = self.queue.get()
                print('feed_level_q:', feed_level)
                self.tk_vars['level'].set(feed_level)
            except queue.Empty:
                pass

    def transmit_temp(self):
        pass

    def transmit_food_amt(self):
        pass

    def transmit_food_freq(self):
        pass


class ThreadedClient:

    def __init__(self, root: tk.Tk, tk_vars: dict, piio: PiIo):
        self.root = root
        self.tk_vars = tk_vars
        self.feed_level_queue = Queue()
        self.gui = GuiPart(root=self.root, feed_level_q=self.feed_level_queue, tk_vars=self.tk_vars)
