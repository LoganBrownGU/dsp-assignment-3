from transmitter import Transmitter
from receiver import Receiver
from random import randint
import config
from pyfirmata2 import Arduino
import time

message_length = 128
message = [randint(0, 255) for _ in range(message_length)]
recv_message = []

sampling_rate = 1000
baud, f = config.read_config()
PORT = Arduino.AUTODETECT
board = Arduino(PORT,debug=True)
channel = 1

def rx_callback():
    global recv_message
    recv_message.append(receiver.get_uart_buf())

def tx_callback():
    correct = 0
    print([f"{i:08b}" for i in message])
    print([f"{i:08b}" for i in recv_message])
    for t, r in zip(message, recv_message): 
        t_b = f"{t:08b}"
        r_b = f"{r:08b}"
        for ti, ri in zip(t_b, r_b):
            if ti == ri: correct += 1

    print(time.time() - start)
    print(message_length * 8 - correct)
    print(correct / (message_length * 8))

receiver = Receiver(baud, sampling_rate, board, channel, f, False, True, available_callback=rx_callback)
transmitter = Transmitter(baud, board, f, True)

time.sleep(2)
start = time.time()
transmitter.start(message, tx_callback)
