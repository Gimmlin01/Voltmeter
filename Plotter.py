#Plot class

#imports
import pyqtgraph as pg
import numpy as np
import threading

#custom imports
from Connection import Connection

#Plot Class witch inherits from PlotWidget and holds the PlotData and has its
#own Thead to liveplot things
class Plot(pg.PlotWidget):
    def __init__(self,parent):
        super(Plot, self).__init__()

        #save parent
        self.parent=parent
        #Stop Event to make it stoppable
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        #Define Array to contain Measured Points
        self.data=np.empty([0,2])
        #establish Connection
        self.Connection=Connection()
        #create new Plot Thread to liveplot things
        self.PlotThread=PlotThread(self)
        #connect the newData Signal to the updatePlot function
        self.PlotThread.newData.connect(self.updatePlot)

    def start(self):
        #it is now running
        self._stop_event.clear()
        #start the Connection
        self.Connection.start()
        #start the Thread
        self.PlotThread.start()

    #make Plot stoppable
    def stop(self,reason=""):
        if not self._stop_event.is_set():
            self.Connection.stop()
            #wati for the PlotThread to "finish"
            self.PlotThread.wait()
            self._stop_event.set()
            print("Plot stopped: " + reason)

    #make Plot pausable
    def pause(self,reason=""):
        self._pause_event.set()
        self.Connection.pause()
        print("Plot paused: " + reason)

    def unpause(self):
        self._pause_event.clear()
        self.Connection.unpause()
        print("Plot unpaused")

    #function to check if Thread has stopped
    def stopped(self):
        return self._stop_event.is_set() and self.PlotThread.stopped()

    def paused(self):
        return self._pause_event.is_set()

    #function to update the plot (must happen in Main Thread)
    def updatePlot(self,inpData):
        self.plot(self.data, clear=True)
        #show status
        self.parent.statusBar().showMessage("Working",1000)

#PlotThread Class inherits from QThread
#looks for Items in Queue and if one found calls for an Plot update
class PlotThread(pg.QtCore.QThread):
    #newData Signal
    newData = pg.QtCore.Signal(object)

    def __init__(self,parent):
        super(PlotThread, self).__init__()
        self._stop_event = threading.Event()
        self.parent=parent
        self.inQueue=self.parent.Connection.outQueue

    #make Thead stoppable
    def stop(self,reason=""):
        if not self._stop_event.is_set():
            self._stop_event.set()
            print("PlotThread stopped: " + reason)

    #function to check if Thread has stopped
    def stopped(self):
        return self._stop_event.is_set()

    #custom run function
    def run(self):
        print("Running Default PlotThread")
        while not self.stopped():
            #get Item from inQueue
            inpData=self.inQueue.get()
            if inpData == None:
                self.stop("Input Queue shutdown")
            else:
                #append the Item to the data array
                self.parent.data=np.append(self.parent.data,inpData,axis=0)
                #broadcast the new data array
                self.newData.emit(inpData)
