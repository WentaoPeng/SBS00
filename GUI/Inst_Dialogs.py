#! encoding = utf-8


from PyQt5 import QtCore, QtWidgets, QtGui
from GUI import SharedWidgets as Shared
from API import general as api_gen

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
        self.selEVNA = QtWidgets.QComboBox()
        self.selEVNA.addItems(['N.A.'])
        self.selEVNA.addItems(instList)
        self.selEDFA1 = QtWidgets.QComboBox()
        self.selEDFA1.addItems(['N.A.'])
        self.selEDFA1.addItems(instList)
        self.selEDFA2 = QtWidgets.QComboBox()
        self.selEDFA2.addItems(['N.A.'])
        self.selEDFA2.addItems(instList)
        self.selOSA = QtWidgets.QComboBox()
        self.selOSA.addItems(['N.A.'])
        self.selOSA.addItems(instList)
        self.selDC1 = QtWidgets.QComboBox()
        self.selDC1.addItems(['N.A.'])
        self.selDC1.addItems(instList)
        self.selDC2 = QtWidgets.QComboBox()
        self.selDC2.addItems(['N.A.'])
        self.selDC2.addItems(instList)
        self.selDC3 = QtWidgets.QComboBox()
        self.selDC3.addItems(['N.A.'])
        self.selDC3.addItems(instList)

        selInstLayout.addRow(QtWidgets.QLabel('AWG'), self.selAWG)
        selInstLayout.addRow(QtWidgets.QLabel('EVNA'), self.selEVNA)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA1'), self.selEDFA1)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA2'), self.selEDFA2)
        selInstLayout.addRow(QtWidgets.QLabel('OSA'), self.selOSA)
        selInstLayout.addRow(QtWidgets.QLabel('DC1'), self.selDC1)
        selInstLayout.addRow(QtWidgets.QLabel('DC2'), self.selDC2)
        selInstLayout.addRow(QtWidgets.QLabel('DC3'), self.selDC3)

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

        item_count=self.selAWG.count()

        for i in range(item_count-1):
            self.selAWG.removeItem(1)
            self.selEVNA.removeItem(1)
            self.selEDFA1.removeItem(1)
            self.selEDFA2.removeItem(1)
            self.selOSA.removeItem(1)
            self.selDC3.removeItem(1)
            self.selDC2.removeItem(1)
            self.selDC1.removeItem(1)
        self.selAWG.addItems(instList)
        self.selEVNA.addItems(instList)
        self.selEDFA1.addItems(instList)
        self.selEDFA2.addItems(instList)
        self.selOSA.addItems(instList)
        self.selDC1.addItems(instList)
        self.selDC2.addItems(instList)
        self.selDC3.addItems(instList)

    def accept(self):
        # 关闭旧的设备连接
        api_gen.close_inst(self.parent.AWGHandle,
                           self.parent.EVNAHandle,
                           self.parent.OSAHandle,
                           self.parent.EDFA1Handle,
                           self.parent.EDFA2Handle,
                           self.parent.DC1Handle,
                           self.parent.DC2Handle,
                           self.parent.DC3Handle)
        # 开启新的设备连接
        self.parent.AWGHandle=api_gen.list_inst(self.selAWG.currentText())
        self.parent.EVNAHandle=api_gen.list_inst(self.selEVNA.currentText())
        self.parent.OSAHandle=api_gen.list_inst(self.selOSA.currentText())
        self.parent.EDFA1Handle=api_gen.list_inst(self.selEDFA1.currentText())
        self.parent.EDFA2Handle=api_gen.list_inst(self.selEDFA2.currentText())
        self.parent.DC1Handle=api_gen.list_inst(self.selDC1.currentText())
        self.parent.DC2Handle=api_gen.list_inst(self.selDC2.currentText())
        self.parent.DC3Handle=api_gen.list_inst(self.selDC3.currentText())

        self.done(True)