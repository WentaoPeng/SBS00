#! encoding = utf-8
''' GUI Panels. '''

# import standard libraries
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import pyvisa
import numpy as np
from GUI import SharedWidgets as Shared
from API import AWGapi as api_awg
from API import validators as api_val
from pyqtgraph import siEval
import SBS_DSP
import matplotlib.pyplot as plt


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
        refreshButton = QtWidgets.QPushButton('Manual Refresh')
        moreInfoButton = QtWidgets.QPushButton('More Info.')
        self.addressText = QtWidgets.QLabel()
        self.InstEnable = QtWidgets.QLabel()
        self.ChannelNum = QtWidgets.QLabel()
        self.Amplitude = QtWidgets.QLabel()
        self.DACset = QtWidgets.QLabel()
        self.ShapeStatus = QtWidgets.QLabel()
        self.CWSet = QtWidgets.QLabel()
        self.BWSet = QtWidgets.QLabel()
        self.DFSet = QtWidgets.QLabel()
        self.errMsgLabel = QtWidgets.QLabel()
        errorMsgBtn = QtWidgets.QPushButton('Error MsgLog')

        # AWG波形设置信息框
        designGroup = QtWidgets.QGroupBox()
        designGroup.setTitle('AWG-PUMP DesignInfo')
        designGroup.setAlignment(QtCore.Qt.AlignLeft)
        designGroup.setCheckable(False)
        designGroupLayout = QtWidgets.QGridLayout()
        designGroupLayout.addWidget(QtWidgets.QLabel('Shape Status'), 0, 0)
        designGroupLayout.addWidget(QtWidgets.QLabel('CW'), 1, 0)
        designGroupLayout.addWidget(QtWidgets.QLabel('BW'), 2, 0)
        designGroupLayout.addWidget(QtWidgets.QLabel('DF'), 3, 0)
        designGroupLayout.addWidget(self.ShapeStatus, 0, 1)
        designGroupLayout.addWidget(self.CWSet, 1, 1)
        designGroupLayout.addWidget(self.BWSet, 2, 1)
        designGroupLayout.addWidget(self.DFSet, 3, 1)
        designGroup.setLayout(designGroupLayout)

        # AWGStatus整体布局
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        # top Buttons布局
        mainLayout.addWidget(refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtWidgets.QLabel('Inst Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        # 基本状态信息
        mainLayout.addWidget(QtWidgets.QLabel('InstEnable'), 2, 0)
        mainLayout.addWidget(self.InstEnable, 2, 1, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('ChannelNum'), 3, 0)
        mainLayout.addWidget(self.ChannelNum, 3, 1, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Amp'), 4, 0)
        mainLayout.addWidget(self.Amplitude, 4, 1, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('DACset'), 5, 0)
        mainLayout.addWidget(self.DACset, 5, 1, 1, 3)
        #     AWG波形设置信息框
        mainLayout.addWidget(designGroup, 6, 0, 3, 4)
        mainLayout.addWidget(errorMsgBtn, 9, 0)
        mainLayout.addWidget(self.errMsgLabel, 9, 1, 1, 3)
        self.setLayout(mainLayout)
        #     点击事件触发
        refreshButton.clicked.connect(self.refresh_fun)
        moreInfoButton.clicked.connect(self.show_InstMoreInfo)
        errorMsgBtn.clicked.connect(self.err_msg)

        # 初始显示
        self.print_info()

        self.clicked.connect(self.check)

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

    def print_info(self):
        '''初始见面显示信息'''
        # self.addressText.setText(self.parent.)
        self.addressText.setText(self.parent.AWGInfo.instName)
        self.InstEnable.setText('ON' if self.parent.AWGInfo.AWG_Status else 'OFF')
        self.ChannelNum.setText(str(self.parent.AWGInfo.ChannelNum))
        self.DACset.setText(str(self.parent.AWGInfo.DAC_index))
        self.ShapeStatus.setText(self.parent.AWGInfo.mod_sel)
        self.CWSet.setText(str(self.parent.AWGInfo.CFFreq) + 'Hz')
        self.BWSet.setText(str(self.parent.AWGInfo.BWFreq) + 'Hz')
        self.DFSet.setText(str(self.parent.AWGInfo.DFFreq) + 'Hz')
        self.Amplitude.setText(str(self.parent.AWGInfo.AWGPower) + 'Mv')

    def refresh_fun(self):
        # if self.parent.testModeAction.isChecked() or  (not self.parent.AWGHandle):
        #     pass
        # else:
        self.addressText.setText(self.parent.AWGInfo.instName)
        self.InstEnable.setText('ON' if self.parent.AWGInfo.AWG_Status else 'OFF')
        self.ChannelNum.setText(str(self.parent.AWGInfo.ChannelNum))
        self.DACset.setText(str(self.parent.AWGInfo.DAC_index))
        self.ShapeStatus.setText(self.parent.AWGInfo.mod_sel)
        self.CWSet.setText(str(self.parent.AWGInfo.CFFreq) + 'Hz')
        self.BWSet.setText(str(self.parent.AWGInfo.BWFreq) + 'Hz')
        self.DFSet.setText(str(self.parent.AWGInfo.DFFreq) + 'Hz')
        self.Amplitude.setText(str(self.parent.AWGInfo.AWGPower) + 'Mv')

    def show_InstMoreInfo(self):
        # 待扩展
        return

    def err_msg(self):
        '''AWG反馈错误信息'''
        if self.parent.AWGHandle:
            self.parent.AWGInfo.errMsg = api_awg.M9502A.err_check()
            self.errMsgLabel.setText(self.parent.AWGInfo.errMsg)
        else:
            pass


class OSAStatus(QtWidgets.QGroupBox):
    '''
    光谱仪状态显示
    '''

    def __init__(self, parent):
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

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('EDFA Status')
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

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
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


class PNACtrl(QtWidgets.QGroupBox):
    '''
    VNA控制界面
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('PNA Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        response = QtWidgets.QGroupBox()
        response.setTitle('RESPONSE')
        response.setFlat(True)
        response.setAlignment(QtCore.Qt.AlignTop)
        responseLayout = QtWidgets.QGridLayout()
        responseLayout.setAlignment(QtCore.Qt.AlignTop)
        # responseLayout.setSpacing(0)

        self.addressText = QtWidgets.QLabel()
        # self.InstEnable = QtWidgets.QLabel()
        self.AvgPoints = QtWidgets.QSpinBox()
        self.EnterBtu = QtWidgets.QPushButton('Enter')
        self.AllMeasBtu = QtWidgets.QPushButton('ALLMeas')

        self.ScaleSet = QtWidgets.QWidget()
        self.ScaleSetUnitSel = QtWidgets.QComboBox()
        self.ScaleSetUnitSel.addItems(['S11', 'S12', 'S21', 'S22'])
        self.ScaleSetUnitSel.setCurrentIndex(1)

        responseLayout.addWidget(QtWidgets.QLabel('Inst:'), 0, 0)
        responseLayout.addWidget(self.addressText, 0, 1, 1, 3)
        responseLayout.addWidget(QtWidgets.QLabel('Scale'),1,0)
        responseLayout.addWidget(self.ScaleSetUnitSel, 1, 1, 1, 3)
        responseLayout.addWidget(QtWidgets.QLabel('AvgPoints'), 2, 0)
        responseLayout.addWidget(self.AvgPoints, 2, 1,1,3)
        responseLayout.addWidget(self.EnterBtu, 3, 0,1,2)
        responseLayout.addWidget(self.AllMeasBtu, 3, 2,1,2)
        response.setLayout(responseLayout)

        stimulus = QtWidgets.QGroupBox()
        stimulus.setTitle('STIMULUS')
        stimulus.setFlat(True)
        stimulus.setAlignment(QtCore.Qt.AlignLeft)
        stimulusLayout = QtWidgets.QGridLayout()
        stimulusLayout.setSpacing(0)

        self.PointSet = QtWidgets.QWidget()
        self.SPoints = QtWidgets.QSpinBox()
        SPointsLayout = QtWidgets.QGridLayout()
        SPointsLayout.addWidget(QtWidgets.QLabel('Sweep Points'), 0, 0)
        SPointsLayout.addWidget(self.SPoints, 0, 1, 1, 2)
        self.PointSet.setLayout(SPointsLayout)

        self.StartFset = QtWidgets.QWidget()
        self.StartFsetFill = QtWidgets.QLineEdit('10')
        self.StartFsetUnitSel = QtWidgets.QComboBox()
        self.StartFsetUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.StartFsetUnitSel.setCurrentIndex(2)
        StartFLayout = QtWidgets.QHBoxLayout()
        StartFLayout.addWidget(QtWidgets.QLabel('StartFerq'))
        StartFLayout.addWidget(self.StartFsetFill)
        StartFLayout.addWidget(self.StartFsetUnitSel)
        self.StartFset.setLayout(StartFLayout)

        self.EndFset = QtWidgets.QWidget()
        self.EndFsetFill = QtWidgets.QLineEdit('20')
        self.EndFsetUnitSel = QtWidgets.QComboBox()
        self.EndFsetUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.EndFsetUnitSel.setCurrentIndex(3)
        EndFsetLayout = QtWidgets.QHBoxLayout()
        EndFsetLayout.addWidget(QtWidgets.QLabel('EndFerq'))
        EndFsetLayout.addWidget(self.EndFsetFill)
        EndFsetLayout.addWidget(self.EndFsetUnitSel)
        self.EndFset.setLayout(EndFsetLayout)

        self.powerset = QtWidgets.QWidget()
        self.powersetFill = QtWidgets.QLineEdit('0')
        self.powersetUnitSel = QtWidgets.QComboBox()
        self.powersetUnitSel.addItems(['dBm', 'mW'])
        self.powersetUnitSel.setCurrentIndex(0)
        powersetLayout = QtWidgets.QHBoxLayout()
        powersetLayout.addWidget(QtWidgets.QLabel('Power'))
        powersetLayout.addWidget(self.powersetFill)
        powersetLayout.addWidget(self.powersetUnitSel)
        self.powerset.setLayout(powersetLayout)

        stimulusLayout.addWidget(self.StartFset, 2, 1, 1, 2)
        stimulusLayout.addWidget(self.EndFset, 3, 1, 1, 2)
        stimulusLayout.addWidget(self.PointSet, 1, 1, 1, 2)
        stimulusLayout.addWidget(self.powerset, 0, 1, 1, 2)
        stimulus.setLayout(stimulusLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(response)
        mainLayout.addWidget(stimulus)
        self.setLayout(mainLayout)

    def check(self):
        ''' Enable/disable this groupbox '''
        if (self.parent.testModeAction.isChecked() or self.parent.VNAHandle):
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

        #     AWG设置面板设置参量
        AWGWidget = QtWidgets.QWidget()
        self.DACset = QtWidgets.QSpinBox()
        self.channelNumset = Shared.AWGChannelBox()

        #     显示参量
        AWGLayout = QtWidgets.QGridLayout()
        AWGLayout.addWidget(QtWidgets.QLabel('DAC'), 0, 0)
        AWGLayout.addWidget(self.DACset, 0, 1, 1, 2)

        AWGLayout.addWidget(QtWidgets.QLabel('AWGChannel'), 1, 0)
        AWGLayout.addWidget(self.channelNumset, 1, 1, 1, 3)
        AWGWidget.setLayout(AWGLayout)

        #     AWG输出功率设置以及运行按钮
        self.AWGPowerSwitchBtu = QtWidgets.QPushButton('OFF')
        self.AWGPowerSwitchBtu.setCheckable(True)
        AWGPowerInput = QtWidgets.QPushButton('Set Power')

        AWGPowerLayout = QtWidgets.QHBoxLayout()
        AWGPowerLayout.setAlignment(QtCore.Qt.AlignLeft)
        AWGPowerLayout.addWidget(AWGPowerInput)
        AWGPowerLayout.addWidget(QtWidgets.QLabel('Pump Switch'))
        AWGPowerLayout.addWidget(self.AWGPowerSwitchBtu)
        AWGPowerCtrl = QtWidgets.QWidget()
        AWGPowerCtrl.setLayout(AWGPowerLayout)

        self.powerSwitchTimer = QtCore.QTimer()
        self.powerSwitchTimer.setInterval(500)
        self.powerSwitchTimer.setSingleShot(True)
        self.powerSwitchProgBar = QtWidgets.QProgressBar()
        self.progDialog = QtWidgets.QDialog()
        self.progDialog.setWindowTitle('AWG Running')
        progDialogLayout = QtWidgets.QVBoxLayout()
        progDialogLayout.addWidget(self.powerSwitchProgBar)
        self.progDialog.setLayout(progDialogLayout)

        #     pump设计子界面
        PumpDesign = QtWidgets.QGroupBox()
        PumpDesign.setTitle('PUMPDesign_AWG')
        PumpDesign.setFlat(True)
        PumpDesign.setAlignment(QtCore.Qt.AlignLeft)
        PumpLayout = QtWidgets.QGridLayout()
        PumpLayout.setSpacing(0)

        self.PumpModeSel = QtWidgets.QComboBox()
        self.PumpModeSel.addItems(api_awg.Shape_MODE_LIST)

        self.CenterFreq = QtWidgets.QWidget()
        self.CenterFreqFill = QtWidgets.QLineEdit('10')
        self.CenterFreqUnitSel = QtWidgets.QComboBox()
        self.CenterFreqUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.CenterFreqUnitSel.setCurrentIndex(3)
        CenterFreqLayout = QtWidgets.QHBoxLayout()
        CenterFreqLayout.addWidget(QtWidgets.QLabel('CenterFreq'))
        CenterFreqLayout.addWidget(self.CenterFreqFill)
        CenterFreqLayout.addWidget(self.CenterFreqUnitSel)
        self.CenterFreq.setLayout(CenterFreqLayout)

        self.BandWidth = QtWidgets.QWidget()
        self.BandWidthFill = QtWidgets.QLineEdit('200')
        self.BandWidthUnitSel = QtWidgets.QComboBox()
        self.BandWidthUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.BandWidthUnitSel.setCurrentIndex(2)
        BandWidthLayout = QtWidgets.QHBoxLayout()
        BandWidthLayout.addWidget(QtWidgets.QLabel('BandWidth'))
        BandWidthLayout.addWidget(self.BandWidthFill)
        BandWidthLayout.addWidget(self.BandWidthUnitSel)
        self.BandWidth.setLayout(BandWidthLayout)

        self.CombFreq = QtWidgets.QWidget()
        self.CombFreqFill = QtWidgets.QLineEdit('10')
        self.CombFreqUnitSel = QtWidgets.QComboBox()
        self.CombFreqUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.CombFreqUnitSel.setCurrentIndex(2)
        CombFreqLayout = QtWidgets.QHBoxLayout()
        CombFreqLayout.addWidget(QtWidgets.QLabel('Comb DF'))
        CombFreqLayout.addWidget(self.CombFreqFill)
        CombFreqLayout.addWidget(self.CombFreqUnitSel)
        self.CombFreq.setLayout(CombFreqLayout)

        self.PumpDesignDoneBtu = QtWidgets.QPushButton('Done')
        self.PumpDesignDoneBtu.setCheckable(True)

        PumpLayout.addWidget(QtWidgets.QLabel('Pump Shape :'), 0, 0)
        PumpLayout.addWidget(self.PumpDesignDoneBtu, 1, 0, 3, 1)
        PumpLayout.addWidget(self.PumpModeSel, 0, 1)
        PumpLayout.addWidget(self.CenterFreq, 1, 1, 1, 3)
        PumpLayout.addWidget(self.BandWidth, 2, 1, 1, 3)
        PumpLayout.addWidget(self.CombFreq, 3, 1, 1, 3)
        PumpDesign.setLayout(PumpLayout)

        #     设置主界面
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(AWGPowerCtrl)
        mainLayout.addWidget(AWGWidget)
        mainLayout.addWidget(PumpDesign)
        self.setLayout(mainLayout)

        # 设计窗口若有改变，更改后台参数，滤波类型编号，中心波长，带宽，间隔等参数同步改变
        self.DACset.valueChanged.connect(self.tune_mod_parameter)
        self.channelNumset.currentIndexChanged.connect(self.tune_mod_parameter)
        self.PumpModeSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.CenterFreqFill.textChanged.connect(self.tune_mod_parameter)
        self.CenterFreqUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.BandWidthFill.textChanged.connect(self.tune_mod_parameter)
        self.BandWidthUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.CombFreqFill.textChanged.connect(self.tune_mod_parameter)
        self.CombFreqUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)

        AWGPowerInput.clicked.connect(self.AWGRFPower)
        self.AWGPowerSwitchBtu.clicked.connect(self.AWGRFPowerSwitch_auto)
        self.AWGPowerSwitchBtu.clicked.connect(self.AWGPowerSwitch_Label)
        self.powerSwitchTimer.timeout.connect(self.ramp_AWGRFPower)
        # 设计泵浦事件
        self.PumpDesignDoneBtu.clicked.connect(self.DesignPump)

        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.AWGHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()

    def AWGRFPower(self):
        if self.parent.testModeAction.isChecked():
            self.parent.AWGInfo.AWGPower = 500
        else:
            self.parent.AWGInfo.AWGPower = api_awg.read_AWG_power(self.parent.AWGHandle)

        target_Power, okay = QtWidgets.QInputDialog.getInt(self, 'RF POWER',
                                                           'Manual Input (0mV to 1000mV)', self.parent.AWGInfo.AWGPower,
                                                           0, 1000, 1)
        if okay:
            if self.parent.testModeAction.isChecked():
                pass
            else:
                self.parent.AWGInfo.AWGPower = target_Power
                # api_awg.set_AWG_power(self.parent.AWGHandle,target_Power,self.parent.AWGInfo.ChannelNum)

            self.AWGPowerSwitchBtu.setChecked(True)
            self.powerSwitchProgBar.setRange(1000, abs(self.parent.AWGInfo.AWGPower - target_Power))
            self.powerSwitchProgBar.setValue(1000)
            if self.parent.AWGInfo.AWGPower > target_Power:
                self.ramper = api_awg.ramp_down(self.parent.AWGInfo.AWGPower, target_Power)
            else:
                self.ramper = api_awg.ramp_up(self.parent.AWGInfo.AWGPower, target_Power)
            self.ramp_AWGRFPower()
            self.progDialog.exec_()
        else:
            pass

    def AWGRFPowerSwitch_auto(self, btu_pressed):
        '''自动打开关闭RF输出'''
        if self.parent.testModeAction.isChecked():
            self.parent.AWGInfo.AWGPower = 500
        else:
            self.parent.AWGInfo.AWGPower = api_awg.read_AWG_power(self.parent.AWGHandle)

        if btu_pressed:
            if self.parent.testModeAction():
                pass
            else:
                # 带更改需要Running代码
                api_awg.set_AWG_power(self.parent.AWGHandle, True)
            self.ramper = api_awg.ramp_up(self.parent.AWGInfo.AWGPower, 1000)
            self.powerSwitchProgBar.setRange(1000, abs(self.parent.AWGInfo.AWGPower))
            self.powerSwitchProgBar.setValue(1000)
            self.ramp_AWGRFPower()
            self.progDialog.exec_()
        elif self.parent.AWGInfo.AWGPower > 0:
            self.ramper = api_awg.ramp_down(self.parent.AWGInfo.AWGPower, 0)
            self.powerSwitchProgBar.setRange(1000, abs(self.parent.AWGInfo.AWGPower + 0))
            self.powerSwitchProgBar.setValue(1000)
            self.ramp_AWGRFPower()
            result = self.progDialog.exec_()
            if self.parent.testModeAction.isChecked():
                self.AWGPowerSwitchBtu.setChecked(False)
            else:
                self.parent.AWGInfo.AWGPower = api_awg.read_AWG_power(self.parent.AWGHandle)
                if result and (self.parent.AWGInfo.AWGPower <= 0):
                    api_awg.set_AWG_power(self.parent.AWGHandle, False)
                    self.AWGPowerSwitchBtu.setChecked(False)
                else:
                    self.AWGPowerSwitchBtu.setChecked(True)
        else:
            if self.parent.testModeAction.isChecked():
                pass
            else:
                api_awg.set_AWG_power(self.parent.AWGHandle, False)
            self.AWGPowerSwitchBtu.setChecked(False)

        self.parent.AWGStatus.print_info()

    def AWGPowerSwitch_Label(self, toggle_state):
        '''更换按键文本'''
        if toggle_state:
            self.AWGPowerSwitchBtu.setText('ON')
        else:
            self.AWGPowerSwitchBtu.setText('OFF')

    def ramp_AWGRFPower(self):
        return

    def tune_mod_parameter(self):
        # 状态信息同步
        # 波形状态
        mod_index = self.PumpModeSel.currentIndex()
        self.parent.AWGInfo.mod_index = mod_index
        self.parent.AWGInfo.mod_sel = self.PumpModeSel.currentText()
        print(self.PumpModeSel.currentText())
        # DAC选择
        DAC_index = self.DACset.text()
        self.parent.AWGInfo.DAC_index = DAC_index
        print(DAC_index)
        # 通道选择
        Channel_N = self.channelNumset.currentText()
        self.parent.AWGInfo.ChannelNum = Channel_N
        print(Channel_N)
        CF_status, CF_freq = api_val.val_awgCW_mod_freq(self.CenterFreqFill.text(),
                                                        self.CenterFreqUnitSel.currentText())
        BW_status, BW_freq = api_val.val_awgBW_mod_freq(self.BandWidthFill.text(),
                                                        self.BandWidthUnitSel.currentText())
        DF_status, DF_freq = api_val.val_awgDF_mod_freq(self.CombFreqFill.text(),
                                                        self.CombFreqUnitSel.currentText())
        self.CenterFreqFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(CF_status)))
        self.BandWidthFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(BW_status)))
        self.CombFreqFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(DF_status)))

        self.parent.AWGInfo.CFFreq = CF_freq
        self.parent.AWGInfo.BWFreq = BW_freq
        self.parent.AWGInfo.DFFreq = DF_freq

    def DesignPump(self):

        AWG_framerate = 64e9  # AWG采样率
        Df = 1 * 10 ** 6
        # FM_AWG = AWG_framerate / 2.56   # AWG最高分析频率
        N_AWG = int(AWG_framerate / Df)
        t_AWG = N_AWG * (1 / AWG_framerate)
        CF = self.parent.AWGInfo.CFFreq
        BW = self.parent.AWGInfo.BWFreq
        DF = self.parent.AWGInfo.DFFreq

        if self.parent.AWGInfo.mod_index == 0:
            f_list, amp_list, phase_list = SBS_DSP.square_filter(CF, BW, DF)
        elif self.parent.AWGInfo.mod_index == 1:
            f_list, amp_list, phase_list = SBS_DSP.triangle_filter(CF, BW, DF)
        elif self.parent.AWGInfo.mod_index == 2:
            f_list, amp_list, phase_list = SBS_DSP.Band_stop_filter(CF, BW, DF, signal_BW=1 * 10 ** 9)
        else:
            amp_list = []
            f_list = []
            phase_list = []

        ts = np.linspace(0, t_AWG, N_AWG, endpoint=False)
        ys = SBS_DSP.synthesize1(amp_list, f_list, ts, phase_list)
        self.parent.AWGInfo.ts = ts
        self.parent.AWGInfo.ys = ys
        FFT_y, Fre = SBS_DSP.get_fft(ys, AWG_framerate)
        self.parent.AWGInfo.FFT_y = FFT_y
        self.parent.AWGInfo.Fre = Fre
        # Lorenz拟合
        Tb = 20 * 10 ** 6  # 10~30Mhz布里渊线宽
        omega_sbs = 9.7e9  # 布里渊平移量
        f_measure = np.arange(CF - 2 * BW - omega_sbs, CF + 2 * BW - omega_sbs, 10 ** 6)
        self.parent.AWGInfo.f_measure = f_measure
        total_lorenz = SBS_DSP.add_lorenz(f_measure, amp_list * 0.008, f_list, Tb)

        self.parent.AWGInfo.gb = total_lorenz
        # plt.figure()
        # plt.plot(f_measure,total_lorenz,'b')
        # plt.show()


class ADisplay(QtWidgets.QGroupBox):
    def __init__(self, parent):
        # super(ADisplay, self).__init__()
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        #
        pg.setConfigOptions(leftButtonPan=False)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        #
        self.pw = pg.MultiPlotWidget()
        self.plot_data = self.pw.addPlot(left='Amp', bottom='Time/s', title='Pump')
        #
        self.plot_btn = QtWidgets.QPushButton('Replot', self)
        self.plot_btn.clicked.connect(self.plot1)

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.addWidget(self.pw)
        self.v_layout.addWidget(self.plot_btn)
        self.setLayout(self.v_layout)

    def plot1(self):
        self.plot_data.clear()
        x = self.parent.AWGInfo.ts
        y = self.parent.AWGInfo.ys
        r_symbol = np.random.choice(['o', 's', 't', 't1', 't2', 't3', 'd', '+', 'x', 'p', 'h', 'star'])
        r_color = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])
        self.plot_data.plot(x, y, pen=r_color)
        self.plot_data.showGrid(x=True, y=True)


class FcombDisplay(QtWidgets.QGroupBox):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        pg.setConfigOptions(leftButtonPan=False, antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        self.pw = pg.MultiPlotWidget()
        self.plot_data = self.pw.addPlot(left='Amp', bottom='Freq(Hz)', title='FreqCombs&LorenzSBSGain')

        #
        self.plot_btn = QtWidgets.QPushButton('Replot', self)
        self.plot_btn.clicked.connect(self.plot2)

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.addWidget(self.pw)
        self.v_layout.addWidget(self.plot_btn)
        self.setLayout(self.v_layout)

    def plot2(self):
        self.plot_data.clear()
        z = self.parent.AWGInfo.Fre
        w = self.parent.AWGInfo.FFT_y
        gb = self.parent.AWGInfo.gb
        f_measure = self.parent.AWGInfo.f_measure
        r_symbol = np.random.choice(['o', 's', 't', 't1', 't2', 't3', 'd', '+', 'x', 'p', 'h', 'star'])
        r_color1 = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])
        r_color2 = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])
        self.plot_data.plot(z, w, pen=r_color1)
        self.plot_data.plot(f_measure, gb, pen=r_color2)
        self.plot_data.showGrid(x=True, y=True)


class OSACtrl(QtWidgets.QGroupBox):
    '''
    光谱仪控制显示,功能带扩展
    '''

    def __init__(self, parent):
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


class EDFACtrl(QtWidgets.QGroupBox):
    '''光信号EDFA控制栏'''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
        self.setTitle('EDFA1 Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        self.addressEDFA1=QtWidgets.QLabel()
        self.addressEDFA2=QtWidgets.QLabel()



    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.EDFAHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)
        self.parent.EDFA1Ctrl.print_info()


class VNAMonitor(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.pgPlot = pg.PlotWidget(title='PNA Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass


class OSAMonitor(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='OSA Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass
