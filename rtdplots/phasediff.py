from ..baseplot import RtdAxis, RtdFigure, plt, np, Lock
from ..mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from .fringes import grabBaseInfo


class RtdPhaseDiffMeterAxis(RtdAxis):
	initialized = False
	def initPlot(self):
		
		axis = self.axis
		elms = self.elements

		##
		# Setup the axis
		axis.clear()
		axis.set_xlabel("")
		axis.set_ylabel("")
		axis.axis('off')

		with Lock(self.dataCom) as dataCom:
			nPolar = dataCom.config["N.POLAR"]
			nTel = dataCom.config["N.TEL"]

		if nPolar < 2:
			axis.text(0.0, 0.5, "Wollaston Off")
			axis.set_xlim(0,1)
			axis.set_ylim(0.4,0.6)
			self.initialized = False	
			return  

			
		align = self.parameters.get("align", "horizontal")

		step = 1.0/nTel

		if align == "horizontal":
			for i, phase in enumerate(range(nTel)):
				
				elms["TEXT%d"%i] = axis.text( 
					0.5, 1-step-i*step,"", 
					transform=axis.transAxes, 
					horizontalalignment="center",
					verticalalignment="bottom"
				)
				r = plt.Rectangle( (0.0, 1-step-i*step), 
					width=0.0, height=0.2, facecolor="green", 
					alpha=0.4, visible=False, 
					edgecolor="white"
					)
				axis.add_patch(r)

				elms["RECTANGLE%d"%i] = r
		else:
			
			for i, phase in enumerate(range(dataCom.config["N.TEL"])):
				
				elms["TEXT%d"%i] = axis.text( 
						i*step ,.5, "", 
						transform=axis.transAxes 
						)
				r = plt.Rectangle( (i*step, 0.5), width=0.2, height=0, facecolor="green", 
													  alpha=0.4, visible=False)
				axis.add_patch(r)

				elms["RECTANGLE%d"%i] = r
		self.initialized = True	

		if align=="horizontal":
			def _set(r, v):
				r.set_width(v)
			
			def _setlim(axis):
				axis.set_ylim(0,1.0)
				axis.set_xlim(-30, 30)
		else:
			def _set(r, v):
				r.set_height(v)			
			def _setlim(axis):
				axis.set_xlim(0,1.0)
				axis.set_ylim(-30, 30)
				
				
		self.setRPhase = _set
		self.setLim = _setlim		
			
	def update(self):
		
		axis = self.axis
		elms = self.elements

		with Lock(self.dataCom) as dataCom:
			if not dataCom.checkStep("computeDifferentialPhase"):
				return 
			nPolar = dataCom.config["N.POLAR"]
			phases = dataCom.data["PHASE.TEL"]

		if nPolar < 2:
			return 
										
		colors = ["green", "red"]
		for i, phase in enumerate(phases):
			elms["TEXT%d"%i].set_text("%+.0f"%phase)
			r = elms["RECTANGLE%d"%i]
			r.set_facecolor(colors[np.abs(phase)>5])
			r.set_visible(True)
			self.setRPhase(r, phase)

		self.setLim(axis)


class RtdPhaseDiffMeterFigure(RtdFigure):		
	AxisClass = RtdPhaseDiffMeterAxis
	def isReady(self):
		return True
		return self.dataCom.checkStep("computeDifferentialPhase")
		
	def turnOn(self):		
		return 
		# no need to turn it on/off 
		#self.dataCom.turnRecipyOn("niobate")
	
	def turnOff(self):
		return 
		# no need to turn it on/off 		
		#self.dataCom.turnRecipyOff("niobate")	

	def makeSubPlots(self):

		return [self.AxisClass(self.dataCom, self.fig.add_subplot(1,1,1))]


class RtdPhaseDiffAxis(RtdAxis):

	def initPlot(self):
		baseIndex = self.parameters["baseIndex"]
		axis = self.axis
		

		###
		# grab some info
		with Lock(self.dataCom) as dataCom:
			(self.tel1, self.tel2, 
		     self.dl1, self.dl2, 
		     self.polar) = grabBaseInfo(dataCom,baseIndex)

			mapc = dataCom.config["MAPC"]
		


		self.iUp   = np.where( (mapc[T1]==self.tel1) *  (mapc[T2]==self.tel2)* (mapc[POL]=="U") )[0][0]
		self.iDown = np.where( (mapc[T1]==self.tel1) *  (mapc[T2]==self.tel2)* (mapc[POL]=="D") )[0][0]


		##
		# Setup the axis
		axis.clear()
		axis.set_xlabel("")
		axis.set_ylabel("")
		axis.axis('off')

		elms = self.elements
		##
		# init some plot objects 
		# lines will be incremented in the axis.lines object 
		elms["LINE.UP"], = axis.plot([0],[0], color="red")
		elms["LINE.DOWN"], = axis.plot([0],[0], color="green")
		elms["LINE.ENVELOP"], = axis.plot([0],[0], color="blue")
		
		axis.text(0.02, 0.88, "%d-%d"%(self.tel1,self.tel2), 
				  				      color="red", transform=axis.transAxes) 

		elms["TEXT.MAX"] = axis.text(-0.1, 1.0, "", size="small", transform=axis.transAxes)




	def update(self):


		with Lock(self.dataCom) as dataCom:
			if not dataCom.checkStep("computeDifferentialPhase"):
				return 
			nPolar = dataCom.config["N.POLAR"]
			data = dataCom.data		
			y = data["SCAN.SCI.CMB.FILTERED.NORMALIZED"]	
			x = data["SCAN.OPD.CMB"]


		if nPolar < 2:
			return 

		opdRange = slice(0,None)

		axis = self.axis
		baseIndex = self.parameters["baseIndex"]
		elms = self.elements
		iUp, iDown = self.iUp, self.iDown

		yall = y[:,opdRange]			
		yUp   = y[iUp][opdRange]
		yDown = y[iDown][opdRange]
		x = x[iUp][opdRange]
		

		
		envelop =  np.abs(yUp+yDown)/2.0
		emax = envelop.max()

		

		xmin, xmax = x.min(), x.max()
		ymin, ymax = min(yUp.min(), yDown.min()),  max(yUp.max(), yDown.max())	

		
		am = np.argmax( np.abs( yall[:6,:]+yall[6:,:] ), axis=1)[baseIndex] 
		axis.set_xlim(x[am]-2.5, x[am]+2.5)
		axis.set_ylim(0, max(ymax, emax))

		#axis.set_ylim(ymin, ymax)
		#axis.set_xlim(xmin, xmax)

		####
		# update the plots obblect
		elms["LINE.UP"].set_data(x, yUp.real)
		elms["LINE.DOWN"].set_data(x, yDown.real)
		elms["LINE.ENVELOP"].set_data(x, envelop)
		elms["TEXT.MAX"].set_text("%1.1f"%emax)


class RtdPhaseDiff2Axis(RtdAxis):

	def initPlot(self):
		baseIndex = self.parameters["baseIndex"]		
		axis = self.axis
		

		###
		# grab some info
		with Lock(self.dataCom) as dataCom:
			(self.tel1, self.tel2, 
		     self.dl1, self.dl2, 
		     self.polar) = grabBaseInfo(dataCom,baseIndex)

			mapc = dataCom.config["MAPC"]

		self.iUp   = np.where( (mapc[T1]==self.tel1) *  (mapc[T2]==self.tel2)* (mapc[POL]=="U") )[0][0]
		self.iDown = np.where( (mapc[T1]==self.tel1) *  (mapc[T2]==self.tel2)* (mapc[POL]=="D") )[0][0]


		##
		# Setup the axis
		axis.clear()
		axis.set_xlabel("")
		axis.set_ylabel("")
		axis.axis('off')

		elms = self.elements
		##
		# init some plot objects 
		# lines will be incremented in the axis.lines object 
		elms["LINE.UP"], = axis.plot([0],[0], color="red")
		elms["LINE.DOWN"], = axis.plot([0],[0], color="green")
		elms["LINE.ENVELOP.UP"], = axis.plot([0],[0], color="red")
		elms["LINE.ENVELOP.DOWN"], = axis.plot([0],[0], color="green")

		axis.text(0.02, 0.88, "%d-%d"%(self.tel1,self.tel2), 
				  				      color="red", transform=axis.transAxes) 

		elms["TEXT.MAX"] = axis.text(-0.1, 1.0, "", size="small", transform=axis.transAxes)




	def update(self):

		with Lock(self.dataCom) as dataCom:
			if not dataCom.checkStep("computeDifferentialPhase"):
				return 
			nPolar = dataCom.config["N.POLAR"]
			data = dataCom.data		
			y = data["SCAN.SCI.CMB.FILTERED.NORMALIZED"]	
			x = data["SCAN.OPD.CMB"]

		if nPolar < 2:
			return

		opdRange = slice(0,None)

		axis = self.axis
		baseIndex = self.parameters["baseIndex"]
		elms = self.elements
		iUp, iDown = self.iUp, self.iDown

		yall = y[:,opdRange]			
		yUp   = y[iUp][opdRange]
		yDown = y[iDown][opdRange]
		x = x[iUp][opdRange]

		yUpE = np.abs(yUp)
		yDownE = np.abs(yDown)

		xmin, xmax = x.min(), x.max()
		ymin, ymax = min(yUp.min(), yDown.min()),  max(yUp.max(), yDown.max())			
		am = np.argmax( np.abs( yall[:6,:]+yall[6:,:] ), axis=1)[baseIndex] 
		axis.set_xlim(x[am]-30, x[am]+30)
			
		axis.set_ylim(0, max(ymax,yUpE.max(), yDownE.max()))


		#axis.set_ylim(ymin, ymax)
		#axis.set_xlim(xmin, xmax)

		####
		# update the plots obblect
		elms["LINE.UP"].set_data(x, yUp.real)
		elms["LINE.DOWN"].set_data(x, yDown.real)
		elms["LINE.ENVELOP.UP"].set_data(x, yUpE )
		elms["LINE.ENVELOP.DOWN"].set_data(x, yDownE)

		elms["TEXT.MAX"].set_text("%1.1f"%ymax)




class RtdPhaseDiffFigure(RtdFigure):		
	AxisClass = RtdPhaseDiffAxis
	def isReady(self):
		return self.dataCom.checkStep("computeDifferentialPhase")

	def turnOn(self):
		return 
		# no need to turn it on/off 
		#self.dataCom.turnRecipyOn("niobate")
	
	def turnOff(self):
		return 
		# no need to turn it on/off 		
		#self.dataCom.turnRecipyOff("niobate")	

	def makeSubPlots(self):
		dataCom = self.dataCom
		nBase = len(dataCom.data["SCAN.SCI.CMB"])//2					
		M, N = 1, nBase

		subPlots = [ ]
		for i in range(nBase):
			axis = self.fig.add_subplot(N,M,i+1)
			basePlot = self.AxisClass(self.dataCom, axis, baseIndex=i)			
			subPlots.append(basePlot)
		return subPlots


class RtdPhaseDiff2Figure(RtdFigure):		
	AxisClass = RtdPhaseDiff2Axis
	def isReady(self):
		return self.dataCom.checkStep("computeDifferentialPhase")

	def turnOn(self):
		return 
		# no need to turn it on/off 
		#self.dataCom.turnRecipyOn("niobate")
	
	def turnOff(self):
		return 
		# no need to turn it on/off 		
		#self.dataCom.turnRecipyOff("niobate")	

	def makeSubPlots(self):
		dataCom = self.dataCom
		nBase = len(dataCom.data["SCAN.SCI.CMB"])//2					
		M, N = 1, nBase

		subPlots = [ ]
		for i in range(nBase):
			axis = self.fig.add_subplot(N,M,i+1)
			basePlot = self.AxisClass(self.dataCom, axis, baseIndex=i)			
			subPlots.append(basePlot)
		return subPlots
				
