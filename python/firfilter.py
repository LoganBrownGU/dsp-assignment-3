import numpy as np



class RingBuffer:
    def __init__(self, size):
        self.buff = np.zeros(size)
        self.start = 0

    def append(self, x):
        self.buff[self.start] = x
        self.start += 1
        if self.start == len(self.buff):
            self.start = 0

    def __getitem__(self, i) -> int:
        index = self.start + i
        if index >= len(self.buff):
            index -= len(self.buff)

        return self.buff[index]

    def __str__(self) -> str:
        output = "["
        for i in range(len(self.buff)):
            output += str(self.get(i)) + " "
        return output[:-1] + "]"


class FIRFilter:
    def __init__(self, coefficients):
        self.coefficients = coefficients
        self.n_taps = len(coefficients)
        self.buff = RingBuffer(self.n_taps)

    def filter(self, v):
        outv = 0

        self.buff.append(v)

        for i in range(len(self.coefficients)):
            outv += self.buff[i] * self.coefficients[i]        

        return outv
    
    def filterAdaptive(self, x_n, d_n, mu):
        # do the filtering
        y_n = 0
        self.buff.append(x_n)
        for i in range(len(self.coefficients)):
            y_n += self.buff[i] * self.coefficients[i]        

        # do the adapting
        e_n = d_n - y_n
        for i in range(len(self.coefficients)):
            self.coefficients[i] += mu * e_n * self.buff[i]

        return e_n
