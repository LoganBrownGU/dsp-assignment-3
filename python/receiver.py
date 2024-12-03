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
    n_taps = int(0.5 * fs)
    n_taps += 1 if n_taps % 2 == 0 else 0  # ensure no. taps is odd for symmetry
    return signal.firwin(numtaps=n_taps, cutoff=[f1,f2], fs=fs, pass_zero="bandpass") * np.kaiser(n_taps, 16.8)

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
        bin_str = "".join([f"{x:08b}" for x in out_bytes])
        chr_str = "".join([f"{chr(x)}" for x in out_bytes])
        print(f"{bin_str}\n{"|------|" * len(out_bytes)}\n{chr_str}")

a1s = []
a2s = []
out_bytes = []

def foo():
    out_bytes.append(receiver.uart.get_buf())

class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f1, f2):
        self.uart = uart.UART_Rx(baud, foo)
        # self.uart = uart.UART_Rx(baud, lambda: print(chr(self.uart.get_buf()), end="", flush=True))
        self.board = board
        self.board.samplingOn(1000 / sampling_rate)
        self.board.analog[analogue_channel].register_callback(self.update)
        self.board.analog[analogue_channel].enable_reporting()
        self.buf1 = uart.RingBuffer(int(sampling_rate/f1))
        self.buf2 = uart.RingBuffer(int(sampling_rate/f2))
        self.filter1 = FIRFilter(fir_coeff_bp(sampling_rate, f1 - 5, f1 + 5))
        self.filter2 = FIRFilter(fir_coeff_bp(sampling_rate, f2 - 5, f2 + 5))

    def update(self, data):

        self.buf1.append(abs(self.filter1.filter(data)))
        self.buf2.append(abs(self.filter2.filter(data)))
        
        # a1 = self.filter1.filter(data)
        # a2 = self.filter2.filter(data)
        a1 = np.max(self.buf1)
        a2 = np.max(self.buf2)
        a1s.append(a1)
        a2s.append(a2)

        # print(f"{"\b" * 100}{a1}\t{a2}", end="", flush=True)
        thresh = 0.005
        self.uart.d = 0 if a2 < thresh else 1
        # print(f"{"\b" * 100}{self.uart.d}", end="")

PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)

baud = 5
f1 = 10
f2 = 20
receiver = Receiver(baud, 500, board, 1, f1, f2)
transmitter = Transmitter(baud, board, f1, f2)
# board.samplingOn(1)
# board.analog[1].register_callback(lambda x : print(x))
time.sleep(1)
string = "hello\n"
print("".join([f"{x:08b}" for x in map(ord, string)]))
transmitter.start(map(ord, string))

plt.plot(a1s)
plt.plot(a2s)
plt.show()