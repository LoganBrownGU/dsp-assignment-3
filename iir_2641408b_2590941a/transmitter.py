import uart
import config
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


    def __init__(self, baud, board, f, save_data):
        self.__uart = uart.UART_Tx(baud, None)
        self.__board = board
        self.__output_pin = self.__board.get_pin("d:4:o")
        self.__output_pin.write(1)

        self.__lo = self.LocalOscillator(f)

        self.__lo_timer = None
        self.__lo_update_interval = 0.001
        self.__update()

    def __update(self):
        self.__lo_timer = Timer(self.__lo_update_interval, self.__update)
        self.__lo_timer.start()

        self.__output_pin.write(self.__lo.state() if self.__uart.q else 0)

    def start(self, data, callback=None):
        print("Sending...")
        self.__uart.send_bulk(data, self.end_sending if callback == None else callback)


    def end_sending(self):
        print("Done")
    
    def teardown(self):
        self.__lo_timer.cancel()
        self.__board.exit()

    def prompt(self):
        message = input("Enter message: ") + "\n"
        if message == "q\n":
            self.teardown()
        else:
            self.start(map(ord, message))
            self.prompt()

if __name__ == "__main__":
    PORT = Arduino.AUTODETECT
    board = Arduino(PORT,debug=True)

    baud, f1 = config.read_config()
    transmitter = Transmitter(baud, board, f1, False) 

    transmitter.prompt()