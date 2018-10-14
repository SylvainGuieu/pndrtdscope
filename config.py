from .mapping import WIN, T1, T2, BASE, PHI, POL, VIS, PndrsMappingArray
import numpy as np
pi = np.pi 

###################################################
#
#   The 4-ABCD-H IONIC component on PIONIER 
#
####################################################

####
# 
# Input order 
#	  WIN winow number starting from 1
#     |   T1 tel1 number starting from 1
#     |   |  T2 tel2 number starting from 1
#     |   |  |  BASE base number starting from 1
#     |   |  |  |   POL polarisation string must be "N", "U" or "D"
#     |   |  |  |   |   PHI  phase 
#     |   |  |  |   |   |    VIS visibility (not used)
#     |   |  |  |   |   |    |
#    (1,  1, 2, 1, "N", 0.0, 1.0)
mapABCD_H = PndrsMappingArray(
	[(1,  1, 2, 1, "N",  0.0*pi, 1.0),
	 (2,  1, 2, 1, "N",  1.0*pi, 1.0), 
	 (3,  1, 2, 1, "N",  1.6*pi, 1.0), 
	 (4,  1, 2, 1, "N",  0.6*pi, 1.0),
	 (5,  2, 3, 2, "N",  0.0*pi, 1.0),
	 (6,  2, 3, 2, "N",  1.0*pi, 1.0), 
	 (7,  1, 3, 3, "N",  0.0*pi, 1.0),
	 (8,  1, 3, 3, "N",  1.0*pi, 1.0),
	 (9,  1, 3, 3, "N",  1.6*pi, 1.0),
	 (10, 1, 3, 3, "N",  0.6*pi, 1.0),
	 (11, 1, 4, 4, "N",  0.0*pi, 1.0),
	 (12, 1, 4, 4, "N",  1.0*pi, 1.0),
	 (13, 1, 4, 4, "N", 1.83*pi, 1.0),
	 (14, 1, 4, 4, "N", 0.83*pi, 1.0), 
	 (15, 2, 4, 5, "N",  0.0*pi, 1.0),
	 (16, 2, 4, 5, "N",  1.0*pi, 1.0),
	 (17, 2, 4, 5, "N",  1.6*pi, 1.0),
	 (18, 2, 4, 5, "N",  0.6*pi, 1.0),
	 (19, 2, 3, 2, "N",  1.6*pi, 1.0),
	 (20, 2, 3, 2, "N",  0.6*pi, 1.0), 
	 (21, 3, 4, 6, "N",  0.0*pi, 1.0),
	 (22, 3, 4, 6, "N",  1.0*pi, 1.0), 
	 (23, 3, 4, 6, "N",  1.6*pi, 1.0), 
	 (24, 3, 4, 6, "N",  0.6*pi, 1.0)
	]
)

###################################################
#
#      The 4-ABCD-H IONIC component on PIONIER 
#   ***********   WITH Wollaston  *************
#
####################################################


mapABCD_Hpol = PndrsMappingArray(list(mapABCD_H)+list(mapABCD_H))
mapABCD_Hpol[POL][0:24] = "D"
mapABCD_Hpol[POL][24:]  = "U"
mapABCD_Hpol[BASE][24:] +=  6
mapABCD_Hpol[WIN][24:]  +=  24


###################################################
#
#  Put all the IOB map array inside a loockup 
#  The loockup keys is a tuple
#  (obcType, nOutput)
# where obcType is the INS.OBC.TYPE
# and nOuput is the total number of output
####################################################

mapLoockUp = {
	("4T-ABCD-H", 24) : mapABCD_H, 
	("4T-ABCD-H", 48) : mapABCD_Hpol
}


###############################################
#
#  Time Out for communication sendCommand 
#
###############################################
# 60 seconds
pndcomTimeout = int(60000)

#######################################
# /* Filters in m-1 */
#
#
filterH  = np.array([0.515,0.756])
filterHl = np.array([0.45,0.75])
filterHw = np.array([0.3,0.9])

filterLoockUp = {
	"H"  : filterH, 
	"Hl" : filterHl,
	"Hw" : filterHw
}




###############################################
#
#  Put in defaults all parameters  
#
###############################################


defaults = {

	###############################################
	#
	#  Signal Processing confgurations 
	#
	###############################################


	##
	# Simulation mode for debug and development pupose
	"SIMU.MODE": False,

	##
	# The filters  min/max value in wave number 
	"FILTER.IN"  : filterH ,
	"FILTER.OUT" : filterHw,

	##
	# The SNR min for tracking  
	"SNR.MIN"    : 2.0,
	"STRENGTH.TURBULENCE"    : 0.13, 
	##
	# Substract the dark windows to raw data
	# should be True in Normal operation 
	"TEST.SUBSTRACT.DARKWIN" : True, 
	##
	# Number of telescope used 
	"N.TEL" : 4,
	##
	# Number of value to clean at begining of a scan 
	"N.FIRST.SCAN.TO.CLEAN": 3, 

	##
	# Compute or not the oversmapling factor 
	# Oversampling factor will be 1 if False
	"TEST.COMPUTE.OVERSAMP.FACTOR": False,
	##
	# Process the oversampling when filtering fringes
	"TEST.PROCESS.OVERSAMP": True, 

	##
	# the size of the ring buffer that record the last N PSD for 
	# smooth plot purpose 
	"SIZE.PSD.BUFFER": 10, 


	###############################################
	#
	#  Configuration for plot and Tk Pannel 
	#
	###############################################

	##
	# The small panel used to manage tracking and rtdscope
	"PANEL.MANAGER.GEOMETRY": "300x100",

	##
	# The RTDSCOPE Panel size 
	"PANEL.RTDSCOPE.SIZE": (1200, 700), #(1300,1000) 

	##
	# the RTDSCOPE panel background color 
	"PANEL.RTDSCOPE.BACKGROUND": "white",

	##
	# The width/height size proportion of the figure  
	# This is expressed as fraction of PANEL.RTDSCOPE.SIZE 
	"PANEL.RTDSCOPE.FIG.SIZE.RATIO": (0.42, 0.85), 

	##
	# The width/height size proportion of the mini figure
	# located on the side of the panel (the Flux,SNR, ... meters)  
	# This is expressed as fraction of PANEL.RTDSCOPE.SIZE 
	"PANEL.RTDSCOPE.MINIFIG.SIZE.RATIO": (0.10, 0.2), 

	##
	# background color of the RTDSCOPE figures
	"PANEL.RTDSCOPE.FIG.FACECOLOR": "white",
	"PANEL.RTDSCOPE.MINIFIG.FACECOLOR": "white"
}


####
# Try to include a local configuration file
# and update the configuration parameters with 
# the new ones 
try:
	import pndrtdscope_config as localconf
except Exception as e:
	pass
else:
	if hasattr(localconf, "defaults"):
		defaults.update(localconf.defaults)

