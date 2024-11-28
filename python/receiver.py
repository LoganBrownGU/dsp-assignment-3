import uart
import numpy as np
import matplotlib.pyplot as plt
from pyfirmata2 import Arduino
from threading import Timer

class Transmitter():
    def __init__(self, baud, board):
        self.uart = uart.UART_Tx(baud, self.update)
        self.board = board
        self.output_pin = self.board.get_pin("d:4:o")

    def update(self, q):
        self.output_pin.write(q)

    def start(self, data):
        print("sending...")
        self.uart.send_bulk(data, lambda : print("done"))


class Receiver():
    def __init__(self, baud, sampling_rate, board):
        self.uart = uart.UART_Rx(baud, lambda : print(f"{chr(self.uart.get_buf)}"))
        self.board = board
        self.board.samplingOn(1000 / sampling_rate)
        self.board.analog[1].register_callback(self.update)
        self.buf = uart.RingBuffer(int(sampling_rate * 0.5))

    def update(self, data):
        self.buf.append(data)
        max = -1
        min = 1
        for i in range(len(self.buf)):
            if self.buf[i] > max: max = self.buf[i]
            if self.buf[i] < min: min = self.buf[i]

        diff = max - min
        print(0 if (data - min) < 0.25 * diff else 1)
        self.uart.d = 0 if (data - min) < 0.25 * diff else 1

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 10 
receiver = Receiver(baud, 1000, board)
transmitter = Transmitter(baud, board)
transmitter.start(map(ord, "hello there\n"))