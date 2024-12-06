import uart
import numpy as np
import matplotlib.pyplot as plt
import time

from pyfirmata2 import Arduino
from threading import Timer

class Transmitter():
    class LocalOscillator():
        def __init__(self, f):
            self.__time_offset = time.time_ns()
            self.__period_ns = 10**9 / f

        def state(self):
            t = time.time_ns() - self.__time_offset
            return (t % self.__period_ns) < (self.__period_ns / 2)


    def __init__(self, baud, board, f1, f2):
        assert f1 < f2

        self.__uart = uart.UART_Tx(baud, lambda q: print(int(q), end="", flush=True))
        self.__board = board
        self.__output_pin = self.__board.get_pin("d:4:o")
        self.__output_pin.write(1)

        self.__lo1 = self.LocalOscillator(f1)
        self.__lo2 = self.LocalOscillator(f2)

        self.__f1 = f1
        self.__f2 = f2

        self.__lo_timer = None
        self.update()

    def update(self):
        self.__lo_timer = Timer(0.5 / (self.__f2), self.update)
        self.__lo_timer.start()

        self.__output_pin.write(self.__lo2.state() if self.__uart.q else self.__lo1.state())

    def start(self, data):
        self.__uart.send_bulk(data, self.end)

    def end(self):
        print("\ndone")
        self.__lo_timer.cancel()
        self.__board.exit()

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

transmitter = Transmitter(10, board, 20, 40) 
string = input("Enter message: ") + "\n"
transmitter.start(map(ord, string))