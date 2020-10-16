#! encoding = utf-8
''' Main GUI Window '''

from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from GUI import SharedWidgets as Shared
from GUI import Inst_Dialogs as Dialogs
from GUI import Panels


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)

        # 设置窗口属性
        self.setWindowTitle('SBSSystem')
        self.setMinimumSize(1500, 840)
        self.testModeSignLabel = QtWidgets.QLabel('[TEST MODE ACTIVE -- NOTHING IS REAL]!')
        self.testModeSignLabel.setStyleSheet('color: {:s}'.format(Shared.msgcolor(0)))
        self.testModeSignLabel.setAlignment(QtCore.Qt.AlignCenter)

        # 初始化设备
        self.VNAHandle = None
        self.AWGHandle = None
        self.OSAHandle = None
        self.EDFA1Handle = None
        self.EDFA2Handle = None
        self.DC1Handle = None
        self.DC2Handle = None
        self.DC3Handle = None
        # 设置菜单栏动作
        # 退出系统
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        exitAction.setStatusTip('Exit program')
        exitAction.triggered.connect(self.on_exit)

        # 设备选项
        # 设备选择通信方式
        seleInstAction = QtWidgets.QAction('Select Inst_Port', self)
        seleInstAction.setShortcut('Ctrl+Shift+I')
        seleInstAction.setStatusTip('Select Instrument Port')
        seleInstAction.triggered.connect(self.select_inst)

        # 选择性保存数据
        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcuts('Ctrl+S')
        saveAction.setStatusTip('Save Data')
        # saveAction.triggered.connect(self.savedata)
        # CNN训练数据导入？
        impdataAction = QtWidgets.QAction('Import Data', self)
        impdataAction.setShortcuts('Ctrl+I')
        impdataAction.setStatusTip('Import CNN Train DATA')

        # 系统测试模式
        self.testModeAction = QtGui.QAction('Test Mode', self)
        self.testModeAction.setCheckable(True)
        self.testModeAction.setShortcut('Ctrl+T')
        self.testModeAction.setWhatsThis(
            'Toggle the test mode to bypass all instrument communication for GUI development.')

        # 设置菜单栏
        self.statusBar()

        menuFile = self.menuBar().addMenu('&File')
        menuFile.addAction(exitAction)
        menuInst = self.menuBar().addMenu('&Instrument')
        menuInst.addAction()
        menuScan = self.menuBar().addMenu('&Scan')
        menuScan.addAction()
        menuData = self.menuBar().addMenu('&Data')
        menuData.addAction(saveAction)
        menuData.addAction(impdataAction)
        menuTest = self.menuBar().addMenu('&Test')
        menuTest.addAction(self.testModeAction)



    def load_dialogs(self):
        # 加载小部件
        self.selInstDialog=Dialogs.selectInstDialog(self)


    def on_exit(self):
        self.close()

    # 保存函数可以实现选择性保存需求数据
    # def savedata(self):

    def select_inst(self):
        result=self.selInstDialog.exec_()

        if result:
            if self.AWGHandle:
