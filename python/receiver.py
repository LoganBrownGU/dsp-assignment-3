import uart
import numpy as np
import matplotlib.pyplot as plt
from pyfirmata2 import Arduino
from threading import Timer

class Receiver():
    def __init__(self, clock_freq, time_step, data, board):
        self.uart = uart.UART_Tx(clock_freq, time_step)
        self.uart.start(data.pop(0))
        self.data = data
        self.output_pin = board.get_pin("d:4:o")
        self.timer = None
        self.time_step = time_step

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)