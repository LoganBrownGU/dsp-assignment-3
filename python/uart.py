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
    
    def __len__(self) -> int:
        return len(self.buf)


class ShiftRegister:
    def __init__(self, size):
        self.buf = RingBuffer(size)
        self.d = 0

    def __len__(self) -> int:
        return len(self.buf)

    def clock(self):
        self.buf.append(self.d)

    def clr(self):
        self.buf = RingBuffer(len(self.buf))

    def get_data(self) -> chr:
        val = 0
        for i in range(len(self.buf)):
            val += int(2**i * self.buf[i])

        return chr(val)


class UART:
    def __init__(self, baud_rate):
        self._baud_rate = baud_rate
        self._buf = ShiftRegister(8)


class UART_Rx(UART):
    def __init__(self, baud_rate, available_callback):
        UART.__init__(self, baud_rate)

        self.__clk_divisor = 8
        self.__periods = 0
        self.__clocked_bits = 0
        self.__available_callback = available_callback
        self.__clk_period = 1 / (self.__clk_divisor * self._baud_rate)
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
            self.__clocked_bits += 1 

        if self.__clocked_bits == len(self._buf):
            self.__available_callback()
            self.__clocked_bits = 0
            self.__receiving = False

    def get_buf(self):
        return self._buf.get_data()

        

rx = UART_Rx(9600, (lambda : print(rx.get_buf())))


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