import numpy as np
import matplotlib.pyplot as plt
from receiver import Receiver
from transmitter import Transmitter
import config
from pyfirmata2 import Arduino
import time
import uart

sampling_rate = 500
baud, f = config.read_config()
PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)
channel = 1

receiver = Receiver(baud, sampling_rate, board, channel, f, False)
transmitter = Transmitter(baud, board, f)

def callback():
    callback_data, uart_data = receiver.get_graphing_data()
    plt.plot([x for x in callback_data])
    plt.figure()
    plt.plot([x for x in uart_data])
    plt.show()

x = []
start = time.time_ns()
x.append(time.time_ns() - start)
print(time.time_ns() - start)

message = "w"
time.sleep(1)
transmitter.start(map(ord, message), callback=callback)