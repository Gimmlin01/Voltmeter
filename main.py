#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget,QFileDialog,QLCDNumber
from PyQt5.QtGui import QIcon
import numpy as np

#custom imports
from Plotter import Plot

#define mainPage
class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage,self).__init__()

        #Array to save the Multiple Plots
        self.Plots=[]
        self.lcd=LcdPage()
        self.initUI()

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

        #add Action to Display Current Value LCD Style
        self.lcdToogleAction = QAction(QIcon('icons/NumberIcon.png'), '&LCD', self)
        self.lcdToogleAction.setShortcut('Ctrl+L')
        self.lcdToogleAction.setStatusTip('Display Current Value')
        self.lcdToogleAction.triggered.connect(self.toggleLcd)

        #add Action to Save the Data of the current Plot
        self.saveDataAction = QAction(QIcon('icons/SaveIcon.png'), '&Save', self)
        self.saveDataAction.setShortcut('Ctrl+S')
        self.saveDataAction.setStatusTip('Save Plot Data')
        self.saveDataAction.triggered.connect(self.saveData)

        #add Action to Load the Data
        self.loadDataAction = QAction(QIcon('icons/LoadIcon.png'), '&Open', self)
        self.loadDataAction.setShortcut('Ctrl+O')
        self.loadDataAction.setStatusTip('Open saved Plot Data')
        self.loadDataAction.triggered.connect(self.loadData)

        #add Action to Start Measuring again
        self.startAction = QAction(QIcon('icons/StartIcon.png'), '&Start', self)
        self.startAction.setShortcut('Ctrl+R')
        self.startAction.setStatusTip('Start Measurement')
        self.startAction.triggered.connect(self.startMeasure)
        self.startAction.setEnabled(False)

        #add Action to Pause Measuring
        self.pauseAction = QAction(QIcon('icons/PauseIcon.png'), '&Pause', self)
        self.pauseAction.setShortcut('Ctrl+P')
        self.pauseAction.setStatusTip('Pause Measurement')
        self.pauseAction.triggered.connect(self.pauseMeasure)
        self.pauseAction.setEnabled(False)

        #add Action to Stop Measuring
        self.stopAction = QAction(QIcon('icons/StopIcon.png'), '&Stop', self)
        self.stopAction.setShortcut('Ctrl+C')
        self.stopAction.setStatusTip('Stop Measurement')
        self.stopAction.triggered.connect(self.stopMeasure)
        self.stopAction.setEnabled(False)

        #create new MenuBar
        menubar = self.menuBar()
        #MenuBar entrys
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newMeasurementAction)
        fileMenu.addAction(self.saveDataAction)
        fileMenu.addAction(self.loadDataAction)
        fileMenu.addAction(self.exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(self.exitAction)
        toolbar.addAction(self.newMeasurementAction)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.pauseAction)
        toolbar.addAction(self.stopAction)
        toolbar.addAction(self.lcdToogleAction)

        #create Main Widget
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.tabWidget.tabCloseRequested.connect(self.tabClosed)
        #set Central Widget to Main Widget
        self.setCentralWidget(self.tabWidget)

        #show MainWindow
        self.show()

    #function to start a new Measuring
    def newMeasure(self):
        self.newPlot(start=True)

    #function to make a new Plot
    def newPlot(self,start=False):
        #create new Plot
        plotWidget = Plot(self)
        self.Plots.append(plotWidget)
        if start:
            plotWidget.start()
        #New Plot Tab
        plotTab = QWidget()
        plotLayout = QVBoxLayout()
        plotLayout.addWidget(plotWidget)
        plotTab.setLayout(plotLayout)
        self.tabWidget.addTab(plotTab, 'Plot ' + str(len(self.Plots)))
        return plotWidget

    #function to start Measuring again
    def startMeasure(self):
        #find the current Plot in the displayed tab
        currPlot = self.tabWidget.currentWidget().findChild(Plot)
        if currPlot.stopped():
            #if its stopped start it
            currPlot.start()
        elif currPlot.paused():
            #if its paused start it
            currPlot.unpause()
        else:
            print("Plot neither stopped nor paused")
        self.startAction.setEnabled(False)
        self.pauseAction.setEnabled(True)
        self.stopAction.setEnabled(True)

    #function to pause Measuring
    def pauseMeasure(self):
        self.tabWidget.currentWidget().findChild(Plot).pause("User Paused")
        self.startAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(True)

    #function to stop Measuring
    def stopMeasure(self):
        #stop current plot
        self.tabWidget.currentWidget().findChild(Plot).stop("User Stopped")
        #change Actions
        self.startAction.setEnabled(True)
        self.pauseAction.setEnabled(False)
        self.stopAction.setEnabled(False)

    #function to Handle if User Changes the Tab
    def tabChanged(self):
        currWidget=self.tabWidget.currentWidget()
        if not currWidget==None:
            currPlot=currWidget.findChild(Plot)
            #disconnect all Signals from all Plots (saves ressources), so they don't update their plot when not shown
            for p in self.Plots:
                p.disconnectAll()
            #connect the current Plot (live Updates)
            currPlot.connect()
            #connect the Lcd to the current Plot
            self.lcd.connectTo(currPlot)
            #fix Actions
            if currPlot.stopped():
                self.startAction.setEnabled(True)
                self.pauseAction.setEnabled(False)
                self.stopAction.setEnabled(False)
            elif currPlot.paused():
                self.startAction.setEnabled(True)
                self.pauseAction.setEnabled(False)
                self.stopAction.setEnabled(True)
            else:
                self.startAction.setEnabled(False)
                self.pauseAction.setEnabled(True)
                self.stopAction.setEnabled(True)
        else:
            self.startAction.setEnabled(False)
            self.pauseAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.lcd.display(0.000)

    #function to handle Tab Close
    def tabClosed(self,tab_index):
        self.tabWidget.widget(tab_index).findChild(Plot).stop("Tab Closed")
        self.tabWidget.removeTab(tab_index)

    #function to save the data of the Current opened Plot
    def saveData(self):
        fileName = QFileDialog.getSaveFileName(self, 'Dialog Title', '', filter='*.txt')[0]
        if fileName != "":
            #enshure it is a .txt file
            if not fileName[len(fileName)-4:] == ".txt":
                fileName=fileName+".txt"
            np.savetxt(fileName,self.tabWidget.currentWidget().findChild(Plot).data)

    #function to load data to a new Plot
    def loadData(self):
        fileName = QFileDialog.getOpenFileName(self, 'Dialog Title', '', filter='*.txt')[0]
        if fileName != "":
            loadedData = np.loadtxt(fileName)
            plotWidget = self.newPlot()
            plotWidget.data=loadedData
            plotWidget.updatePlot()

    #function to toggle Lcd on and off
    def toggleLcd(self):
        if not self.lcd.isVisible():
            self.lcd.display(0.000)
            self.lcd.show()
        else:
            self.lcd.close()


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
        self.lcd.close()
        for p in self.Plots:
            #Stop Connection and its Thread
            if p.connection.stopped():
                print("Connection already stopped")
            else:
                p.connection.stop("App CloseEvent")
            #Stop Plot and its Thread
            if p.stopped():
                print("Plot already stopped")
            else:
                p.stop("App CloseEvent")

        allstopped=True
        for p in self.Plots:
            if p.connection.stopped() and p.stopped():
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

#class for the LCD Page witch shows the Current Value
class LcdPage(QLCDNumber):
    def __init__(self):
        super(LcdPage,self).__init__()
        self.initUI()

    def initUI(self):
        #cosmeticals
        self.setGeometry(1100, 50, 250 , 250)
        self.setWindowTitle('LCD Display')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))

    #connect the updateLcd function to the newData signal of the given plot
    def connectTo(self,plot):
        plot.newData.connect(self.updateLcd)

    #update displayed value
    def updateLcd(self,inpData):
        self.display(inpData[0][1])

if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window (opens a new Window if not bound into another widget)
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
