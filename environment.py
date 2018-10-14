""" Provide a durty but quick input/output comminucation with a process running 

"""

import os
import time
import string
import random
import threading 

## for python3
try:
    unicode
except NameError:
    basestring = (str,bytes)

def randomString(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class TimeoutError(IOError):
    pass


def _readString(f, head):
    size = int(head)
    s = f.read(size)
    f.readline() # Get read of the "\n"
    return s

def _writeString(f, v):
    f.write("str {}\n{}\n".format(len(v), v))


def _readFloat(f, head):    
    return float(head)

def _writeFloat(f, v):
    f.write("float %s\n"%v)

def _readInt(f, head):    
    return int(head)

def _writeInt(f, v):
    f.write("int %s\n"%v)    

def _readComplex(f, head):    
    return complex(head)

def _writeComplex(f, v):
    f.write("complex %s\n"%v)    

def _readBool(f, head):
    if head.strip() in ["false", "False", "F" ]:
        return False
    return True        

def _writeBool(f, v):
    if v:
        f.write("bool True\n")
    else:
        f.write("bool False\n")



wrLoockup = [
    (bool,   _writeBool),
    (int,   _writeInt),
    (float, _writeFloat), 
    (complex,_writeComplex),     
    (str, _writeString), 
    (unicode, _writeString),
    (basestring, _writeString)
]

rdLoockup = {
    "int":_readInt,
    "float":_readFloat, 
    "complex":_readComplex, 
    "bool":_readBool, 
    "str":_readString
}        





class MonitorThread(threading.Thread):
    def __init__(self, env, cycleTime=0.01):
        self.env = env
        self.cycleTime = cycleTime
        threading.Thread.__init__(self)
            

    def run(self):
        while True:
            if self.env.quitCheck():
                return 

            self.env.monitor()                                
            time.sleep(self.cycleTime)



class Server(object):
    """ Server object need a name and a diretory to be created 
    
    The connumnications are made with files : 
        {directory}/{name}.in
        {directory}/{name}.out
        {directory}/{name}.err
    
    The Server is writing in the `.out` and reading the `.in` 
    A client will readt the `.out` and send instruction to server on the `.out`

    The readInput function must be defined by a server subclass

    """
    def __init__(self, name, directory):
        if os.path.exists(directory) and not os.path.isdir(directory):
            raise IOError("Cannot create environment in '%s', is it a file "%directory)
        if not os.path.exists(directory):
            raise IOError("The environment does not exist")

        stdIn  = open(os.path.join(directory, name+".in"), "a+" )
        stdOut = open(os.path.join(directory, name+".out"), "a+" )
        stdErr = open(os.path.join(directory, name+".err"), "a+" )
        

        #stdIn.seek(0)
        #stdIn.truncate()
        self.directory = directory 
        self.name = name        
        self.stdIn, self.stdOut, self.stdErr = stdIn, stdOut, stdErr
        self.clientsOut = {}


    def thread(self, cycleTime=0.01):
        return MonitorThread(self, cycleTime)


    def monitor(self):
        stdIn, stdOut, stdErr = self.stdIn, self.stdOut, self.stdErr

        replies = []
        errors  = []

        #stdIn  = open(os.path.join(self.directory, self.name+".in"), "r" )
        
        stdIn.seek(0)
        line = stdIn.readline().rstrip("\n")
       
        if not line:
            return 

        while line:
            try:    
                reply = self.readInput(line)
            except IOError as e:
                errors.append(str(e))                
            else:                
                if reply is not None:    
                    replies.append(reply)
            line = stdIn.readline().rstrip("\n")                    

        stdIn.seek(0)
        stdIn.truncate()
        
        stdOut.seek(0)
        stdOut.truncate()

        stdErr.seek(0)
        stdErr.truncate()
        
                    
        stdErr.write("%d\n"%len(errors))
        for er in errors:           
            stdErr.write("%s\n"%er)
        stdErr.flush()
        
        stdOut.write("%d\n"%len(replies))
        for reply in replies:
            self.writeReply(self.stdOut, reply)

        stdOut.flush()            
        return replies, errors
    
    def writeReply(self, f, reply):
        if reply is None:
            return 
        for tpe, wrfunc in wrLoockup:
            if isinstance(reply, tpe):
                wrfunc(f, reply)
                return 
        raise RuntimeError("type %s is not valid fo communication reply"%type(reply))        


    def readInput(self, line):
        raise NotImplementedError('readInput')            
                
    def quitCheck(self):
        raise NotImplementedError("quitCheck")              

        



class Client(object):
    def __init__(self, name, directory):
        if not os.path.exists(directory):
            raise IOError("The environment does not exist")
        
        stdOut =  open(os.path.join(directory, name+".in"), "a+" )
        stdIn  =  open(os.path.join(directory, name+".out"), "a+" )
        stdErr =  open(os.path.join(directory, name+".err"), "a+" )

        lockFile = os.path.join(directory, name+".lock")
        self.directory = directory 
        self.name = name
        self.stdOut = stdOut
        self.stdIn  = stdIn
        self.stdErr = stdErr
        self.lockFile = lockFile
        
        self.unlock()

    def lock(self):
        with open(self.lockFile, "w"):
            pass    

    def unlock(self):
        try:
            os.remove(self.lockFile)
        except OSError:
            pass    

    def isLocked(self):
        return os.path.exists(self.lockFile)    



    def read(self, timeout=1000):

        #stdIn  =  open(os.path.join(self.directory, self.name+".out"), "r" )
        stdIn= self.stdIn
        stdErr = self.stdErr

        stdIn.seek(0)

        l =stdIn.readline()        
        s = time.time()  
        while not l:
            time.sleep(0.01)
            if  ((time.time()-s)*1000) > timeout:
                    self.unlock()
                    raise TimeoutError("no reply receive after %s ms"%(((time.time()-s)*1000)))
            stdIn.seek(0)
            #stdIn  =  open(os.path.join(self.directory, self.name+".out"), "r" )                 
            l = stdIn.readline()
            
        try:
            n = int(l)
        except TypeError as e:
            self.unlock()
            raise RuntimeError("Unknown reply format: %s"%e)    
        except ValueError as e:
            self.unlock()
            raise RuntimeError("Unknown reply format: %s"%e) 
                
        replies = []
        for _ in range(n):
            headline = stdIn.readline().strip("\n")
            tpe, _, head = headline.partition(" ")
            tpe = tpe.strip()
            head = head.strip()

            try:
                rfunc = rdLoockup[tpe]
            except KeyError:
                raise RuntimeError("value header not valid: '%s', type not understood"%headline)
            
            replies.append(rfunc(stdIn, head))            

        #replies = list(stdIn.readline().rstrip("\n") for _ in range(n)  )


        stdErr.seek(0)
        l = stdErr.readline()    
        if l:
            try:
                n = int(l)
            except TypeError as e:
                self.unlock()
                raise RuntimeError("Unknown reply format in error: %s"%e)    
            except ValueError as e:
                self.unlock()
                raise RuntimeError("Unknown reply format in error: %s"%e) 

            errors = list(stdErr.readline().rstrip("\n") for _ in range(n))
        else:
            errors = []                

        #stdIn.seek(0)
        #stdIn.truncate()
        self.unlock()        
        return replies, errors


    def send(self, messages, timeout=1000, nowait=False):

        if isinstance(messages, basestring):
            messages = [messages]

        stdIn, stdOut = self.stdIn, self.stdOut

        s = time.time()
        while self.isLocked():
            time.sleep(0.01)
            ss = time.time()
            if  ((ss-s)*1000) > timeout:
                raise TimeoutError("com locked after timeout")
            if (ss-s) > 120: ## we cannot wait for ever 
                raise TimeoutError("com locked after timeout")
        
        self.lock()

        stdIn.seek(0)
        stdIn.truncate()

        stdIn  =  open(os.path.join(self.directory, self.name+".out"), "r" )

        try:
            for message in messages:
                self.stdOut.write("%s\n"%message)
            self.stdOut.flush()

        except Exception as e:
            print "Error in write", e
            self.unlock()
            raise e
        
        if nowait:
            self.unlock()
            return [], []        
        return self.read(timeout)            