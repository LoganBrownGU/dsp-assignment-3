import uart
import numpy as np
import matplotlib.pyplot as plt

from pyfirmata2 import Arduino
from threading import Timer

class Transmitter():

    def __init__(self, clock_freq, time_step, data, board):
        self.uart = uart.UART_Tx(clock_freq, time_step)
        self.uart.start(data.pop(0))
        self.data = data
        self.output_pin = board.get_pin("d:4:o")
        self.timer = None
        self.time_step = time_step
    

    def callback(self):
        self.timer = Timer(self.time_step, self.callback)
        self.timer.start()

        if self.uart.finished:
            self.uart.start(self.data.pop(0))
            
        v = self.uart.send()
        self.output_pin.write(v)

    def start(self):
        self.timer = Timer(self.time_step, self.callback)
        self.timer.start()

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

data = [[0, 1, 0, 1, 0, 1, 0, 1] for i in range(10)]

print(data)
tx = Transmitter(1, 0.001, data, board)
tx.start()
