#! encoding = utf-8

import sys
from PyQt5 import QtWidgets

import GUI.SBSInterface

if __name__ =='__main__':
    app=QtWidgets.QApplication(sys.argv)

    window=GUI.MainWindow.MainWindow()
    window.show()

    sys.exit(app.exec_())