from ..baseplot import RtdAxis, RtdFigure, plt, np, Lock
from ..mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from .fringes import grabBaseInfo



def grabBaseInfo(dataCom, index):
    map = dataCom.config["MAP"][index]
    return map[T1], map[T2], map[POL]     

class RtdRawFFTAxis(RtdAxis):
    baseIndex = 0
    
    def initPlot(self):
        baseIndex = self.parameters['baseIndex']

        axis = self.axis 
        ###
        # grab some info
        with Lock(self.dataCom) as dataCom:
	        (self.tel1, self.tel2,          
    	     self.polar) = grabBaseInfo(dataCom, baseIndex)
        	self.nScan = dataCom.config["N.OPL"]
        ##
        # Setup the axis        
        axis.clear()
        #axis.set_xlabel("OPD [$\mu m$]")
        #axis.set_ylabel("")
        #axis.grid(True)
        axis.axis('off')

        elms = self.elements
        ##
        # init some plot objects 
        # lines will be incremented in the axis.lines object 
        elms['LINE.FFT'], = axis.plot([0],[0], color="black");
        
                        
        ## legend of the plod 
        elms['TEXT.BASE'] = axis.text(0.02, 0.88, "%d-%d"%(self.tel1,self.tel2), 
                                      color="red", transform=axis.transAxes) 

    

        # The Flux mean text (position static, value change)
        #elms['TEXT.MEAN.FLUX'] = axis.text(-0.1, 0.6, "", transform=axis.transAxes, size="small", color="blue") 
        #elms['TEXT.RMS.FLUX']  = axis.text(-0.1, 0.25, "", transform=axis.transAxes, size="small", color="blue") 


    def update(self):
        baseIndex =  self.parameters['baseIndex']
        axis = self.axis
        

        opdRange = slice(3,self.nScan//2)    
        ##
        # grab the data
        with Lock(self.dataCom) as dataCom:
        	if not self.dataCom.checkStep("computeDataFFTRaw"):
        		return 
	        data =  dataCom.data
	        y = data['FFT.SCI.RAW']
	        x = data['FFT.SIGMA.RAW']
			        

        y = np.abs(y[baseIndex][opdRange])
        x = x[baseIndex][opdRange]

        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()

        elms = self.elements

        ####
        # update the fringes
        elms["LINE.FFT"].set_data(x, y)
        
        ###
        # set the axis limits               
        axis.set_xlim(xmin, xmax)
        axis.set_ylim(ymin, ymax)
        
        #elms["TEXT.MEAN.FLUX"].set_text("%1.2e"%y.mean())
        #elms["TEXT.RMS.FLUX"].set_text("+-%1.2e"%y.std())


class RtdRawFFTFigure(RtdFigure):       
    AxisClass = RtdRawFFTAxis
    def isReady(self):
        return self.dataCom.checkStep("computeDataFFTRaw")

    def turnOn(self):
        self.dataCom.turnRecipyOn("raw")
    
    def turnOff(self):
        self.dataCom.turnRecipyOff("raw")   

    def makeSubPlots(self):
        dataCom = self.dataCom
        nBase = dataCom.config["N.WIN.SCI"]

        N = nBase// int(np.sqrt(nBase))
        M = int(np.ceil(nBase/N))

        subPlots = [ ]
        for i in range(nBase):
            axis = self.fig.add_subplot(N,M,i+1)
            basePlot = self.AxisClass(self.dataCom, axis, baseIndex=i)          
            subPlots.append(basePlot)
        return subPlots





