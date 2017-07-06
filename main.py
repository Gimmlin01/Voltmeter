#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget,QFileDialog
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
        self.Plots=[]

    def initUI(self):
        #cosmeticals
        self.setGeometry(50, 50, 1000, 500)
        self.setWindowTitle('Voltmeter')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))

        #add Action to Close Programm
        self.exitAction = QAction(QIcon('icons/ExitIcon.png'), '&Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

        #add Action to add New Plot and start Measuring
        self.newMeasurementAction = QAction(QIcon('icons/PlusIcon.png'), '&New', self)
        self.newMeasurementAction.setShortcut('Ctrl+N')
        self.newMeasurementAction.setStatusTip('Create New Measurement')
        self.newMeasurementAction.triggered.connect(self.newMeasure)

        #add Action to Save the Data
        self.saveDataAction = QAction(QIcon('icons/SaveIcon.png'), '&Save', self)
        self.saveDataAction.setShortcut('Ctrl+S')
        self.saveDataAction.setStatusTip('Save Plot Data')
        self.saveDataAction.triggered.connect(self.saveData)

        #add Action to Start Measuring again
        self.startAction = QAction(QIcon('icons/StartIcon.png'), '&Start', self)
        self.startAction.setShortcut('Ctrl+R')
        self.startAction.setStatusTip('Start Measurement')
        self.startAction.triggered.connect(self.startMeasure)
        self.startAction.setEnabled(False)

        #add Action to Stop Measuring
        self.stopAction = QAction(QIcon('icons/PauseIcon.png'), '&Stop', self)
        self.stopAction.setShortcut('Ctrl+P')
        self.stopAction.setStatusTip('Pause Measurement')
        self.stopAction.triggered.connect(self.stopMeasure)
        self.stopAction.setEnabled(False)

        #create new MenuBar
        menubar = self.menuBar()
        #MenuBar entrys
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newMeasurementAction)
        fileMenu.addAction(self.saveDataAction)
        fileMenu.addAction(self.exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(self.exitAction)
        toolbar.addAction(self.newMeasurementAction)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.stopAction)

        #create Main Widget
        self.tabWidget = QTabWidget()
        self.tabWidget.tabsClosable=True
        self.tabWidget.currentChanged.connect(self.tabChanged)

        #set Central Widget to Main Widget
        self.setCentralWidget(self.tabWidget)

        #show MainWindow
        self.show()

    #function to start a new Measuring
    def newMeasure(self):
        #create new Plot
        plotWidget = Plot(self)
        self.Plots.append(plotWidget)
        #New Plot Tab
        plotTab = QWidget()
        plotLayout = QVBoxLayout()
        plotLayout.addWidget(plotWidget)
        plotTab.setLayout(plotLayout)
        self.tabWidget.addTab(plotTab, 'Plot ' + str(len(self.Plots)))

    #function to start Measuring again
    def startMeasure(self):
        self.tabWidget.currentWidget().findChild(Plot).start()
        self.startAction.setEnabled(False)
        self.stopAction.setEnabled(True)

    #function to stop Measuring
    def stopMeasure(self):
        self.tabWidget.currentWidget().findChild(Plot).stop("User Stopped")
        self.startAction.setEnabled(True)
        self.stopAction.setEnabled(False)

    #function to Handle if User Changes the Tab
    def tabChanged(self):
        if self.tabWidget.currentWidget().findChild(Plot).stopped():
            self.startAction.setEnabled(True)
            self.stopAction.setEnabled(False)
        else:
            self.startAction.setEnabled(False)
            self.stopAction.setEnabled(True)

    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Dialog Title', '', filter='.txt')
        if fileName:
            np.savetxt(fileName[0]+fileName[1],self.tabWidget.currentWidget().findChild(Plot).data)
            print (fileName)

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

        for p in self.Plots:
            #Stop Connection and its Thread
            if p.Connection.stopped():
                print("Connection already stopped")
            else:
                p.Connection.stop("App CloseEvent")
            #Stop Plot and its Thread
            if p.stopped():
                print("Plot already stopped")
            else:
                p.stop("App CloseEvent")

        allstopped=True
        for p in self.Plots:
            if p.Connection.stopped() and p.stopped():
                allstopped=True
            else:
                allstopped=False

        #check if all are stopped
        if not allstopped:
            #ignore the event
            event.ignore()
            #try again
            self.close()
        else:
            event.accept()


class Plot(pg.PlotWidget):
    def __init__(self,parent):
        super(Plot, self).__init__()

        #save parent
        self.parent=parent

        #establish ConnectionP
        self.Connection=Connection()

        #Stop Event to make it stoppable
        self._stop_event = threading.Event()

        #Define Array to contain Measured Points
        self.data=np.empty([0,2])

        self.start()

    def start(self):
        #create new Plot Thread to liveplot things
        self._stop_event.clear()
        self.PlotThread=PlotThread(self)
        self.PlotThread.newData.connect(self.updatePlot)
        self.PlotThread.start()

    #make Thead stoppable
    def stop(self,reason=""):
        if not self._stop_event.is_set():
            self.PlotThread.stop()
            self.PlotThread.wait()
            self._stop_event.set()
            print("Plot stopped: " + reason)

    #function to check if Thread has stopped
    def stopped(self):
        return self._stop_event.is_set() and self.PlotThread.stopped()

    #function to update the plot (must happen in Main Thread)
    def updatePlot(self,data):
        self.plot(data, clear=True)
        #show status
        self.parent.statusBar().showMessage("Working")


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
                self.newData.emit(self.parent.data)

if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
