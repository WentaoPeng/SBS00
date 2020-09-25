#! encoding = utf-8

import sys
from PyQt5 import QtGui

import GUI.SBSInterface

if __name__ =='__main__':
    app=QtGui.QApplication(sys.argv)

    window=GUI.SBSInterface.Ui_SBSsystem()
    window.show()

 iuiuiu   sys.exit(app.exec_())