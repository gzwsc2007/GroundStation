import wx
import time
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab

TIME_SPAN_SECONDS = 3.0

class AltimeterPlot(wx.Panel):
    def __init__(self, parent, size, style):
        wx.Panel.__init__(self, parent, size=size, style=style)

        self.altMax = 200
        self.refAlt = 100
        self.refAltMin = 50
        self.altData = np.array([])
        self.timeData = np.array([])
        self.initTime = time.time()

        self.cycleStart = True
        self.cycleStartTime = time.time()
        self.cycleStartIndex = 0

        self.initPanel()

    def setGreenRefAltitude(self, refAlt):
        self.refAlt = refAlt
        self.greenLine.set_ydata([refAlt, refAlt])
        self.redrawPlot()

    def setRedRefAltitude(self, refAlt):
        self.refAltMin = refAlt
        self.redLine.set_ydata([refAlt, refAlt])
        self.redrawPlot()

    def addDataPoint(self, alt):
        now = time.time()

        # Resize the data array if necessary. Prevent it from growing too large.
        if (self.cycleStart):
            self.cycleStart = False
            self.cycleStartTime = now
            self.cycleStartIndex = len(self.altData)
        elif (now - self.cycleStartTime >= TIME_SPAN_SECONDS):
            self.altData = self.altData[self.cycleStartIndex:]
            self.timeData = self.timeData[self.cycleStartIndex:]
            self.cycleStart = True

        self.altData = np.append(self.altData, alt)
        self.timeData = np.append(self.timeData, now - self.initTime)

        # Create a sliding window effect
        xmax = self.timeData[-1] if self.timeData[-1] > TIME_SPAN_SECONDS else TIME_SPAN_SECONDS
        xmin = xmax - TIME_SPAN_SECONDS
        self.axes.set_xbound(lower=xmin, upper=xmax)

        # Adjust y bound
        if (alt >= self.altMax):
            self.altMax = alt + 50
            self.axes.set_ybound(lower=0, upper=self.altMax)

        self.redrawPlot()

    def redrawPlot(self):
        self.plotData.set_xdata(self.timeData)
        self.plotData.set_ydata(self.altData)
        self.canvas.draw()

    def initPanel(self):
        self.fig = Figure((3.0, 6.0), dpi=100)

        self.axes = self.fig.add_subplot(111, xmargin=0, ymargin=0)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('Altitude (m)', size=10)
#        self.axes.set_xlabel('Time (s)', size=10)
        self.axes.grid(True, color='gray')
        self.axes.set_yticks(range(0, 1000, 25))
        self.axes.set_ybound(lower=0, upper=self.altMax)
        self.axes.set_xbound(lower=0, upper=TIME_SPAN_SECONDS)
        self.axes.set_autoscale_on(False)

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        self.plotData = self.axes.plot(
            self.altData, 
            linewidth=2,
            color=(1, 1, 0),
            )[0]

        self.greenLine = self.axes.axhline(self.refAlt, linewidth=3, color="green")
        self.redLine = self.axes.axhline(self.refAltMin, linewidth=3, color="red")

        self.canvas = FigCanvas(self, -1, self.fig)
