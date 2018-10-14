
import numpy as np

from . import config
if config.defaults.get("SIMU.MODE", False):
    from . import comsimu as com 
else:
    from . import com

""" 
data parameters 
---------------
All the following parameters are deleted when a new scan arrive.  

|   Param   | constructor | Alterator | comment |
|-----------|-------------|-----------|---------|
| POSITIONS | getPos      |           | (N.TEL) |
|           |             |           |         |
"""
class DlCommunication(object):
    def __init__(self, map):
        
        self.config = config.defaults.copy()
        NTEL = config.get("N.TEL", 4)
        self.config.update(
            {
                "STEP.SEARCH": 200 
            }
        )
        self.data = {}
        self.permanentData = {
            "CYCLES" : [0]*NTEL,
            "SIGNS" : [1]*NTEL            
        }        
        self.reset(map)

        self.steps = {} 
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


    def lock(self):
        """ lock the running data 

        if the locked the .data  dictionary cannot been cleaned until it has been un locked

        """
        self._locked = True

    def unlock(self):
        """ unlock the running data 

        if the locked the .data  dictionary cannot been cleaned until it has been un locked

        """
        self._locked = False

    def getPos(self, datacom):
        if not datacom..checkStep("computeOpdPerTelescope"):
            raise RunTimeError("computeOpdPerTelescope not yet done in datacom")
        self._tic("getPos")

        D = self.data

        D["POSITIONS"] = np.array([com.getDlPos(i) for i in range(self.config["N.TEL"])])

        D["SNR.BASE"] = datacom.data["SNR.BASE"]
        D["SNR.TEL"]  = datacom.data["SNR.TEL"]

        self._tac("getPos")

    def resetData(self, map):
        self.data.clear()



