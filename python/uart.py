import numpy as np
from threading import Timer
import time

rx_output = []
rx_clk = []

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
            output += str(self[i]) + " "
        return output[:-1] + "]"
    
    def __len__(self) -> int:
        return len(self.buf)


class ShiftRegister:
    def __init__(self, size):
        self.buf = RingBuffer(size)
        self.d = 0
        self.q = 0

    def __len__(self) -> int:
        return len(self.buf)

    def __str__(self) -> str:
        return str(self.buf)

    def clock(self):
        self.buf.append(self.d)
        self.q = self.buf[0]

    def clr(self):
        self.buf = RingBuffer(len(self.buf))

    def get_data(self) -> chr:
        val = 0
        print(self.buf)
        for i in range(len(self.buf)):
            val += int(2**i * self.buf[i])

        return chr(val)


class UART:
    def __init__(self, baud_rate):
        self._baud_rate = baud_rate
        self._buf = ShiftRegister(8)
        self._clocked_bits = 0


class UART_Rx(UART):
    def __init__(self, baud_rate, available_callback):
        UART.__init__(self, baud_rate)

        self.__clk_divisor = 8
        self.__periods = 0
        self.__available_callback = available_callback
        self.__clk_period = 1 / (self.__clk_divisor * self._baud_rate)
        print(self.__clk_period)
        self.__low_for = 0
        self.__high_for = 0
        
        # Flags 
        self.__receiving = False

        # Timers
        self.__clk = Timer(self.__clk_period, self.__clk_callback)
        self.__clk.start()

        # Rx data line, accessible outside the receiver
        self.d = 1

    # Returns True if start bit detected
    # Should only be called ONCE per clock cycle
    def __check_start(self):
        if self.d == 1:             # If high, then we are not receiving this bit time, and 
            self.__low_for = 0      # we can consider it a spurious pulse

        self.__low_for += 1
        if self.__low_for == self.__clk_divisor:
            self.__low_for = 0
            return True
        return False

    def __clk_restart(self):
        self.__clk = Timer(self.__clk_period, self.__clk_callback)
        self.__clk.start()

    def __clk_callback(self):
        # Can assume that callback will take less time than the clock period
        # Restart timer immediately so that clock period doesn't include processing time
        self.__clk_restart()
        global rx_output
        global rx_clk
        rx_output.append(self.d)
        rx_clk.append(0)

        if not self.__receiving:
            self.__receiving = self.__check_start()
            return

        # If reaching this point, then must be receiving
        self.__periods  += 1
        self.__low_for  += 1 if self.d == 0 else 0    
        self.__high_for += 1 if self.d == 1 else 0   

        if self.__periods == self.__clk_divisor:
            self._buf.d = 1 if self.__high_for > self.__low_for else 0
            self._buf.clock()
            self.__periods = 0 

            print(f"{self.__high_for} {self.__low_for}")
            rx_clk.pop()
            rx_clk.append(1)

            self.__high_for = 0
            self.__low_for = 0

            self._clocked_bits += 1 

        if self._clocked_bits == len(self._buf):
            self.__available_callback()
            self._clocked_bits = 0
            self.__receiving = False

    def get_buf(self):
        return self._buf.get_data()
    
    def stop(self):
        self.__clk.cancel() 

        
class UART_Tx(UART):
    def __init__(self, baud_rate):
        UART.__init__(self, baud_rate)
        self.__clk = Timer(1 / baud_rate, self.__send_data)
        
        # Tx data line
        self.q = 1

        # Flags
        self.sending = False
    
    
    def __send_data(self):
        self.q = self._buf.q
        self._buf.clock()
        clocked_bits = self._clocked_bits
        self._clocked_bits += 1

        if clocked_bits != len(self._buf):
            self.__clk = Timer(1 / self._baud_rate, self.__send_data)
            self.__clk.start()
        else:
            self.q = 1
            self.sending = False
            self.__clk = Timer(1 / self._baud_rate, self.__send_data)
            self._clocked_bits = 0

    def load_data(self, data: chr):
        val = ord(data)
        for i in range(len(self._buf)):
            self._buf.d = val // 2**(7-i)
            if val // 2**(7-i) != 0: val -= 2 ** (7-i)
            self._buf.clock()
        self._buf.d = 0
        # print(self._buf)

    def send_frame(self):
        self.q = 0
        self.sending = True
        self.__clk.start()
        print(f"tx: {self._buf}")

rx = UART_Rx(9.6, (lambda : print(f":{rx.get_buf()}:")))
tx = UART_Tx(4.8)

idx = 0
data = "aa"
# data = "Hello World"
time.sleep(0.5)
while idx < len(data):
    rx.d = tx.q
    # print(tx.q, end="")
    if not tx.sending:
        tx.load_data(data[idx])
        tx.send_frame()
        idx += 1

while tx.sending: x = 0
rx.stop()


import matplotlib.pyplot as plt
plt.plot(rx_output)
plt.plot(rx_clk)
plt.ylim(-0.1, 1.1)
plt.show()

# import time
# data = []
# clock = [0]
# c = 0
# def clk():
#     global c
#     c = 1 if c == 0 else 0
#     Timer(1/96, clk).start()

# def foo():
#     global c
#     data.append(tx.q)
#     clock.append(c)
#     c = 0
#     if len(data) == 1000:
#         return

#     t = Timer(0.0001, foo)
#     t.start()

# t = Timer(0.0001, foo)
# tx.load_data('a')
# tx.send_frame()
# t.start()
# clk()

# time.sleep(2)
# plt.plot(data)
# plt.plot(clock)
# plt.show()


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