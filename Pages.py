from PyQt5.QtWidgets import QWidget,QHBoxLayout, QVBoxLayout,QGroupBox,QRadioButton,QGridLayout,QPushButton,QCheckBox,QSpinBox,QLabel,QColorDialog,QLCDNumber,QGridLayout
from PyQt5.QtGui import QIcon,QColor,QFont
from PyQt5.QtCore import QSettings,QSize,QPoint,Signal,Qt
from functools import partial
import sys,os

defaultColors=[
QColor(5, 252, 82, 255),QColor(8, 248, 253, 255),QColor(253, 7, 241, 255),QColor(75, 0, 255, 255),
QColor(255, 0, 0, 255),QColor(239, 41, 41, 255),QColor(138, 226, 52, 255),QColor(114, 159, 207, 255),
QColor(173, 127, 168, 255),QColor(136, 138, 133, 255),QColor(164, 0, 0, 255),QColor(206, 92, 0, 255),
QColor(196, 160, 0, 255),QColor(78, 154, 6, 255),QColor(32, 74, 135, 255),QColor(92, 53, 102, 255)
]

prefix = {-24:"y",-21:"z",-18:"a",-15:"f",-12:"p",-9:"n",-6:"u",-3:"m",-2:"c",-1:"d",0:"",
                3:"k",6:"M",9:"G",12:"T",15:"P",18:"E",21:"Z",24:"Y"}

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

#class for the Settings Dialog
class SettingsPage(QWidget):

    uiChange = Signal(object)

    def __init__(self):
        super(SettingsPage,self).__init__()
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        self.resize(self.settings.value('settingsPageSize', QSize(250, 250)))
        self.move(self.settings.value('settingsPagePos', QPoint(1100, 50)))
        self.devs=[]
        self.initDevices()
        self.initUI()

    def initDevices(self):
        self.devs=[]
        try:
            devs=os.listdir("devices")
            for d in devs:
                if d[-3:] == ".py" and d[:2] != "__":
                    print(d+" found!")
                    self.devs.append(d[:-3])
        except:
            print("Device folder not found")
            devs=None


    def show(self):
        QWidget().setLayout(self.grid)
        self.initDevices()
        self.initUI()
        super(SettingsPage, self).show()

    def initUI(self):
        #cosmeticals
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.grid = QGridLayout()

        #Create Menu to Choose Connections
        self.conGroupBox=QGroupBox("Connections")
        conVbox = QVBoxLayout()
        activeConnection = self.settings.value("connection","Dummy")
        for d in self.devs:
            radio = QRadioButton(d)
            radio.toggled.connect(partial(self.setConnection,radio))
            conVbox.addWidget(radio)
            if (d==activeConnection):
                radio.setChecked(True)
        conVbox.addStretch(1)
        self.conGroupBox.setLayout(conVbox)
        self.grid.addWidget(self.conGroupBox)

        #Create Menu to set Appearence
        self.uiGroupBox=QGroupBox("UI")
        uiVbox = QVBoxLayout()
        thickInp=QSpinBox()
        thickInp.setPrefix("Axis Lable: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("axisThickness", 20,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changeAxisThickness)
        uiVbox.addWidget(thickInp)
        thickInp=QSpinBox()
        thickInp.setPrefix("Tick Lable: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("tickThickness", 15,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changeTickThickness)
        uiVbox.addWidget(thickInp)
        self.uiGroupBox.setLayout(uiVbox)
        self.grid.addWidget(self.uiGroupBox)

        #Create Menu to Choose Plot appearing
        self.plotGroupBox=QGroupBox("Plot")
        plotVbox = QVBoxLayout()
        thickInp=QSpinBox()
        thickInp.setPrefix("Line Thickness: ")
        thickInp.setSuffix("px")
        lineThick=self.settings.value("lineThickness", 3,int)
        thickInp.setValue(lineThick)
        thickInp.valueChanged.connect(self.changeLineThickness)
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
        self.uiChange.emit(None)
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
        self.uiChange.emit(None)

    def changeAxisThickness(self,thick):
        self.settings.setValue("axisThickness",thick)
        self.uiChange.emit(None)

    def changeTickThickness(self,thick):
        self.settings.setValue("tickThickness",thick)
        self.uiChange.emit(None)

    def changeLineThickness(self,thick):
        self.settings.setValue("lineThickness",thick)
        self.uiChange.emit(None)

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("settingsPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("settingsPagePos",self.pos())



#class for the LCD Page witch shows the Current Value
class LcdPage(QWidget):
    def __init__(self):
        super(LcdPage,self).__init__()
        self.settings = QSettings('yoxcu.de', 'Voltmeter')
        self.resizeEvent = self.onResize
        self.initUI()

    def onResize(self,event):
        self.font.setPixelSize(self.height()*0.65)
        self.text.setFont(self.font)

    def initUI(self):
        #cosmeticals
        self.resize(self.settings.value('lcdPageSize', QSize(200, 350)))
        self.move(self.settings.value('lcdPagePos', QPoint(1100, 50)))
        self.setWindowTitle('LCD Display')
        self.setWindowIcon(QIcon(resource_path('icons/AppIcon.png')))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        grid=QGridLayout()
        self.lcd=QLCDNumber()
        self.lcd.setDigitCount(5)
        self.text=QLabel("unit")
        self.font=QFont()
        self.font.setPixelSize(self.height()*0.65)
        self.text.setFont(self.font)
        grid.addWidget(self.lcd,0,0)
        grid.addWidget(self.text,0,1)
        grid.setColumnStretch(0,5)
        grid.setColumnStretch(1,1)
        self.setLayout(grid)

    def display(self,what):
        self.lcd.display(what)

    #connect the updateLcd function to the newData signal of the given plot
    def connectTo(self,plot):
        plot.newData.connect(self.updateLcd)

    #update displayed value
    def updateLcd(self,inpData):
        number,prefix = self.parseNumber(inpData[1])
        self.display(round(number,2))
        self.lcd.setDigitCount(len(str(round(number,2))))
        self.text.setText(str(prefix) + str(inpData[3][1]))

    def parseNumber(self,n,s=0):
        nt=abs(n)
        if nt == 0:
            return (0,prefix[0])
        elif nt >1000:
            return self.parseNumber(n/1000,s+3)
        elif nt<1:
            if s > -3:
                return self.parseNumber(n*10,s-1)
            elif s<-24:
                return (0,prefix[0])
            else:
                return self.parseNumber(n*1000,s-3)
        elif nt<10:
                return (round(n,2),prefix[s])
        elif nt<100:
            return (round(n,1),prefix[s])
        else:
            return (round(n,0),prefix[s])

    #override the closeEvent function to catch the event and do things
    def closeEvent(self, event):
        #save Window sizes
        if (self.settings.value("Size",True,bool)):
            self.settings.setValue("lcdPageSize",self.size())
        if (self.settings.value("Position",True,bool)):
            self.settings.setValue("lcdPagePos",self.pos())
