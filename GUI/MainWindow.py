#! encoding = utf-8
''' Main GUI Window '''

from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from GUI import SharedWidgets as Shared
from GUI import Inst_Dialogs as Dialogs
from GUI import Panels
from API import AWGapi
from API import PNAapi
from API import general as api_gen
import logging
import traceback
import sys
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)

        # 设置窗口属性
        self.setWindowTitle('SBSSystem')
        self.setMinimumSize(1500, 840)
        self.testModeSignLabel = QtWidgets.QLabel('[TEST MODE ACTIVE -- NOTHING IS REAL]!')
        self.testModeSignLabel.setStyleSheet('color: {:s}'.format(Shared.msgcolor(0)))
        self.testModeSignLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.errorSignLabel = QtWidgets.QLabel()
        self.errorSignLabel.setStyleSheet('color:{:s}'.format(Shared.msgcolor(0)))
        self.errorSignLabel.setAlignment(QtCore.Qt.AlignCenter)
        # self.setWindowOpacity(1)  # 设置窗口透明度
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框
        # 提取后台log文档并显示
        # self.logger=self.get_logger('./log.txt',logging.INFO)

        # self.errorSignLabel.setText(self.predicted(features))

        # 初始化设备
        self.PNAHandle = None
        self.AWGHandle = None
        self.LightHandle = None
        self.EDFA1Handle = None
        self.EDFA2Handle = None
        # 设置菜单栏动作
        # 退出系统
        exitAction = QtWidgets.QAction('Exit', self)
        exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        exitAction.setStatusTip('Exit program')
        exitAction.triggered.connect(self.on_exit)

        # 设备选项
        # 设备选择通信方式
        # 自动选择
        seleInstAction = QtWidgets.QAction('Select Inst_Port', self)
        seleInstAction.setShortcut('Ctrl+Shift+I')
        seleInstAction.setStatusTip('Select Instrument Port')
        seleInstAction.triggered.connect(self.select_inst)
        # 手动输入
        ManualInstAction = QtWidgets.QAction('Manual input', self)
        ManualInstAction.setShortcut('Ctrl+Shift+M')
        ManualInstAction.setStatusTip('Manual input(LAN_IP)')
        ManualInstAction.triggered.connect(self.Manual_inst)

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
        menuInst.addAction(ManualInstAction)
        menuInst.addAction(closeInstAction)
        menuScan = self.menuBar().addMenu('&Scan')
        menuScan.addAction(viewInstAction)
        menuData = self.menuBar().addMenu('&Data')
        menuData.addAction(saveAction)
        menuData.addAction(impdataAction)
        menuTest = self.menuBar().addMenu('&Test')
        menuTest.addAction(self.testModeAction)

        self.AWGInfo = Shared.AWGInfo()
        self.PNAInfo = Shared.PNAInfo()
        self.LightInfo = Shared.LightInfo()
        self.EDFAInfo = Shared.EDFAInfo()
        self.Display = 0
        # 状态监控栏
        self.AWGStatus = Panels.AWGStatus(self)
        # 设备控制栏
        self.AWGCtrl = Panels.AWGCtrl(self)
        self.PNACtrl = Panels.PNACtrl(self)
        self.LightCtrl = Panels.LightCtrl(self)
        self.EDFACtrl = Panels.EDFACtrl(self)

        # 设置显示模块
        self.AWGDisplay = Panels.ADisplay(self)
        self.FcombDisplay = Panels.FcombDisplay(self)
        self.VNAMonitor = Panels.VNAMonitor(self)

        # 反馈模块
        self.Feedback = Panels.Feedback(self)

        # 设置主要模块显示位置
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setSpacing(12)
        self.mainLayout.addWidget(self.AWGStatus, 0, 2, 4, 2)

        self.mainLayout.addWidget(self.AWGCtrl, 0, 0, 4, 2)
        self.mainLayout.addWidget(self.PNACtrl, 4, 0, 6, 2)
        self.mainLayout.addWidget(self.LightCtrl, 10, 0, 2, 4)
        self.mainLayout.addWidget(self.EDFACtrl, 4, 2, 6, 2)

        self.mainLayout.addWidget(self.testModeSignLabel, 12, 5, 1, 2)
        self.mainLayout.addWidget(self.errorSignLabel, 12, 7, 1, 2)

        self.mainLayout.addWidget(self.AWGDisplay, 0, 5, 4, 2)  # 画两幅，时域与频域2*2
        self.mainLayout.addWidget(self.FcombDisplay, 0, 7, 4, 2)
        self.mainLayout.addWidget(self.Feedback, 4, 5, 2, 4)
        self.mainLayout.addWidget(self.VNAMonitor, 6, 5, 6, 4)

        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.load_dialogs()
        self.refresh_inst()
        self.testModeAction.toggled.connect(self.refresh_inst)

    # def get_logger(file_path, logging_level):
    #     logger = logging.getLogger(__name__)
    #     logger.setLevel(level=logging.INFO)
    #     hander = logging.FileHandler(file_path)
    #     hander.setLevel(logging.INFO)
    #     formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    #     hander.setFormatter(formatter)
    #     logger.addHandler(hander)
    #     return logger

    # def predicted(features):
    #     try:
    #         result = predictor(features)
    #     except Exception  as e:
    #         self.logger.info('model predictor may be fail')
    #         self.logger.error('model error %s' % traceback.format_exc())  # 具体的错误会捕获

    def refresh_inst(self):

        if self.testModeAction.isChecked():
            self.setWindowTitle('SBSSystem [TEST MODE!]')
            self.testModeSignLabel.show()
            self.AWGCtrl.setChecked(True)
            self.PNACtrl.setChecked(True)
            self.LightCtrl.setChecked(True)
            self.EDFACtrl.setChecked(True)

            self.AWGStatus.setChecked(True)
        else:
            self.setWindowTitle('SBSSystem')
            self.testModeSignLabel.hide()
            self.AWGCtrl.setChecked(not (self.AWGHandle is None))
            self.PNACtrl.setChecked(not (self.PNAHandle is None))
            self.LightCtrl.setChecked(not (self.LightHandle is None))
            # self.OSACtrl.setChecked(not (self.OSAHandle is None))
            # self.EDFA2Ctrl.setChecked(not (self.EDFA2Handle is None))
            self.EDFACtrl.setChecked(not (self.EDFA1Handle or self.EDFA2Handle is None))

            self.AWGStatus.setChecked(not (self.AWGHandle is None))
            # self.PNAStatus.setChecked(not (self.PNAHandle is None))

    def load_dialogs(self):
        # 加载小部件
        self.selInstDialog = Dialogs.selectInstDialog(self)
        self.ManualInstDialog = Dialogs.manualInstDialog(self)
        self.viewInstDialog = Dialogs.viewInstDialog(self)
        self.closeInstDialog = Dialogs.CloseSelInstDialog(self)

    def on_exit(self):
        self.close()

    # 保存函数可以实现选择性保存需求数据
    # def savedata(self):

    def Manual_inst(self):
        result = self.ManualInstDialog.exec_()

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
        d = Dialogs.CloseSelInstDialog(self)
        d.exec_()
        self.refresh_inst()

    def closeEvent(self, event):
        q = QtGui.QMessageBox.question(self, 'Quit?',
                                       'Are you sure to quit?', QtGui.QMessageBox.Yes |
                                       QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if q == QtGui.QMessageBox.Yes:
            status = api_gen.close_inst(self.AWGHandle, self.PNAHandle,
                                        self.LightHandle, self.EDFA1Handle, self.EDFA2Handle)
            if not status:  # safe to close
                self.close()
            else:
                qq = QtGui.QMessageBox.question(self, 'Error',
                                                '''Error in disconnecting instruments.
                                                Are you sure to force quit?''', QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if qq == QtGui.QMessageBox.Yes:
                    self.close()
                else:
                    event.ignore()
        else:
            event.ignore()
