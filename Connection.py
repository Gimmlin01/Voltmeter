#Default Connection class
# author: Michael Auer

import threading
from queue import Queue


class Connection(object):
    def __init__(self):
        super(Connection,self).__init__()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.outQueue=Queue()
        self.inputThread=InputThread(self)

    def start(self):
        self._stop_event.clear()
        self.inputThread.start()

    def stop(self,reason=""):
        if not self._stop_event.is_set():
            print("Connection stop called: " + reason)
            self.inputThread.stop()
            self.inputThread.join()
            self._stop_event.set()
            print("Connection stopped")

    def pause(self):
        if not self._pause_event.is_set():
            self._pause_event.set()
            self.inputThread.pause()
            print("Connection paused")

    def unpause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.inputThread.unpause()
            print("Connection started Again")

    def paused(self):
        return self._pause_event.is_set() and self.inputThread.paused()

    def stopped(self):
        return self._stop_event.is_set() and self.inputThread.stopped()

class InputThread(threading.Thread):
    def __init__(self,parent):
        super(InputThread, self).__init__()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.parent=parent
        self.startTime=0

    def stop(self):
        if not self._stop_event.is_set():
            self.parent.outQueue.put(None)
            self._stop_event.set()
            print("InputThread stopped")

    def pause(self):
        if not self._pause_event.is_set():
            self._pause_event.set()
            print("InputThread paused")

    def unpause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            print("InputThread started Again")

    def stopped(self):
        return self._stop_event.is_set()

    def paused(self):
        return self._pause_event.is_set()

    def run(self):
        import random
        import math
        import time
        print("Running Dummy InputThread")
        a=random.random()
        self.startTime=time.time()
        while not self.stopped():
            if not self.paused():
                t=time.time()-self.startTime
                self.parent.outQueue.put([[t,math.sin(a*t)]])
                time.sleep(0.1)
            else:
                time.sleep(0.5)
