#! encoding = utf-8


from PyQt5 import QtCore, QtWidgets, QtGui
from GUI import SharedWidgets as Shared
from API import general as api_gen
from API import AWGapi as api_awg
from API import PNAapi as api_pna
from API import LightAPI as api_light
import re

from pyqtgraph import siFormat
import pyqtgraph as pg


class selectInstDialog(QtWidgets.QDialog):
    '''
    设备通信方式选择，利用VISA结合NI MAX自动搜索设备ip及COM地址
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(400, 400)
        self.setWindowTitle('Select Inst_Port')

        refreshButton = QtGui.QPushButton('Refresh Available Instrument List')
        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))

        self.availableInst = QtWidgets.QLabel()
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtWidgets.QWidget()
        selInstLayout = QtWidgets.QFormLayout()
        self.selAWG = QtWidgets.QComboBox()
        self.selAWG.addItems(['N.A.'])
        self.selAWG.addItems(instList)
        self.selPNA = QtWidgets.QComboBox()
        self.selPNA.addItems(['N.A.'])
        self.selPNA.addItems(instList)
        self.selEDFA1 = QtWidgets.QComboBox()
        self.selEDFA1.addItems(['N.A.'])
        self.selEDFA1.addItems(instList)
        self.selEDFA2 = QtWidgets.QComboBox()
        self.selEDFA2.addItems(['N.A.'])
        self.selEDFA2.addItems(instList)
        self.selLight = QtWidgets.QComboBox()
        self.selLight.addItems(['N.A.'])
        self.selLight.addItems(instList)

        selInstLayout.addRow(QtWidgets.QLabel('AWG'), self.selAWG)
        selInstLayout.addRow(QtWidgets.QLabel('PNA'), self.selPNA)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA1'), self.selEDFA1)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA2'), self.selEDFA2)
        selInstLayout.addRow(QtWidgets.QLabel('LightWave'), self.selLight)

        selInst.setLayout(selInstLayout)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.availableInst, 0, 0, 1, 2)
        mainLayout.addWidget(refreshButton, 1, 0, 1, 2)
        mainLayout.addWidget(selInst, 2, 0, 1, 2)
        mainLayout.addWidget(cancelButton, 3, 0)
        mainLayout.addWidget(acceptButton, 3, 1)

        self.setLayout(mainLayout)

        refreshButton.clicked.connect(self.refresh)
        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

    def refresh(self):
        '''
        刷新设备列表
        :return:
        '''
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        item_count = self.selAWG.count()

        for i in range(item_count - 1):
            self.selAWG.removeItem(1)
            self.selPNA.removeItem(1)
            self.selEDFA1.removeItem(1)
            self.selEDFA2.removeItem(1)
            self.selLight.removeItem(1)
        self.selAWG.addItems(instList)
        self.selPNA.addItems(instList)
        self.selEDFA1.addItems(instList)
        self.selEDFA2.addItems(instList)
        self.selLight.addItems(instList)


    def accept(self):
        # 关闭旧的设备连接
        api_gen.close_inst(self.parent.AWGHandle,
                           self.parent.PNAHandle,
                           self.parent.LightHandle,
                           self.parent.EDFA1Handle,
                           self.parent.EDFA2Handle,)
        # 开启新的设备连接
        AWGIP=re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',str(self.selAWG.currentText()),re.S)
        PNAIP=re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',str(self.selPNA.currentText()),re.S)
        self.parent.AWGHandle = api_awg.M9502A(AWGIP)
        self.parent.PNAHandle = api_pna.PNASCPI(PNAIP)
        self.parent.LightHandle = api_light.LightSCPI(self.selLight.currentText())
        self.parent.EDFA1Handle = api_gen.open_inst(self.selEDFA1.currentText())
        self.parent.EDFA2Handle = api_gen.open_inst(self.selEDFA2.currentText())

        self.done(True)

class manualInstDialog(QtWidgets.QDialog):
    '''
    手动输入设备IP
    '''
    def __init__(self,parent):
        QtWidgets.QDialog.__init__(self,parent)
        self.parent=parent
        self.setMinimumSize(200,200)
        self.setWindowTitle('Manual Input Inst_IP')
        self.awgip='192.168.1.102'

        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))

        ManualInst=QtWidgets.QWidget()
        ManualInstLayout=QtWidgets.QFormLayout()
        self.AWGIP=QtWidgets.QWidget()
        self.AWGIPFill=QtWidgets.QLineEdit()
        self.AWGIPFill.setInputMask("000.000.000.000")

        self.PNAIP=QtWidgets.QWidget()
        self.PNAIPFill=QtWidgets.QLineEdit()
        self.PNAIPFill.setInputMask("000.000.000.000")

        ManualInstLayout.addRow("AWG_IP",self.AWGIPFill)
        ManualInstLayout.addRow("PNA_IP",self.PNAIPFill)

        ManualInst.setLayout(ManualInstLayout)

        mainLayout=QtWidgets.QGridLayout()
        mainLayout.addWidget(ManualInst,0,0,2,1)
        mainLayout.addWidget(acceptButton,3,1)
        mainLayout.addWidget(cancelButton,3,0)
        self.setLayout(mainLayout)

        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

        # 更新后台ip
        self.AWGIPFill.textChanged.connect(self.updateIP)
        self.PNAIPFill.textChanged.connect(self.updateIP)

    def updateIP(self):
        self.awgip=self.AWGIPFill.text()
        self.pnaip=self.PNAIPFill.text()

    def accept(self):
        if self.awgip=='N.A.':
            return None
        else:
            try:
                self.parent.AWGHandle=api_awg.M9502A(self.awgip,reset=True)
                print(self.parent.AWGHandle)
                self.done(True)
            except:
                return None

        if self.pnaip=='N.A.':
            return None
        else:
            try:
                self.parent.PNAHandle=api_pna.PNASCPI(self.pnaip,reset=True)
                print(self.parent.PNAHandle)
                self.done(True)
            except:
                return None

        self.done(True)


class viewInstDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)

        self.setMinimumSize(400, 400)
        self.setWindowTitle('View Instrument Status')

class CloseSelInstDialog(QtWidgets.QDialog):
    '''
    关闭设备
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(400,400)
        self.setWindowTitle('Close Instrument')

        inst=QtWidgets.QWidget()
        self.awgToggle=QtWidgets.QCheckBox()
        self.pnaToggle=QtWidgets.QCheckBox()
        self.EDFA1Toggle=QtWidgets.QCheckBox()
        self.EDFA2Toggle=QtWidgets.QCheckBox()
        self.LightToggle=QtWidgets.QCheckBox()

        instLayout=QtWidgets.QFormLayout()
        instLayout.addRow(QtWidgets.QLabel('Instrument'),QtWidgets.QLabel('Status'))

        if self.parent.AWGHandle:
            self.awgToggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('AWG'),self.awgToggle)
        else:
            self.awgToggle.setCheckState(False)

        if self.parent.PNAHandle:
            self.pnaToggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('PNA'),self.pnaToggle)
        else:
            self.pnaToggle.setCheckState(False)

        if self.parent.EDFA1Handle:
            self.EDFA1Toggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('EDFA1'),self.EDFA1Toggle)
        else:
            self.EDFA1Toggle.setCheckState(False)

        if self.parent.EDFA2Handle:
            self.EDFA2Toggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('EDFA2'),self.EDFA2Toggle)
        else:
            self.EDFA2Toggle.setCheckState(False)

        inst.setLayout(instLayout)

        okButton=QtWidgets.QPushButton(Shared.btn_label('complete'))
        mainLayout=QtWidgets.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(QtWidgets.QLabel('No command will be sent before you hit the accept button'))
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        okButton.clicked.connect(self.accept)

    def close_inst_handle(self,inst_handle,check_state):

        if check_state and inst_handle:
            api_gen.close_inst(inst_handle)
            return None
        else:
            return inst_handle

    def accept(self):
        if self.awgToggle.isChecked() and self.parent.AWGHandle:
            # self.parent.AWGHandle=api_awg.M9502A.stop(ch=self.parent.AWGInfo.ChannelNum)
            self.parent.AWGHandle=self.close_inst_handle(self.parent.AWGHandle,
                                                         self.awgToggle.isChecked())

        self.parent.PNAHandle=self.close_inst_handle(self.parent.PNAHandle,
                                                     self.pnaToggle.isChecked())
        self.parent.EDFA1Handle=self.close_inst_handle(self.parent.EDFA1Handle,
                                                       self.EDFA1Toggle.isChecked())
        self.parent.EDFA2Handle=self.close_inst_handle(self.parent.EDFA2Handle,
                                                       self.EDFA2Toggle.isChecked())
        self.parent.LightHandle=self.close_inst_handle(self.parent.LightHandle,

                                                       self.LightToggle.isChecked())
        self.parent.Display==0
        self.close()



class AWGInfoDialog(QtWidgets.QDialog):
    '''AWG设置窗口'''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
