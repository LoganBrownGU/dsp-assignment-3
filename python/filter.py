# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 09:23:31 2024

@author: Dell
"""

import numpy as np
import matplotlib.pyplot as plt

def SecondOrder ( fs, f1, f2 ):

    fc = ( f1 + f2 ) / 2
    w0 = np.pi * 2 * fc / fs
    r = 0.9
  
    a = [ 1, -2 * r * np.cos( w0 ), r ** 2 ]
    b = [ 1, -2 * np.cos( w0 ), 1 ]
    # b = [ 1, 1, 1 ]
      
    return b, a

class Filter():
   def __init__(self, fs, fc1, fc2):
        self.b, self.a = SecondOrder(fs, fc1, fc2)
        print(self.a)
        print(self.b)
       
       # normalise the coefficients
        self.b = [ b_i / self.a[0] for b_i in self.b ]
        self.a = [ a_i / self.a[0] for a_i in self.a ]
       
        self.buf1_in = 0
        self.buf2_in = 0
        self.buf1_out = 0
        self.buf2_out = 0

   def filter(self, sample):
       # apply direct form i filter
        input_acc  = sample - self.a[1] * self.buf1_in - self.a[2] * self.buf2_in
        output_acc = input_acc * self.b[0] + self.buf1_in * self.b[1] + self.b[2] * self.buf2_in
        # output_acc = input_acc

       # update buffers
        self.buf2_in = self.buf1_in
        self.buf1_in = input_acc
        self.buf2_out = self.buf1_out
        self.buf1_out = output_acc

        return output_acc


def test_filter():
    # test signal
    fs = 1000
    t = np.linspace(0, 1, fs)
    data = np.sin(5 * 2 * np.pi * t) + np.sin(50 * 2 * np.pi * t) + np.sin(100 * 2 * np.pi * t)
    out_data = []

    # apply the filter
    out_data = []
    filter = Filter(fs, 45, 55)
    for d in data:
        out_data.append(filter.filter(d))

    plt.plot(np.abs(np.fft.fft(data)) / len(data), label= 'Original FFT')
    plt.plot(np.abs(np.fft.fft(out_data) / len(out_data)), label= 'Filtered FFT')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("FFT of Original and Filtered Signals")
    plt.legend()
    plt.grid()
    plt.show()
    
# test_filter()