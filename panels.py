""" This module provide classes to create tk frame, plot, button panel for the rtd scope


"""


####
# Define the matplotlib default backend 
# Should not be done before
import matplotlib
matplotlib.use("TkAgg")

from collections import OrderedDict

try: # python 2.7
    import Tkinter as tk
    import ttk
except: # python 3
    import tkinter as tk
    from tkinter import ttk 
import time

###
# Canvas used for tk plot 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .config import defaults
if defaults.get("SIMU.MODE", False):
    from . import comsimu as com
else:
    from . import com

####
# plotLoockup a dictionary defining the plots by their name 
# COMBINED.FRINGES:  The combined and filtered  fringes 
# COMBINED.PSD    :  The combined and filtered PSD
# METER.FLUX      :  The meter bars that gives the Flux per telescope 
# METER.SNR       :  The meter bars that gives the SNR per telescope  
# RAW.FRINGES     :  The raw fringes (24 or 48 plots)
# RAW.PSD         :  The raw fringe psd (24 or 48 plots)
# METER.PHASEDIFF :  The meter bars that gives the phase difference 
#                      (when wollaston is on)
# NIOBATE.ZOOM.IN :  The white normalized fringes for each polarizations 
# NIOBATE.ZOOM.OUT:  The normalized fringes for each polarizations 
#                      and the envelops
from .rtdplots import plotLoockup
from matplotlib.pylab import plt

import threading

U = False


def QuitRtd():
    """ trigger the scope flag to False so the rtd scope are stopped """    
    com.setScopeFlag(False)

def QuitSystem():
    """ Stop rtd scope and traking """
    com.sendQuitFlag()


class TrackThread(threading.Thread):
    def __init__(self, dataCom, delay=0.0):
        threading.Thread.__init__(self)
        self.dataCom = dataCom
        self.delay = delay
    def run(self):
        self.dataCom.turnRecipyOn("track")
        while True:
            time.sleep(self.delay)
            if (not com.getTrackingFlag()) and\
               (not com.getScopeFlag()):                  
                return   
            if not self.dataCom.runRecipy("getdatasafe"):                
                self.dataCom.runRecipies()

class ScopeThread(threading.Thread):
    def __init__(self, dataCom, scope, delay=0.0):
        threading.Thread.__init__(self)
        self.dataCom = dataCom
        self.scope = scope
        self.delay = delay

    def run(self):
                
        while True:
            time.sleep(self.delay)
            if not com.getScopeFlag():                  
                return                                           
            self.scope.rtdUpdate()

                                    

class ManagerPanel(tk.Tk):
    """ A very simple little panel 

    It gives the possibility to 
     - stop / start traking  and show status
     - stop / start the rtd scope panel and show status 


    +---------------------------------------------+
    |                                             |
    |   Tracking: [Stop]  [Start]   (status)      | 
    |                                             |
    |   Scope:    [Stop]  [Start]   (status)      |
    |                                             |
    +---------------------------------------------+

    """
    rtdDefaults = {        
        "geometry" : defaults.get("PANEL.MANAGER.GEOMETRY", "300x100")
    }
    def __init__(self, dataCom, parent=None, **kwargs): 
        kwargs = dict(self.rtdDefaults, **kwargs)
        geometry = kwargs.pop("geometry", None)
        tk.Tk.__init__(self, parent, **kwargs)
        if geometry:
            self.geometry(geometry)
        self.dataCom = dataCom

        self.scopePanel = None
        self.scopeThread = None
        self.trackThread = None


        ###
        # create buttons and status labels
        #
        self.trackingStatus = tk.Label(self, bg="white", fg="red", text="off")
        self.stopTrackingButton = tk.Button(
                        self, text="Stop", 
                        fg="red", bg="white", 
                        command=self.stopTracking
                        )
        self.startTrackingButton = tk.Button(
                        self, text="Start", 
                        fg="blue", bg="white",
                        command=self.startTracking
                        )        

        self.scopeStatus   = tk.Label(self, bg="white", fg="red", text="off")
        self.stopScopeButton = tk.Button(
                        self, text="Stop", 
                        fg="red", bg="white", 
                        command=self.stopScope
                        )
        self.startScopeButton = tk.Button(
                        self, text="Start", 
                        fg="blue", bg="white",
                        command=self.startScope
                        ) 


        ###
        # set the layout of button and status 
        #
        tk.Label(self, text="Tracking: ").grid(column=0, row=0)
        self.stopTrackingButton.grid(column=1, row=0)
        self.startTrackingButton.grid(column=2, row=0)
        self.trackingStatus.grid(column=3, row=0)

        tk.Label(self, text="Scope: ").grid(column=0, row=1)
        self.stopScopeButton.grid(column=1, row=1)
        self.startScopeButton.grid(column=2, row=1)
        self.scopeStatus.grid(column=3, row=1)

    
    
    def makeScope(self):
        """ Make a rdtscope panel dependant of the panel Manager """
        t = tk.Toplevel(self)
        t.geometry("%.0fx%.0f"%RtdPanel.panelSize)

        self.scopeFrame = RtdFrame(t, self.dataCom)
        
        self.quitButton = tk.Button(t, text="Quit", 
                                    command=self.stopScope, 
                                    bg="gray", fg="blue"
                            )
        self.scopeFrame.pack()

        self.quitButton.place(relx=0.08, rely=0.9, anchor=tk.NE)
        self.scopePanel = t


    def rtdUpdate(self):
        """ update the panel 
        
        lunch or restart the traking thread if needed
        lunch the rtdscope panel if needed or update it 
        
        """
        if com.getTrackingFlag():
            ##
            # set status label to on 
            self.trackingStatus.config(text="on", fg="blue")
            ##
            # lunch the thread if not active 
            if not self.trackThread or not self.trackThread.isAlive():
                self.trackThread = TrackThread(self.dataCom)
                self.trackThread.start()

        else:
            ##
            # set status label to off 
            self.trackingStatus.config(text="off", fg="red") 

        if com.getScopeFlag():
            ##
            # set status label to on 
            self.scopeStatus.config(text="on", fg="blue")
            if not self.scopePanel:
                # mae a new scope panel 
                self.makeScope()  

            if not self.trackThread or not self.trackThread.isAlive():
                # we need a track thread anyway for the scope but the tracking 
                # flag can still be off
                self.trackThread = TrackThread(self.dataCom)
                self.trackThread.start()

            if not self.scopeThread or not self.scopeThread.isAlive():
                self.scopeThread = ScopeThread(self.dataCom, self.scopeFrame, 0.05)
                self.scopeThread.start()

        else:
            self.scopeStatus.config(text="off", fg="red")            
            if self.scopePanel:
                # wait a bit for everything to finish 
                time.sleep(1)
                self.scopePanel.destroy()
                self.scopePanel = None
                self.scopeFrame = None            

        if U:
            self.update()

    
    def startTracking(self):        
        com.setTrackingFlag(True)
        
    def stopTracking(self):       
        com.setTrackingFlag(False)
    
    def startScope(self):        
        com.setScopeFlag(True)

    def stopScope(self):       
        com.setScopeFlag(False)    
    


class RtdPanel(tk.Tk):
    """ Stand alone rtd panel """   
    panelSize = defaults.get("PANEL.RTDSCOPE.SIZE", (1200,700))
    rtdDefaults = {        
        "title" : "pndrtdscope"        
    }
    def __init__(self, dataCom, parent=None, standalone=True,  **kwargs): 
        kwargs = dict(self.rtdDefaults, **kwargs)   
        kwargs.setdefault("geometry", "%.0fx%.0f"%self.panelSize)
        title = kwargs.pop("title", None)
        geometry = kwargs.pop("geometry", None)
        tk.Tk.__init__(self, parent, **kwargs)
        if geometry:
            self.geometry(geometry)
        self.rtdFrame = RtdFrame(self, dataCom)
        self.rtdFrame.pack()


        self.quitButton = tk.Button(self, text="Quit", 
                                    command=QuitSystem if standalone else QuitRtd, 
                                    bg="gray", fg="blue"
                                    )
        
        self.quitButton.place(relx=0.08, rely=0.9, anchor=tk.NE)

    def rtdUpdate(self):
        self.rtdFrame.rtdUpdate()
        if U:
            self.update()

class RtdFrame(tk.Frame):
    """ Main panel for th rtd 
    
    
    The Panel layout is 

    
    +------------+--------------------------------------------------+
    |            |   |       Plot Tabs filtered/raw/niobate     |   |                        
    | [Savebckg] |   +------------------------------------------+   |
    | [ ]subbckg |  +--------------------+  +--------------------+  |   
    |            |  |                    |  |                    |  | 
    |------------+  |                    |  |                    |  |
    |            |  |                    |  |                    |  |
    |  ===       |  |                    |  |                    |  |
    |  =====     |  |                    |  |                    |  |
    |  =         |  |                    |  |                    |  |
       ====      |  |  Fringes           |  |      PSD           |  |
    |  Tel Flux  |  |                    |  |                    |  |
    |            |  |                    |  |                    |  |
    |  ===       |  |                    |  |                    |  |
    |  =         |  |                    |  |                    |  |
    |  =====     |  |                    |  |                    |  |
    |  ===       |  |                    |  |                    |  |
    |  Tel SNR   |  |                    |  |                    |  |
    |            |  |                    |  |                    |  |
    |  ===       |  |                    |  |                    |  |
    |  =         |  |                    |  |                    |  |
    |  =====     |  |                    |  |                    |  |
    |  ===       |  |                    |  |                    |  |
    |  TelPhdiff |  |                    |  |                    |  |
    |            |  +--------------------+  +--------------------+  |
    |            |                                                  |
    |            |            Status   Information                  |
    +------------+--------------------------------------------------+
    """
    
    ###
    # resizing the graphic on the fly does not work 
    # so figure has fix dimension
    # To maximazie the area taken by the figure, their size
    # is proportionel to the panel size at startups

    
    panelSize = defaults.get("PANEL.RTDSCOPE.SIZE", (1200,700))

    figRatio = defaults.get("PANEL.RTDSCOPE.FIG.RATIO", (0.42, 0.85))


    miniFigRatio = defaults.get("PANEL.RTDSCOPE.MINIFIG.RATIO",(0.10, 0.2))

    filteredFrame = None
    rtdDefaults = {        
        #"title" : "pndrtdscope"        
    }
    def __init__(self, parent, dataCom, **kwargs):        
        kwargs = dict(self.rtdDefaults, **kwargs)                       
        tk.Frame.__init__(self, parent, **kwargs)
        self.panelSize = getattr(parent, "panelSize", (1200,700))       
        ###
        # create the figures 
        #
        dpi = plt.rcParams['figure.dpi']
        ##
        # one big figure is 20% of panel width
        #size_inches  = (x*r/dpi  for x,r in zip(panelSize, figRatio))


        ## Common dictionary for the figures
        # define the size of figure as proportionof the frame
        figKw = dict(
                    figsize=tuple(x*r/dpi  for x,r in zip(self.panelSize, self.figRatio)),
                    facecolor=defaults.get("PANEL.RTDSCOPE.FIG.FACECOLOR","white")
                    )
        ##
        # Build all the necessary plot objects 
        # The plot will be initialized on demand 
        figures = {
            "COMBINED.FRINGES"  : plotLoockup["COMBINED.FRINGES"](
                                        dataCom, "Combined", **figKw
                                        ),
            "COMBINED.PSD"      : plotLoockup["COMBINED.PSD"](
                                        dataCom, "Psd",**figKw
                                        ),
            "RAW.FRINGES"       : plotLoockup["RAW.FRINGES"](
                                        dataCom, "Raw",**figKw
                                        ),
            "RAW.PSD"           : plotLoockup["RAW.PSD"](
                                        dataCom, "PSD", **figKw
                                        ),
            "NIOBATE.ZOOM.IN"   : plotLoockup["NIOBATE.ZOOM.IN"](
                                        dataCom, "Niobate Zoom",**figKw
                                        ),
            "NIOBATE.ZOOM.OUT"  : plotLoockup["NIOBATE.ZOOM.OUT"](
                                        dataCom, "Niobate",**figKw
                                        )
        }

        ## 
        # Common dictionary for the mini figures
        # define the size of figure as proportionof the frame
        miniFigKw = dict(#figsize=(7,11), 
                    figsize=tuple(x*r/dpi  for x,r in zip(self.panelSize, self.miniFigRatio)),
                    facecolor=defaults.get("PANEL.RTDSCOPE.MINIFIG.FACECOLOR","white")
                    )
        ##
        # Build the mini figures for FLUX, SNR, PHASE diff meter 
        meterFigure = {
            "METER.FLUX": plotLoockup["METER.FLUX"](
                                dataCom, "flux", **miniFigKw
                                ),
            "METER.SNR" : plotLoockup["METER.SNR"](
                                dataCom, "snr", **miniFigKw
                                ),
            "METER.PHASEDIFF": plotLoockup["METER.PHASEDIFF"](
                                dataCom, "Phase Diff", **miniFigKw
                            ) 
        }

        ##
        # Attach the necessary figures for live plot 
        # by default attach the filtered fringes and psd and all meters
        figures["COMBINED.FRINGES"].attach()
        figures["COMBINED.PSD"].attach()

        meterFigure["METER.FLUX"].attach()
        meterFigure["METER.SNR"].attach()
        meterFigure["METER.PHASEDIFF"].attach()

        self.meterFigure = meterFigure
        self.figures = figures


        bckg = defaults.get("PANEL.RTDSCOPE.BACKGROUND","white")
        self.configure(
            background=bckg
        )

        self.dataCom = dataCom

        ##
        # Build the main plot in a Tab frame 
        # PlotTabFrame will use the figures dictionary above created
        self.plotsTab = PlotTabFrame(self)

        ##
        # the side bar left frame (containing the meters, button, etc ...)        
        self.leftFrame = Frame(self, dataCom, background=bckg)

        ##
        # button to save the background 
        self.saveDataOffsetButton = tk.Button(self.leftFrame, text="Save Bckg", bg=bckg, fg="blue", command=com.sendSaveDataOffsetFlag)

        ##
        # A check button to substract background (enabled if a background has
        # been saved)
        self.substractDataOffset = tk.IntVar()
        self.substractDataOffsetCheckButton = tk.Checkbutton(self.leftFrame, text="Substract Bckg", variable=self.substractDataOffset, 
            onvalue=1, offvalue=0
        )

        ##
        # build the frames for the meter miniplots 
        meterFrames = OrderedDict()
        for n,label in [ ("METER.FLUX", "flux"), 
                         ("METER.SNR", "SNR"), 
                         ("METER.PHASEDIFF", "Phase Diff")]:
            meterFrames[n] = MiniPlotFrame(
                                self.leftFrame, 
                                meterFigure[n], 
                                label=label
                                )        
        
        ##
        # The frame with status information 
        self.statusFrame = StatusFrame(self)
        
        self.saveDataOffsetButton.pack()
        self.substractDataOffsetCheckButton.pack()
        for f in meterFrames.values():
            f.pack(pady=5)

        self.meterFrames = meterFrames
                

                
        ####
        # set the layout 
        
        self.plotsTab.grid(column=1, row=1, sticky=tk.NSEW)
        self.leftFrame.grid(column=0, row=1 , sticky=tk.N, padx=2, pady=18)
        self.statusFrame.grid(column=1,row=2, sticky=tk.S)

        #for tab in self.plotsTab.tabs.itervalues():
        #    for pf in tab.plotFrames:
        #        pf.resizeFig((600,300))

    def rtdUpdate(self):
        """ update the full frame 
        
        - the status
        - the main plots 
        - the meter plots
        """

        self.statusFrame.rtdUpdate()

        self.plotsTab.rtdUpdate()
        for f in self.meterFrames.values():
            f.rtdUpdate()

        ##
        # enable/disable the substrack data check button if there
        # is a saved background or not
        if self.dataCom.hasSavedOffset():
            self.substractDataOffsetCheckButton.config(state=tk.NORMAL)
        else:
            self.substractDataOffsetCheckButton.config(state=tk.DISABLED)  
        com.setSubstractDataOffsetFlag(self.substractDataOffset.get())
        if U:
            self.update()


class Frame(tk.Frame):
    """ a generic Frame object with a dataCom attached """
    rtdDefaults = { }
    def __init__(self, parent, dataCom,  **kwargs):
        ##
        # update some default to kwargs 
        kwargs =dict(self.rtdDefaults, **kwargs)    
        tk.Frame.__init__(self, parent, **kwargs)
        self.dataCom = dataCom


class StatusFrame(tk.Frame):
    """ A small Frame showing the status of the scope """
    rtdDefaults = {
      #'relief':tk.GROOVE, 
      #'borderwidth':2, 
      #'width':100, 'height':100
    }
    def __init__(self, parent,  **kwargs):
        ##
        # update some default to kwargs 
        kwargs =dict(self.rtdDefaults, **kwargs)    
        tk.Frame.__init__(self, parent, **kwargs)

        self.dataCom = parent.dataCom
        
        self.statusText = tk.Label(self, text="")
        self.statusText.pack()
        self.time = 0.0#time.time()

    def rtdUpdate(self):
        """ update the status message """
        dataCom = self.dataCom
        thistime = time.time()
        elpased = thistime-self.time if self.time else 0.0
        text = time.strftime("%Y-%m-%dT%H:%M:%S",time.localtime())+" - " 

        if not dataCom.isDataValid():
            text += "Waiting for scan data Elpased time %.2f"%(elpased)
        elif dataCom.data.get("TEST.NEW", False):
            text += "Configuration Changed. Reploting...."
        else:
            text += "%d Scan - Refresh %.2f sec"%(dataCom.config["N.OPL"],elpased)

        self.statusText.config(text=text)
        self.time = thistime
        if U:
            self.update()

            
            


class PlotTabFrame(tk.Frame):
    """ Frame that contain the tabs and the main plots """
    rtdDefaults = {
      #'width':1200, 'height':650, 
      'relief':tk.GROOVE, 
      'borderwidth':2
    }
    def __init__(self, parent,  **kwargs):
        ##
        # update some default to kwargs 
        kwargs =dict(self.rtdDefaults, **kwargs)    
        tk.Frame.__init__(self, parent, **kwargs)

        self.dataCom = parent.dataCom
        self.figures = parent.figures

        ####
        # without notebook 
        # self.filteredTab = HorizontalPlotFrame(self, 
        #     self.figures["filtered"], 
        #     self.figures["filteredPsd"], 
        #     width=600, height=400
        #     )
        # self.filteredTab.pack(fill=None, expand=False)
        # return 

        notebook = ttk.Notebook(self)
        notebook.dataCom = self.dataCom
        

        self.tabs = OrderedDict(
            [
            ("COMBINED" , HorizontalPlotFrame(
                notebook, 
                self.figures["COMBINED.FRINGES"], 
                self.figures["COMBINED.PSD"]
                )
            ),
            ("RAW" , HorizontalPlotFrame(
                notebook, 
                self.figures["RAW.FRINGES"], 
                self.figures["RAW.PSD"]
                )
            ),
            ("NIOBATE" , HorizontalPlotFrame(
                notebook, 
                self.figures["NIOBATE.ZOOM.IN"], 
                self.figures["NIOBATE.ZOOM.OUT"]
                )
            )
            ]
        )

        ## keep the original order when adding 
        for n, label in [("COMBINED", "Fringes"),
                         ("RAW", "Raw"),
                         ("NIOBATE", "Niobate")
                        ]:
            notebook.add(self.tabs[n], text=label)
                
        #notebook.pack(sticky=tk.NSEW)
        notebook.grid(sticky=tk.NSEW)
        self.notebook = notebook
    
    def rtdUpdate(self):
        """ update the plots that are active (selected tab)
    
        disable the plots that are not actived
        """

       

        ####
        # without notebook 
        # self.filteredTab.rtdUpdate()
        # return 

        ####
        # Check the if a Tab to focus comes from outside         
        focus = com.getPlotFocus()
        if not focus or focus not in ["COMBINED", "RAW", "NIOBATE"]:
            # if no focus comming from outside 
            # get the current tab selected 
            nb = self.notebook 
            i = nb.index(nb.select())            
            focus = list(self.tabs.keys())[i]  
        else:
            # clean the focus as ordered from outside 
            com.setPlotFocus(None)            
            self.notebook.select(self.tabs.get(focus, self.tabs["COMBINED"]))

        # detach all figures     
        for plotName, tab in self.tabs.items():
            if not (plotName == focus):
                for plotFrame in tab.plotFrames:
                    plotFrame.rtdFig.detach()

        # attach the figures activated             
        for plotName, tab in self.tabs.items():                    
            if plotName == focus:
                for plotFrame in tab.plotFrames:
                    plotFrame.rtdFig.attach()

            ##
            # update the plots inside the tab                                              
            tab.rtdUpdate()                                   
        if U:            
            self.update()
            

class HorizontalPlotFrame(tk.Frame):
    """ Contain several plotFrames side by side typicaly two """
    rtdDefaults = {
      'width':1200, 'height':600
    }
    def __init__(self, parent, *rtdFigs,  **kwargs):
        kwargs =dict(self.rtdDefaults, **kwargs)

        tk.Frame.__init__(self, parent, **kwargs)
        self.dataCom = parent.dataCom
        plotFrames = [PlotFrame(self, rtdFig) for rtdFig in rtdFigs ]
        
        ##
        # pack the frames 
        for i,plotFrame in enumerate(plotFrames):
            plotFrame.grid(column=i+1,row=1, sticky=tk.NSEW)
            #plotFrame.pack(side=tk.LEFT)

        self.plotFrames = plotFrames

    def rtdUpdate(self):
        for plotFrame in self.plotFrames:
            plotFrame.rtdUpdate()             


class PlotFrame(tk.Frame):
    """ A frame that contain one Figure plot """
    rtdDefaults = {
      #'width':400, 'height':600
      "background": defaults.get("PANEL.RTDSCOPE.BACKGROUND", "white")
    }
    def __init__(self, parent, rtdFig, **kwargs):
        kwargs =dict(self.rtdDefaults, **kwargs)
        tk.Frame.__init__(self, parent, **kwargs)
        self.dataCom = parent.dataCom
        self.rtdFig = rtdFig
           
        ##
        # change the canvas update 
        # rtdFig.updateCanvas =  updateCanvasTk
                        
        canvas = FigureCanvasTkAgg(rtdFig.fig, master=self)

        ##
        # the matplotlib figure drawing and update protocol is different for 
        # each backend (in order to do it as fast as possible).
        # why need to run checkCanvas, so that the replot methods are optimized 
        # for tk backend
        rtdFig.checkCanvas()
        
        self.plotWidget = canvas.get_tk_widget()
        self.plotWidget.configure(background=defaults.get("PANEL.RTDSCOPE.BACKGROUND","white"))
        #self.plotWidget.pack(fill=tk.BOTH)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.plotWidget.grid(column=1, row=1, sticky=tk.NSEW)

    def rtdUpdate(self): 
        """ update the figure """
        self.rtdFig.update()                
        if U:
            self.update()        

    def resizeFig(self, sizes):
        """ deprecated, Does not work """
        self.rtdFig.fig.set_size_inches(sizes)    

class MiniPlotFrame(tk.Frame):
    """ A frame that contain one Figure plot, the small meter plots"""
    rtdDefaults = {      
      "background": defaults.get("PANEL.RTDSCOPE.BACKGROUND", "white")
    }
    def __init__(self, parent, rtdFig, **kwargs):
        kwargs =dict(self.rtdDefaults, **kwargs)
        label = kwargs.pop("label", "")
        tk.Frame.__init__(self, parent, **kwargs)

        self.subFrame = tk.Frame(self, relief=tk.GROOVE, borderwidth=2)
        self.label = tk.Label(self, text=label, 
                                    bg=defaults.get("PANEL.RTDSCOPE.BACKGROUND", "white"), 
                                    fg="black", 
                                    anchor=tk.CENTER
                            )


        self.dataCom = parent.dataCom
        self.rtdFig = rtdFig
        
        ##
        # change the canvas update 
        # rtdFig.updateCanvas =  updateCanvasTk
                        
        canvas = FigureCanvasTkAgg(rtdFig.fig, master=self.subFrame)
        rtdFig.checkCanvas()
        #rtdFig.fig.set_size_inches((400,400))

        self.plotWidget = canvas.get_tk_widget()
        self.plotWidget.configure(
                background=defaults.get("PANEL.RTDSCOPE.BACKGROUND", "white")
            )
        #self.plotWidget.pack(fill=tk.BOTH)
        self.subFrame.pack(pady=12)
        self.label.place(relx=0.25, rely=0.0, anchor=tk.NW)

        self.subFrame.grid_rowconfigure(1, weight=0)
        self.subFrame.grid_columnconfigure(1,weight=0)
        self.plotWidget.grid(column=1,row=1, sticky=tk.NSEW)

    def rtdUpdate(self): 
        self.rtdFig.update()        
        if U:
            self.update()
        
    def resizeFig(self, sizes):
        self.rtdFig.fig.set_size_inches(sizes)    




