import numpy as np
import matplotlib.pyplot as plt
from receiver import Receiver
from transmitter import Transmitter
import config
from pyfirmata2 import Arduino
import time
import uart

sampling_rate = 1000
baud, f = config.read_config()
PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)
channel = 1

receiver = Receiver(baud, sampling_rate, board, channel, f, False, True)
transmitter = Transmitter(baud, board, f, True)

def callback():
    receiver.teardown()
    transmitter.teardown()
    callback_data, uart_data, filtered_data, input_data = receiver.get_graphing_data()
    
    backsamples = 1500
    np.savetxt("assets/callback.dat", callback_data[-backsamples:])
    np.savetxt("assets/uart.dat", uart_data[-backsamples:])
    np.savetxt("assets/filtered.dat", filtered_data[-backsamples:])
    np.savetxt("assets/input.dat", input_data[-backsamples:])

x = []
start = time.time_ns()
x.append(time.time_ns() - start)
print(time.time_ns() - start)

message = "S"
time.sleep(1)
transmitter.start(map(ord, message), callback=callback)