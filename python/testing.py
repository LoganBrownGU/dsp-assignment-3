#!/usr/bin/python3
"""
Plots channel zero at 1kHz. Requires pyqtgraph.

Copyright (c) 2018-2021, Bernd Porr <mail@berndporr.me.uk>
see LICENSE file.

"""

import uart
from firfilter import FIRFilter
from filter import Filter

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as signal

from pyfirmata2 import Arduino
from threading import Timer

PORT = Arduino.AUTODETECT
# sampling rate: 1kHz
samplingRate = 1000

def fir_coeff_bp(fs, f1, f2):
    n_taps = int(500)                # want to be able to sample down to 0.5 Hz, then double to account for transition window
    n_taps += 1 if n_taps % 2 == 0 else 0  # ensure no. taps is odd for symmetry
    return signal.firwin(numtaps=n_taps, cutoff=[f1,f2], fs=fs, pass_zero="bandpass") * np.kaiser(n_taps, 16.8)

class QtPanningPlot:

    def __init__(self,layout,title):
        self.pw = pg.PlotWidget()
        layout.addWidget(self.pw)
        self.pw.setYRange(-1,1)
        self.pw.setXRange(0,500/samplingRate)
        self.plt = self.pw.plot()
        self.data = []
        # any additional initalisation code goes here (filters etc)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def update(self):
        self.data=self.data[-500:]
        if self.data:
            self.plt.setData(x=np.linspace(0,len(self.data)/samplingRate,len(self.data)),y=self.data)

    def addData(self,d):
        self.data.append(d)


class Blink():
    def __init__(self, board, seconds):
        # pin 13 which is connected to the internal LED
        self.digital_0 = board.get_pin('d:4:o')

        # flag that we want the timer to restart itself in the callback
        self.timer = None

        # delay
        self.DELAY = seconds

    # callback function which toggles the digital port and
    # restarts the timer
    def blinkCallback(self):
        # call itself again so that it runs periodically
        self.timer = Timer(self.DELAY,self.blinkCallback)

        # start the timer
        self.timer.start()
        
        # now let's toggle the LED
        v = self.digital_0.read()
        v = not v
        self.digital_0.write(v)

    # starts the blinking
    def start(self):
        # Kickstarting the perpetual timer by calling the
        # callback function once
        self.blinkCallback()

    # stops the blinking
    def stop(self):
        # Cancel the timer
        self.timer.cancel()


app = pg.mkQApp()
mw = QtWidgets.QMainWindow()
mw.setWindowTitle('1kHz PlotWidget')
mw.resize(800,800)
cw = QtWidgets.QWidget()
mw.setCentralWidget(cw)

# Vertical arrangement
l = QtWidgets.QVBoxLayout()
cw.setLayout(l)

# Let's create a plot window
qtPanningPlot1 = QtPanningPlot(l,"Arduino 1st channel")
label = QtWidgets.QLabel("This label show how to add another Widget to the layout.")
l.addWidget(label)

# called for every new sample at channel 0 which has arrived from the Arduino
# "data" contains the new sample
# filter = Filter(samplingRate, 49, 51)
filter = FIRFilter(fir_coeff_bp(samplingRate, 25, 35))
def callBack(data):
    # filter your channel 0 samples here:
    # data = self.filter_of_channel0.dofilter(data)
    # send the sample to the plotwindow
    qtPanningPlot1.addData(filter.filter(data))
    # qtPanningPlot1.addData(data)

# Get the Ardunio board.
board = Arduino(PORT,debug=True)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)
channel = 1

# Register the callback which adds the data to the animated plot
# The function "callback" (see above) is called when data has
# arrived on channel 0.
print(len(board.analog))
board.analog[channel].register_callback(callBack)

# Enable the callback
board.analog[channel].enable_reporting()

t = Blink(board, 1/60)
t.start()

# Show the window
mw.show()

# showing all the windows
pg.exec()

t.stop()
# needs to be called to close the serial port
board.exit()

print("Finished")


np.savetxt("dump.dat", qtPanningPlot1.data)