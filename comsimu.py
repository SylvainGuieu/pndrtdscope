""" contain function to talk with the instrument via pndcom
or via data base.


Some function are juste use internaly, with python variable, 
but they are here for future implementation. 

"""
from __future__ import print_function
from  subprocess import Popen, PIPE
import re
from . import config
import numpy as np
import time
from .mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from imp import reload

#from . import pndcom
#from .pndcom import openCom, isOpen, sendCommand, receiveData, getMJD, log

print("THIS IS THE SIMULATION MODE")


simuConfig= {
    "N.TEL":4, 
    "N.SCI.WIN": 24,
    "N.DARK.WIN": 2, 
    "N.OPL": 512,

    "STROKES.SCAN" : [-40, -120, 40, 120],
    #"SPEED.SCAN" :   [69, 206, 69, 206],
    "SPEED.SCAN" :   [156.25, 468.75, 156.25,468.75],
    "SIGN.SCAN" : [-1,-1,1,1],
      
    "RATE.FRAME" : 2000, #Hz   
    "OBC":"4T-ABCD-H",
    "AMPLITUDE.NOISE": 0.1, # noize by spectral chanel
    "AMPLITUDE.READ.NOISE": 1, # readout noise 
    "FLUXES": [200]*4, 
    "NS.DL": [1,2,3,4], 
       
    "SPECTRA": np.ones( (4,1000), float )/1000., 
    "WAVELENGTHS" : np.linspace(1.4, 1.8, 1000), #micron
    #"SPECTRA": 200*np.ones( (4,1), float ), 
    #"WAVELENGTHS" : np.linspace(1.2, 1.4, 1),
    "PHASES.DIFF": [0.0, 0.0, 0.0, 0.0],
    "GINGLE.STRENGTH" : 10.,# 10 fraction of wavelenght
    "STRETCH.STRENGTH": 1./150, #fraction of stroke
    "POS.DL": [0]*4, 
    "FLAG.QUIT": False,
    "FLAG.TRACKING": True,
    "FLAG.SCOPE": True,
    "FLAG.QUIT": False, 
    "PLOT.FOCUS": "COMBINED",
    "SNR.MIN": 2.0,
    "SNRS":[0]*4, 

    ## noise free
    #"GINGLE.STRENGTH" : 0.,# 10 fraction of wavelenght
    #"STRETCH.STRENGTH": 0.0, #fraction of stroke
    #"AMPLITUDE.NOISE": 0.001,
    #"AMPLITUDE.READ.NOISE": 1,
}


simuConfigPol = simuConfig.copy()
simuConfigPol.update ({
    "N.TEL":4, 
    "N.SCI.WIN": 48,        
    "MAP": config.mapABCD_Hpol, 
    "N.POLAR": 2, 
    #"PHASES.DIFF": [-70.0, 5.0, 70.0, 0.0],
    "PHASES.DIFF": [-70.0, 0.0, 0.0, 10.0],
})
simuConfig = simuConfigPol


def reloadConfig():
    global simuConfig

    try:
        import pndrtdscope_config    
    except ImportError as e:
        print(e)
        return

        
    try: 
        reload(pndrtdscope_config)        
    except Exception as e:
        print(e)
        return 

    if hasattr(pndrtdscope_config, "simuConfig"):
        simuConfig.update(pndrtdscope_config.simuConfig)
    

VERBOSE = 1
def log(msg, level=1):
    if not VERBOSE or level>VERBOSE:
        return 
    print("%s"%( msg))


def openCom(host):
    return 1

def isOpen(device):
    return True



lastcallTime = 0
scanCounter = 0
scanPoses = None
def receiveData(device, shape, dtype, timeout=1000):
    global lastcallTime, scanCounter, scanPoses
    reloadConfig()

    if lastcallTime:
        dt = time.time()-lastcallTime
        log("SIMU Time Elapsed %.2f"%dt, 3)
        if dt<0.3:
            pass
            #time.sleep(0.3-dt)
    else:
        dt = 0.0                    
    #time.sleep(1.)

    lastcallTime = time.time()
    C = simuConfig
    nOpl, nData = shape
    nTel = C["N.TEL"]
    dPhiTel = simuConfig["PHASES.DIFF"]


    a = np.zeros( (nData,nOpl), dtype )


    spectra = C["SPECTRA"]

    noise = C["AMPLITUDE.NOISE"]
    wls = C["WAVELENGTHS"]
    nWave = len(wls)
    freq = C["RATE.FRAME"]

    if scanPoses is None:        
        scanPoses = [-p/2.0 for p in C["STROKES.SCAN"]]


    tels = np.zeros( (nTel, nWave, nOpl), np.complex)

    sign = [1.0, -1.0][scanCounter%2]
    scanCounter += 1 

    #time = np.linspace(0, 1.0/freq*nOpl, nOpl)
    stime = 1.0/freq * np.arange(nOpl)

    #for i, stroke in enumerate(simuConfig["STROKES.SCAN"]):
    #    #a[i,:] = np.linspace(-stroke, stroke,  nOpl)
    #    a[i,:] = np.linspace(-stroke, stroke,  nOpl)

    for i, (pos,s,speed) in enumerate(zip(scanPoses, C["SIGN.SCAN"],C["SPEED.SCAN"])):
        #a[i,:] = np.linspace(-stroke, stroke,  nOpl)
        a[i,:] = pos+sign*s*speed*stime #np.linspace(-stroke, stroke,  nOpl)

    scanPoses = list(a[0:nTel,-1])

    pi2 = 2*np.pi
    #pi2 = 1.0

    noises = np.random.normal(0.0, noise, (nTel, nWave, nOpl))

    g = C["GINGLE.STRENGTH"]
    gingles = np.random.random((nTel,))*g-g/2.0 / wls.mean()

    s = C["STRETCH.STRENGTH"]
    f = np.array(C["STROKES.SCAN"])*s
    stretch = np.random.random((nTel,nOpl))*f[:,None]-f[:,None]/2.0

    fluxes = np.asarray(C["FLUXES"])

    tels = (fluxes[:,None,None]*spectra[:,:,None]+noises)*np.exp(1j*(a[:nTel,None,:]+gingles[:,None,None]+stretch[:,None,:])*pi2/wls[None,:,None])
        
    j = 0
    map = findMap(simuConfig["OBC"], simuConfig["N.SCI.WIN"])
    for i, baseMap in enumerate(map, start=simuConfig["N.TEL"]):
        t1i = baseMap[T1]-1
        t2i = baseMap[T2]-1 

        if j>=24:
            phasediff1 = simuConfig["PHASES.DIFF"][t1i]/2.0*np.pi/180.
            phasediff2 = -simuConfig["PHASES.DIFF"][t2i]/2.0*np.pi/180.
        else:
            phasediff1 = -simuConfig["PHASES.DIFF"][t1i]/2.0*np.pi/180.
            phasediff2 = +simuConfig["PHASES.DIFF"][t2i]/2.0*np.pi/180.  

        tmp = tels[t1i]/4.+tels[t2i]/4.*np.exp(-1j*baseMap[PHI])*np.exp(1j*(phasediff1+phasediff2))
        tmp = np.abs(tmp)**2
        a[i,:] = tmp.sum(axis=0)
        j += 1

    nDark = simuConfig["N.DARK.WIN"]
    a[-nDark:] =  np.random.normal(0.0,C["AMPLITUDE.READ.NOISE"], (nDark,nOpl) )
    a[0:nTel,:] *= 1e-6

    dt = time.time()-lastcallTime
    log("SIMU Computed in %.2f"%dt, 3)
    return a.T
   



def getMJD():
    return time.time()/(24*3600)


def getScanDataShape(device):
    """ return the scan data dimention from pndcom

    Parameters
    ----------
    device : Device
        The device connection class 

    Outputs
    -------
    nData : int
        Number of window + Number of Telescope
    nOpl : int 
        numberof opl 
        
    Raises
    ------
    RuntimeError : if cannot proceed
    """ 
    reloadConfig()
    return simuConfig["N.TEL"]+simuConfig["N.SCI.WIN"]+simuConfig["N.DARK.WIN"], simuConfig["N.OPL"]
        



def getObcType():
    """ return the current OBC configuration 

    Parameters
    ----------
    None

    Outputs
    -------
    obc : string
        The OBC type as indicated in INS.OBC.TYPE

    Raises
    ------
    RuntimeError : if cannot proceed
    """ 
    return simuConfig["OBC"]    

def findMap(obc, nWin):
    """ from a obc name find a IOB mapping array 

    The list of IOB should be defined in config.mapLoockUp 

    Parameters
    ----------
    obc : string
        The OBC type as indicated in INS.OBC.TYPE
    nWin : int
        Number of windows (typicaly 12, 24 or 48)

    Outputs
    -------
    map : PndrsMappingArray  (defined in mapping.py)
        array containing the IOB mapping
    """
    try:
        return config.mapLoockUp[(obc,nWin)]
    except KeyError:
        return None


def dbRead(dbPoint):
    """ read inside the data base and return string result 

    Parameters
    ----------
    dbPoint : string
        defining the data base point (e.g. "pndrtdScope:track.newSNRmin")

    Outputs
    -------
    dbResult : string
        the untouch dbRead result

    Raises
    ------
    RuntimeError : if communication problem 
    """
    raise NotImplementedError('dbRead in simu mode')

def dbWrite(dbPoint, formatedValue):
    """ write inside the data base

    Parameters
    ----------
    dbPoint : string
        defining the data base point (e.g. "pndrtdScope:track.newSNRmin")
    formatedValue : string
        the value formated correctly into a string 
    
    Outputs
    -------
    None

    Raises
    ------
    RuntimeError : if communication problem 
    """
    raise NotImplementedError('dbWrite in simu mode')

_dbParserRe = re.compile("^([^ ]+) value = (.+)")
def parseDbValue(buffer, vtype=str):
    """ parse a data base output to get value 
            
    buffer is expected to be of the form e.g.:
        "DOUBLE value = 4.5"    

    Parameters
    ----------
    buffer : string
        has returned by dbRead(..)
    vtype : any, optional
        a function or type to return the value e.g. float, int, etc
        default is str

    Outputs
    -------
    vltType : string
        VLT value type e.g. "INT32", "LOGICAL", "DOUBLE", etc ...
    value : string
        the value associated, not converted
    
    Raises
    ------
    RuntimeError : if cannot parse           
    """    
    m = _dbParserRe.match(buffer.strip())
    if not m:       
        raise RuntimeError("cannot parse value from dbBuffer %r"%buffer)    
    vltType, svalue = m.groups()    
    try:
        value = vtype(svalue)
    except (TypeError, ValueError):
        raise RuntimeError("cannot convert value from dbBuffer %r into a %r"%(buffer, vtype))

    return vltType, value           


def getDlConfig(beamNumber):
    """ Return the Delay Line number of a given beam 

    *Warning* beam number start from 0 
    
    Parameters
    ----------
    baeamNumber : int
        the beam number, first one being 0 !

    Outputs 
    -------
    dlNumber : int
        the delay line number 1,2,3,4,5 or 6 (7,8 maybe one day! )  
    
    Raises
    ------
    RuntimeError : if communication problem 

    """
    return simuConfig["NS.DL"][beamNumber]



def getDlPos(beamNumber):
    """ Return the Delay Line position of a given beam 

    *Warning* beam number start from 0 
    
    Parameters
    ----------
    baeamNumber : int
        the beam number, first one being 0 !

    Outputs 
    -------
    pos : float
        delay line position in meter  
    
    Raises
    ------
    RuntimeError : if communication problem 

    """
    return simConfig["POS.DL"][beamNumber]


def setDlPos(beamNumber, pos):
    """ setthe VLTI Delay Line position

    *Warning* beam number start from 0 
    
    Parameters
    ----------
    baeamNumber : int
        the beam number, first one being 0 !
    pos : float
        position in meter    

   
    Raises
    ------
    RuntimeError : if communication problem 

    """
    simConfig["POS.DL"][beamNumber] = pos

def getDlsConfig():
    """ Return all the 4 Delay Line numbers for the current config
    
    Parameters
    ----------
    None

    Outputs 
    -------
    dlNumbers : list of int
        the delay line numbers 

    Raises
    ------
    RuntimeError : if communication problem         
    """
    return [getDlConfig(beam) for beam in range(4)]


quitFlag = False
def getQuitFlag():
    """ return the quit flag 
    
    Outputs
    -------
    test : bool
        True if rtdscope need to be quit

    Raises
    ------
    RuntimeError : if communication problem 
    """    
    return simuConfig["FLAG.QUIT"]

def clearQuitFlag():
    """ clear the quit flag in dBase

    Outputs
    -------
    None
    
    Raises
    ------
    RuntimeError : if communication problem 
    """
    simuConfig["FLAG.QUIT"] = False


saveDataOffset = False
def getSaveDataOffsetFlag():
    return saveDataOffset

def clearSaveDataOffsetFlag():
    global saveDataOffset 
    saveDataOffset = False 

def sendSaveDataOffsetFlag():
    """ turn onthe flag for saving data offset (background)

    Outputs
    -------
    None      
    """
    global saveDataOffset 
    saveDataOffset = True 

substractDataOffset = False
def getSubstractDataOffsetFlag():
    return substractDataOffset

def setSubstractDataOffsetFlag(val):
    global substractDataOffset 
    substractDataOffset = bool(val)     


def getSnrMin():
    """ Read the database to get the SNR min defined by operator 

    Outputs
    -------
    snrMin : float
        SNR min defined by operator
    """
    return simuConfig["SNR.MIN"]

def setSnrMin(_snrMin):
    """ set the snrMin in dBase for pannel feedback
    
    Parameters
    ----------
    snrMin : float
        snrMin for tracking
    
    Outputs
    -------
    None
    
    Raises
    ------
    RuntimeError : if communication problem 
    """
    
    simuConfig["SNR.MIN"] = _snrMin   



def getSnr(tel):
    """ Read the database to get the SNR of a given telescope
    
    Parameters
    ----------
    tel : int
        The telescope number starting from 0

    Outputs
    -------
    snr : float
        SNR min defined by operator
    """
    
    return simuConfig["SNRS"][tel]



def setSnr(tel, snr):
    """ set the snr in dBase for a given telescope
    
    Parameters
    ----------
    tel : int
        The telescope number starting from 0
    snr : float
        SNR value for that telescope

    Outputs
    -------
    None
    
    Raises
    ------
    RuntimeError : if communication problem 
    """
    simuConfig["SNRS"] = snr


def getTrackingFlag():
    """ return the tracking Flag 

    Outputs
    -------
    trackingFlag : bool
        if True offset are sent to delay line if asked (dataCom)
        if False dataCom.sendOffet will have no effect 
    """
    return simuConfig["FLAG.TRACKING"]

def setTrackingFlag(flag):
    """ set the trackingFlag 

    Parameters
    ----------
    trackingFlag : bool
        if True offset are sent to delay line if asked (dataCom)
        if False dataCom.sendOffet will have no effect     
    """
    simuConfig["FLAG.TRACKING"] = bool(int(flag))

   
def getScopeFlag():
    """ return the scope Flag 

    Outputs
    -------
    scopeFlag : bool
        if True a gui visual rtdscope is asked        
    """
    return simuConfig["FLAG.SCOPE"]

def setScopeFlag(flag):
    """ set the scopeFlag 

    Parameters
    ----------
    scopeFlag : bool
        if True a gui vidual rtdscope is asked                    
    """
    simuConfig["FLAG.SCOPE"] =  bool(int(flag)) # int in case is a string    


def sendDifferentialPhase(phases):
    pass
    #simConfig["PHASES.DIFF"] = list(phases)

    
def sendOffsets(device, offsets, timeout=1000):
    """ send the DL offset to data base and Delay Lines 
    
    Parameters
    ----------
    device : pndcom.Device
        the opened connection 
    offsets : array like (nTel,)
        offset for each telescope **In micron** !!!
    timeout : int, optional
        timeout in milisec      
    """
    return         


def sendQuitFlag():
    """ Send a quit flag for any loop running that will check getQuitFlag() """
    simuConfig["FLAG.QUIT"] = True

def getQuitFlag():    
    """ Return the quit flag """
    return simuConfig["FLAG.QUIT"]


plotFocusList = ["COMBINED", "RAW", "NIOBATE"]
def setPlotFocus(pt):
    """ Change the plot focus 

    plot focus can be red by the rtd plot running

    Parameters
    ----------
    focus : string
        one of "filtered", "raw" or  "niobate"        
    """    
    if pt not in [None]+plotFocusList:
        return None
    simuConfig["PLOT.FOCUS"] = pt

def getPlotFocus():
    """ return the curent plot focus 

    Outputs
    -------
    focus : string
        one of "filtered", "raw" or  "niobate" 
    """
    return simuConfig["PLOT.FOCUS"]



