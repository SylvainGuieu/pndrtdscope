from collections import OrderedDict
from matplotlib.pylab import plt
from .mapping import WIN, T1, T2, BASE, PHI, POL, VIS
import numpy as np
from .datacom import Lock

FIGVERBOSELEVEL = 2

class RtdAxis(object):
	""" A base class for axis rtd plot 

	The object is splited in 3 base function 

	initPlot : 
	"""
	def __init__(self, dataCom, axis, parameters={}, **kwargs):
		self.axis = axis		
		self.dataCom = dataCom
		self.parameters = dict(parameters, **kwargs)

		self.elements = OrderedDict()

	
	def update(self):
		raise NotImplementedError('update')	

	def initPlot(self, i):
		return 	

	def draw(self):				
		elms, axis = self.elements, self.axis
		##
		# draw what we have to draw 
		for el in elms.values():
			axis.draw_artist(el)


class RtdFigure(object):
	attached = False

	def isReady(self):
		raise NotImplementedError('isReady')	

	def makeSubPlots(self):
		raise NotImplementedError('makeSubPlots')		

	def turnOn(self):
		raise NotImplementedError('turnOn')

	def turnOff(self):
		raise NotImplementedError('turnOff')	


	def __init__(self, dataCom, figId, **kwargs):
		fig = plt.figure(figId, **kwargs)
		self._initkwargs = kwargs
		self.figId = figId
		self.dataCom = dataCom
		self.lastDataCounter = -99
		self.lastConfigCounter = -99
		self.fig = fig
		self.rtdSubPlots = []
		self.checkCanvas()
		self.showed = False


	def checkCanvas(self):
		""" Check the canvas type of the figure 

		This is done in order to setup the right methods to update the canvas as
		fast as possible
		"""
		fig = self.fig
		canvasName = fig.canvas.__class__.__name__

		if canvasName == 'FigureCanvasMac':
			def updateCanvas(fig):															
				fig.canvas.draw()
			def initCanvas(fig):
				fig.canvas.draw()
			def drawSubplot(p):
				return 

		elif canvasName == 'FigureCanvasTkAgg':
			import matplotlib.backends.tkagg as tkagg

			def updateCanvas(fig):
				canvas = fig.canvas
				canvas.show()
				tkagg.blit(canvas._tkphoto,canvas.renderer._renderer, colormode=2)
				canvas._master.update_idletasks()
				canvas.flush_events()
				
			def initCanvas(fig):				
				fig.canvas.draw()
				fig.CanvasBackgrounds = [fig.canvas.copy_from_bbox(fig.bbox)]

			def drawSubplot(p):
				p.draw()


		elif canvasName == 'FigureCanvasQT':
			def updateCanvas(fig):
				#fig.show()
				fig.canvas.update()
			def initCanvas(fig):				
				fig.canvas.draw()
				fig.CanvasBackgrounds = [fig.canvas.copy_from_bbox(fig.bbox)]
			def drawSubplot(p):
				p.draw()
		else:
			def updateCanvas(fig):
				#fig.show()				
				fig.canvas.draw()
			def initCanvas(fig):
				fig.canvas.draw()
			def drawSubplot(p):
				return
		self.updateCanvas = updateCanvas
		self.initCanvas = initCanvas
		self.drawSubplot = drawSubplot

	def attach(self):
		###
		# if wasn't attached we need to re-init if rtdSubPlots is empty 
		if not self.attached:			
			if not self.rtdSubPlots:
				self.initPlots()
			self.turnOn()
			self.update()

		self.attached = True

	def detach(self):
		self.turnOff()
		self.attached = False		

	def clear(self):
		self.fig.clear()


	def show(self):
		if self.fig is None:
			self.fig = plt.figure(self.figId, **self._initkwargs)
					
		if not self.showed:		
			self.fig.show()
			self.showed = True
	
	def close(self):
		if self.fig is not None:
			plt.rtdSubPlots = []
			fig = self.fig
			fig.clear()
			self.fig = None
			plt.close(fig)
		


	def initPlots(self):
		##
		# if the plot is detached just return

		if not self.attached:
			return 
		dataCom = self.dataCom
		
		##
		# if igure has been close we need to build a new one
		if self.fig is None:
			self.fig = plt.figure(self.figId, **self._initkwargs)


		fig = self.fig					
		## clear the figure 
		fig.clear()
		
		###
		# make the subplots 		
		self.rtdSubPlots = self.makeSubPlots()

		###
		# init all subplots 
		for p in self.rtdSubPlots:
			p.initPlot()

		try:
			fig.canvas.show()	
		except AttributeError:
			pass	
		
		self.lastConfigCounter = dataCom.permanentData["COUNTER.CONFIG"]
		self.initCanvas(fig)		
		self.figSize = list(fig.get_size_inches())


	def update(self):
		####
		# if the plot is detached just return 		
		if not self.attached:
			return 

				
		dataCom = self.dataCom
		## No new data exit 
		if self.lastDataCounter == dataCom.permanentData["COUNTER.DATA"]:			
			return False

		if not self.isReady():
			dataCom.log("%s not ready "%self.figId, FIGVERBOSELEVEL)			
			return 

		dataCom.log("Updating figure %s"%self.figId, FIGVERBOSELEVEL)

		newSize = list(self.fig.get_size_inches())
		## The configuration has changed or size as changed, we need to reinit the plot		
		if self.lastConfigCounter!= dataCom.permanentData["COUNTER.CONFIG"] or\
			self.figSize!=newSize:			
				self.initPlots()
				self.figSize = newSize


		fig = self.fig

		if hasattr(fig, "canvasBackgrounds"):
			_ = [fig.canvas.restore_region(background) for background in fig.canvasBackgrounds]

		for p in self.rtdSubPlots:
			p.update()
			self.drawSubplot(p)

		self.lastDataCounter = dataCom.permanentData["COUNTER.DATA"]

		self.updateCanvas(self.fig)	




