#! /usr/bin/python3
# author: Michael Auer

#imports
import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, QWidget, QMessageBox, QAction,qApp
from PyQt5.QtGui import QIcon

#define mainPage
class MainPage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        exitAction = QAction(QIcon('icons/ExitIcon.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        startAction = QAction(QIcon('icons/StartIcon.png'), '&Exit', self)
        startAction.setShortcut('Ctrl+R')
        startAction.setStatusTip('Start Measurement')
        startAction.triggered.connect(self.startMeasure)

        self.statusBar().showMessage("Working")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(startAction)
        toolbar = self.addToolBar('Tool')
        toolbar.addAction(exitAction)
        toolbar.addAction(startAction)
        self.statusBar().showMessage('Ready')

        self.setGeometry(1000, 500, 300, 220)
        self.setWindowTitle('Voltmeter')
        self.setWindowIcon(QIcon('icons/AppIcon.png'))
        self.show()

    def startMeasure(self):
        print("lol")
    # def closeEvent(self, event):
    #
    #     reply = QMessageBox.question(self, 'Message',
    #         "Are you sure to quit?", QMessageBox.Yes |
    #         QMessageBox.No, QMessageBox.No)
    #
    #     if reply == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


if __name__ == "__main__":
    #create Main app
    app = QApplication(sys.argv)

    #create new Window
    MainWindow=MainPage()

    #start main loop
    sys.exit(app.exec_())
