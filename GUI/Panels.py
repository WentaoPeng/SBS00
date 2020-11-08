#! encoding = utf-8
''' GUI Panels. '''

# import standard libraries
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import pyvisa
import numpy as np
from GUI import SharedWidgets as Shared


class VNAStatus(QtWidgets.QGroupBox):
    '''
        VNA状态显示
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('VNA Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

    # 设定检测VNA状态信息，扫频信号功率，频率范围，数据点

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()


class AWGStatus(QtWidgets.QGroupBox):
    '''
        AWG状态显示
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('AWG Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        # 设定检测AWG状态信息，运行，输出通道等



    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()

class OSAStatus(QtWidgets.QGroupBox):
    '''
    光谱仪状态显示
    '''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('OSA Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.OSAStatus.print_info()

class EDFA1Status(QtWidgets.QGroupBox):
    '''小信号EDFA1状态信息'''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self,parent)
        self.parent=parent

        self.setTitle('EDFA1 Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)
        self.parent.EDFA1Status.print_info()

class EDFA2Status(QtWidgets.QGroupBox):
    '''级联大信号EDFA2状态信息'''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self,parent)
        self.parent=parent
        self.setTitle('EDFA2 Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def Check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)
        self.parent.EDFA2Status.print_info()

class VNACtrl(QtWidgets.QGroupBox):
    '''
    VNA控制界面
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('VNA Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()

class AWGCtrl(QtWidgets.QGroupBox):
    '''
    AWG控制界面
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('AWG Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()

class OSACtrl(QtWidgets.QGroupBox):
    '''
    光谱仪控制显示
    '''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('OSA Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.OSACtrl.print_info()

class EDFA1Ctrl(QtWidgets.QGroupBox):
    '''小信号EDFA控制栏'''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self,parent)
        self.parent=parent
        self.setTitle('EDFA1 Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)
        self.parent.EDFA1Ctrl.print_info()

class EDFA2Ctrl(QtWidgets.QGroupBox):
    '''EDFA2控制栏'''
    def __init__(self,parent):
        QtWidgets.QGroupBox.__init__(self,parent)
        self.parent=parent
        self.setTitle('EDFA2 Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)
    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)
        self.parent.EDFA2Ctrl.print_info()

class AWGDesignMonitor(QtWidgets.QWidget):
    '''
    设计波形展示窗口
    '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.counter = 0

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()


class VNAMonitor(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='EVNA Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass

class OSAMonitor(QtWidgets.QGroupBox):

    def __init__(self,parent):
        QtWidgets.QWidget.__init__(self,parent)
        self.parent=parent

        self.pgPlot=pg.PlotWidget(title='OSA Monitor')
        mainLayout=QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot,0,0)
        self.setLayout(mainLayout)
    def plot(self):
        pass