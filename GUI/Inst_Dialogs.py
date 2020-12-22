#! encoding = utf-8


from PyQt5 import QtCore, QtWidgets, QtGui
from GUI import SharedWidgets as Shared
from API import general as api_gen
from API import AWGapi as api_awg
from API import PNAapi as api_pna
from API import LightAPI as api_light

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
        self.parent.AWGHandle = api_gen.open_inst(self.selAWG.currentText())
        self.parent.PNAHandle = api_pna.PNASCPI(self.selPNA.currentText())
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
        self.awgip='192.168.1.103'

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


class AWGInfoDialog(QtWidgets.QDialog):
    '''AWG设置窗口'''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
