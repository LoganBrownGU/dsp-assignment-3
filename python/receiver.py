import uart
from firfilter import FIRFilter 
from filter import Filter
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib
from pyfirmata2 import Arduino
from threading import Timer
from graph import Graph

matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets

samples = [[], []]


class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f1, f2):
        self.__uart = uart.UART_Rx(baud, self.end)
        self.__board = board
        self.__board.samplingOn(1000 / sampling_rate)
        self.__board.analog[analogue_channel].register_callback(self.update)
        self.__board.analog[analogue_channel].enable_reporting()
        self.__buf1 = uart.RingBuffer(int(sampling_rate/f1))
        self.__buf2 = uart.RingBuffer(int(sampling_rate/f2))
        self.__filter1 = Filter(sampling_rate, f1)
        self.__filter2 = Filter(sampling_rate, f2)

    def update(self, data):
        a1 = self.__filter1.filter(data)
        a2 = self.__filter2.filter(data)
        self.__buf1.append(abs(a1))
        self.__buf2.append(abs(a2))

        a1 = np.max(self.__buf1)
        a2 = np.max(self.__buf2)

        samples[0].append(a1)
        samples[1].append(a2)

        thresh = 0.02
        self.__uart.d = 0 if a2 < thresh else 1

    def end(self):
        print(chr(self.__uart.get_buf()), end="", flush=True)

# PORT = Arduino.AUTODETECT
# board = Arduino(PORT,debug=True)

# baud = 10
# f1 = 20
# f2 = 40
# receiver = Receiver(baud, 500, board, 1, f1, f2)
# time.sleep(1)

app = QtWidgets.QApplication([])
w = Graph()
app.exec()