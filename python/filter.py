import numpy as np
from scipy.signal import butter
from scipy.signal import freqz
import scipy.signal as signal
import matplotlib.pyplot as plt
import unittest

class IIRFilter():
    def __init__(self, fs, fc1 ):
       self.b, self.a = self.bandpass(fs, fc1-7, fc1+7)
       
       # normalise the coefficients
       self.b = [ b_i / self.a[0] for b_i in self.b ]
       self.a = [ a_i / self.a[0] for a_i in self.a ]
       
       self.buf1_in = 0
       self.buf2_in = 0
       self.buf1_out = 0
       self.buf2_out = 0

    def bandpass(self, fs, f1 , f2):
        nyquist = fs / 2
        f1 = min(nyquist, max(0.001, f1 / nyquist))
        f2 = min(nyquist, max(0.001, f2 / nyquist))
        
        b, a = butter(1, [f1, f2], btype = 'bandpass')
    
        return b, a

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
        self.__iirs = [IIRFilter(fs, fc1) for i in range(4)]

    def filter(self, sample):
        for iir in self.__iirs:
           sample = iir.filter(sample)

        return sample

def test_filter():
    # test signal
    fs = 1000
    data = np.abs(np.fft.ifft(np.ones(fs)))

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

class FilterTest(unittest.TestCase):

    def gen_test_signal(self, fs):
        return np.abs(np.fft.ifft(np.ones(fs)))

    tolerance_places = 2

    # TEST PASSBAND PERFORMANCE
    def passband_attenuation(self, f_pass):
        fs = 1000
        signal = self.gen_test_signal(fs)

        filter = Filter(fs, f_pass)
        out_signal = [filter.filter(x) for x in signal]
        self.assertAlmostEqual(np.abs(np.fft.fft(out_signal))[f_pass], np.abs(np.fft.fft(signal))[f_pass], places=self.tolerance_places)

    def test_passband_attenuation_1Hz(self):
        self.passband_attenuation(1)

    def test_passband_attenuation_10Hz(self):
        self.passband_attenuation(10)
    
    def test_passband_attenuation_100Hz(self):
        self.passband_attenuation(100)

    def test_passband_attenuation_200Hz(self):
        self.passband_attenuation(200)


    # TEST INDIVIDUAL IIR PASSBAND PERFORMANCE
    @unittest.skip("")
    def iir_passband_attenuation(self, f_pass):
        fs = 1000
        signal = self.gen_test_signal(fs)

        filter = Filter(fs, f_pass)
        out_signal = [filter.filter(x) for x in signal]
        filter = IIRFilter(fs, f_pass)
        out_signal = [filter.filter(x) for x in signal]
        self.assertAlmostEqual(np.abs(np.fft.fft(out_signal))[f_pass], np.abs(np.fft.fft(signal))[f_pass], places=self.tolerance_places)

    def test_iir_passband_attenuation_1Hz(self):
        self.iir_passband_attenuation(1)

    def test_iir_passband_attenuation_10Hz(self):
        self.iir_passband_attenuation(10)
    
    def test_iir_passband_attenuation_100Hz(self):
        self.iir_passband_attenuation(100)

    def test_iir_passband_attenuation_200Hz(self):
        self.iir_passband_attenuation(200)


    # TEST STOPBAND PERFORMANCE
    @unittest.skip("")
    def stopband_attenation(self, f_pass):
        fs = 1000
        signal = self.gen_test_signal(fs)

        filter = Filter(fs, f_pass)
        out_signal = [filter.filter(x) for x in signal]

        for i in range(f_pass + 5, fs // 2):
            self.assertAlmostEqual(np.abs(np.fft.fft(out_signal))[i], 0, places=self.tolerance_places)
        for i in range(0, f_pass - 5):
            self.assertAlmostEqual(np.abs(np.fft.fft(out_signal))[i], 0, places=self.tolerance_places)

    def test_stopband_attenuation_1Hz(self):
        self.stopband_attenation(1)

    def test_stopband_attenuation_10Hz(self):
        self.stopband_attenation(10)
    
    def test_stopband_attenuation_100Hz(self):
        self.stopband_attenation(100)

    def test_stopband_attenuation_200Hz(self):
        self.passband_attenuation(200)


if __name__ == "__main__":
    unittest.main()