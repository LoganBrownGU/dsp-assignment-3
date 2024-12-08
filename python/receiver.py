import uart
from filter import Filter
import config
import time
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import matplotlib
from pyfirmata2 import Arduino
from threading import Condition, Timer, Thread
from graph import Graph

matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets

samples = [[], []]

class ThreadSafeQueue():
    def __init__(self):
        self.__buf = []
        self.__cv = Condition()

    def append(self, x):
        self.__cv.acquire()
        self.__buf.append(x)
        self.__cv.release()
        
    def pop(self):
        self.__cv.acquire()
        x = self.__buf.pop(0) if len(self.__buf) > 0 else None
        self.__cv.release()
        return x


class Receiver():
    def __init__(self, baud, sampling_rate, board, analogue_channel, f):
        self.__uart = uart.UART_Rx(baud, self.end)
        self.__board = board
        self.__board.samplingOn(1000 / sampling_rate)
        self.__board.analog[analogue_channel].register_callback(self.__poll)
        self.__board.analog[analogue_channel].enable_reporting()
        self.__processing_queue = ThreadSafeQueue()
        self.__buf = uart.RingBuffer(int(2 * sampling_rate/f))
        self.__filter = Filter(sampling_rate, f)

        self.__filtered_graph = Graph("Filtered", 1, 5 * f, ylim=[-0.2, 0.2])
        self.__averaged_graph = Graph("Filtered and averaged", 1, 2 * sampling_rate, ylim=[0, 0.2])
        self.__raw_graph = Graph("Raw data", 1, sampling_rate / 2)

        self.__callback_graphing = uart.RingBuffer((sampling_rate / baud) * 10)     # save approx. one byte's worth
        self.__uart_input_graphing = uart.RingBuffer((sampling_rate / baud) * 10)     

        self.__update_timer = Timer(0.01, self.__update)
        self.__update_timer.start()

    def __update(self):
        self.__update_timer = Timer(0.01, self.__update)
        self.__update_timer.start()

        data = self.__processing_queue.pop()
        while (data != None):
            self.__raw_graph.add_sample(data, 0)
            x = self.__filter.filter(data)
            self.__buf.append(abs(x))
            self.__filtered_graph.add_sample(x, 0)

            x = np.max(self.__buf)

            self.__averaged_graph.add_sample(x, 0)

            thresh = 0.03
            self.__uart.d = 0 if x < thresh else 1

            data = self.__processing_queue.pop()
    
    def __poll(self, data):
        start_time = time.time_ns()
        self.__processing_queue.append(data)
        self.__callback_graphing.append(time.time_ns() - start_time)

    def end(self):
        print(chr(self.__uart.get_buf()), end="", flush=True)

    def teardown(self):
        self.__averaged_graph.close()
        self.__filtered_graph.close()
        self.__raw_graph.close()
        self.__uart.stop()
        self.__board.exit()
        self.__update_timer.cancel()    

    def get_graphing_data(self):
        return self.__callback_graphing, self.__uart_input_graphing

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    PORT = Arduino.AUTODETECT
    board = Arduino(PORT,debug=True)

    baud, f = config.read_config()
    receiver = Receiver(baud, 1000, board, 1, f)
    time.sleep(1)

    Thread(target = app.exec).start()

    input("")
    receiver.teardown()