import uart
from filter import Filter
import config
import time
import numpy as np
from pyfirmata2 import Arduino
from threading import Condition, Timer, Thread
from graph import Graph

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
    def __init__(self, baud, sampling_rate, board, analogue_channel, f, enable_graphs, save_data):
        self.__uart = uart.UART_Rx(baud, self.end)
        self.__board = board
        self.__board.samplingOn(1000 / sampling_rate)
        self.__board.analog[analogue_channel].register_callback(self.__poll)
        self.__board.analog[analogue_channel].enable_reporting()
        self.__processing_queue = ThreadSafeQueue()
        self.__buf = uart.RingBuffer(int(2 * sampling_rate/f))
        self.__filter = Filter(sampling_rate, f)

        if enable_graphs: 
            self.__filtered_graph = Graph("Filtered", 1, 5 * f, ylim=[-0.2, 0.2])
            self.__averaged_graph = Graph("Filtered and averaged", 1, 2 * sampling_rate, ylim=[0, 0.2])
            self.__raw_graph = Graph("Raw data", 1, sampling_rate / 2)
        else:
            self.__filtered_graph = None
            self.__averaged_graph = None
            self.__raw_graph = None

        self.__save_data = save_data
        self.__callback_data = []
        self.__uart_input_data = []
        self.__filtered_data = []   
        self.__input_data = []   

        self.__update_timer = Timer(0.01, self.__update)
        self.__update_timer.start()

    def __update(self):
        self.__update_timer = Timer(0.01, self.__update)
        self.__update_timer.start()

        data = self.__processing_queue.pop()
        while (data != None):
            if self.__save_data: self.__input_data.append(data)

            if self.__raw_graph != None: self.__raw_graph.add_sample(data, 0)
            x = self.__filter.filter(data)
            self.__buf.append(abs(x))

            if self.__save_data: self.__filtered_data.append(x)
            if self.__filtered_graph != None: self.__filtered_graph.add_sample(x, 0)

            x = np.max(self.__buf)

            if self.__averaged_graph != None: self.__averaged_graph.add_sample(x, 0)
            if self.__save_data: self.__uart_input_data.append(x)

            thresh = 0.03
            self.__uart.d = 0 if x < thresh else 1

            data = self.__processing_queue.pop()
    
    def __poll(self, data):

        try:
            start_time = time.time_ns()
            self.__processing_queue.append(data)
            processing_time = time.time_ns() - start_time
            if self.__save_data: self.__callback_data.append(processing_time)
        except Exception as _:
            pass    # Occasionally a spurious name error is thrown  

    def end(self):
        print(chr(self.__uart.get_buf()), end="", flush=True)

    def teardown(self):
        if self.__averaged_graph != None: self.__averaged_graph.close()
        if self.__filtered_graph != None: self.__filtered_graph.close()
        if self.__raw_graph != None:      self.__raw_graph.close()

        self.__uart.stop()
        self.__board.exit()
        self.__update_timer.cancel()    

    def get_graphing_data(self):
        return self.__callback_data, self.__uart_input_data, self.__filtered_data, self.__input_data

if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Qt5Agg')
    from PyQt6 import QtWidgets

    app = QtWidgets.QApplication([])

    PORT = Arduino.AUTODETECT
    board = Arduino(PORT,debug=True)

    baud, f = config.read_config()
    receiver = Receiver(baud, 1000, board, 1, f, True, False)
    time.sleep(1)

    Thread(target = app.exec).start()

    input("")
    receiver.teardown()