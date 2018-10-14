import numpy as np

WIN, T1, T2, BASE, PHI, POL, VIS = "win", "t1", "t2", "base", "phi", "pol", "vis"


pndrsMappingDtype = [
					 (WIN, "int16"), # window number (starting from 1)
					 (T1, "int16"), # telescope number for channel 1
					 (T2, "int16"), # telescope number for channel 2
					 (BASE, "int16"), # base index number 
					 (POL, "U1"), # Polarimetry string 'D' for down, 'U'for up 'N' for natural
					 (PHI, "float64"),
                                         (VIS, "float")
					]

class PndrsMappingArray(np.recarray):	
	def __new__(subtype, data):
		obj = np.array(data, dtype=pndrsMappingDtype).view(subtype)
		return obj
	def __array_finalize__(self, obj):
		pass		
		


