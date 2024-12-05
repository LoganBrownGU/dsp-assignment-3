import uart
from firfilter import FIRFilter 
from filter import Filter
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
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
        chr_str = "".join([f"{chr(x)}" for x in out_bytes])
        print(f"{chr_str}")

out_bytes = []

def foo():
    out_bytes.append(receiver.uart.get_buf())
    print(chr(out_bytes[-1]), end="", flush=True)

class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f1, f2):
        self.uart = uart.UART_Rx(baud, foo)
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

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 10
f1 = 20
f2 = 40
transmitter = Transmitter(baud, board, f1, f2)
time.sleep(1)
receiver = Receiver(baud, 500, board, 1, f1, f2)
time.sleep(1)
string = "" 
with open("assets/to_send.txt") as f: 
    string = f.read()
print("".join([f"{x:08b}" for x in map(ord, string)]))
transmitter.start(map(ord, string))