import uart
from firfilter import FIRFilter 
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
from pyfirmata2 import Arduino
from threading import Timer


def fir_coeff_hp(fs, fc):
    n_taps = int(500)                # want to be able to sample down to 0.5 Hz, then double to account for transition window
    n_taps += 1 if n_taps % 2 == 0 else 0  # ensure no. taps is odd for symmetry

    # n = np.arange(-n_taps / 2, n_taps / 2)
    # n[int(n_taps / 2)] = 1

    # omc = 2 * np.pi * fc / fs

    # coeff = np.sin(omc * n) / (np.pi * n)
    # coeff /= np.max(coeff)                      # normalise
    # coeff[int(n_taps / 2)] = coeff[int(n_taps / 2) - 1]
    return signal.firwin(numtaps=n_taps, cutoff=fc, fs=fs, pass_zero="highpass") * np.kaiser(n_taps, 16.8)

def fir_coeff_bp(fs, f1, f2):
    n_taps = int(500)                # want to be able to sample down to 0.5 Hz, then double to account for transition window
    n_taps += 1 if n_taps % 2 == 0 else 0  # ensure no. taps is odd for symmetry
    return signal.firwin(numtaps=n_taps, cutoff=[f1,f2], fs=fs, pass_zero="bandpass") * np.kaiser(n_taps, 16.8)

class Transmitter():
    def __init__(self, baud, board):
        self.uart = uart.UART_Tx(baud, self.update)
        self.board = board
        self.output_pin = self.board.get_pin("d:4:o")
        self.output_pin.write(1)

    def update(self, q):
        self.output_pin.write(q)

    def start(self, data):
        print("sending...")
        self.uart.send_bulk(data, lambda : print("done"))


class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel):
        self.uart = uart.UART_Rx(baud, lambda: ())
        self.board = board
        self.board.samplingOn(1000 / sampling_rate)
        self.board.analog[analogue_channel].register_callback(self.update)
        self.board.analog[analogue_channel].enable_reporting()
        self.buf = uart.RingBuffer(int(sampling_rate * 0.5))
        self.filter1 = FIRFilter(fir_coeff_bp(sampling_rate, 15, 25))
        self.filter2 = FIRFilter(fir_coeff_bp(sampling_rate, 25, 35))

    def update(self, data):
        data = self.filter.filter(data)
        # self.buf.append(data)
        # max = -1
        # min = 1
        # for i in range(len(self.buf)):
        #     if self.buf[i] > max: max = self.buf[i]
        #     if self.buf[i] < min: min = self.buf[i]

        # diff = max - min
        # print(f"{"\b" * 100}{0 if (data - min) < 0.25 * diff else 1} : {max}", end="")
        thresh = 0.07
        self.uart.d = 0 if data > thresh else 1
        print(f"{"\b" * 100}{self.uart.d}", end="")

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 10
receiver = Receiver(baud, 1000, board, 1)
transmitter = Transmitter(baud, board)
# board.samplingOn(1)
# board.analog[1].register_callback(lambda x : print(x))
time.sleep(5)
transmitter.start(map(ord, "he\n"))