from ..baseplot import RtdAxis, RtdFigure, plt, np, Lock
from ..mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from .fringes import grabBaseInfo


class RtdCombinedFringesPsdAxis(RtdAxis):

	def initPlot(self):
		baseIndex = self.parameters["baseIndex"]		
		axis = self.axis
		

		###
		# grab some info
		with Lock(self.dataCom) as dataCom:			
			(self.tel1, self.tel2, 
	    	 self.dl1, self.dl2, 
	    	 self.polar) = grabBaseInfo(dataCom,baseIndex)


		##
		# Setup the axis
		axis.clear()
		axis.set_xlabel("Sigma [$1/\mu m$]")
		axis.set_ylabel("")
		axis.axis('off')

		elms = self.elements
		##
		# init some plot objects 
		# lines will be incremented in the axis.lines object 
		elms["LINE.PSD"], = axis.plot([0],[0], color="black")
		
		elms["LINE.MEAN.PSD"], = axis.plot([0],[0], color="blue")
		
		##
		# some static lines

		elms["LINE.FILT1"] = axis.axvline(0.0, 
			color="red", linestyle="dashed",
			visible=False)

		elms["LINE.FILT2"] =axis.axvline(0.0,
		 color="red", linestyle="dashed",
		 visible=False
		 )

		## legend of the plod	
		elms["TEXT.DL1"] = axis.text(0.02, 0.88, "%d-DL%d"%(self.tel1,self.dl1), 
				  color="red", transform=axis.transAxes)
			
		elms["TEXT.DL2"] =axis.text(0.70, 0.88, "%d-DL%d"%(self.tel2,self.dl2), 
				 color="red", transform=axis.transAxes)

		self.first = True
		#axis.draw()

	def update(self):
		dataCom = self.dataCom
		axis = self.axis
		baseIndex = self.parameters["baseIndex"]
		elms = self.elements

		##
		# grab the data 
		sigRange = slice(3,None)

		with Lock(self.dataCom) as dataCom:
			if not (dataCom.checkStep("filterCombinedData") and\
			   dataCom.checkStep("computeOpdPerTelescope")):
				return 
			data = dataCom.data
			try:
				y = data["FFT.SCI.CMB"]
				x = data["FFT.SIGMA"]			
				yMean = dataCom.permanentData["DATA.BUFFER.PSD"]
				filter = dataCom.config.get("FILTER.IN.RESCALED", None)
				tsts = data.get('STATUS.TEL.TRACKING',None)
			except KeyError:				
				return 	
				
		# take the norm 					
		y = np.abs(y[baseIndex])**2
		x = x[baseIndex]
		# take the mean real 
		yMean = yMean[:,baseIndex,:].mean(axis=0).real



		x, y, = x[sigRange], y[sigRange]

		xmin, xmax = x.min(), x.max()
		ymin, ymax = y.min(), y.max()				

						
		yMean = yMean[sigRange]


		yminMean, ymaxMean = yMean.min(), yMean.max()

		###
		# fix the limit, they should be arround
		# the filters limits
		
		if filter is not None:
			xlim2 = 2.5*filter.mean(axis=1).max()
		else:
			xlim2 = xmax
			filter = None	
		###
		# set the axis limits 				
		axis.set_xlim(0.0, xlim2)
		#axis.set_ylim(ymin, ymax)
		axis.set_ylim(min(ymin,yminMean), max(ymax,ymaxMean))

		####
		# update the plots obblect
		elms["LINE.PSD"].set_data(x, y)
		elms["LINE.MEAN.PSD"].set_data(x, yMean)

		####
		# change color if of if not tracking 
		colors = ["red", "blue"]
		

		if tsts is not None:
			ts1 = tsts[self.tel1-1]
			ts2 = tsts[self.tel2-1]
			elms["TEXT.DL1"].set_color(colors[ts1])
			elms["TEXT.DL2"].set_color(colors[ts2])
		
		###
		# the filter lines
		if filter is not None:
			elms["LINE.FILT1"].set_xdata(filter[baseIndex,0])
			elms["LINE.FILT1"].set_visible(True)
			elms["LINE.FILT2"].set_xdata(filter[baseIndex,1])
			elms["LINE.FILT2"].set_visible(True)


class RtdCombinedFringesPsdFigure(RtdFigure):		
	AxisClass = RtdCombinedFringesPsdAxis
	def isReady(self):
		return self.dataCom.checkStep("filterCombinedData") and\
		 self.dataCom.checkStep("computeOpdPerTelescope")
		
	def turnOn(self):
		self.dataCom.turnRecipyOn("filterPsd")
	
	def turnOff(self):
		self.dataCom.turnRecipyOff("filterPsd")	

	def makeSubPlots(self):
		dataCom = self.dataCom
		nBase = len(dataCom.data["SCAN.SCI.CMB"])	
		if nBase>6:
			M, N = 2, int(np.ceil(nBase/2))
		else:			
			M, N = 1, nBase

		subPlots = [ ]
		for i in range(nBase):
			axis = self.fig.add_subplot(N,M,i+1)
			basePlot = self.AxisClass(self.dataCom, axis, baseIndex=i)			
			subPlots.append(basePlot)
		return subPlots






