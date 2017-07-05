#Plotting class

import threading
from queue import Queue
from time import sleep
import numpy as np

plt = pg.plot()

def update(data):
    plt.plot(data, clear=True)

class Thread(pg.QtCore.QThread):
    newData = pg.QtCore.Signal(object)
    def run(self):
        while True:
            data = pg.np.random.normal(size=100)
            # do NOT plot data from here!
            self.newData.emit(data)
            time.sleep(0.05)

thread = Thread()
thread.newData.connect(update)
thread.start()


class Plotter(object):
    def __init__(self,inQueue=None,plot=None):
        super(Plotter,self).__init__()
        self._stop_event = threading.Event()
        self.inQueue=inQueue
        self.plot=plot
        self.data=np.array([[0,0]])
        self.UpdateThread=UpdateThread(self)
        self.UpdateThread.start()

    def stop(self,reason="",wait=True):
        print("Plotter stop called: " + reason)
        self.UpdateThread.stop()
        if wait:
            self.UpdateThread.join()
        self._stop_event.set()
        print("Plotter stopped")

    def stopped(self):
        return self._stop_event.is_set() and self.UpdateThread.stopped()

class UpdateThread(threading.Thread):
    def __init__(self,parent):
        super(UpdateThread, self).__init__()
        self._stop_event = threading.Event()
        self.parent=parent

    def stop(self):
        self._stop_event.set()
        print("UpdateThread stopped")


    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("Running Default UpdateThread")
        while not self.stopped():
            inpData=self.parent.inQueue.get()
            if inpData == None:
                self.parent.stop("Input Queue shutdown",False)
            else:
                self.parent.data=np.append(self.parent.data,inpData,axis=0)
                print(self.parent.data)
                self.parent.plot.plot(self.parent.data)
