import numpy as np
##
# import some constant 
from .mapping import WIN, T1, T2, BASE, PHI, POL, VIS
from . import config

## for python3
try:
    unicode
except NameError:
    basestring = (str,bytes)

WIDIM = 0
OPDIM = 1


def computeDataCmd(data, opd, map, which=slice(0,None)):
    """ compute and return the combined data 

    Parameters
    ----------
    
    data : array
        the data of shape (nWin, nopd)
    opd : array 
        array of opd value     
    map : PndrsMappingArray or recarray
        of dimension nWin
    
    Outputs
    -------
    opdCmb : array 
          combined opd (reversed if in the other way)
    dataCmb : array 
          combined data of shape (nBase, nOpd)
    """
    s1 = np.zeros( (3,), dtype=float)
    s2 = np.zeros( (3,), dtype=float)
    
    if map is None:
        raise RuntimeError("map is None, cannot combine data")
    
    nBase = np.max(map[BASE])
    nRead = data.shape[OPDIM] 
    dataCmb = np.ndarray( (nBase,nRead), dtype=np.complex )
    opdCmb  = np.ndarray( (nBase,nRead), dtype=float )

    ## Build the combined data
    for baseIndex, base in enumerate(range(1,nBase+1)):
        id = np.where(map[BASE]==base)[0][which]
        

        dx = opd[ map[id[0]][T2]-1 ] - opd[ map[id[0]][T1]-1 ]
        
        if dx[1]>dx[0]:
            order = slice(0,None,1)
        else:
            order = slice(-1,None,-1)
            
        # yorick ( data(order,id) * (map(id).vis * exp(1.i*map(id).phi))(-,) )(,sum);
            
        v = 0.0
        for i in id:
            v +=  data[i,order] * (map[i][VIS] * np.exp( 1j*map[i][PHI] ))        
        dataCmb[baseIndex,:] = v
        opdCmb[baseIndex,:]  = dx[order]
            
    return dataCmb, opdCmb



def computeDataFFT(data, opd=None, inverse=False):
    """" Compute the FFT of data 

    Parameters
    ----------    
    data : array
        the prepared data of shape (nWin, nopd) 
        or the combined data of shape (nBase, nOpd)
    opd : array 
        array of opd value     
    inverse : bool, optional
        If True compute the backward fft 

    Outputs
    -------
    fftCmb : array
        The fft array along opddimention
    sigCmd : array 
        the sigma array *IF* opd is given 
    """
        
    nRead = data.shape[OPDIM]
    
    if inverse:
        fft = np.fft.ifftn
    else:
        fft = np.fft.fftn    
    
    fftCmb = fft(data, axes=[OPDIM]) / np.sqrt(nRead)

    if opd is None:
        return fftCmb

    dxs = opd[:,-2] - opd[:,-3]
    
    v = np.linspace(0,1,nRead)
    sigCmb = np.array([v/dx for dx in dxs])

    return fftCmb, sigCmb



def scaleFilter(fre, flt):
    """ Scale the filter according to scaning frequencies
    
    small frequencies will
    have broader filter so that turbulent fringes are in.
    
    Parameters
    ----------
    fre : array 
        Spectral frequencies 
    flt : array like 
         start,end of the filter        
    """
    turbulenceStrength = config.defaults["STRENGTH.TURBULENCE"]

    power = np.abs(fre)[:,-1]/np.abs(fre)[:,-1].min() -1

    norm = np.array([-1,+1])
    newFlt = np.ndarray( (power.size,2), dtype=float )
    freMax = np.max(np.abs(fre))

    for i,p in enumerate(power):
        newFlt[i] = flt* (1+turbulenceStrength*norm)**p
        newFlt[i,0] = max(newFlt[i,0], 0.0)
        newFlt[i,1] = max(newFlt[i,1], 0.0)
        newFlt[i,0] = min(newFlt[i,0], freMax)
        newFlt[i,1] = min(newFlt[i,1], freMax)
    return newFlt


def computeOpdIota(ft, fre, fltIn=None, 
                            fltOut=None, 
                            psdBuffer=None, 
                            psdBufferId=0
                   ):
    """ 
    Compute the fringe position with the IOTA method.
    Position is returned in units of 1./fre, with 0 beeing the
    center of the scan.
    
    The SNR is computed as the ratio between the averaged power
    in fltIn and in fltOut. Filters are given is units of fre.

    The psd is computed and stored in the in/out psdBuffer array 


    Parameters
    ----------    
    ft: array (nBase, nOpd)
         Fourier Transform
    fre: array (nOpd,)
        Spectral frequencies
    fltIn: array (2,) 
        start/end of the filter where the signal should be.
        default is config.filterIn
    fltOut: array (2,)
        start/end of the filter without signal.
        default is config.filterOut
    psdBuffer : None or array (config["SIZE.PSD.BUFFER"], nBase, nOpd)
        buffer where to save psd.
        If None it will be constructed 
    psdBufferId : int
        Id of the current psd in buffer.
        The computed psd will be stored in (psdBufferId+1)%config["SIZE.PSD.BUFFER"]
    
    Outputs:
    --------
    posIota : array (nBase,)
            The piston value for each base
    snrIota : array (nBase,)
        The SNR for the piston computation 
    snrMean : array (nBase,)
        The SNR computed from the PSD buffer ring 
        The number of ellements 
    psdBuffer : array (config.psdBufferSize, nBase, nOpd)
        The updated buffer for PSD computation            
    psdBufferId : int
        buffer array index of the current psd  
    filterInRescaled : array (nbase,2)
        The filter rescaled for each base

    """
    #ndrtdGetOpdIota,  fftCmb, sigCmb, filterIn, filterOut, posIota, snrIota, snrLast;

    psdBufferSize = config.defaults["SIZE.PSD.BUFFER"]

    fltIn = config.defaults["FILTER.IN"] if fltIn is None else fltIn
    fltOut = config.defaults["FILTER.OUT"] if fltOut is None else fltOut

    fltIn  = scaleFilter(fre, fltIn  )
    fltOut = scaleFilter(fre, fltOut )

    #/* build the filter as 0,1 mask */
    maskIn  = np.array([ (abs(f)>fi[0]) & (abs(f)<fi[1]) for\
                         f,fi in zip(fre,fltIn)])
    maskOut = np.array([ (abs(f)>fo[0]) & (abs(f)<fo[1]) & (~mi) for\
                         f,fo,mi in zip(fre,fltOut,maskIn) ])

    # filter fft 
    fftIn = ft*maskIn
    # compute psd
    psd = np.abs(ft)**2.0

    #  /* Piston with the IOTA method (validated) */
    df = fre[:,-2] - fre[:,-3]
    #YOrick pha = -(fftIn(1:-1,) * conj(fftIn(2:0,)))(sum,);
    pha = -( fftIn[:,0:-1] * np.conj(fftIn[:,1:])).sum(axis=1)

    # create the buffer if new or if the buffer does not have the
    # right size 
    if (psdBuffer is None) or (psdBuffer.shape[1:]!=psd.shape ):
        psdBuffer = np.zeros( (psdBufferSize,)+psd.shape, psd.dtype )
        psdBufferId = -1
        newBuffer = True
    else:
        newBuffer = False

    psdBufferId += 1

    psdBuffer[psdBufferId%psdBufferSize] = psd

    meanPsd = psd if newBuffer else psdBuffer.mean(axis=0) 

    noise = (meanPsd*maskOut).sum(axis=1) * maskIn.sum(axis=1) / (maskOut.sum(axis=1) + 1e-10)

    # Convert phasor in piston
    pos = np.array([ (np.arctan2(ph.imag, ph.real) / (2.*np.pi *d)) for ph,d in zip(pha,df)])
    #pos = np.arctan(pha.imag, pha.real) / (2.*np.pi * df[None].T)

    snr = (psd*maskIn).sum(axis=1) / noise
    snrMean = (meanPsd*maskIn).sum(axis=1) / noise

    return pos, snr, snrMean, psdBuffer, psdBufferId, fltIn



def computeFiltered(ft, fre, filter):
    """ Compute the filtered data from fourier transformed data 

    Parameters
    ----------
    ft : array (?,nOpd)
        Fourier transform
    fre : array (?,nOpd)
        spacial frequencies
    filter : string or 2 array         
        "wide", "all", of [start,end] array 

    Outputs
    -------
    dataFiltered : array (?,nOpd)
        Filtered Data 
    opdFiltered : array (?,nOpd)
        opd filtered
    """
    nW, nRead = ft.shape

    # compute the sigma array 
    df = fre[:,1] - fre[:,0]
    l = np.linspace(-0.5, 0.5, nRead)
    opdFiltered = np.array([l/d for d in df])

    if isinstance(filter, basestring):
        if filter == "wide":
            mm = np.abs(fre).max(axis=1)
            mask = np.array([(np.abs(fr) > (0.05*m)) & (np.abs(fr) < (0.45*m)) for fr,m in zip(fre,mm)])
        elif  filter == "all":
            mask = 1.0
        else:
            raise ValueError("Unknown Filter %r"%filter)    
    else:
        filter = scaleFilter(fre, filter)
        mask = np.array([ (np.abs(fr) > fl[0]) & (np.abs(fr)<fl[1]) for fr,fl in zip(fre,filter) ])                        

    # now filter
    fftFilter = ft * mask
    dataFiltered = np.fft.ifftn( fftFilter, axes=[1]) / np.sqrt(nRead)
    return dataFiltered, opdFiltered


def computeOplMatrix(pos, snr, mapc, snrMin=2.0, niobate=False):
    """ Compute the SNR and the DL offset
    
    Compute the SNR and the DL offset for the 4 DLs based on the
    6 opd pos computed for each baseline. 
    
    If niobate=True, the computation is done for
    the differential phases

    Parameters
    ----------
    pos : array (nBase,)
        fringe (piston) position for each bases
    snr : array (nBase,)
        computed SNR for each base
    mapc : PndrsMappingArray or recarray (nBase,)
        Must have unique base number 
    snrMin : float
        the snr treshold         
    niobate : bool
        True is niobate are used 
    
    Ouputs
    ------
    posTel : array (nTel,)
        piston position per telescope
    snrTel : array (nTel,)
        The SNR for each telescope
    pos2 : array (nBase,)
        The recomputed position for each base  
    trackingStatus : array (nBase,) of boolean 
        True for telescope tracking               
    """

    ##
    # init some value and array 
    nTel = max( np.max(mapc[T1]),  np.max(mapc[T2]) )
    snrTel = np.zeros( (nTel,), dtype=float)
    posTel = np.asmatrix(np.zeros( (nTel,), dtype=float))
    trackingStatus = np.zeros( (nTel,), dtype=bool)

    nBase  = np.max(mapc[BASE])
    nBaseTotal = nBase
    # /* If Niobate, we use the matrix of one polar */
    if niobate: 
        nBase = nBaseTotal // 2
    
    # init the matrix
    # Add one component for the pivot in bases
    # matrix = np.zeros( (nTel, nBase), float)

    M = np.zeros( (nTel, nBase+1), float)
    for i in range(nBase):
        M[ mapc[i][T1]-1,i ] = +1
        M[ mapc[i][T2]-1,i ] = -1
    ##
    # M is a matrix     
    M = np.asmatrix(M)    
    #/* Don't use baseline bellow a SNR threshold */
    snr = snr * (snr>snrMin) + 1e-10

    # add componant for the pivot

    snr  = np.concatenate( (snr,[np.max(snr)]) )
    pos  = np.concatenate( (pos, [0.0]) )
    snrU = np.identity(nBase+1) * snr.repeat(nBase+1).reshape((nBase+1,nBase+1))
    ##
    # snrU is a matrix 
    snrU = np.asmatrix(snrU)

    Pos = np.asmatrix(pos).T

    nTelTracked = 0
    #  Loop on the telescopes to solve the system with
    #  different pivot telescopes
    trueSnrTel =  snrTel
    for pivot in range(nTel):
        M[:,-1] = 0.0
        M[pivot,-1] = 1.0

        Mt = M * snrU
        
        try:
            One = np.linalg.inv(Mt * M.T)
        except np.linalg.LinAlgError as e:
            ## this happen when the matrix is singular 
            ## just continue
            #raise RuntimeError("Ssssssssssssssingular %s"%e)
            continue 

        Two = Mt * Pos

        #/* Result and associated SNR */
        posTelP = (One * Two).T;
        #I = np.asmatrix(np.identity(nTel)) 
        #snrTelP = 1.0/((One*I).sum(axis=1))
        snrTelP = 1.0/One.diagonal()
        
        #snrTelP = np.asarray(snrTelP).squeeze()
        #posTelP = np.asarray(posTelP).squeeze()

        #/* Clip the wrong one */
        #test = snrTelP>snrMin
        #snrTelP *= np.asarray(test).squeeze()#0.0
        trueSnrTelP = snrTelP.copy()
        test = snrTelP<=snrMin
        snrTelP[test] = 0.0
        posTelP[test] = 0.0 #*= test#0.0

        

        #/* Compute the number of traked telescopes */
        nTelTracked  = (snrTel>snrMin).sum()
        nTelTrackedP = (snrTelP>snrMin).sum()

        #/* Check if the estimate with the current pivot
        #   is better than previous */
        if (nTelTrackedP>nTelTracked) or\
              ((nTelTrackedP==nTelTracked) and\
               (snrTelP.mean()>snrTel.mean())):
            snrTel = snrTelP
            posTel = posTelP
            trueSnrTel = trueSnrTelP 
            nTelTracked = nTelTrackedP             
            trackingStatus = np.asarray(snrTelP>0.0).squeeze()
        #/* If all telescopes are tracked, just break now */
        if niobate and nTelTracked == nTel:
            break

        

    #/* If only one telescope has high SNR (the pivot),
    #   this means none is OK */
    if nTelTracked<2:
        snrTel[...] = 0.0;
        posTel[...] = 0.0;
        trackingStatus[...] = False
    #posTel[...]= np.asarray(posTel).T* (trackingStatus)


    #/* Recompute each base */ 
    
    pos2 = M[:,0:nBase].T * posTel.T

    ## return the matrix as array to avoid confusion
    return (np.asarray(posTel).squeeze(),
            np.asarray(trueSnrTel).squeeze(),
            np.asarray(pos2).squeeze(), 
            trackingStatus
        )

def computeFluxPerTelescope(data, map):
    """ from data and a map return the flux per telescope

    Parameters
    ----------
    data : array (nBase, nOpd)
        scan per base
    map : PndrsMappingArray or recarray (nBase,)
        the IOBC mapping array

    Outputs
    -------
    flux :  array (nTel,)
        flux for each telescope        
    """
    nBase = np.max(map[BASE])
    nTel = max(np.max(map[T1]), np.max(map[T2]))
    pairFlux = np.zeros( (nBase,), dtype=float)
    bases = np.zeros( (nTel,nBase), dtype=float)

    for baseIndex in range(nBase):
        id = np.where(map[BASE]==(baseIndex+1))[0]
        pairFlux[baseIndex] = (data[id,:].mean(axis=1)).sum()
        bases[map[id[0]][T1]-1, baseIndex] = 1.0
        bases[map[id[0]][T2]-1, baseIndex] = 1.0

    ##
    # preform the linear regression 
    flux,_,_,_ = np.linalg.lstsq(bases.T, pairFlux)
    return flux

def computeDifferentialPhase(data, mapc):
        """ compute the differential phase per telescope 

        Parameters
        ----------
        data : array (nBase, nOpd)
        mapc : PndrsMappingArray or recarray (nBase,)
            Must have unique base number 
        
        Ouputs
        ------
        polPhasesTel : array (nTel,)
            Phases per telescope (in degree)
        """
        idUp = np.where(mapc.pol=="U")[0];
        idDo = np.where(mapc.pol=="D")[0];

        ## keep only the center of packet         
        tmp = data * (np.abs(data) > 0.75)

        tmp = (tmp[idDo,:] * np.conj( tmp[idUp,:] )).sum(axis=1)
        polPhases = np.arctan2(tmp.imag, tmp.real) *180./np.pi

        polPhasesTel, _, _,_ = computeOplMatrix( 
                                    polPhases, 
                                    polPhases*0.0+100.0, #same weight to all baseline
                                    mapc, 
                                    niobate=1)
        return polPhasesTel




