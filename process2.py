from .datacom import com
from .environment import Server
import threading
import time



class ComProcess(Server):
    def readInput(self, line):
        try:
            command, _, option = line.partition(" ")
        except:
            raise IOError("Invalid command line '%s'"%line)

        command = command.strip(" \t")      
        option  = option.strip(" \n\t").upper()    

        if command == "START":        
            if option == "TRACK":
                com.setTrackingFlag(True)

            elif option == "SCOPE":
                com.setScopeFlag(True)
            
            else:
                raise IOError("Expecting  'TRACK' or 'SCOPE' after %s got %s"%(command, option))

        elif command == "STOP":        
            if option == "TRACK":
                com.setTrackingFlag(False)

            elif option == "SCOPE":
                com.setScopeFlag(False)
            
            else:
                raise IOError("Expecting  'TRACK' or 'SCOPE' after %s got %s"%(command, option))        

        elif command == "STATUS":
            if option == "TRACK":
                return com.getTrackingFlag()
                
            elif option == "SCOPE":
                return com.getScopeFlag()

        elif command == "FOCUS":
            if not option:
                raise IOError("A plot tab label should follow FOCUS")
            if not option in com.plotFocusList:
                raise IOError("FOCUS accept on of '%s' got %r"%("', '".join(com.plotFocusList), option))    
            com.setPlotFocus(option)   

        elif command == "QUIT":
            com.sendQuitFlag()                     

    def quitCheck(self):
        return com.getQuitFlag()        

class ComProcessThread(threading.Thread):
    def __init__(self, name="com", directory="./", cycleTime=0.01):
        self.env = ComProcess(name, directory)
        self.cycleTime = cycleTime
        threading.Thread.__init__(self)
            

    def run(self):
        while True:
            if self.env.quitCheck():
                return 
            self.env.monitor()                                
            time.sleep(self.cycleTime)





            





