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

        self.uart = uart.UART_Tx(baud, lambda q: print(int(q), end="", flush=True))
        self.board = board
        self.output_pin = self.board.get_pin("d:4:o")
        self.output_pin.write(1)

        self.__lo1 = self.LocalOscillator(f1)
        self.__lo2 = self.LocalOscillator(f2)

        self.f1 = f1
        self.f2 = f2

        self.update()

    def update(self):
        Timer(0.5 / (self.f2), self.update).start()

        self.output_pin.write(self.__lo2.state() if self.uart.q else self.__lo1.state())

    def start(self, data):
        self.uart.send_bulk(data, self.end)

    def end(self):
        print("\ndone")
        self.lo_timer.cancel()
        self.board.exit()

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

transmitter = Transmitter(10, board, 20, 40) 
string = input("Enter message: ") + "\n"
transmitter.start(map(ord, string))