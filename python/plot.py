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

receiver = Receiver(baud, sampling_rate, board, channel, f, False, True)
transmitter = Transmitter(baud, board, f)

def callback():
    callback_data, uart_data, filtered_data, input_data = receiver.get_graphing_data()
    receiver.teardown()
    transmitter.teardown()

    plt.plot(callback_data)
    plt.plot([0, len(callback_data) - 1], [10**6, 10**6], "r--")

    plt.figure()
    plt.plot(uart_data)

    plt.figure()
    plt.plot(input_data)

    plt.figure()
    plt.plot(filtered_data)

    plt.figure()
    plt.plot(uart_data)
    
    
    plt.show()

x = []
start = time.time_ns()
x.append(time.time_ns() - start)
print(time.time_ns() - start)

message = "S"
time.sleep(1)
transmitter.start(map(ord, message), callback=callback)