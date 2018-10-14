from matplotlib.pylab import plt
import matplotlib.animation as animation

class RtdAxis(object):
    """ A base class for axis rtd plot 

    The object is splited in 3 base function 

    initPlot : 
    """
    def __init__(self, dataCom, axis, parameters={}, **kwargs):
        self.axis = axis        
        self.dataCom = dataCom
        self.parameters = dict(parameters, **kwargs)

        self.elements = OrderedDict()

    
    def update(self):
        raise NotImplementedError('update') 

    def initPlot(self, i):
        return  

    def draw(self):             
        elms, axis = self.elements, self.axis
        ##
        # draw what we have to draw 
        for el in elms.values():
            axis.draw_artist(el)

class RtdFigure(object):

    def __init__(self, dataCom, figure):
        self.dataCom = dataCom
        self.figure = figure

    def init(self):
        # must return a list of artists
        pass

    