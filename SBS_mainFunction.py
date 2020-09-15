import visa

from SBSInterface import *
from SBSPortInfo import *
import sys
import pyvisa
import SBS_DSP

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog

from SBSInterface import Ui_SBSsystem
from SBSPortInfo import Ui_Dialog


class Interface_SBS(QtWidgets.QMainWindow, Ui_SBSsystem):
    def __init__(self,parent=None):
        QMainWindow.__init__(self)
        self.main_ui=Ui_SBSsystem()
        self.main_ui.setupUi(self)
        #super(Interface_SBS, self).__init__(parent=parent)
        #self.setupUi(self)

    #def Check_Button_click(self):
     #  self.AWGs.setText("PASS")

class PortInfo_SBS(QtWidgets.QDialog,Ui_Dialog):
    def __init__(self):
        QMainWindow.__init__(self)
        self.child=Ui_Dialog()
        self.child.setupUi(self)
        self.child.iplineEdit_AWG.setInputMask('000.000.000.000;_')
        self.child.iplineEdit_EVNA.setInputMask('000.000.000.000;_')
        self.child.iplineEdit_OSA.setInputMask('000.000.000.000;_')

    def accept(self):
        AWGip=child.iplineEdit_AWG.text()
        EVNAip=child.iplineEdit_EVNA.text()
        OSAip=child.iplineEdit_OSA.text()
        EDFA1com=child.comboBox_EDFA1.currentText()
        EDFA2com=child.comboBox_EDFA2.currentText()
        DCcom=child.comboBox_DC.currentText()
        TLScom=child.comboBox_TLS.currentText()

##Keysight PNA Network Analyzer N5225A##
class N5225A():
    def __init__(self,ip,visaDLL=None,*args):
        self.ip=ip
        self.visaDLL='C:\Windows\System32\visa64.dll' if visaDLL is None else visaDLL
        self.address='TCPIP::%s::inst0::INSTR' % self.ip
        self.resourceManager = visa.ResourceManager(self.visaDLL)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window= Interface_SBS()
    child=PortInfo_SBS()

    #通过按钮将两个窗体关联
    btn=window.main_ui.Echeck
    btn.clicked.connect(child.show)

    #显示
    window.show()
    sys.exit(app.exec_())
