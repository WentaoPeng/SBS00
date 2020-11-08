#! encoding = utf-8
''' Main GUI Window '''

from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from GUI import SharedWidgets as Shared
from GUI import Inst_Dialogs as Dialogs
from GUI import Panels
from API import AWGapi
from API import EVNAapi


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
        # self.DC1Handle = None
        # self.DC2Handle = None
        # self.DC3Handle = None
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

        closeInstAction = QtWidgets.QAction('Close Instrument', self)
        closeInstAction.setShortcut('Ctrl+Shift+C')
        closeInstAction.setStatusTip('Close Instrument')
        closeInstAction.triggered.connect(self.close_sel_inst)

        viewInstAction = QtWidgets.QAction('View Instrument Status', self)
        viewInstAction.setShortcut('Ctrl+Shift+V')
        viewInstAction.setStatusTip('View status of currently connected instrument')
        viewInstAction.triggered.connect(self.view_inst_status)
        # 选择性保存数据
        saveAction = QtWidgets.QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Data')
        # saveAction.triggered.connect(self.savedata)
        # CNN训练数据导入？
        impdataAction = QtWidgets.QAction('Import Data', self)
        impdataAction.setShortcut('Ctrl+I')
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
        menuInst.addAction(seleInstAction)
        menuInst.addAction(closeInstAction)
        menuScan = self.menuBar().addMenu('&Scan')
        menuScan.addAction(viewInstAction)
        menuData = self.menuBar().addMenu('&Data')
        menuData.addAction(saveAction)
        menuData.addAction(impdataAction)
        menuTest = self.menuBar().addMenu('&Test')
        menuTest.addAction(self.testModeAction)

        self.AWGInfo = Shared.AWGInfo()
        self.EVNAInfo = Shared.EVNAInfo()
        self.OSAInfo = Shared.OSAInfo()
        self.EDFA1Info = Shared.EDFA1Info()
        self.EDFA2Info = Shared.EDFA2Info()

        # 状态监控栏
        self.AWGStatus = Panels.AWGStatus(self)
        self.EVNAStatus = Panels.VNAStatus(self)
        self.OSAStatus = Panels.OSAStatus(self)
        self.EDFA1Status = Panels.EDFA1Status(self)
        self.EDFA2Status = Panels.EDFA2Status(self)

        # 设备控制栏
        self.AWGCtrl = Panels.AWGCtrl(self)
        self.EVNACtrl = Panels.VNACtrl(self)
        self.OSACtrl = Panels.OSACtrl(self)
        self.EDFA1Ctrl = Panels.EDFA1Ctrl(self)
        self.EDFA2Ctrl = Panels.EDFA2Ctrl(self)

        # 设置显示模块
        self.VNAMonitor = Panels.VNAMonitor(self)
        self.OSAMonitor = Panels.OSAMonitor(self)

        # 设置主要模块显示位置
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setSpacing(11)
        self.mainLayout.addWidget(self.AWGStatus, 0, 0, 2, 2)
        self.mainLayout.addWidget(self.EVNAStatus, 2, 0, 2, 2)
        self.mainLayout.addWidget(self.OSAStatus, 4, 0, 2, 2)
        self.mainLayout.addWidget(self.EDFA1Status, 6, 0, 2, 2)
        self.mainLayout.addWidget(self.EDFA2Status, 8, 0, 2, 2)

        self.mainLayout.addWidget(self.AWGCtrl, 0, 2, 2, 2)
        self.mainLayout.addWidget(self.EVNACtrl, 2, 2, 2, 2)
        self.mainLayout.addWidget(self.OSACtrl, 4, 2, 2, 2)
        self.mainLayout.addWidget(self.EDFA1Ctrl, 6, 2, 2, 2)
        self.mainLayout.addWidget(self.EDFA2Ctrl, 8, 2, 2, 2)

        self.mainLayout.addWidget(self.testModeSignLabel, 10, 0, 1, 2)

        self.mainLayout.addWidget(self.VNAMonitor, 0, 5, 4, 4)
        self.mainLayout.addWidget(self.OSAMonitor, 5, 5, 4, 4)

        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.load_dialogs()
        self.refresh_inst()
        self.testModeAction.toggled.connect(self.refresh_inst)

    def refresh_inst(self):

        if self.testModeAction.isChecked():
            self.setWindowTitle('SBSSystem [TEST MODE!]')
            self.testModeSignLabel.show()
            self.AWGCtrl.setChecked(True)
            self.EVNACtrl.setChecked(True)

            self.AWGStatus.setChecked(True)
            self.EVNAStatus.setChecked(True)
        else:
            self.setWindowTitle('SBSSystem')
            self.testModeSignLabel.hide()
            self.AWGCtrl.setChecked(not (self.AWGHandle is None))
            self.EVNACtrl.setChecked(not (self.VNAHandle is None))

            self.AWGStatus.setChecked(not (self.AWGHandle is None))
            self.EVNAStatus.setChecked(not (self.VNAHandle is None))

    def load_dialogs(self):
        # 加载小部件
        self.selInstDialog = Dialogs.selectInstDialog(self)
        self.viewInstDialog = Dialogs.viewInstDialog(self)

    def on_exit(self):
        self.close()

    # 保存函数可以实现选择性保存需求数据
    # def savedata(self):

    def select_inst(self):
        result = self.selInstDialog.exec_()

        if result:
            if self.AWGHandle:
                AWGapi.list_AWGinst(self.AWGHandle)
                #
            else:
                pass


        else:
            pass

    def view_inst_status(self):
        return

    def close_sel_inst(self):
        return
