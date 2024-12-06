import matplotlib
matplotlib.use('Qt5Agg')
from PyQt6 import QtCore, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pyqtgraph as pg # tested with pyqtgraph==0.13.7

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import pyqtgraph as pg

class Graph(QMainWindow):
    def __init__(self, title, n_plots, back_samples):
        super(Graph, self).__init__()

        self.back_samples = back_samples
        self.setWindowTitle(title)

        self.time_plot = pg.PlotWidget()
        self.time_plot.setYRange(0, 0.1)
        # self.time_plot_curve1 = self.time_plot.plot([], symbolPen=pg.mkPen(color=(200, 200, 255)))
        # self.time_plot_curve2 = self.time_plot.plot([])
        self.setCentralWidget(self.time_plot)

            # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(0) # causes the timer to start immediately
        self.timer.timeout.connect(self.update_plot) # causes the timer to start itself again automatically
        self.timer.start()

        self.plot_curves = [self.time_plot.plot([]) for _ in range(n_plots)]
        self.samples = [[] for _ in range(n_plots)]

        self.show()

    def update_plot(self):
        for plot_curve, samples in zip(self.plot_curves, self.samples):
            plot_curve.setData(samples[-self.back_samples:])

    def add_sample(self, sample, plot):
        self.samples[plot].append(sample)