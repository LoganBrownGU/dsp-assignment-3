import numpy as np

class UART:
    def clock(self):
        return 1 if self.t % (1 / self.clock_freq) < 0.5 else 0
    
    def clock_edge(self):
        edge = self.prev_clk and (not self.clock())
        self.prev_clk = self.clock()
        return edge
    
    def __init__(self, clock_freq, time_step):
        self.clock_freq = clock_freq
        self.time_step = time_step
        self.t = 0
        self.char_start = False
        self.char_stop = True
        self.prev = 1
        self.prev_clk = 0
        self.buf_idx = 0
        self.bits_per_char = 8
        self.buf = np.zeros(self.bits_per_char)     


class UART_Rx(UART):
    
    def check_start(self, signal, prev):
        if not self.char_stop or self.char_start:
            return False

        return prev == 1 and signal == 0

    def check_stop(self, signal, prev):
        if not self.char_start or self.char_stop:
            return False

        return prev == 1 and signal == 1 and self.buf_idx == (self.bits_per_char - 1)


    # return None if byte not read, byte if read
    def recv(self, signal):
        self.t += self.time_step
        if not self.clock_edge():
            return None

        prev = self.prev
        self.prev = signal

        if self.check_start(signal, prev):
            self.char_start = True
            return None
        if not self.char_start:
            return None
        
        if self.check_stop(signal, prev):
            self.char_stop = True
            self.char_start = False

            return self.buf_idx 

        print(f"{self.t}: {signal} {self.buf_idx}")
        if (self.buf_idx < self.bits_per_char):
            self.buf[self.buf_idx] = signal
        self.buf_idx += 1

    def __init__(self, clock_freq, time_step):
        UART.__init__(self, clock_freq, time_step)


class UART_Tx(UART):
    # def clock(self):
        # return 1 if (self.t + 0.25 * (1 / self.clock_freq)) % (1 / self.clock_freq) < 0.5 else 0
    
    def start(self, buf):
        if not self.char_stop or self.char_start:
            raise RuntimeError("Attempted to start send while sending")

        assert len(buf) == self.bits_per_char
        self.buf = buf
        self.buf_idx = 0
        self.char_start = True
        self.char_stop = False
        self.stop_bits = 0
        self.finished = False

    def send(self):
        self.t += self.time_step

        if self.char_stop and self.clock_edge():
            self.stop_bits += 1
            if self.stop_bits == 2:
                self.finished = True

        if self.char_stop:
            return 1 

        if self.char_start and self.clock_edge():
            self.char_start = False
            return 0

        if self.char_start:
            return 0
        
        # If not start and not stop then must be sending a char
        if (self.buf_idx == self.bits_per_char):
            self.char_stop = True
            return 1
        
        v = self.buf[self.buf_idx]
        if self.clock_edge():
            self.buf_idx += 1

        return v
        


    def __init__(self, clock_freq, time_step):
        UART.__init__(self, clock_freq, time_step)
        self.stop_bits = 0
        self.finished = False
        

def char_to_buf(char):
    buf = np.zeros(8)

    for i in range(len(buf)):
        pv = 2 ** (7-i)
        buf[i] = int(char // pv != 1)
        if char // pv == 1:
            char -= pv

    print(buf)
    return buf


clock = []
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