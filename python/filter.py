# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 08:34:21 2024

@author: Dell
"""

import numpy as np
from scipy.signal import butter
from scipy.signal import freqz
import scipy.signal as signal
import matplotlib.pyplot as plt

def SecondOrder ( fs, f1, f2 ):

    fc = ( f1 + f2 ) / 2
    w0 = np.pi * 2 * fc / fs
    r = 0.9
   
    a = [ 1, -2 * r * np.cos( w0 ), r ** 2 ]
    b = [ 1, -2 * np.cos( w0 ), 1 ]
       
    return b, a


def Butter( fs, f1, f2 ):
    nyquist = fs / 2
    lowCutoff = f1 / nyquist
    highCutoff = f2 / nyquist
   
    b, a = butter( 1, [ lowCutoff, highCutoff ], btype = 'bandstop' )
   
    return b, a


def doFiltering( data ):
    buffer1 = [0, 0]
    buffer2 = [0, 0]
    inputacc = np.zeros( len( data ) )
    outputacc = np.zeros( len ( data ) )
   
    b, a = Butter( 1000, 45, 55 )
   
    for n in range( len( data ) ):
       
        # accumulator for the IIR part
        inputacc[n] =  data[n]
        inputacc[n] = inputacc[n] - ( a[1] * buffer1[0] )
        inputacc[n] = inputacc[n] - ( a[2] * buffer2[0] )
       
        # accumulator for the FIR part
        outputacc[n] = inputacc[n] + b[0]
        outputacc[n] = outputacc[n] + ( b[1] * buffer1[1] )
        outputacc[n] = outputacc[n] + ( b[2] * buffer2[1] )

        buffer1.pop(0)
        buffer2.pop(0)
        buffer1.append(inputacc[n])
        buffer2.append(outputacc[n])
       
    return outputacc

class Filter():
    def __init__(self, fs, fc1, fc2):
        self.b, self.a = SecondOrder(fs, fc1, fc2)
        print(self.a)
        print(self.b)
        self.buf1 = 0
        self.buf2 = 0

    def filter(self, sample):
        input_acc  = sample - self.a[0] * self.buf1 - self.a[1] * self.buf2 
        output_acc = input_acc * self.b[0] + self.buf1 * self.b[1] + self.b[2] * self.buf2

        self.buf2 = self.buf1
        self.buf1 = input_acc

        return output_acc

# print( butter( 4, [ 0.1, 0.2 ], btype = 'bandstop', output="sos" ))

t = np.linspace(0, 1, 1000)
data = np.sin(5 * 2 * np.pi * t) + np.sin(50 * 2 * np.pi * t) + np.sin(100 * 2 * np.pi * t)
out_data = []

filter = Filter(1000, 45, 55)
for d in data:
    out_data.append(filter.filter(d))

b, a = SecondOrder(1000, 45, 55)
w, h = signal.freqz(b, a)
plt.plot(w / np.pi / 2, np.abs(h))
# plt.plot(np.abs(np.fft.fft(data)))
# plt.plot(np.abs(np.fft.fft(out_data)))
plt.show()