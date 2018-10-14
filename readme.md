# Pndrtdscope

On PIONIER the rtdscope aims to make a quick and live reduction of fringes for
 the following purposes :

- Show reduced fringes and and fringe Power Spetral Density (PSD) fo the operator to juge presence and quality of fringes.
- Compute the optical path difference (OPD) between baseline and send offset to each PIONIER internal delay-lines
- Provide live plot for allignement purpose like for the Niobate plates alignment.

The RtdScope was originaly written in Yorick and was ported in python for maintenance and portablility reasons.

## python modules

The rtdscope is writen in python 2.7 however should work with 3.0 version but not tested. It use standard module present in the VLTI-2016 software with the exception of one, `tkinter`, used to make panels.

Remarkable moduls:

- numpy
- matplotlib 
- or threading, multiprocessing
- Tkinter or tkinter

All other are standards

## Structure of the code 

The code is divied in several parts :

pndcom
: is a compiled wrapper arround pndcom.c of low level functions to talk with PIONIER

rtdplots
: directory, submodule containing plots initialization and updating. One file
per plot type.

com.py
:    high level function for communication with Pionier message send and data base read and write. ex, `getQuitFlag`, `getDlConfig`, `dbRead`, `getSnrMin` etc....


comsimu.py
:    has the same function than com.py but for offline simulation

computing.py
:    handle all the main computations (FFT, matrix inversions, compute OpD)

config.py
:    configure the pndrtscope. 

datacom.py
:    The main class `DataCommunication` is writen there. Describde bellow.

mapping.py
:    Define a small class and constants to define the mapping of the IOBC

pannels.py
:    All Tk objects for the rtdscope pannel (excep plots) are defined here.


### `datacom.py` DataCommunication

The idea is that for each scan the data handling are made inside the  `DataCommunication` object instance. Each functions are executed sequancialy and return update data products. A client process can be aboned to the `DataCommunication` object and ask (and wait) results of a specific computation on the scan. For instance to plot fringes the DataCommunication insatnce need to get the data, prepare the data, combine fringes, filters them etc ...

In this context one can have a process of DataCommunication running for the tracking executed for each scan and a more time consuming plot process which will be executed when possible. Then the plotting speed will not have influences on the instrument performances.

Process can turn of specific `recipies` to be executed on the `DataCommunication` instance :

'getdata'
:   get and prepare the data but raise exception if failure

'getdatasafe'
:   get and prepare the data If failed (e.g. communication problems)
wait a few for next scan

'track'
:   execute all function to compute the fringes position and track fringes by sending OPD offset to PIONIER internal DLs

'filter'
:   do everything to plot filtered data 

'filterPsd'
:   do everything to be abble to plot filteredPsd

'flux'      
:   run everything to get the flux per telescope
            
'snr'
:   run everything to get the tracking snr per telescope
            
'raw'
:   run everything to plot the raw data

'niobate'
:   run to plot niobate fringes and send differential phase
 

Each input and output of DataCommunication are writen in 3 differents dictionary. `.config` that contains the instrument configuration `.data` contains raw data and computed data all is erazed after each scan and `permanentData`  which contains all other data that are persistant over several scan (like counter). See the header of `datacom.py` for an overview of parameters.



