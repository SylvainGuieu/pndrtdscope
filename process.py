from .datacom import DataCommunication, Lock, com
import threading
import time

dataCom = None
trackThread = None
scopeThread = None
tunnel = None
tkMaster = None
## for python3
try:
    unicode
except NameError:
    basestring = (str,bytes)
    

class TrackThread(threading.Thread):
    def __init__(self, dataCom, delay=0.0):
        threading.Thread.__init__(self)
        
        self.dataCom = dataCom
        self.delay = delay

    def run(self):
        ###
        # turn the recipy 'track' on 
        # this is the minimum we can ask 
        self.dataCom.turnRecipyOn("track")
        while True:
            time.sleep(self.delay)
            ####
            # If tracking flag is off and scope is off 
            # The process can be stoped

            if (not com.getTrackingFlag()) and\
               (not com.getScopeFlag()):                  
                return   
            if not self.dataCom.runRecipy("getdatasafe"):                
                self.dataCom.runRecipies()

class ScopeThread(threading.Thread):
    def __init__(self, dataCom, master,  delay=0.0):
        from . import panels
        threading.Thread.__init__(self)
        self.dataCom = dataCom
        self.delay = delay
        self.master = master

    def run(self):
        from . import panels
        if not self.master:
            return 
        if not com.getScopeFlag():
            return     

        scope = panels.tk.Toplevel(self.master)
        scop.geometry("%.0fx%.0f"%panels.RtdPanel.panelSize)
        scopeFrame = panels.RtdFrame(scope, self.dataCom)
        
        quitButton = panels.tk.Button(scope, text="Quit", 
                                command=lambda : com.setScopeFlag(False), 
                                bg="gray", fg="blue"
                        )
        scopeFrame.pack()
        quitButton.place(relx=0.08, rely=0.9, anchor=panels.tk.NE)

        if not com.getScopeFlag():
            return 
        
        scope = panels.RtdPanel(dataCom)   
        while True:
            time.sleep(self.delay)
            if not com.getScopeFlag():                  
                scope.destroy()
                del scope
                del scopeFrame
                return 0

            scopeFrame.rtdUpdate()
            #scope.update_idletasks()                       
            #scope.update()


class ScopeThread(threading.Thread):
    def __init__(self, dataCom, master,  delay=0.0):
        from . import panels
        threading.Thread.__init__(self)
        self.dataCom = dataCom
        self.delay = delay
        self.master = master

    def run(self):
        from . import panels         
        if not com.getScopeFlag():
            return     

        scope = panels.RtdPanel(self.dataCom)
        def _update():
            if not com.getScopeFlag():                  
                scope.destroy()
                del scope
                del scopeFrame
                return 0
            scope.rtdUpdate()                
            scope.after(self.delay, _update)
        _update()            
        scope.mainloop()
        #try:
        #    scope.mainloop()
        #except Exception as e:
        #    print e
        #    return 



def openProcess(host, tun, master=None):
    global dataCom, tunnel, tkMaster
    dataCom = DataCommunication(host)
    if isinstance(tun, basestring):        
        tun = open(tun, "a+")

    tun.seek(0) 
    tun.truncate()   
    tunnel = tun
    tkMaster = master


def startTrackThread():
    global trackThread
    if trackThread is None or not trackThread.isAlive():
        trackThread = TrackThread(dataCom)
        trackThread.start()

def startScopeThread():
    global scopeThread, tkMaster
    if scopeThread is None or not scopeThread.isAlive():
        scopeThread = ScopeThread(dataCom, tkMaster, 0.01)
        scopeThread.start()


def readInput(line):
    global trackThread, scopeThread, dataCom 
    print "Receive", line
    try:
        command, _, option = line.partition(" ")
    except:
        raise IOError("Invalid command line '%s'"%line)

    command = command.strip(" \t")      
    option  = option.strip(" \n\t").upper()

    if command in ["START", "STOP"]:
        if not (option in ["TRACK", "SCOPE"]):          
            raise IOError("Expecting  'TRACK' or 'SCOPE' after %s got %s"%(command, option))

        if (command,option) == ("START", "TRACK"):
            com.setTrackingFlag(True)
            startTrackThread()

        elif (command,option) == ("STOP", "TRACK"):         
            com.setTrackingFlag(False)
    
        if (command,option) == ("START", "SCOPE"):
            com.setScopeFlag(True)
            ###
            # we need a trackThread for the scopeThread to work 
            startTrackThread()
            startScopeThread()
                               
        elif (command,option) == ("STOP", "SCOPE"):         
            com.setScopeFlag(False)         

    else:
        raise IOError("Unknown command '%s' should be 'START' or 'STOP' "%command)
    

def monitorTunnel():
    global tunnel
    tunnel.seek(0)
    l = tunnel.read()
    while l:
        readInput(l)
        l = tunnel.read()

    tunnel.seek(0)  
    tunnel.truncate()

            





