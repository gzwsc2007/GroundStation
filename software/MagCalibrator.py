from Tkinter import *
import threading
import math
import matlab.engine

class MagCalibrator(object):
	def __init__(self):
		self.buf = [] # n x 3 buffer of mag samples
		self.magFieldRadius = 0
		self.hardIronOffsets = [0, 0, 0]
		self.softIronMatrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
		self.visualizer = CoverageVisualizer(600)

	def startAcceptingSamples(self):
		# Clear data buffer
		self.buf = []

		# start converage visualization
		self.visualizer.startVis()

	def doneReceivingAndStartCal(self):
		# Destroy the converage visualization
		self.visualizer.closeVis()

		# Invoke MATLAB to do the calibration work
		eng = matlab.engine.start_matlab()
		M = matlab.double(self.buf)
		eng.workspace['M'] = M
		(BField, Offsets, W_inverted) = eng.ellipsoid_fit2magnetic_data(M, nargout=3)
		self.magFieldRadius = BField
		self.hardIronOffsets = Offsets
		self.softIronMatrix = W_inverted

	def onNewSample(self, mx, my, mz):
		self.buf.append((mx, my, mz))
		self.visualizer.onNewSample(mx, my, mz)

	def getMagFieldRadius(self):
		return self.magFieldRadius

	def getHardIronOffsets(self):
		return self.hardIronOffsets

	def getSoftIronMatrix(self):
		return self.softIronMatrix


class CoverageVisualizer(threading.Thread): 
	def __init__(self, boxSize):
		self.boxSize = boxSize
		r = boxSize / 2
		self.box1Origin = (r, r)
		self.box2Origin = (r+boxSize, r)
		self.box3Origin = (r+boxSize+boxSize, r)
		self.boxRadius = int(0.9*r) # drawable area

		self.notRunning = True

	def startVis(self):
		self.root = Tk()
		self.root.overrideredirect(1)
		canvas = Canvas(self.root, width=3*self.boxSize, height=self.boxSize)
		canvas.pack()

		# draw box separators
		canvas.create_line(self.boxSize, 0, self.boxSize, self.boxSize)
		canvas.create_line(2*self.boxSize, 0, 2*self.boxSize, self.boxSize)

		# draw titles
		canvas.create_text(self.box1Origin[0], 10, text="XY")
		canvas.create_text(self.box2Origin[0], 10, text="YZ")
		canvas.create_text(self.box3Origin[0], 10, text="XZ")

		# draw the bounding circles
		canvas.create_oval(self.box1Origin[0]-self.boxRadius, self.box1Origin[1]-self.boxRadius,
											 self.box1Origin[0]+self.boxRadius, self.box1Origin[1]+self.boxRadius)
		canvas.create_oval(self.box2Origin[0]-self.boxRadius, self.box2Origin[1]-self.boxRadius,
											 self.box2Origin[0]+self.boxRadius, self.box2Origin[1]+self.boxRadius)
		canvas.create_oval(self.box3Origin[0]-self.boxRadius, self.box3Origin[1]-self.boxRadius,
											 self.box3Origin[0]+self.boxRadius, self.box3Origin[1]+self.boxRadius)

		self.canvas = canvas
		self.notRunning = False

		# ugly hack to allow multiple invocation of the same thread object
		threading.Thread.__init__(self)
		self.start()

	def closeVis(self):
		self.notRunning = True
		self.root.destroy()

	def onNewSample(self, mx, my, mz):
		if self.notRunning:
			return

		# First normalize the readings
		norm = math.sqrt(mx*mx+my*my+mz*mz)
		mx /= norm
		my /= norm
		mz /= norm

		r = 2

		# draw XY on box1
		x = self.box1Origin[0] + int(mx * self.boxRadius)
		y = self.box1Origin[1] + int(my * self.boxRadius)
		self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="red")

		# draw YZ on box2
		x = self.box2Origin[0] + int(my * self.boxRadius)
		y = self.box2Origin[1] + int(mz * self.boxRadius)
		self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="red")

		# draw XZ on box3
		x = self.box3Origin[0] + int(mx * self.boxRadius)
		y = self.box3Origin[1] + int(mz * self.boxRadius)
		self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="red")

	def run(self):
		self.root.mainloop()