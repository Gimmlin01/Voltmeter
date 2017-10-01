#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,QHBoxLayout, QVBoxLayout,QTabWidget,QFileDialog,QLCDNumber,QGroupBox,QRadioButton,QGridLayout,QPushButton,QCheckBox,QSpinBox,QLabel,QColorDialog
from PyQt5.QtGui import QIcon,QColor
from PyQt5.QtCore import QSettings,QSize,QPoint
from functools import partial
import numpy as np

#custom imports
from Plotter import Plot

#Constants
Connections=["Dummy","UT61C"]
defaultColors=[
QColor(5, 252, 82, 255),QColor(8, 248, 253, 255),QColor(253, 7, 241, 255),QColor(75, 0, 255, 255),
QColor(255, 0, 0, 255),QColor(239, 41, 41, 255),QColor(138, 226, 52, 255),QColor(114, 159, 207, 255),
QColor(173, 127, 168, 255),QColor(136, 138, 133, 255),QColor(164, 0, 0, 255),QColor(206, 92, 0, 255),
QColor(196, 160, 0, 255),QColor(78, 154, 6, 255),QColor(32, 74, 135, 255),QColor(92, 53, 102, 255)
]
#define mainPage
class MainPage(QMainWindow):
    def __init__(self):
        super(MainPage,self).__init__()
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        #Array to save the Multiple Plots
        self.Plots=[]
        self.lcdPage=LcdPage()
        self.settingsPage=SettingsPage()
        self.initUI()
    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('mainPageSize', QSize(1000, 400)))
        self.move(self.settings.value('mainPagePos', QPoint(50, 50)))
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
        self.lcdPageToogleAction = QAction(QIcon('icons/NumberIcon.png'), '&LCD', self)
        self.lcdPageToogleAction.setShortcut('Ctrl+L')
        self.lcdPageToogleAction.setStatusTip('Display Current Value')
        self.lcdPageToogleAction.triggered.connect(self.toggleLcd)

        #add Action to Open Settings
        self.openSettingsAction = QAction(QIcon('icons/SettingsIcon.png'), '&Settings', self)
        self.openSettingsAction.setShortcut('Ctrl+E')
        self.openSettingsAction.setStatusTip('Open Settings')
        self.openSettingsAction.triggered.connect(self.openSettings)

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
        fileMenu.addAction(self.openSettingsAction)
        fileMenu.addAction(self.exitAction)

        #create Toolbar
        toolbar = self.addToolBar('Tool')
        #Toolbar entrys
        toolbar.addAction(self.exitAction)
        toolbar.addAction(self.newMeasurementAction)
        toolbar.addAction(self.startAction)
        toolbar.addAction(self.pauseAction)
        toolbar.addAction(self.stopAction)
        toolbar.addAction(self.lcdPageToogleAction)

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
            self.lcdPage.connectTo(currPlot)
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
            self.lcdPage.display(0.000)

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
        if not self.lcdPage.isVisible():
            self.lcdPage.display(0.000)
            self.lcdPage.show()
        else:
            self.lcdPage.close()

    #function to open Settings
    def openSettings(self):
        try:
            if not self.settingsPage.isVisible():
                self.settingsPage.show()
            else:
                self.settingsPage.close()
        except Exception as e:
            print(e)

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

        #close additional Windows
        self.lcdPage.close()
        self.settingsPage.close()

        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("mainPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("mainPagePos",self.pos())
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
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        self.initUI()

    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('lcdPageSize', QSize(250, 250)))
        self.move(self.settings.value('lcdPagePos', QPoint(1100, 50)))
        self.setWindowTitle('LCD Display')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))

    #connect the updateLcd function to the newData signal of the given plot
    def connectTo(self,plot):
        plot.newData.connect(self.updateLcd)

    #update displayed value
    def updateLcd(self,inpData):
        self.display(inpData[0][1])

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("lcdPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("lcdPagePos",self.pos())

#class for the Settings Dialog
class SettingsPage(QWidget):
    def __init__(self):
        super(SettingsPage,self).__init__()
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        self.initUI()

    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('settingsPageSize', QSize(250, 250)))
        self.move(self.settings.value('settingsPagePos', QPoint(1100, 50)))
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))
        self.grid = QGridLayout()

        #Create Menu to Choose Connections
        self.conGroupBox=QGroupBox("Connections")
        conVbox = QVBoxLayout()
        activeConnection = self.settings.value("connection","Dummy")
        for c in Connections:
            radio = QRadioButton(c)
            radio.toggled.connect(partial(self.setConnection,radio))
            conVbox.addWidget(radio)
            if (c==activeConnection):
                radio.setChecked(True)
        conVbox.addStretch(1)
        self.conGroupBox.setLayout(conVbox)
        self.grid.addWidget(self.conGroupBox)

        #Create Menu to Choose Plot appearing
        self.plotGroupBox=QGroupBox("Plot")
        plotVbox = QVBoxLayout()
        thickInp=QSpinBox()
        thickInp.setPrefix("Line Thickness: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("lineThickness", 3,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changeThickness)
        plotVbox.addWidget(thickInp)
        colors=self.settings.value("colors",defaultColors,QColor)
        plotHbox = QHBoxLayout()
        for c in range(16):
            cl=QPushButton()
            cl.setFixedSize(20,20)
            p = cl.palette()
            p.setColor(cl.backgroundRole(), colors[c])
            cl.setPalette(p)
            cl.setAutoFillBackground(True)
            plotHbox.addWidget(cl)
            cl.setFlat(True)
            cl.clicked.connect(partial(self.colorPicker,c))
            if (c==7):
                plotHbox.addStretch(1)
                plotVbox.addLayout(plotHbox)
                plotHbox = QHBoxLayout()
        plotHbox.addStretch(1)
        plotVbox.addLayout(plotHbox)
        plotVbox.addStretch(1)
        self.plotGroupBox.setLayout(plotVbox)
        self.grid.addWidget(self.plotGroupBox)

        #Create Menu to Choose Size/Pos saving
        self.exGroupBox=QGroupBox("Save on Exit")
        exVbox = QVBoxLayout()
        for s in ["Size","Position"]:
            cb = QCheckBox(s)
            cb.toggled.connect(partial(self.toggled,cb))
            exVbox.addWidget(cb)
            cb.setChecked(self.settings.value(s,True,bool))
        exVbox.addStretch(1)
        self.exGroupBox.setLayout(exVbox)
        self.grid.addWidget(self.exGroupBox)

        #Create Possibility to reset Settings
        settingsResetButton = QPushButton("Reset Settings")
        settingsResetButton.clicked.connect(lambda:self.resetSettings())
        self.grid.addWidget(settingsResetButton)

        #Create Possibility to reset Settings
        settingsCloseButton = QPushButton("Close Settings")
        settingsCloseButton.clicked.connect(lambda:self.close())
        self.grid.addWidget(settingsCloseButton)

        #set Grid as Layout
        self.setLayout(self.grid)

    def colorPicker(self,nr):
        colors=self.settings.value("colors",defaultColors,QColor)
        colors[nr] = QColorDialog.getColor(colors[nr])
        self.settings.setValue("colors",colors)
        QWidget().setLayout(self.grid)
        self.initUI()

    def setConnection(self,wich):
        if (wich.isChecked()):
            self.settings.setValue('connection', wich.text())

    def toggled(self,wich):
        self.settings.setValue(wich.text(), wich.isChecked())

    def resetSettings(self):
        QWidget().setLayout(self.grid)
        self.settings.clear()
        self.initUI()

    def changeThickness(self,thick):
        self.settings.setValue("lineThickness",thick)

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("settingsPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("settingsPagePos",self.pos())


if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window (opens a new Window if not bound into another widget)
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
