import numpy as np
from threading import Timer

class RingBuffer:
    def __init__(self, size):
        self.buf = np.zeros(size)
        self.start = 0

    def append(self, x):
        self.buf[self.start] = x
        self.start += 1
        if self.start == len(self.buf):
            self.start = 0

    def __getitem__(self, i) -> int:
        index = self.start + i
        if index >= len(self.buf):
            index -= len(self.buf)

        return self.buf[index]

    def __str__(self) -> str:
        output = "["
        for i in range(len(self.buf)):
            output += str(self.get(i)) + " "
        return output[:-1] + "]"
    
    def __sizeof__(self) -> int:
        return len(self.buf)


class ShiftRegister:
    def __init__(self, size):
        self.buf = RingBuffer(size)
        self.d = 0

    def clock(self):
        self.buf.append(self.d)

    def clr(self):
        self.buf = RingBuffer(len(self.buf))


class UART:
    def __init__(self, baud_rate):
        self._baud_rate = baud_rate
        self._buf = ShiftRegister(8)


class UART_Rx(UART):
    def __init__(self, baud_rate, available_callback):
        UART.__init__(self, baud_rate)

        self.__clk_divisor = 8
        self.__available_callback = available_callback
        self.__last_level = 10
        self.__clk_period = 1 / (self.__clk_divisor * self._baud_rate)
        self.__low_for = 0
        
        # Flags 
        self.__receiving = False

        # Timers
        self.__clk = Timer(self.__clk_period, self.clk_callback)
        self.__clk.start()

        # Rx data line, accessible outside the receiver
        self.d = 0

    # Returns True if start bit detected
    def check_start(self):
        if self.d == 1:             # If high, then we are not receiving this bit time, and 
            self.__low_for = 0      # we can consider it a spurious pulse

        self.__low_for += 1
        if self.__low_for == self.__clk_divisor:
            self.__low_for = 0
            return True
        return False

    def clk_callback(self):
        if not self.__receiving:
            pass

rx = UART_Rx(9600, print)



# data = []
# buf = char_to_buf(33)
# tstep = 0.1
# tx = UART_Tx(1, tstep)
# rx = UART_Rx(tx.clock_freq, tx.time_step)
# for i in range(0, int(15 / tstep)):
#     if (i == 10):
#         tx.start(buf)

#     clock.append(rx.clock())
#     d = tx.send()
#     data.append(d)
#     d = rx.recv(d)

# print(rx.buf)
# print(buf)

# import matplotlib.pyplot as plt
# plt.plot(clock)
# plt.plot(data)

# plt.show()