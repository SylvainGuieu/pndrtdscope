""" contain function to talk with the instrument via pndcom
or via data base.


Some function are juste use internaly, with python variable, 
but they are here for future implementation. 

"""
from  subprocess import Popen, PIPE
import re
from . import config

from . import pndcom
from .pndcom import openCom, isOpen, sendCommand, receiveData, getMJD, log
VERBOSE = 1


##############
##  Some of the capabilities has so far no physical connection with 
##  PIONIER because database or capabilities are missing 
##  However they are still here for future integration 
##  The values are stored in the loockup table bellow 

loockup = {
    "POS.DL": [0]*10, # delay lines position in meter 
    "SNRS"  : [0]*10, # SNR of each telescopes 
    "FLAG.TRACKING" : True, # flag for on/off tracking
    "FLAG.SCOPE" : True,    # flag for the scope working
    "PLOT.FOCUS" : "COMBINED" # whish plot must be in focus 
}


def getScanDataShape(device):
    """ return the scan data dimention from pndcom

    Parameters
    ----------
    device : Device
        The device connection class 

    Outputs
    -------
    nData : int
        Number of window +  Number of Telescope
    nOpl : int 
        numberof opl 
        
    Raises
    ------
    RuntimeError : if cannot proceed
    """ 
    try:
        replies = sendCommand(device,"GETDATA","SCAN_DATA")
    except RuntimeError as e:             
        raise RuntimeError("Data Error: %s"%e) 

    if len(replies)<1:            
        raise RuntimeError("Data Error: reply list is empty")
    
    ## get the nData, nOpl values in integer 
    nData, nOpl = (int(s) for s in replies[0].split(" ") if s.strip())
    return nData, nOpl





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
    p = Popen("icbConfigGet PIONIER INS.OBC.TYPE", shell=True, stdout=PIPE, stderr=PIPE)
    status = p.wait() # wait to be finished and return status
    
    if status:
        raise RuntimeError("Cannot get the OBC type")
    
    obc = p.stdout.read()
    obc = obc.strip(" \t\n")
    return obc


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
    p = Popen("dbRead \"%s\""%dbPoint, shell=True, stdout=PIPE, stderr=PIPE)
    status = p.wait()
    if status:
        raise RuntimeError("dbRead retuned error %s"%status)
    return p.stdout.read()      

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
    p = Popen("dbWrite \"%s\" %s"%(dbPoint,formatedValue), shell=True, stdout=PIPE, stderr=PIPE)
    status = p.wait()
    if status:
        raise RuntimeError("dbWrite retuned error %s"%status)

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
    msg = "@wvgvlti:Appl_data:VLTI:isscfg:data:currentVLTI.isscfgARMS(%d,2)"%beamNumber
    try:
        out = dbRead(msg)
    except RuntimeError as e:
        raise RuntimeError("Cannot get Dl Configuration -> %s"%e)

    vtype, value = parseDbValue(out, int)
    return value


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
    return loockup['POS.DL'][beamNumber]


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
    loockup['POS.DL'][beamNumber] = pos    


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
    out = dbRead("<alias>pndrtdScope.quit")
    _, test = parseDbValue(out, bool)
    return test

def clearQuitFlag():
    """ clear the quit flag in dBase

    Outputs
    -------
    None
    
    Raises
    ------
    RuntimeError : if communication problem 
    """
    dbWrite("<alias>pndrtdScope.quit", 0)

saveDataOffset = False
def getSaveDataOffsetFlag():
    """ return the flag for saving data offset (background)
    
    Outputs
    -------
    test : bool
        True if it is needed to save the data 
    
    """
    return saveDataOffset

def clearSaveDataOffsetFlag():
    """ clear the flag for saving data offset (background)

    Outputs
    -------
    None      
    """
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
    """ get the flag for substracting data offset (background)
    
    Outputs
    -------
    test : bool
        True if it is offset (background) need to be substracted
    
    """
    return substractDataOffset

def setSubstractDataOffsetFlag(val):
    """ set the flag for substracting data offset (background)
    
    Parameters
    -------
    test : bool
        True if it is offset (background) need to be substracted    
    """
    global substractDataOffset 
    substractDataOffset = bool(val) 



def getSnrMin():
    """ Read the database to get the SNR min defined by operator 

    Outputs
    -------
    snrMin : float
        SNR min defined by operator
    """
    out = dbRead("<alias>pndrtdScope:track.SNRmin")
    _, snrMin = parseDbValue(out, float)
    return snrMin

def setSnrMin(snrMin):
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
    dbWrite("<alias>pndrtdScope:track.SNRmin", "%.3f"%snrMin)

snrs = [0]*10
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
    return loockup["SNRS"][tel]



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
    loockup["SNRS"][tel] = snr



def getTrackingFlag():
    """ return the tracking Flag 

    Outputs
    -------
    trackingFlag : bool
        if True offset are sent to delay line if asked (dataCom)
        if False dataCom.sendOffet will have no effect 
    """
    return loockup["FLAG.TRACKING"]

def setTrackingFlag(flag):
    """ set the trackingFlag 

    Parameters
    ----------
    trackingFlag : bool
        if True offset are sent to delay line if asked (dataCom)
        if False dataCom.sendOffet will have no effect     
    """    
    loockup["FLAG.TRACKING"] =  bool(int(flag)) # int in case is a string 
    



def getScopeFlag():
    """ return the scope Flag 

    Outputs
    -------
    scopeFlag : bool
        if True a gui visual rtdscope is asked        
    """
    return loockup["FLAG.SCOPE"]

def setScopeFlag(flag):
    """ set the scopeFlag 

    Parameters
    ----------
    scopeFlag : bool
        if True a gui vidual rtdscope is asked                    
    """    
    loockup["FLAG.SCOPE"] = bool(int(flag)) # int in case is a string 


def sendDifferentialPhase(phases):
    for i, phase in enumerate(phases):
        dbWrite("<alias>pndrtdScope:birefringence.diffPhase(%d)"%i, "%.1f"%phase)

    
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
            
    args = ["DET.TRK.DL%i.OPDREL %.7f"%(dl,offset*1e-6) for\
              dl,offset in enumerate(offsets,start=1)]
    
    # send to the data base 
    for i,offset in enumerate(offsets):
        dbWrite("<alias>pndrtdScope:track.relOpd(%d)"%i, "%.7f"%offset)
        
    reply = pndcom.sendCommand(device, "SETUP", " ".join(args), timeout)        
    return reply


quitFlag = False
def sendQuitFlag():
    """ Send a quit flag for any loop running that will check getQuitFlag() """
    global quitFlag
    quitFlag = True

def getQuitFlag():    
    """ Return the quit flag """
    global quitFlag
    return quitFlag

plotFocus = "COMBINED"
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
    loockup["PLOT.FOCUS"] = pt    

def getPlotFocus():
    """ return the curent plot focus 

    Outputs
    -------
    focus : string
        one of "filtered", "raw" or  "niobate" 
    """
    return loockup["PLOT.FOCUS"]






