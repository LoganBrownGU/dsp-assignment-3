import uart
from firfilter import FIRFilter 
from filter import Filter
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib
from pyfirmata2 import Arduino
from threading import Condition, Timer
from graph import Graph

matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets

samples = [[], []]

class ThreadSafeQueue():
    def __init__(self):
        self.__buf = []
        self.__cv = Condition()

    def append(self, x):
        self.__cv.acquire()
        self.__buf.append(x)
        self.__cv.release()
        
    def pop(self):
        self.__cv.acquire()
        x = self.__buf.pop(0) if len(self.__buf) > 0 else None
        self.__cv.release()
        return x


class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f1, f2):
        self.__uart = uart.UART_Rx(baud, self.end)
        self.__board = board
        self.__board.samplingOn(1000 / sampling_rate)
        self.__board.analog[analogue_channel].register_callback(self.__poll)
        self.__board.analog[analogue_channel].enable_reporting()
        self.__temp_buf = ThreadSafeQueue()
        self.__buf1 = uart.RingBuffer(int(sampling_rate/f1))
        self.__buf2 = uart.RingBuffer(int(sampling_rate/f2))
        self.__filter1 = Filter(sampling_rate, f1)
        self.__filter2 = Filter(sampling_rate, f2)

        self.__graph = Graph("Filtered and averaged", 2, 2000)

        Timer(0.01, self.__update).start()

    def __update(self):
        Timer(0.01, self.__update).start()

        data = self.__temp_buf.pop()
        while (data != None):
            a1 = self.__filter1.filter(data)
            a2 = self.__filter2.filter(data)
            self.__buf1.append(abs(a1))
            self.__buf2.append(abs(a2))

            a1 = np.max(self.__buf1)
            a2 = np.max(self.__buf2)

            self.__graph.add_sample(a1, 0)
            self.__graph.add_sample(a2, 1)

            thresh = 0.02
            self.__uart.d = 0 if a2 < thresh else 1

            data = self.__temp_buf.pop()
    
    def __poll(self, data):
        self.__temp_buf.append(data)

    def end(self):
        print(chr(self.__uart.get_buf()), end="", flush=True)

app = QtWidgets.QApplication([])

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 10
f1 = 20
f2 = 40
receiver = Receiver(baud, 500, board, 1, f1, f2)
time.sleep(1)

app.exec()