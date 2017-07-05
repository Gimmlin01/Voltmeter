#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import numpy as np
import time
import threading

#custom imports
from Connection import Connection

#define mainPage
class MainPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.Connection=None
        self.Plotter=None

    def initUI(self):
        #cosmeticals
        self.setGeometry(50, 50, 1000, 500)
        self.setWindowTitle('Voltmeter')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))

        #add Action to Close Programm
        exitAction = QAction(QIcon('icons/ExitIcon.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        #add Action to Start Measuring
        startAction = QAction(QIcon('icons/StartIcon.png'), '&Exit', self)
        startAction.setShortcut('Ctrl+R')
        startAction.setStatusTip('Start Measurement')
        startAction.triggered.connect(self.startMeasure)

        #create new MenuBar
        menubar = self.menuBar()
        #MenuBar entrys
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(startAction)
        fileMenu.addAction(exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(exitAction)
        toolbar.addAction(startAction)

        #create Plot
        self.plotWidget = pg.PlotWidget()

        #create Main Widget
        self.tabWidget = QTabWidget()

        #New Plot Tab
        self.plotTab = QWidget()
        self.plotLayout = QVBoxLayout()
        self.plotLayout.addWidget(self.plotWidget)
        self.plotTab.setLayout(self.plotLayout)
        self.tabWidget.addTab(self.plotTab, 'Plot')

        #set Central Widget to Main Widget
        self.setCentralWidget(self.tabWidget)

        #show MainWindow
        self.show()

    #function to start Measuring
    def startMeasure(self):
        #establish Connection
        self.Connection=Connection()

        #create new Plotter Thread to liveplot things
        self.Plotter=Plotter(inQueue=self.Connection.outQueue)
        self.Plotter.newData.connect(self.updatePlot)
        self.Plotter.start()

    #function to update the plot (must happen in Main Thread)
    def updatePlot(self,data):
        self.plotWidget.plot(data, clear=True)
        #show status
        self.statusBar().showMessage("Working")

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        print("App called CloseEvent")
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes |
        #     QMessageBox.No, QMessageBox.No)
        #
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

        #Stop Connection and its Thread
        if not self.Connection == None:
            if self.Connection.stopped():
                print("Connection already stopped")
            else:
                self.Connection.stop("App CloseEvent")
        #Stop Plotter and its Thread
        if not self.Plotter == None:
            if self.Plotter.stopped():
                print("Plotter already stopped")
            else:
                self.Plotter.stop("App CloseEvent")
        #check if both are stopped
        if not self.Connection.stopped() or not self.Plotter.stopped():
            #ignore the event
            event.ignore()
            #try again
            self.close()
        else:
            event.accept()


#Plotter Class inherits from QThread
class Plotter(pg.QtCore.QThread):
    #newData Signal
    newData = pg.QtCore.Signal(object)

    def __init__(self,inQueue):
        super(Plotter, self).__init__()
        self._stop_event = threading.Event()
        self.inQueue=inQueue
        self.data=[[0,0]]

    #make Thead stoppable
    def stop(self,reason=""):
        self._stop_event.set()
        print("Plotter stopped: " + reason)

    #function to check if Thread has stopped
    def stopped(self):
        return self._stop_event.is_set()

    #custom run function
    def run(self):
        print("Running Default Plotter")
        while not self.stopped():
            #get Item from inQueue
            inpData=self.inQueue.get()
            if inpData == None:
                self.stop("Input Queue shutdown")
            else:
                #append the Item to the data array
                self.data=np.append(self.data,inpData,axis=0)
                #broadcast the new data array
                self.newData.emit(self.data)



if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
