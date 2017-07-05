#! /usr/bin/python3
# author: Michael Auer

#Standart imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction
from PyQt5.QtGui import QIcon
#custom imports
from Connection import Connection
#define mainPage
class MainPage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.Connection=None


    def initUI(self):
        exitAction = QAction(QIcon('icons/ExitIcon.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        startAction = QAction(QIcon('icons/StartIcon.png'), '&Exit', self)
        startAction.setShortcut('Ctrl+R')
        startAction.setStatusTip('Start Measurement')
        startAction.triggered.connect(self.startMeasure)

        self.statusBar().showMessage("Working")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(startAction)
        fileMenu.addAction(exitAction)
        toolbar = self.addToolBar('Tool')
        toolbar.addAction(exitAction)
        toolbar.addAction(startAction)
        self.statusBar().showMessage('Ready')

        self.setGeometry(1000, 500, 300, 220)
        self.setWindowTitle('Voltmeter')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))
        self.show()

    def startMeasure(self):
        self.Connection=Connection()


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
        if not self.Connection == None:
            self.Connection.stop()
        event.accept()



if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
