import uart
from firfilter import FIRFilter 
from filter import Filter
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from pyfirmata2 import Arduino
from threading import Timer

class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f1, f2):
        self.uart = uart.UART_Rx(baud, self.end)
        self.board = board
        self.board.samplingOn(1000 / sampling_rate)
        self.board.analog[analogue_channel].register_callback(self.update)
        self.board.analog[analogue_channel].enable_reporting()
        self.buf1 = uart.RingBuffer(int(sampling_rate/f1))
        self.buf2 = uart.RingBuffer(int(sampling_rate/f2))
        self.filter1 = Filter(sampling_rate, f1)
        self.filter2 = Filter(sampling_rate, f2)

    def update(self, data):

        a1 = self.filter1.filter(data)
        a2 = self.filter2.filter(data)
        self.buf1.append(abs(a1))
        self.buf2.append(abs(a2))

        a1 = np.max(self.buf1)
        a2 = np.max(self.buf2)

        thresh = 0.03
        self.uart.d = 0 if a2 < thresh else 1

        # print(f"{"\b" * 100}: {a1}", end="")

    def end(self):
        print(chr(receiver.uart.get_buf()), end="", flush=True)

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 10
f1 = 20
f2 = 40
receiver = Receiver(baud, 500, board, 1, f1, f2)
time.sleep(1)