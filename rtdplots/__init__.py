""" This module provide the matplotlib plots for the RTD scope 

All plots are stored in the dictionary `plotLoockup`

The plots are defined has follow: 
	
COMBINED.FRINGES:  The combined and filtered  fringes 
COMBINED.PSD    :  The combined and filtered PSD
METER.FLUX      :  The meter bars that gives the Flux per telescope 
METER.SNR       :  The meter bars that gives the SNR per telescope  
RAW.FRINGES     :  The raw fringes (24 or 48 plots)
RAW.PSD         :  The raw fringe psd (24 or 48 plots)
METER.PHASEDIFF :  The meter bars that gives the phase difference 
                    (when wollaston is on)
NIOBATE.ZOOM.IN :  The white normalized fringes for each polarizations 
NIOBATE.ZOOM.OUT:  The normalized fringes for each polarizations 
                     and the envelops	

"""


from .meters import RtdTelSnrFigure, RtdTelFluxFigure
from .psd import RtdCombinedFringesPsdFigure
from .fringes import RtdCombinedFringesFigure
from .rawfringes import RtdRawFringesFigure
from .rawfft import RtdRawFFTFigure
from .phasediff import RtdPhaseDiffFigure, RtdPhaseDiff2Figure, RtdPhaseDiffMeterFigure

import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 0.8
from matplotlib.pylab import plt

plotLoockup = {	
	"COMBINED.FRINGES": RtdCombinedFringesFigure, 
	"COMBINED.PSD"    : RtdCombinedFringesPsdFigure, 
	"METER.FLUX"      : RtdTelFluxFigure, 
	"METER.SNR"       : RtdTelSnrFigure, 
	"RAW.FRINGES"     : RtdRawFringesFigure, 
	"RAW.PSD"         :  RtdRawFFTFigure, 
	"METER.PHASEDIFF" : RtdPhaseDiffMeterFigure, 
	"NIOBATE.ZOOM.IN" : RtdPhaseDiffFigure, 
	"NIOBATE.ZOOM.OUT": RtdPhaseDiff2Figure
}