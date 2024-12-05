import numpy as np
from scipy.signal import butter
from scipy.signal import freqz
import scipy.signal as signal
import matplotlib.pyplot as plt

def bandpass( fs, f1 , f2):
   nyquist = fs / 2
   f1 = f1 / nyquist
   f2 = f2 / nyquist
 
   b, a = butter( 1, [f1, f2], btype = 'bandpass' )
 
   return b, a

def highpass(fs, fc):
   nyquist = fs / 2
   fc /= nyquist
 
   b, a = butter( 2, fc, btype = 'highpass' )
 
   return b, a

class IIRFilter():
    def __init__(self, fs, fc1 ):
       self.b, self.a = bandpass(fs, fc1 - 2, fc1 + 2)
       
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

       # update buffers
       self.buf2_in = self.buf1_in
       self.buf1_in = input_acc
       self.buf2_out = self.buf1_out
       self.buf1_out = output_acc

       return output_acc

class Filter():
    def __init__(self, fs, fc1):
        self.__iirs = [IIRFilter(fs, fc1) for i in range(3)]

    def filter(self, sample):
        for iir in self.__iirs:
           sample = iir.filter(sample)

        return sample

def test_filter():
    # test signal
    fs = 1000
    t = np.linspace(0, 1, fs)
    data = np.sin(5 * 2 * np.pi * t) + np.sin(50 * 2 * np.pi * t) + np.sin(70 * 2 * np.pi * t)
    out_data = []

    # apply the filter
    out_data = []
    filter = Filter(fs, 50)
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