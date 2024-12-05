import uart
import numpy as np
import matplotlib.pyplot as plt
import time

from pyfirmata2 import Arduino
from threading import Timer

class Transmitter():
    def __init__(self, baud, board, f1, f2):
        self.uart = uart.UART_Tx(baud, None)
        self.board = board
        self.output_pin = self.board.get_pin("d:4:o")
        self.output_pin.write(1)

        self.state = False
        self.lo_timer = Timer(0.5/f2, self.lo)
        self.lo_timer.start()

        self.f1 = f1
        self.f2 = f2

    def lo(self):
        self.lo_timer = Timer(0.5 / (self.f2 if self.uart.q == 1 else self.f1), self.lo)
        self.lo_timer.start()

        self.state = not self.state
        self.output_pin.write(self.state)

    def start(self, data):
        self.uart.send_bulk(data, self.end)

    def end(self):
        time.sleep(1)
        print("done")
        self.lo_timer.cancel()
        self.board.exit()

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

transmitter = Transmitter(10, board, 20, 40) 
string = "" 
with open("assets/to_send.txt") as f: 
    string = f.read()
print("".join([f"{x:08b}" for x in map(ord, string)]))
transmitter.start(map(ord, string))