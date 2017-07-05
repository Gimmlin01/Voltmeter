#Default Connection class

import threading
from queue import Queue
from time import sleep


class Connection(object):
    def __init__(self):
        super(Connection,self).__init__()
        self._stop_event = threading.Event()
        self.outQueue=Queue()
        self.measureThread=InputThread(self.outQueue)
        self.measureThread.start()

    def stop(self):
        self._stop_event.set()
        self.measureThread.stop()
        print("Connection stop")

    def stopped(self):
        return self._stop_event.is_set() and self.measureThread.stopped()

class InputThread(threading.Thread):
    def __init__(self,outQueue):
        super(InputThread, self).__init__()
        self._stop_event = threading.Event()
        self.outQueue=outQueue

    def stop(self):
        self._stop_event.set()
        print("Thread stop")


    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("a")
        while not self.stopped():
            print("lool")
            sleep(10)
