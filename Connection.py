#Default Connection class

import threading
from queue import Queue


class Connection(object):
    def __init__(self):
        super(Connection,self).__init__()
        self._stop_event = threading.Event()
        self.outQueue=Queue()
        self.measureThread=InputThread(self)
        self.measureThread.start()

    def stop(self,reason=""):
        if not self._stop_event.is_set():
            print("Connection stop called: " + reason)
            self.measureThread.stop()
            self.measureThread.join()
            self._stop_event.set()
            print("Connection stopped")

    def stopped(self):
        return self._stop_event.is_set() and self.measureThread.stopped()

class InputThread(threading.Thread):
    def __init__(self,parent):
        super(InputThread, self).__init__()
        self._stop_event = threading.Event()
        self.parent=parent
        self.startTime=0

    def stop(self):
        if not self._stop_event.is_set():
            self.parent.outQueue.put(None)
            self._stop_event.set()
            print("InputThread stopped")


    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        import random
        import time
        print("Running Dummy InputThread")
        self.startTime=time.time()
        while not self.stopped():
            t=time.time()-self.startTime
            self.parent.outQueue.put([[t,-0.5*(t-20)*(t-20)+20]])
            time.sleep(0.01)
