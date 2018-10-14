from ..baseplot import RtdAxis, RtdFigure, plt, np, Lock
from ..mapping import WIN, T1, T2, BASE, PHI, POL, VIS


class RtdTelFluxAxis(RtdAxis):

	def initPlot(self, *args):		
		
		axis = self.axis		
		axis.axis("off")
		#axis.set_title("Flux")

		with Lock(self.dataCom) as dataCom:
			map = dataCom.config.get("MAP", None)

		align = self.parameters.get("align", "horizontal")


		if map is not None:
			nTel = max(map["t1"].max(), map["t2"].max())
		else:
			nTel = 4


		elms = self.elements
		
		step = 1.0/nTel

		if align == "horizontal":
			for tel in range(nTel):			
				r = plt.Rectangle( (0.0, 1.0-step -tel*step), width=0.0, height=0.2, facecolor="green", alpha=0.4, visible=False, 
					edgecolor="white"
					)
				axis.add_patch(r)
				elms["RECTANGLE.TEL%d"%tel] = r

				elms["TEXT.FLUX.TEL%d"%tel] = axis.text(
					0.0, 1.0-step-tel*step,
					
					"%d"%(tel+1), 
					transform=axis.transAxes, 
					rotation=0.0, size="smaller",
					horizontalalignment="left", 
					verticalalignment="bottom", 
				)

		else:	

			for tel in range(nTel):			
				r = plt.Rectangle( (tel*step, 0.2), width=0.2, height=0, facecolor="green", alpha=0.4, visible=False, 
					edgecolor="white"
					)
				axis.add_patch(r)
				elms["RECTANGLE.TEL%d"%tel] = r

				elms["TEXT.FLUX.TEL%d"%tel] = axis.text(
					tel*step, 0.0,
					"%d"%(tel+1), 
					transform=axis.transAxes, 
					rotation=-90, size="smaller",
					horizontalalignment="left", 
					verticalalignment="bottom", 
				)
			
		if align=="horizontal":
			def _set(r, v):
				r.set_width(v)
			
			def _setlim(axis, mini, maxi):
				axis.set_xlim(mini, maxi)
				#axis.set_ylim(1.0/nTel, 1.0+1.0/nTel)

		else:
			def _set(r, v):
				r.set_height(v)			
			def _setlim(axis, mini, maxi):
				axis.set_ylim(mini, maxi)
				#axis.set_xlim(0, 1.0)
	

		self.setRFlux = _set
		self.setLim = _setlim



		# elms["TEXT.MAX"] = axis.text(0.0 , 1.0, "", size="small", horizontalalignment="left", transform=axis.transAxes)
		# elms["TEXT.MIN"] = axis.text(0.0 , 0.05, "", size="small", horizontalalignment="left", transform=axis.transAxes)

	def update(self):
		axis =  self.axis
					

		with Lock(self.dataCom) as dataCom:	
			if not dataCom.checkStep("computeFlux"):
				return 

			data = dataCom.data			
			fluxes = data["FLUX.TEL"]
			tsts = data.get("STATUS.TEL.TRACKING",None)

		elms = self.elements

		


		
		if tsts is None:
			tsts = [False]*len(snr)

		colors = ["red", "green"]


		med = False		


		mfluxes = fluxes-np.median(fluxes) if med else fluxes

		for i, (mflux,flux,ts) in enumerate(zip(mfluxes, fluxes, tsts)):
			r = elms["RECTANGLE.TEL%d"%i]


			self.setRFlux(r, mflux)
			r.set_visible(True)
			r.set_facecolor(colors[ts])				

			t = elms["TEXT.FLUX.TEL%d"%i]
			t.set_text("%g"%flux)



		if med:
			l = np.max(np.abs(mfluxes))
			self.setLim(axis, -l, l)
		else:	
			xmin, xmax = np.min(fluxes), np.max(fluxes)
			ylim1 = xmin-(xmax-xmin)*0.15
			self.setLim(axis, ylim1, xmax)
		


		#elms["TEXT.MAX"].set_y(xmax)
		#elms["TEXT.MAX"].set_text("%1.2E"%xmax)
		#elms["TEXT.MIN"].set_y(xmin)
		#elms["TEXT.MIN"].set_text("%1.2E"%xmin)
	

class RtdTelFluxFigure(RtdFigure):	

	def isReady(self):
		return self.dataCom.checkStep("computeFlux")
	def turnOn(self):
		self.dataCom.turnRecipyOn("flux")
	def turnOff(self):
		self.dataCom.turnRecipyOff("flux")
	
	def makeSubPlots(self):
		fig = self.fig		
		axis = fig.add_subplot(1,1,1)
		rtdPlot = RtdTelFluxAxis(self.dataCom, axis)
		return [rtdPlot]

	def initPlots(self):
		#self.fig.subplots_adjust(left=0.2)

		RtdFigure.initPlots(self)



class RtdTelSnrAxis(RtdAxis):

	def initPlot(self, *args):		
		
		axis = self.axis		
		axis.axis("off")
		#axis.set_title("SNR")
		elms = self.elements

		align = self.parameters.get("align", "horizontal")

		with  Lock(self.dataCom) as dataCom:
			map = dataCom.data.get("MAP", None)

		if map is not None:			
			nTel = max(map["t1"].max(), map["t2"].max())
		else:
			nTel = 4

		step = 1.0/nTel

		if align=="horizontal":

			for tel in range(nTel):			
				r = plt.Rectangle( (-1, 1.0-step - tel*step), width=0.0, height=0.2, facecolor="green", alpha=0.4, visible=False, 
					edgecolor="white"
					)
				axis.add_patch(r)
				elms["RECTANGLE.TEL%d"%tel] = r

				elms["TEXT.SNR.TEL%d"%tel] =  axis.text(
					0.0, 1.0-step-tel*step,					
					"", 
					transform=axis.transAxes, 
					rotation=0.0, size="smaller",
					horizontalalignment="left", 
					verticalalignment="bottom"
				)
				
		else:


			for tel in range(nTel):			
				r = plt.Rectangle( (tel*step, -1.0), width=0.2, height=0, facecolor="green", alpha=0.4, visible=False, 
					edgecolor="white"
					)
				axis.add_patch(r)
				elms["RECTANGLE.TEL%d"%tel] = r
				
				elms["TEXT.SNR.TEL%d"%tel] =  axis.text(					
					tel*step, 0.2, 
					"", 
					transform=axis.transAxes, 
					rotation=90, size="smaller",
					horizontalalignment="left", 
					verticalalignment="bottom"
				)
		if align=="horizontal":
			def _set(r, v):
				r.set_width(v)
			
			def _setlim(axis, mini, maxi):
				axis.set_xlim(mini, maxi)

		else:
			def _set(r, v):
				r.set_height(v)			
			def _setlim(axis, mini, maxi):
				axis.set_ylim(mini, maxi)	
				
		self.setRSNR = _set
		self.setLim = _setlim		

		#elms["TEXT.MAX"] = axis.text(0.17,0.0, "      ", size="small", horizontalalignment="right")
		#elms["TEXT.MIN"] = axis.text(0.17,0.0, "",size="small", horizontalalignment="right")
					
	def update(self):
		axis = self.axis
		elms = self.elements

		with Lock(self.dataCom) as dataCom:
			if not dataCom.checkStep("computeOpdPerTelescope"):
				return 
							
			data = dataCom.data
			snrs = data["SNR.TEL"]
			stst = data.get("STATUS.TEL.TRACKING", None)

		if stst is None:
			stst = [False]*len(snr)			

		for i,(snr,ts) in enumerate(zip(snrs, stst)):
			r = elms["RECTANGLE.TEL%d"%i]

			self.setRSNR(r,snr+1)
			r.set_visible(True)
			if not ts:
				r.set_facecolor( "red")
			else:
				if snr<3:
					r.set_facecolor( "orange")
				else:
					r.set_facecolor( "green")						
			
			t = elms["TEXT.SNR.TEL%d"%i]
			t.set_text("%.0f"%snr)		

		xmin, xmax = np.min(snrs), np.max(snrs)
		ylim1 = 0.0 
		self.setLim(axis, -1.0, max(6,xmax))
		#elms["TEXT.MAX"].set_y(xmax)
		#elms["TEXT.MAX"].set_text("%.0f"%xmax)
		#elms["TEXT.MIN"].set_y(xmin)
		#elms["TEXT.MIN"].set_text("%.0f"%xmin)
		

class RtdTelSnrFigure(RtdFigure):	

	def isReady(self):
		return self.dataCom.checkStep("computeOpdPerTelescope")
	def turnOn(self):
		self.dataCom.turnRecipyOn("snr")
	def turnOff(self):
		self.dataCom.turnRecipyOff("snr")
	
	def makeSubPlots(self):
		fig = self.fig		
		axis = fig.add_subplot(1,1,1)
		rtdPlot = RtdTelSnrAxis(self.dataCom, axis)
		return [rtdPlot]
	


