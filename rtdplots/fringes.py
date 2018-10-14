from ..baseplot import RtdAxis, RtdFigure, plt, np, Lock
from ..mapping import WIN, T1, T2, BASE, PHI, POL, VIS

def grabBaseInfo(dataCom, index):

	map = dataCom.config["MAP"]

	if map is None:
		return 0,0,0,0,"N"
	baseMapIds = np.where(map[BASE]==(index+1))[0]	
	if not len(baseMapIds):
		return 0,0,0,0,"N"

	baseMapId = baseMapIds[0]	
	tel1, tel2 = map[baseMapId][T1],map[baseMapId][T2]
	polar = map[baseMapId][POL]

	dlsNumbers = dataCom.config["NS.DL"]
	if tel1 and tel2 and\
	    dlsNumbers is not None:
	    	dl1, dl2 = dlsNumbers[tel1-1], dlsNumbers[tel2-1]
	else:
		dl1, dl2 = 0, 0 
	
	return tel1, tel2, dl1, dl2, polar		



class RtdCombinedFringesAxis(RtdAxis):
	baseIndex = 0
	
	def initPlot(self):
		baseIndex = self.parameters['baseIndex']

		axis= self.axis	
		###
		# grab some info
		with Lock(self.dataCom) as dataCom:
			(self.tel1, self.tel2, 
		     self.dl1, self.dl2, 
	    	 self.polar) = grabBaseInfo(dataCom, baseIndex)
		

		##
		# Setup the axis		
		axis.clear()
		axis.set_xlabel("OPD [$\mu m$]")
		axis.set_ylabel("")
		axis.grid(True)
		axis.axis('off')

		elms = self.elements
		##
		# init some plot objects 
		# lines will be incremented in the axis.lines object 
		elms['LINE.FRINGES'], = axis.plot([0],[0], color="black");
		elms['LINE.OPD'] = axis.axvline(0.0, linestyle="dashed")			
		
				
		## legend of the plod	
		elms['TEXT.DL1'] = axis.text(0.02, 0.88, "%d-DL%d"%(self.tel1,self.dl1), 
				  				      color="red", transform=axis.transAxes) 

		elms['TEXT.DL2'] = axis.text(0.70, 0.88, "%d-DL%d"%(self.tel2,self.dl2), 
				  					 color="red", transform=axis.transAxes) 

		# The 0 in x - axis (static)
		axis.text(0.5,-0.15, "0", transform=axis.transAxes)
		# The max OPD position 
		elms['TEXT.MAX.OPD'] = axis.text(0.0,-0.15, "", transform=axis.transAxes)

		# The max Flux text (position static, value change)
		elms['TEXT.MAX.FLUX'] = axis.text(-0.1, 1.0, "", transform=axis.transAxes) #MAXFLUXTEXT


	def update(self):
		baseIndex = self.parameters['baseIndex']
		axis = self.axis
		

		opdRange = slice(0,None)	
		##
		# grab the data
		
		with Lock(self.dataCom) as dataCom:
			if not (dataCom.checkStep("filterCombinedData") and\
		 	dataCom.checkStep("computeOpdPerTelescope")):
		 		return 
			data = 	dataCom.data	
			try:
				y = data['SCAN.SCI.CMB.FILTERED']
				x = data['SCAN.OPD.CMB.FILTERED']
				tst =  data.get("STATUS.TEL.TRACKING", None)
				posPerBase = data.get("POS.BASE", None)
			except KeyError:
				return 	
					
		y = y[baseIndex].real
		x = x[baseIndex]

		xmin, xmax = x.min(), x.max()
		ymin, ymax = y.min(), y.max()

		elms = self.elements

		####
		# update the fringes
		elms["LINE.FRINGES"].set_data(x[opdRange], y[opdRange])
		
		###
		# set the axis limits 				
		axis.set_xlim(xmin, xmax)
		axis.set_ylim(ymin, ymax)
		

		ytext = ymin-(ymax-ymin)*0.1				
		

		mopdt = elms["TEXT.MAX.OPD"]							
		xmopdt = int(xmax)
		## transform xmopdt to system axis (0->1)
		mopdt.set_x(xmopdt/xmax/2.0+0.5)
		mopdt.set_text("%d"%xmopdt)


		elms["TEXT.MAX.FLUX"].set_text("%.2f"%ymax)
		
		####
		# update color of legend and vertical line
		
		if  tst is not None:
			colors = ["red", "blue"] # colors[True] -> "blue"

			ts1 = tst[self.tel1-1]
			ts2 = tst[self.tel2-1]

			elms["TEXT.DL1"].set_color(colors[ts1])
			elms["TEXT.DL2"].set_color(colors[ts2])
			
			elms["LINE.OPD"].set_color(colors[ts1 and ts2])

		####
		# update The vertical line
		
		if posPerBase is not None:
			elms["LINE.OPD"].set_xdata(posPerBase[baseIndex])


class RtdCombinedFringesFigure(RtdFigure):		
	AxisClass = RtdCombinedFringesAxis
	def isReady(self):
		return self.dataCom.checkStep("filterCombinedData") and\
		 self.dataCom.checkStep("computeOpdPerTelescope")
		
	def turnOn(self):
		self.dataCom.turnRecipyOn("filter")
	
	def turnOff(self):
		self.dataCom.turnRecipyOff("filter")	

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






