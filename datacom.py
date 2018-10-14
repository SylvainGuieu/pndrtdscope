""" This implpement the DataCommunication class

The class contains all functions to handle Pionier raw scan, reduce them, and send basic command 
to PIONIER.

To simplify the class contain also named recipies that can be turned on/off and executed in a loop.
The recipies correspond to concrete scenarios (e.g. 'track' to track fringes, 
                                               'raw' to prepare the raw data for plot ...)

Example:
    >>> from pndrtdscope import DataCommunication
    >>> dc = DataCommunication("wpndcs")
    >>> dc.runRecipy("filter")
    >>> plot(dc.data['SCAN.SCI.CMB.FILTERED'][0], dc.data['SCAN.OPD.CMB.FILTERED'][0])


All configuration and data are stored in 3 dictionaries:

.data: data parameters 
----------------------
All the following parameters are deleted when a new scan arrive.  

|              Param               |       constructor        |     Alterator      |         type             |
|----------------------------------|--------------------------|--------------------|--------------------------|
| SCAN.SCI                         | receiveData              | prepareData        | float (N.WIN.SCI,N.OPL)  |
| SCAN.DARK                        | receiveData              | prepareData        | float (N.WIN.DARK,N.OPL) |
| SCAN.OPD                         | receiveData              | prepareData        | float (N.TEL,N.OPL)      |
| TIME.MJD                         | receiveData              |                    | float                    |
| TIME.ELAPSED                     | receiveData              |                    | float                    |
| TEST.NEW                         | receiveData              |                    | bool                     |
| SCAN.SCI.OFFSET                  | saveDataOffset           |                    | float (N.WIN.SCI,N.OPL)  |
| SCAN.DARK.OFFSET                 | saveDataOffset           |                    | float (N.WIN.DARK,N.OPL) |
| SCAN.SCI.CMB                     | combineData              | filterCombinedData | float (N.BASE.N.OPL)     |
| SCAN.OPD.CMB                     | combineData              | filterCombinedData | float (N.BASE.N.OPL)     |
| FFT.SCI.CMB                      | computeDataFFTCmb        |                    | float (N.BASE,N.OPL)     |
| FFT.SIGMA                        | computeDataFFTCmb        |                    | float (N.BASE,N.OPL)     |
| POS.BASE                         | computeOpdPerBase        |                    | float (N.BASE,)          |
| SNR.BASE                         | computeOpdPerBase        |                    | float (N.BASE,)          |
| SNR.BASE.MEAN                    | computeOpdPerBase        |                    | float (N.BASE,)          |
| POS.TEL                          | computeOpdPerTelescope   |                    | float (N.TEL,)           |
| SNR.TEL                          | computeOpdPerTelescope   |                    | float (N.TEL,)           |
| POS.BASE.RECOMP                  | computeOpdPerTelescope   |                    | float (N.BASE,)          |
| STATUS.TEL.TRACKING              | computeOpdPerTelescope   |                    | bool (N.TEL,)            |
| SCAN.SCI.CMB.FILTERED            | filterCombinedData       |                    | float (N.BASE, N.OPL)    |
| SCAN.OPD.CMB.FILTERED            | filterCombinedData       |                    | float (N.BASE, N.OPL)    |
| SCAN.SCI.RAW                     | prepareRaw               | computeDataFFTRaw  | float (N.WIN.SCI, N.OPL) |
| SCAN.OPD.RAW                     | prepareRaw               | computeDataFFTRaw  | float (N.WIN.SCI, N.OPL) |
| FLUX.TEL                         | computeFlux              |                    | float (N.TEL,)           |
| FFT.SCI.RAW                      | computeDataFFTRaw        |                    | float (N.WIN.SCI, N.OPL) |
| FFT.SIGMA.RAW                    | computeDataFFTRaw        |                    | float (N.WIN.SCI, N.OPL) |
| SCAN.SCI.CMB.FILTERED.NORMALIZED | normalizeDataCmb         |                    | float (N.BASE, N.OPL)    |
| PHASE.TEL                        | computeDifferentialPhase |                    | float (N.TEL,)           |


.permanentData: Permanent Data Parameters
-----------------------------------------

This parameter are not erazed but are linked to data (not config)

|      Param       | constructor |     Alterator     |       type          |
|------------------|-------------|-------------------|---------------------|
| COUNTER.DATA     | __init__    | receiveData       | long                |
| COUNTER.CONFIG   | __init__    | prepareData       | int                 |
| DATA.BUFFER.PSD  | __init__    | computeOpdPerBase | (10,N.BASE, N.SCAN) |
| ID.BUFFER        | __init__    | computeOpdPerBase | int                 |
| SCAN.SCI.OFFSET  | prepareData |                   | (N.BASE, N.SCAN)    |
| SCAN.DARK.OFFSET | prepareData |                   | (N.BASE, N.SCAN)    |
| SEARCH.DL.POS    | __init__    |                   | (?, N.TEL)          |
| SEARCH.SNR       | __init__    |                   | (?, N.TEL)          |


.config: Configuration Parameters
---------------------------------

Parameters related to instrument configuration and computation 


|            Param             |    constructor    |  Alterator  |         type             |
|------------------------------|-------------------|-------------|--------------------------|
| N.WIN.SCI                    | __init__          | receiveData | int                      |
| N.WIN.DARK                   | __init__          | receiveData | int                      |
| N.POLAR                      | __init__          | receiveData | int                      |
| N.OPL                        | __init__          | receiveData | int                      |
| N.BASE                       | __init__          | prepareData | int  N.TRUE.BASE*N.POLAR |
| N.TRUE.BASE                  | __init__          | prepareData | int                      |
| N.TEL                        | __init__          | prepareDa   | int                      |
| NS.DL                        | __init__          | receiveData | (N.TEL,)                 |
| OBC                          | __init__          | prepareData | string                   |
| MAP                          | __init__          | prepareData | recarray(N.WIN.SCI,)     |
| MAPC                         | __init__          | prepareData | recarray(N.BASE,)        |
| SNR.MIN                      | __init__          | prepareData | float                    |
| FILTER.IN                    | __init__          |             | float (2,)               |
| FILTER.OUT                   | __init__          |             | float (2,)               |
| STRENGTH.TURBULENCE          | config.defaults   |             | float                    |
| TEST.SUBSTRACT.DARKWIN       | __init__          | prepareData | bool                     |
| TEST.COMPUTE.OVERSAMP.FACTOR | config.defaults   |             | bool                     |
| TEST.PROCESS.OVERSAMP        | config.defaults   |             | bool                     |
| ID.OVERSAMPLING              | preparedData      |             | int(-undefined-,)        |
| FREQ.MAX                     | preparedData      |             | float                    |
| FILTER.IN.RESCALED           | computeOpdPerBase |             | float (2,)               |
| N.FIRST.SCAN.TO.CLEAN        | config.defaults   |             | int                      |


"""

recipiesInfo = """
            getdata     : get and prepare data 
                        Will fail and raise Exception if problem 

            getdatasafe : get and prepare the data 
                          If failed (e.g. communication problems, or scan not running)
                          wait a few before giving back the hand for an other try  

            track     : run for tracking the fringes
                        - Combine the data
                        - Compute the FFT of combined data
                        - Compute the OPD per base
                        - Compute the OPD per telescope
                        - send offset to the telescope

            filter    : run to plot filtered data
                        - Run all the track computing
                        - filter the combined data

            filterPsd : run to plot the filtered Psd
                        do the same as 'filter'

            flux      : run to get the flux per telescope
                        - prepare raw data
                        -compute the Flux per telescope

            snr       : run to get the tracking snr per telescope
                        - run all the track computing

            raw       : run to plot the raw data
                        - prepare raw 
                        - compute its fft
                        
            niobate   : run to plot niobate fringes 
                        and send differential phase 
                        - run the same computing than track
                        - compute differential phase
                        - send the computed differential phase    
"""


import numpy as np

from . import config
if config.defaults.get("SIMU.MODE", False):
    from . import comsimu as com 
else:
    from . import com

from . import computing
from .mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from time import time as _time
import time
from collections import OrderedDict

## for python3
try:
    unicode
except NameError:
    basestring = (str,bytes)




class DataCommunication(object):
    """ Class that handle communication with pndcom and some raw data handling 

    The class is constructed with one string parameter, the host name
    """

    device = None # Device object set after connection opened

    ## 
    # The log function maybe update it one day  
    log = staticmethod(com.log)

            
    def __init__(self, host="localhost"):
        if not isinstance(host, basestring):
            raise ValueError("Expecting a string for host got %r"%host)         

        self.host = host

        NTEL = config.defaults.get("N.TEL", 4)
        self.config = config.defaults.copy()        
        self.config.update ( 
            {
            # init the real time parameters
            "N.WIN.SCI" : 0,  #number of Science windows
            "N.WIN.DARK": 0,  # number of dark windows
            "N.POLAR": 1,      
            "N.OPL"  : 0,     # number of scan point (OPL)
            "N.TRUE.BASE" : 0,  
            "MAP" : None,     # full MAP information corresponding to the IOBC
            "MAPC": None,     # reduced MAP information, one per base (without ABCD)
            "NS.DL": [0]*NTEL,  # delay line numbers
            "OBC": "" 
            }   
        )
        self.permanentData = {
            "DATA.BUFFER.PSD":None,  #list buffer of PSD 
            "ID.BUFFER":-1,          
            "COUNTER.DATA": 0,
            "COUNTER.CONFIG": 0, 
            "TIMES.TRACK": np.ones((10,), float)*_time()           
        }
        self.steps = {} 
        self.data = {} 
        self._locked = False
        self.resetData()
        self.timers = {}        
        self.elapsedTimes = {}   
        


    def _tic(self,label):
        self.timers[label] = _time()
        self.steps[label] = False

    def _tac(self,label):
        try:
            tic = self.timers[label]
        except KeyError:
            return None
        self.elapsedTimes[label] = (_time()-tic)
        self.steps[label] = True

    def checkStep(self, step):
        return self.steps.get(step, False)

    def open(self):
        """ open the communication. If already open do nothing 
        
        Parameters
        ----------
        None

        Outpus
        ------
        None

        Raises
        ------
        RuntimeError : with pndcom error code and message in it      
        """
        if not self.isOpen():
            self.device = com.openCom(self.host)
    
    def isOpen(self):
        """ Check if communication is opened 

        Parameters
        ----------
        None

        Outpus
        ------
        test : bool

        """
        if not self.device:
            return False        
        return com.isOpen(self.device)

    def resetData(self, timeout=5, ignore=False):
        """ reset all the data componant to None 
        
        if the data is locked (from plot interface for example), wait that it get unlocked 
        before clearing data. 
        If it does not get unlock after `timeout` a RuntimeError is raise unless ignore is False

        Parameters
        ----------
        None
        
        Outpus
        ------
        None
        """  
        s = time.time()
        if ignore:
            while self._locked:
                time.sleep(0.01)
                if (time.time()-s)>timeout:
                    break
            self._locked = False                   
        else:    
            while self._locked:
                time.sleep(0.01)
                if (time.time()-s)>timeout:
                    raise RuntimeError("The data is locked")

        self.data.clear()  # clear all data
        self.steps.clear() # clear the step dictionary 
      

    def lock(self):
        """ lock the running data 

        if locked, the .data  dictionary cannot been cleaned until it has been unlocked
        
        """
        self._locked = True

    def unlock(self):
        """ unlock the running data 

        if locked the .data  dictionary cannot been cleaned until it has been un locked

        """
        self._locked = False

                
    def receiveData(self, timeout=1000):
        """ Wait for scanning data and populate the data parameters 

        Data Product
        ------------
        TIME.ELAPSED : float
            time in seconds since last scan
        TIME.MJD : float
            MJD time of scan
        TEST.NEW : bool
            True if the data has a new shape than previous scan
        
        SCAN.OPD: float (N.TEL,N.OPL) 
            Opd for each scan point and telescope 
        SCAN.SCI : float (N.WIN.SCI, N.OPL) 
            Scientific flux measurement for each outputs and scan point 
        SCAN.DARK : float (N.WIN.DARK, N.OPL) 
            Flux for the dark windows
        
        Permanent Data Product
        ----------------------
        COUNTER.DATA : int
            scan counter

        Configuration Product
        ---------------------
        N.WIN.SCI: int
            Number of scientific windows
        N.WIN.DARK: int
            number of dark windows
        N.OPL: int
            number of OPL per scan (size of the scan typicaly 512)
        N.TEL: int
            number of telescopes
        """
        self._tic("receiveData")
        ###
        # record the previous data format to check if the data is new
        config, data = self.config, self.data

        previous_nWin, previous_nOpl = config["N.WIN.SCI"]+config["N.WIN.DARK"],config["N.OPL"] 
        previousMjd = data.get('TIME.MJD',0)

        
                
        # open communication if needed
        # open() is ignored if communication already exists
        try:
            self.open()
        except RuntimeError as e:
            self.resetData()
            raise RuntimeError("Data Error: %s"%e) 
                       

        ## get the nData, nOpl values in integer        
        nData, nOpl = com.getScanDataShape(self.device)


        if not (nData*nOpl):
            self.log("No scanning data")
            self.resetData()
            return 1
        
        ## Now retrieve the data         
        try:
            rawData = com.receiveData(self.device, (nOpl,nData), float, timeout)
        except RuntimeError as e:  
            self.resetData()           
            raise RuntimeError("Data Error: %s"%e)
        
        #######
        # Now that we have recieve new data we can reset the curent one
        #
        self.resetData()    
       
        mjd = com.getMJD()   
        if previousMjd:
            data['TIME.ELAPSED'] = (mjd-previousMjd)*24*3600
        else:
            data['TIME.ELAPSED'] = 0.0    
        data['TIME.MJD'] = mjd    
        



        ## 
        # 
        nTel = config["N.TEL"]
        nWin = nData - nTel

        ###
        # Check if data has a new shape
        isNewShape = (previous_nWin!=(nWin)) or (previous_nOpl!=nOpl)

        ##
        # the dark window are at the end 
        # as we do not know how many they are 
        # we can assume that the number of base is 6
        # and so the numberof of science window is 12 or 24
        # :TODO: find a better way to find dark window 
        nDarkWin = nWin%12 if nWin>12 else 0

        nSciWin = nWin - nDarkWin

        ##
        # Transpose the data to have window/tel indices first
        rawData = rawData.T
        oplData = rawData[0:nTel,:]
        sciData = rawData[nTel:nSciWin+nTel,:]
        if nDarkWin:
            darkData = rawData[nSciWin+nTel:,:]
        else:
            darkData = 0.0 
        
        config["N.WIN.SCI"]  = nSciWin
        config["N.WIN.DARK"] = nDarkWin
        config["N.OPL"] = nOpl
        config["N.TEL"] = nTel


        data["TEST.NEW"] = isNewShape

        self.permanentData["COUNTER.DATA"] += 1 
        data["SCAN.OPD"]  = oplData
        data["SCAN.SCI"]  = sciData
        data["SCAN.DARK"] = darkData

        self.log("receive #%d  %dx%d data "%(
            self.permanentData["COUNTER.DATA"],
            nData, nOpl)
        )

        self._tac("receiveData")
        return 0

    def isDataValid(self):
        """ check if raw data is valid 
        
        if ready the data are stored in:
            'SCAN.OPD'
            'SCAN.SCI'
            'SCAN.DARK'
            

            exists also isDataReady which check also 
                if the data is valid and has been prepared
                
        Parametes
        ---------
        None

        Outputs
        -------
        test : bool
            True is the data is valid 

        """
        return self.data.get("SCAN.SCI",None) is not None
        
    def isDataReady(self):
        """ check is the data has been prepared 
                
        Parametes
        ---------
        None

        Outputs
        -------
        test : bool
            True is the data is ready 
        """
        return self.checkStep("prepareData")
    
    def hasSavedOffset(self):
        """ True if data offset (background) has been saved 

        Outputs
        -------
        test : bool
            True if data offset (background) has been saved 
        """
        return "SCAN.SCI.OFFSET" in self.permanentData
        
    def prepareData(self):
        """ Prepare the raw data 
        
        - cleanup  the first scan   (N.FIRST.SCAN.TO.CLEAN)
        - substract the dark windows if TEST.SUBSTRACT.DARKWIN
        - compute oversampling factor if TEST.COMPUTE.OVERSAMP.FACTOR
        - save the current scan as offset if user asked for it
        - remove the offset to the scan if user asked for it
        - center the scan 
        IF the shape of data has changed (change of instrument config)
            - del the stored offsets
            - update the config keys and mapping
        """
        if not self.isDataValid():
            self.log("Data not valid")
            return 

        if self.checkStep("prepareData"):
            self.log("Data already prepared")
            return          

        self._tic("prepareData")

        ##
        # note all operation will modify
        # the array inplace
        config, data = self.config, self.data

        sciData  = data["SCAN.SCI"]        
        darkData = data["SCAN.DARK"]
        oplData  = data["SCAN.OPD"]
                
        nOpl    = config["N.OPL"]
        nSciWin = config["N.WIN.SCI"]

        ###
        # clean a few first
        nFclean = config["N.FIRST.SCAN.TO.CLEAN"]
        for i in range(nFclean):
            sciData[:,i] = sciData[:,nFclean]
                        
        ####
        # substract the darkwindows 
        #
        if config["TEST.SUBSTRACT.DARKWIN"] and (darkData is not None):
            sciData  -= np.mean(darkData)            
            self.log("Dark windows substracted",3)        
    
        ####
        # Change opd unit (was like that in yorick :( ) 
        #
        oplData *= 1e6
        self.log("Opd is now in micron",3)


        ###
        # compute the oversampling factor 
        # 
        if config["TEST.COMPUTE.OVERSAMP.FACTOR"]:
            dx = (oplData[:,18] - oplData[:,17]) ## in um
            #
            nd = dx.size

            sampling = 1.0 / config["FILTER.IN"].mean() / np.max( np.abs(dx - a.repeat(nd).reshape((nd,nd))) ) 
            self.log("sampling=%s"%sampling, 3)
            overSamplingFactor = np.max( int(sampling/3.5), 1)
        else:           
            overSamplingFactor = 1;
        self.log("overSamplingFactor=%d"%overSamplingFactor, 3)
        

        ####
        # Remove the saved offset if any 
        #
        if com.getSaveDataOffsetFlag():
            self.permanentData["SCAN.SCI.OFFSET"]  = sciData
            self.permanentData["SCAN.DARK.OFFSET"] = darkData
            com.clearSaveDataOffsetFlag()

        if com.getSubstractDataOffsetFlag() and self.hasSavedOffset():
                        
            sciData  -= self.permanentData["SCAN.SCI.OFFSET"]
            darkData -= self.permanentData["SCAN.DARK.OFFSET"]
                                
        # Center the scan and move it to the right 
        # yorick : opl -= opl(nopl/2,)(-,);
        for i in range(len(oplData)):
            oplData[i,:] -= oplData[i,nOpl//2] 

        ##
        # This is not needed as
        # the array are modified inplace
        #self.sciData = sciData
        #self.darkData = darkData
        #self.oplData = oplData
        

        ####
        # reload the snrMin
        config["SNR.MIN"] = com.getSnrMin()        
            
        ####
        # If the data shape is the same than before,
        # nothing else to do.
        if not data["TEST.NEW"]:
            self.log("-%04d Data prepared in %.3f sec "%(self.permanentData["COUNTER.DATA"],(com.getMJD()-data["TIME.MJD"])*24*3600), 2)
            self._tac("prepareData")            
            return

        ####
        # From Here the data shape has changed 

        ###
        # new config, increase the counter
        self.permanentData["COUNTER.CONFIG"] += 1    

        ##########
        ## continue
                
        self.log("Data shape is shanged or new. Check for new setup")
        obc = com.getObcType()
        self.log("The obc is %r"%obc)
        
        #######
        # the offset are not anymore valids
        if self.hasSavedOffset():
            del self.permanentData["SCAN.SCI.OFFSET"]
            del self.permanentData["SCAN.DARK.OFFSET"]  

        ###
        # Check if we know the mapping (correlation matrix)
        map = com.findMap(obc, nSciWin) 
        if map is not None:
            ##
            # store mapc which is a map with unique base on it 
            # And sorted by increasing base number 
            bases  = list(set(map[BASE]))
            bases.sort()            
            mapids = [np.where(map[BASE]==b)[0][0] for b in bases]
            mapc = map[mapids]

            ###
            # From map determine how many polar type is ued
            nPolar = len(set(map[POL]))
        else:
            nPolar = 0
            mapc = None    
        
        dlsNumbers = com.getDlsConfig()
        
        freqmax = nOpl//2//overSamplingFactor
        
        u = np.arange(nOpl)
        idOversampling = (u) - (nOpl*(u > nOpl/2))

        ###
        # update the dictionary 
        # all other data has been altered in place 

        config["ID.OVERSAMPLING"] = np.where( (idOversampling<=freqmax) * (idOversampling>-freqmax))[0]

        config["FREQ.MAX"] = freqmax
        config["MAP"] = map
        config["MAPC"] = mapc
        config["N.TRUE.BASE"] = len(mapc)
        config["N.BASE"] = np.max(map[BASE])
        config["OBC"] = obc
        config["N.POLAR"] = nPolar
        config["NS.DL"] = dlsNumbers
                                     
        self._tac("prepareData")  


    def combineData(self):
        """ Make the combined data 

        The result is saved in SCAN.SCI.CMB and SCAN.OPD.CMB
        Data must be prepared before and have a map associated  
        
        Data Product
        ------------
        SCAN.SCI.CMB : array (N.BASE, N.OPL)
            Combined data per base 
        SCAN.OPD.CMB : array (N.BASE, N.OPL)
            The opd for combined data (can be is changed)

        """
        if not self.checkStep("prepareData"):
            raise RuntimeError("Data must be prepared first")

        if self.checkStep("combineData"):
            self.log("Data already combined")
            return

        self._tic("combineData")            
        data, config = self.data, self.config
        map = config["MAP"]
        if map is None:
            raise RuntimeError("No interaction matrix map given, cannot combine data")
        
        (
         data["SCAN.SCI.CMB"],
         data["SCAN.OPD.CMB"] 
        ) = computing.computeDataCmd(
            data["SCAN.SCI"],
            data["SCAN.OPD"],
            map
        )
        self._tac("combineData")

    def computeDataFFTCmb(self):
        """ Compute the FFT on combined data 
        
        Data Product
        ------------
        FFT.SCI.CMB : array (N.BASE, N.OPL)
            The fft of combined data 
        FFT.SIGMA : array (N.BASE, N.OPL) 
            spectral frequency         
        """
        if not self.checkStep("combineData"):
            raise RuntimeError("computeDataFFTCmd: Data must be combined first")

        if self.checkStep("computeDataFFT"):
            self.log("FFT already computed")
            return 

        self._tic("computeDataFFTCmb")

        data, config = self.data, self.config

        (
         sciFFTCmb, 
         sigCmb
         ) = computing.computeDataFFT(
                data["SCAN.SCI.CMB"],
                data["SCAN.OPD.CMB"] 
            )
        if config["TEST.PROCESS.OVERSAMP"]:
            sciFFTCmb = sciFFTCmb[:,config["ID.OVERSAMPLING"]]
            sigCmb = sigCmb[:,config["ID.OVERSAMPLING"]]

        data["FFT.SCI.CMB"] = sciFFTCmb
        data["FFT.SIGMA"] =   sigCmb
                            
        self._tac("computeDataFFTCmb")


    def computeOpdPerBase(self):
        """ Compute the piston with IOTA method 

        
        Data Products
        -------------
        POS.BASE : array (N.BASE,)
            The piston value for each base
        SNR.BASE : array (N.BASE,)
            The SNR for the piston computation 
        SNR.BASE.MEAN : array (N.BASE,)
            The SNR computed from the PSD buffer ring 
            The number of ellements 
        
        Permanent Data Products
        -----------------------            
        DATA.BUFFER.PSD  : array (config["SIZE.PSD.BUFFER"], N.BASE, N.OPL)
            The updated buffer for PSD computation            
        ID.BUFFER : int
            buffer array index of the current psd 
        
        Config Products
        ---------------                
        FILTER.IN.RESCALED : array (N.BASE,)
            The filter rescale for each base        
        """
        if not self.checkStep("computeDataFFTCmb"):
            raise RuntimeError("computeOpdIota: FFTcmb must be computed first")
        if self.checkStep("computeOpdPerBase"):
            return 

        self._tic("computeOpdPerBase")
        permanentData, data, config = self.permanentData, self.data, self.config

        (data["POS.BASE"], 
         data["SNR.BASE"], 
         data["SNR.BASE.MEAN"],
         permanentData["DATA.BUFFER.PSD"],
         permanentData["ID.BUFFER"], 
         config["FILTER.IN.RESCALED"]
         ) = computing.computeOpdIota(
                data["FFT.SCI.CMB"], 
                data["FFT.SIGMA"], 

                fltIn = config["FILTER.IN"], 
                fltOut= config["FILTER.OUT"],
                psdBuffer=  permanentData["DATA.BUFFER.PSD"],
                psdBufferId = permanentData["ID.BUFFER"]
        )        
        self._tac("computeOpdPerBase")

    def computeOpdPerTelescope(self):
        """ Compute the SNR and the DL offset 

        Compute the SNR and the DL offset for the 4 DLs based on the
        6 opd pos computed for each baseline. 

        Data Products
        -------------
        POS.TEL : array (N.TEL,)
            piston position per telescope
        SNR.TEL : array (N.TEL,)
            The SNR for each telescope
        POS.BASE.RECOMP : array (N.BASE,)
            The recomputed position for each base                       
        STATUS.TEL.TRACKING : array (N.BASE,) of boolean 
            True for telescope tracking                                         
        """

        if self.config.get("MAP", None) is None:
            raise RuntimeError("No IOBC mapping ")
        self._tic("computeOpdPerTelescope") 
        data, config = self.data, self.config

        (
         data["POS.TEL"],
         data["SNR.TEL"],
         data["POS.BASE.RECOMP"],
         data["STATUS.TEL.TRACKING"]
        ) = computing.computeOplMatrix(
                    data["POS.BASE"],
                    data["SNR.BASE"],
                    config["MAPC"],                    
                    config["SNR.MIN"],
                    niobate= False# must be false at that point
        )
        self._tac("computeOpdPerTelescope") 

    def filterCombinedData(self):
        """ filter the combined data 

        Altered Data Products
        ----------------------
        SCAN.SCI.CMB
        SCAN.OPD.CMB
        
        Data Products
        -------------
        SCAN.SCI.CMB.FILTERED : array (N.BASE, N.OPL)
            The filtered, combined data
        SCAN.OPD.CMB.FILTERED : array (N.BASE, N.OPL)
        
        """
        

        if not self.checkStep("computeDataFFTCmb"):
            raise RuntimeError("no combined fft computed")
        if self.checkStep("filterCombinedData"):
            return 

        self._tic("filterCombinedData")    
        data, config = self.data, self.config

        ##
        # filter back to the binned combined data
        (
         data["SCAN.SCI.CMB"],
         data["SCAN.OPD.CMB"]
        ) = computing.computeDataFFT(
              data["FFT.SCI.CMB"], 
              data["FFT.SIGMA"],
              inverse=True
        )

          

        (   
         data["SCAN.SCI.CMB.FILTERED"], 
         data["SCAN.OPD.CMB.FILTERED"]             
        ) = computing.computeFiltered(
                data["FFT.SCI.CMB"], 
                data["FFT.SIGMA"],
                config["FILTER.IN"]
        )
        self._tac("filterCombinedData") 

    def prepareRaw(self):
        """ prepare the raw data 

        Mainly for plot purpose, compute the OPD per base

        Data Products
        -------------
        SCAN.OPD.RAW : array (N.BASE, N.OPL)
            opd per base 
        SCAN.SCI.RAW : array (N.BASE, N.OPL)
            is alias of the sciData array                       
        """
        if not self.checkStep("prepareData"):
            raise RuntimeError("prepareRaw data is not ready")
        if self.checkStep("prepareRaw"):
            return             
        self._tic("prepareRaw")  
        data, config = self.data, self.config

        map = config["MAP"]

        data["SCAN.SCI.RAW"] = data["SCAN.SCI"]
        data["SCAN.OPD.RAW"] = data["SCAN.OPD"][map[T2]-1,:]- data["SCAN.OPD"][map[T1]-1,:]

        self._tac("prepareRaw")

    def computeDataFFTRaw(self):
        """ Compute the fft for raw data 

        Saved Attributes
        ----------------
        FFT.SIGMA.RAW : array (N.BASE, N.OPL)
            spatial frequenices per base
        FFT.SCI.RAW: array (N.BASE, N.OPL)
            fft of sciDataRaw
        
        Altered Product
        ---------------
        If TEST.PROCESS.OVERSAMP is True:
        SCAN.SCI.RAW 
        SCAN.OPD.RAW        
        """
        if not self.checkStep("prepareRaw"):
            raise RuntimeError("prepareDataFFTRaw raw data not prepared")
        if self.checkStep("computeDataFFTRaw"):
            return             
        self._tic("computeDataFFTRaw") 
        data, config = self.data, self.config

        (
         sciFFTRaw, 
         sigRaw
         )  = computing.computeDataFFT(
                data["SCAN.SCI.RAW"],
                data["SCAN.OPD.RAW"] 
            )
        
        if config["TEST.PROCESS.OVERSAMP"]:

            sigRaw = sigRaw[:,config["ID.OVERSAMPLING"]]
            sciFFTRaw = sciFFTRaw[:,config["ID.OVERSAMPLING"]]

            (
              data["SCAN.SCI.RAW"],
              data["SCAN.OPD.RAW"]  
            ) = computing.computeDataFFT(
                sciFFTRaw,  sigRaw, inverse=1
            )                                                
        
        data["FFT.SCI.RAW"]   = sciFFTRaw
        data["FFT.SIGMA.RAW"] = sigRaw

        self._tac("computeDataFFTRaw")           

    def computeFlux(self):
        """ Compute the flux per telescope 
        
        Data Products
        -------------
        FLUX.TEL : array (N.TEL,)
        """

        if not self.checkStep("prepareRaw"):
            raise RuntimeError("prepareDataFFTRaw raw data not prepared")
        if self.checkStep("computeFlux"):
            return


        self._tic("computeFlux")          

        data, config = self.data, self.config
        data["FLUX.TEL"] = computing.computeFluxPerTelescope(
            data["SCAN.SCI.RAW"], 
            config["MAP"]
        )

        self._tac("computeFlux") 
    
    def normalizeDataCmb(self):
        """ Normalize the combined data to the same contrast 

        (usefull to plot niobate differential phase)
        
        Data Products
        ----------------
        SCAN.SCI.CMB.FILTERED.NORMALIZED : array (N.BASE, N.OPL)
        """
        if not self.checkStep("filterCombinedData"):
            raise RuntimeError("data not filtered")
        if self.checkStep("normalizeDataCmb"):
            return             
        self._tic("normalizeDataCmb")

        a = self.data["SCAN.SCI.CMB.FILTERED"]
        den = np.abs(a).max(axis=1)
        den[den<1e-9] = 1e-9
        tmp = (a.T / den).T

        self.data["SCAN.SCI.CMB.FILTERED.NORMALIZED"] = tmp

        self._tac("normalizeDataCmb") 


    def computeDifferentialPhase(self):
        """ Compute the differential phase 

        Data Products
        ---------------
        PHASE.TEL :  array (N.TEL,)
            phase per telescope (in degree)
        """

        ## ignore if no polar 
        map = self.config.get("MAP", None)
        if map is None:
            return  
        if len(set(map[POL]))<2:
            return 

        if not self.checkStep("normalizeDataCmb"):
            raise RuntimeError("Data must be normalized")                                 
        if self.checkStep("computeDifferentialPhase"):
            return     
            
        self._tic("computeDifferentialPhase")

        data, config = self.data, self.config

        data["PHASE.TEL"] = computing.computeDifferentialPhase(
                data["SCAN.SCI.CMB.FILTERED.NORMALIZED"], 
                config["MAPC"]
            )                
        self._tac("computeDifferentialPhase")   




   #######
   # The recipy dictionary  
   # A client can decide which recipies must be turned on/off
   # For instance to plot filtered fringes the plot process can turn the recipy
   # 'filter' on    
    recipies = OrderedDict(
            [   
                ('getdata', False),
                ('getdatasafe', False),
                ('track', False), 
                ('filter', False), 
                ('filterPsd', False),
                ('flux', False),
                ('snr', False),
                ('raw', False),
                ('niobate', True) # Can be on if not wollaston in
                                  #  This will do nothing  
            ]
    )
    
    def turnRecipyOn(self, recipy): 
        """ Turn a given recipy on for the runRecipies function

        Parameters
        ----------
        recipy : string
            one of  

        """+recipiesInfo       
        try:
            self.recipies[recipy]
        except KeyError:
            raise ValueError["Unknown recipy %r"%recipy]            
        self.recipies[recipy] = True

    def turnRecipyOff(self, recipy):
        """ Turn a given recipy off for the runRecipies function

        Parameters
        ----------
        recipy : string
            one of  
                    
        """+recipiesInfo         
        try:
            self.recipies[recipy]
        except KeyError:
            raise ValueError["Unknown recipy %r"%recipy]            
        self.recipies[recipy] = False

    def runRecipies(self):
        """ Run all the recipies that has been turned on 

        see turnRecipyOff, turnRecipyOn
        """
        self._tic("recipy:all")
        for recipy, state in self.recipies.items():
            if state:
                if self.runRecipy(recipy):
                    break
        self._tac("recipy:all")        
        return 0

    def runRecipy(self,recipy):
        """ run a given recipy 

        Parameters
        ----------
        recipy : string
            one of  
        """+recipiesInfo   

        def run(check, cmd):
            if not self.checkStep(check):
                cmd()
        if recipy == "getdata":
            self._tic("recipy:getdata")
            self.open() # try to open connection if closed
            self.receiveData()
            run("prepareData",self.prepareData)
            self._tac("recipy:getdata")
            return 0

        if recipy == "getdatasafe":
            """ get the data in the safe way
            no exception raised if no data found but sleep for a time before returning
            the hand for an other try.            
            """
            self._tic("recipy:getdatasafe")

            sleepTime = 2 # seconds           
            try:
                self.open()
            except RuntimeError:    
                self.log("Connection to host '%s' failed wait %f sec"%(self.host, sleepTime))
                time.sleep(sleepTime)
                self._tac("recipy:getdatasafe")
                return 1
            ##
            # try to get the data and check if data is valid 
            try:
                self.receiveData()
            except RuntimeError:
                self.log("Waiting for scan, wait %f sec"%sleepTime)
                time.sleep(sleepTime)
                self._tac("recipy:getdatasafe")
                return 1

            if not self.isDataValid():
                self.log("Waiting for scan, wait %f sec"%sleepTime)
                time.sleep(sleepTime)
                self._tac("recipy:getdatasafe")
                return 1

            run("prepareData",self.prepareData)
            if not self.isDataReady():
                self.log("Wrong data retry wait %f sec "%sleepTime)
                time.sleep(sleepTime)
                self._tac("recipy:getdatasafe")    
                return 1
                        
            self._tac("recipy:getdatasafe")
            return 0

        if recipy == "track":
            self._tic("recipy:track")
            run("combineData", self.combineData)
            run("computeDataFFTCmb", self.computeDataFFTCmb)
            run("computeOpdPerBase", self.computeOpdPerBase)
            run("computeOpdPerTelescope", self.computeOpdPerTelescope)                                                            
            self.sendOffsets()       
            self._tac("recipy:track")
            return 0    
        
        elif recipy == "filter" or recipy == "filterPsd":
            self._tic("recipy:filter")            
            run("combineData", self.combineData)
            run("computeDataFFTCmb", self.computeDataFFTCmb)
            run("computeOpdPerBase", self.computeOpdPerBase)
            run("computeOpdPerTelescope", self.computeOpdPerTelescope)
            run("filterCombinedData", self.filterCombinedData)
            self._tac("recipy:filter")
            return 0

        elif recipy == "flux":
            self._tic("recipy:flux")
            run("prepareRaw",  self.prepareRaw)
            run("computeFlux", self.computeFlux)
            self._tac("recipy:flux")
            return 0

        elif recipy == "snr": # same as track but without sending offsets
            self._tic("recipy:snr")
            run("combineData", self.combineData)
            run("computeDataFFTCmb", self.computeDataFFTCmb)
            run("computeOpdPerBase", self.computeOpdPerBase)
            run("computeOpdPerTelescope", self.computeOpdPerTelescope)                        
            self._tac("recipy:snr")
            return 0

        elif recipy == "raw":
            self._tic("recipy:raw")
            run("prepareRaw", self.prepareRaw)
            run("computeDataFFTRaw", self.computeDataFFTRaw)
            run("computeFlux", self.computeFlux)
            self._tac("recipy:raw")
            return 0

        elif recipy == "niobate":    
            self._tic("recipy:niobate")
            run("combineData", self.combineData)            
            run("computeDataFFTCmb", self.computeDataFFTCmb)
            run("filterCombinedData", self.filterCombinedData)
            run("normalizeDataCmb", self.normalizeDataCmb)
            run("computeDifferentialPhase", self.computeDifferentialPhase)
            self.sendDifferentialPhase()
            self._tac("recipy:niobate")
            return 0


    ##########################################
    #
    # Communication, action function 
    #
    ##########################################


    def sendDifferentialPhase(self):
        """ Send the differential phase to PIONIER 

        This will be ignored if no wallaston in place or if one of the
        baseline is not tracking (no fringes).
        """
        
        map = self.config.get("MAP", None)
        if map is None:
            return 
        ## ignore if no polar 
        if len(set(map[POL]))<2:
            return
        if not self.checkStep("computeDifferentialPhase"):                       
            raise RuntimeError("differential phase not computed")
        ## send the differential phase only if all
        ## telescope are tracking
        if all(self.data.get("STATUS.TEL.TRACKING", [False])):
            com.sendDifferentialPhase(self.data['PHASE.TEL'])
            

    def sendOffsets(self, timeout=1000):
        """ Send the computed offset to the delay lines 
    
        Parmeters
        ---------
        timeout : int, optional
            time out in milisecond (default is 1000)    

        Outputs
        -------
        None
        """

        if not self.checkStep("computeOpdPerTelescope"):
            raise RuntimeError("tel offset position not computed")
        
        tt = self.permanentData["TIMES.TRACK"]        
        tt[1:] = tt[0:-1]
        tt[1] = _time()

        ## if no tracking return 
        if not com.getTrackingFlag():
            return             

        try:
            com.sendOffsets(self.device, self.data["POS.TEL"], timeout=timeout) 
        except RuntimeError:
            self.log("ERROR Offset to DL: %s failed !"%(", ".join("%.2f"%o for o in self.data["POS.TEL"])),1)    



    def sendSnr(self, timeout=1000):
        """ Send the computed SNR to Pionier
    
        Parmeters
        ---------
        timeout : int, optional
            time out in milisecond (default is 1000)    

        Outputs
        -------
        None
        """

        if not self.checkStep("computeOpdPerTelescope"):
            raise RuntimeError("tel offset position not computed")
        
        for i,snr in self.data["SNR.TEL"]:
            com.setSnr(i,snr)


class Lock(object):
    """ decorate a dataCom instance so it will be locked in a with instance 

    Example
    -------
        with Lock(dataCom) as dc:
            # do stuff
    

    """
    def __init__(self, dataCom):
        self.dataCom = dataCom
    
    def __enter__(self):
        self.dataCom.lock()
        return self.dataCom

    def __exit__(self,type, value, traceback):
        self.dataCom.unlock()



class FringeState(object):
    def __init__(self, base, map):
        ou = np.where(map[BASE] == base)[0]
        if not ou:
            raise RuntimeError("Invalid base number for this map")
        i = ou[0]
        self.tels = [map[i][T1], map[i][T2]]

        self.dlOrigins = [com.getDlPos(t-1) for t in self.tels]
        self.signs = [1, 1]
        self.steps = [ ]




