import numpy as np

class UART:
    def clock(self):
        return 1 if self.t % (1 / self.clock_freq) < 0.5 else 0
    
    def clock_edge(self):
        prev = (self.t - self.time_step) % (1 / self.clock_freq) < 0.5
        return prev and (not self.t % (1 / self.clock_freq) < 0.5)
    
    def __init__(self, clock_freq, time_step):
        self.clock_freq = clock_freq
        self.time_step = time_step
        self.t = 0
        self.char_start = False
        self.char_stop = True
        self.prev = 1
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
        if not self.clock_edge:
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

        if (self.buf_idx < self.bits_per_char):
            self.buf[self.buf_idx] = signal
        self.buf_idx += 1

    def __init__(self, clock_freq, time_step):
        UART.__init__(self, clock_freq, time_step)


class UART_Tx(UART):
    
    def start(self, buf):
        if not self.char_stop or self.char_start:
            raise RuntimeError("Attempted to start send while sending")

        assert len(buf) == self.bits_per_char
        self.buf = buf
        self.buf_idx = 0
        self.char_start = True
        self.char_stop = False

    def send(self):
        self.t += self.time_step

        if self.char_stop:
            return 1 

        if self.char_start:
            self.char_start = False
            return 0
        
        # If not start and not stop then must be sending a char
        if self.clock_edge():
            self.buf_idx += 1
        if (self.buf_idx == self.bits_per_char):
            self.char_stop = True
            return 1

        return self.buf[self.buf_idx]
        


    def __init__(self, clock_freq, time_step):
        UART.__init__(self, clock_freq, time_step)
        

def char_to_buf(char):
    buf = np.zeros(8)

    for i in range(len(buf)):
        pv = 2 ** (7-i)
        buf[i] = char // pv
        if char // pv == 1:
            char -= pv

    print(buf)
    return buf


clock = []
data = []
tx = UART_Tx(1, 0.1)
rx = UART_Rx(tx.clock_freq, tx.time_step)
for i in range(0, 150):
    if (i == 10):
        tx.start(char_to_buf(200))

    clock.append(tx.clock())
    d = tx.send()
    data.append(d)
    d = rx.recv(d)

print(rx.buf)

import matplotlib.pyplot as plt
plt.plot(clock)
plt.plot(data)

plt.show()