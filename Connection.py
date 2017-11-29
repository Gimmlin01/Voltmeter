#Connection class
#author: Michael Auer

import threading,time,os,importlib,sys
from queue import Queue
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox



class Connection(threading.Thread):
    def __init__(self):
        super(Connection, self).__init__()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._stop_event.set()
        self.outQueue=Queue()
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        self.device=None

    def initDevice(self):
        try:
            activeConnection = self.settings.value('connection', "Dummy")
            if activeConnection:
                sys.path.append(self.settings.value("path",""))
                folderModule = importlib.import_module("devices")
                deviceModule = importlib.import_module("devices."+activeConnection)
                importlib.reload(folderModule)
                importlib.reload(deviceModule)
                return getattr(deviceModule, activeConnection)()
        except Exception as e:
            text="Device not initiated"
            textd="There is a problem in the "+activeConnection+".py in the device folder.\nMake sure you Name each Device Class like its filename:\n Dummy -> Dummy.py"
            self.showDialog(t=text,td=textd,ti=str(e))

    def start(self):
        self.device=self.initDevice()
        if not self.device:
            return False
        if not self.device.isOpen():
            self.showDialog()
            return False

        print("Device Open")
        self._stop_event.clear()
        super(Connection, self).start()
        return True

    def stop(self,reason=""):
        print("Connection stop called: " + reason)
        if not self._stop_event.is_set():
            self.outQueue.put(None)
            self._stop_event.set()
            self.join()
            print("Connection stopped")

    def pause(self):
        if not self._pause_event.is_set():
            self._pause_event.set()
            print("Connection paused")

    def unpause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            print("Connection unpaused")

    def stopped(self):
        return self._stop_event.is_set()

    def paused(self):
        return self._pause_event.is_set()

    def run(self):
        print("Connection started")
        while not self.stopped():
            if not self.paused():
                value=self.device.measure()
                self.outQueue.put(value)
            else:
                time.sleep(0.5)

    def showDialog(self,t=None,ti=None,td=None):
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Warning)
       if (t==None):
           t,ti,td = self.device.warningText
       msg.setText(t)
       msg.setInformativeText(ti)
       msg.setWindowTitle("Warning")
       msg.setDetailedText(td)
       msg.setStandardButtons(QMessageBox.Ok)
       retval = msg.exec_()
