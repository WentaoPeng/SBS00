#! encoding = utf-8
''' GUI Panels. '''

# import standard libraries
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import pyvisa
import time
import os
import datetime
import pandas as pd
import numpy as np
from GUI import SharedWidgets as Shared
from API import AWGapi as api_awg
from API import validators as api_val
from API import PNAapi as api_pna
from API import LightAPI as api_light
from API import EDFAAPI as api_edfa
from pyqtgraph import siEval
import SBS_DSP
import multi_Lorenz_2_triangle as mlt
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks, peak_widths, peak_prominences
from threading import Timer


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

        if (self.parent.testModeAction.isChecked() or self.parent.AWGHandle):
            self.setChecked(True)
            self.parent.AWGStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No AWG is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.AWGStatus.setChecked(False)

        self.parent.AWGStatus.print_info()

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
        self.InitialBtu = QtWidgets.QPushButton('Initial')
        self.EnterBtu = QtWidgets.QPushButton('Enter')
        self.AllMeasBtu = QtWidgets.QPushButton('ALLMeas')

        self.ScaleSet = QtWidgets.QWidget()
        self.ScaleSetUnitSel = QtWidgets.QComboBox()
        self.ScaleSetUnitSel.addItems(['S11', 'S12', 'S21', 'S22'])
        self.ScaleSetUnitSel.setCurrentIndex(1)

        responseLayout.addWidget(QtWidgets.QLabel('Inst:'), 0, 0)
        responseLayout.addWidget(self.addressText, 0, 1, 1, 3)
        responseLayout.addWidget(QtWidgets.QLabel('Scale'), 1, 0)
        responseLayout.addWidget(self.ScaleSetUnitSel, 1, 1, 1, 3)
        responseLayout.addWidget(QtWidgets.QLabel('AvgPoints'), 2, 0)
        responseLayout.addWidget(self.AvgPoints, 2, 1, 1, 3)
        responseLayout.addWidget(self.InitialBtu, 3, 0, 1, 2)
        responseLayout.addWidget(self.AllMeasBtu, 3, 2, 1, 2)
        response.setLayout(responseLayout)

        stimulus = QtWidgets.QGroupBox()
        stimulus.setTitle('STIMULUS')
        stimulus.setFlat(True)
        stimulus.setAlignment(QtCore.Qt.AlignLeft)
        stimulusLayout = QtWidgets.QGridLayout()
        stimulusLayout.setSpacing(0)

        self.PointSet = QtWidgets.QWidget()
        self.SPoints = QtWidgets.QLineEdit()
        self.SPoints.setPlaceholderText('High sampling')
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
        stimulusLayout.addWidget(self.EnterBtu, 4, 1)
        stimulus.setLayout(stimulusLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(response)
        mainLayout.addWidget(stimulus)
        self.setLayout(mainLayout)

        # 信息同步，单位转换
        self.AvgPoints.valueChanged.connect(self.tune_mod_parameter)
        self.ScaleSetUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.powersetFill.textChanged.connect(self.tune_mod_parameter)
        self.SPoints.textChanged.connect(self.tune_mod_parameter)
        self.StartFsetFill.textChanged.connect(self.tune_mod_parameter)
        self.EndFsetFill.textChanged.connect(self.tune_mod_parameter)

        self.InitialBtu.clicked.connect(self.InitialF)
        self.EnterBtu.clicked.connect(self.setPNA)
        self.AllMeasBtu.clicked.connect(self.AllDisplay)

        self.clicked.connect(self.check)

    def AllDisplay(self):
        if self.parent.testModeAction.isChecked() or self.parent.PNAHandle:
            self.parent.PNAHandle.allmeas()
            self.parent.Display = 1

    def InitialF(self):
        if self.parent.testModeAction.isChecked() or self.parent.PNAHandle:
            self.parent.PNAHandle.PNA_setup(measName=self.parent.PNAInfo.Scale)

    def setPNA(self):
        if self.parent.testModeAction.isChecked() or self.parent.PNAHandle:
            self.parent.PNAHandle.configure(startFreq=self.parent.PNAInfo.StartFerq,
                                            endFreq=self.parent.PNAInfo.EndFerq,
                                            numpoints=self.parent.PNAInfo.SweepPoints,
                                            avgpoints=self.parent.PNAInfo.AvgPoints,
                                            power=self.parent.PNAInfo.Power)

    def tune_mod_parameter(self):
        self.parent.PNAInfo.Scale = self.ScaleSetUnitSel.currentText()
        self.parent.PNAInfo.AvgPoints = int(self.AvgPoints.text())
        self.parent.PNAInfo.SweepPoints = int(self.SPoints.text())
        self.parent.PNAInfo.Power = int(self.powersetFill.text())
        SF_status, SF_value = api_val.val_PNA_F(self.StartFsetFill.text(),
                                                self.StartFsetUnitSel.currentText())
        EF_status, EF_value = api_val.val_PNA_F(self.EndFsetFill.text(),
                                                self.EndFsetUnitSel.currentText())

        self.parent.PNAInfo.StartFerq = SF_value
        self.parent.PNAInfo.EndFerq = EF_value

    def check(self):
        ''' Enable/disable this groupbox '''
        if (self.parent.testModeAction.isChecked() or self.parent.PNAHandle):
            self.setChecked(True)
            self.parent.PNACtrl.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No PNAN5225A is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.PNACtrl.setChecked(False)

        # self.parent.PNACtrl.print_info()


class AWGCtrl(QtWidgets.QGroupBox):
    '''
    AWG控制界面
    调制器级联方案。多通道选择，同时发送信号。
    '''

    def __init__(self, parent, pumpLayout=None):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
        # super(AWGCtrl,self).__init__(parent)

        self.setTitle('AWG Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        #     AWG设置面板设置参量
        AWGWidget = QtWidgets.QWidget()
        self.DACset = QtWidgets.QSpinBox()
        self.channelNumset = Shared.AWGChannelBox()

        #     显示参量
        DACLayout = QtWidgets.QHBoxLayout()  # 第二行
        DACLayout.addWidget(QtWidgets.QLabel('DAC'))
        DACLayout.addWidget(self.DACset)

        AWGChannelLayout =  QtWidgets.QHBoxLayout()  # 第三行
        AWGChannelLayout.addWidget(QtWidgets.QLabel('AWGChannel'))
        AWGChannelLayout.addWidget(self.channelNumset)

        #     AWG输出功率设置以及运行按钮
        self.AWGPowerSwitchBtu = QtWidgets.QPushButton('OFF')
        self.AWGPowerSwitchBtu.setCheckable(True)
        AWGPowerInput = QtWidgets.QPushButton('Set Power')

        AWGPowerLayout = QtWidgets.QHBoxLayout()  # 第一行
        AWGPowerLayout.setAlignment(QtCore.Qt.AlignLeft)
        AWGPowerLayout.addWidget(AWGPowerInput)
        AWGPowerLayout.addWidget(QtWidgets.QLabel('Pump Switch'))
        AWGPowerLayout.addWidget(self.AWGPowerSwitchBtu)
        AWGPowerCtrl = QtWidgets.QWidget()

        AWGLayout = QtWidgets.QVBoxLayout()
        AWGLayout.addLayout(AWGPowerLayout)
        AWGLayout.addLayout(DACLayout)
        AWGLayout.addLayout(AWGChannelLayout)
        AWGWidget.setLayout(AWGLayout)

        #     pump设计子界面
        PumpDesign = QtWidgets.QGroupBox()
        PumpDesign.setTitle('PUMPDesign_AWG')
        PumpDesign.setFlat(True)
        PumpDesign.setAlignment(QtCore.Qt.AlignLeft)

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

        self.rand_seed=QtWidgets.QWidget()
        self.rand_SFill = QtWidgets.QLineEdit('0')
        rand_seedLayout=QtWidgets.QHBoxLayout()
        rand_seedLayout.addWidget(QtWidgets.QLabel('Rand_S'))
        rand_seedLayout.addWidget(self.rand_SFill)
        self.rand_seed.setLayout(rand_seedLayout)


        self.PumpDesignDoneBtu = QtWidgets.QPushButton('Done')
        # self.PumpDesignDoneBtu.setCheckable(True)
        self.PumpDesignDoneBtu.setStyleSheet('''QPushButton:hover{background:yellow;}''')
        self.PumpDesignDoneBtu.setMaximumSize(200,200)

        self.pumpdesignsetBtu=QtWidgets.QPushButton('Set')
        self.pumpdesignsetBtu.setCheckable(True)
        self.pumpdesignsetBtu.setStyleSheet('''QPushButton:hover{background:yellow;}''')
        self.pumpdesignsetBtu.setMaximumSize(200, 200)

        self.sweepFreq=QtWidgets.QCheckBox('Sweep_Freq')
        # self.sweepFreq.setCheckState(True)
        self.sweepFreq.setChecked(False)
        self.plusFreq=QtWidgets.QCheckBox('Plus')
        self.plusFreq.setChecked(False)
        self.minusFreq=QtWidgets.QCheckBox('Minus')

        PumpLayout = QtWidgets.QGridLayout()

        PumpLayout.addWidget(QtWidgets.QLabel('Pump Shape :'), 0, 0)
        PumpLayout.addWidget(self.pumpdesignsetBtu,1,0,2,1)
        PumpLayout.addWidget(self.PumpDesignDoneBtu,3, 0, 2, 1)
        PumpLayout.addWidget(self.PumpModeSel, 0, 1)
        PumpLayout.addWidget(self.CenterFreq, 1, 1, 2, 3)
        PumpLayout.addWidget(self.BandWidth, 2, 1, 2, 3)
        PumpLayout.addWidget(self.CombFreq, 3, 1, 2, 3)
        PumpLayout.addWidget(self.rand_seed,4, 1, 2, 3)
        PumpLayout.addWidget(self.sweepFreq,6,0)
        PumpLayout.addWidget(self.plusFreq,6,1)
        PumpLayout.addWidget(self.minusFreq,6,2)
        # PumpLayout.addWidget(QtWidgets.QLabel('Sweep_Freq'),5,1)
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
        self.rand_SFill.textChanged.connect(self.tune_mod_parameter)

        AWGPowerInput.clicked.connect(self.AWGRFPower)
        self.AWGPowerSwitchBtu.clicked.connect(self.AWGRFPowerSwitch_auto)
        self.AWGPowerSwitchBtu.toggled.connect(self.AWGPowerSwitch_Label)
        # self.powerSwitchTimer.timeout.connect(self.ramp_AWGRFPower)
        # 设计泵浦事件
        self.PumpDesignDoneBtu.clicked.connect(self.DonePump)
        self.pumpdesignsetBtu.clicked.connect(self.designset)
        # self.pumpdesignsetBtu.setChecked(False)
        self.timer=QtCore.QTimer(self)
        self.timer.timeout.connect(self.DonePump)
        # self.timer.start(10)

        self.clicked.connect(self.check)

    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.AWGHandle):
            self.setChecked(True)
            self.parent.AWGCtrl.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No AWG is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.AWGCtrl.setChecked(False)

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
        Channel_N = api_val.AWGCHANNELSET[self.channelNumset.currentIndex()]
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
        self.parent.AWGInfo.rand_seed=int(self.rand_SFill.text())

    def AWGRFPower(self):
        if self.parent.testModeAction.isChecked():

            target_Power, okay = QtWidgets.QInputDialog.getDouble(self, 'RF POWER',
                                                                  'Manual Input (0mV to 1000mV)',
                                                                  self.parent.AWGInfo.AWGPower, 0, 1000, 0.01)
            self.parent.AWGInfo.AWGPower = target_Power

        else:
            target_Power, okay = QtWidgets.QInputDialog.getDouble(self, 'RF POWER',
                                                                  'Manual Input (0mV to 1000mV)',
                                                                  self.parent.AWGInfo.AWGPower, 0, 1000, 0.01)
            self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                                                channel=self.parent.AWGInfo.ChannelNum)

            self.parent.AWGInfo.AWGPower = target_Power

        if okay:
            if self.parent.testModeAction.isChecked():
                pass
            # else:
            #     self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
            #                                         channel=self.parent.AWGInfo.ChannelNum)
        else:
            pass

    def AWGRFPowerSwitch_auto(self, status):
        '''自动打开关闭RF输出'''
        if status:
            if self.parent.testModeAction.isChecked():
                pass
            else:
                # 设置波形np.array，并检验，以及下载波形，Running
                # ys = np.ones(len(self.parent.AWGInfo.ys))*self.parent.AWGInfo.ys
                # self.parent.AWGHandle.clear_all_wfm()
                # wfmID = self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                #                                            ch=self.parent.AWGInfo.ChannelNum)
                # self.parent.AWGHandle.play(wfmID=wfmID, ch=self.parent.AWGInfo.ChannelNum)
                # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                #                                     channel=self.parent.AWGInfo.ChannelNum)
                self.parent.AWGHandle.play()
                # self.parent.AWGHandle.err_check()
                self.parent.AWGInfo.AWG_Status = True
        else:
            self.parent.AWGHandle.stop(ch=self.parent.AWGInfo.ChannelNum)
            self.parent.AWGHandle.delete_segment(ch=self.parent.AWGInfo.ChannelNum)
            self.parent.AWGInfo.AWG_Status = False

        self.parent.AWGStatus.print_info()

    def AWGPowerSwitch_Label(self, toggle_state):
        '''更换按键文本'''
        if toggle_state:
            self.AWGPowerSwitchBtu.setText('ON')
        else:
            self.AWGPowerSwitchBtu.setText('OFF')


    def pre_amp_seq(self, BW, DF):
        # 产生AWG波形前，自动迭代出最佳泵浦幅值
        # auto mode (automatically stop loop when meets need)
        ''' [1] input initial settings (set requirements of filter) '''
        bandwidth = BW/1e6  # MHz
        comb_df = DF/1e6  # MHz
        iteration_type = 1  # 迭代方式，[1]-2+3，[2]-线性，[3]-根号,[4]-边界参考旁边 (默认选[1])
        gamma_B = self.parent.AWGInfo.gamma_b  # MHz，布里渊线宽(通过单梳测量得到，可以只存一次）
        type_filter = 'square'  # type_filter='square','triangle'

        ''' [2] check and preprocess '''
        # assert bandwidth % comb_df == 0
        N_pump = int(bandwidth / comb_df)+1
        central_freq = 0  # 因为只要确定形状，故此处中心频率采用相对值，设置为0
        BFS = 0  # 因为只要确定形状，故不考虑布里渊频移，设置为0

        ''' [2-1] 初始化频梳幅值，频率与相位'''
        amp_seq = mlt.initial_amp_seq(N_pump, type_filter)
        f_seq = mlt.initial_f_seq(N_pump, central_freq, comb_df)
        phase_list = np.zeros(N_pump)  # 先不考虑随机相位问题
        # phase_list = [sd.randen_phase() for i in range(N_pump)]  # 随机相位
        nml_amp_seq = mlt.normalize_amp_seq(amp_seq, f_seq, phase_list)  # 归一化后泵浦

        ''' [2-2] 计算增益谱 '''
        f_measure = np.linspace(central_freq - bandwidth, central_freq + bandwidth, 40000)  # 设置扫频范围与点数，单位MHz
        measure_brian = mlt.conv_lorenz(f_measure, nml_amp_seq, f_seq, gamma_B, BFS)

        ''' [3] 迭代反馈,当平整度增加时停止迭代 '''
        N_iteration = 0  # 迭代次数统计
        f_index = mlt.search_index(f_seq - BFS, f_measure)  # 找到梳齿对应单布里渊增益中心位置索引
        f_measure_sam = [f_measure[i] for i in f_index]  # 最接近频梳对应的单布里渊增益中心的采样点频率
        brian_measure_sam = np.array([measure_brian.real[i] for i in f_index])  # 最接近频梳频率的采样点增益
        expected_gain_sam = mlt.expected_gain2(f_index, measure_brian.real, type_filter)
        bias = abs(measure_brian[f_index[0]:f_index[-1]] - np.mean(expected_gain_sam))
        flatness = (max(bias) - min(bias))
        while N_iteration < 30:  # 设置迭代上限
            # 更新amp_seq，目前有4种方式
            new_amp_seq = mlt.change_amp_seq(amp_seq, expected_gain_sam, brian_measure_sam, iteration_type)
            nml_amp_seq = mlt.normalize_amp_seq(amp_seq, f_seq, phase_list)
            new_measure_brian = mlt.conv_lorenz(f_measure, nml_amp_seq, f_seq, gamma_B, BFS)  # 单位MHz

            # 更新后采样计算平均偏差值
            brian_measure_sam = np.array([new_measure_brian.real[i] for i in f_index])  # 最接近频梳频率的采样点增益
            expected_gain_sam = mlt.expected_gain2(f_index, new_measure_brian.real, type_filter)

            bias = abs(new_measure_brian[f_index[0]:f_index[-1]] - np.mean(expected_gain_sam))
            new_flatness = (max(bias) - min(bias))
            if new_flatness >= flatness:
                break
            # if N_iteration % 10 == 0:
            #     plt.plot(f_measure, measure_brian.real, label='迭代' + str(N_iteration) + '次幅值')

            amp_seq = new_amp_seq
            flatness = new_flatness
            measure_brian = new_measure_brian
            N_iteration += 1
        return amp_seq

    def designset(self):
        AWG_framerate = 64e9  # AWG采样率
        Df = 1 * 10 ** 6
        # FM_AWG = AWG_framerate / 2.56   # AWG最高分析频率
        N_AWG = int(AWG_framerate / Df)
        t_AWG = N_AWG * (1 / AWG_framerate)
        CF = self.parent.AWGInfo.CFFreq
        BW = self.parent.AWGInfo.BWFreq
        DF = self.parent.AWGInfo.DFFreq
        ts = np.linspace(0, t_AWG, N_AWG, endpoint=False)
        self.parent.AWGInfo.ts=ts
        if self.parent.AWGInfo.mod_index == 0:
            f_list, amp_list, phase_list = SBS_DSP.square_filter(CF, BW, DF, self.parent.AWGInfo.rand_seed)
        elif self.parent.AWGInfo.mod_index == 1:
            f_list, amp_list, phase_list = SBS_DSP.triangle_filter(CF, BW, DF)
        elif self.parent.AWGInfo.mod_index == 2:
            f_list, amp_list, phase_list = SBS_DSP.Band_stop_filter(CF, BW, DF, signal_BW=1 * 10 ** 9)
        elif self.parent.AWGInfo.mod_index == 3:
            f_list, amp_list, phase_list = SBS_DSP.Guass_filter(CF, BW, DF)
        else:
            amp_list = []
            f_list = []
            phase_list = []
        self.parent.AWGInfo.f_list = f_list
        self.parent.AWGInfo.amp_list = amp_list
        self.parent.AWGInfo.phase_list = phase_list
        ys = SBS_DSP.synthesize1(amp_list, f_list, ts, phase_list)
        self.parent.AWGInfo.f_list = f_list
        self.parent.AWGInfo.amp_list = amp_list
        self.parent.AWGInfo.phase_list = phase_list
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


    def sweep_Pump(self,i,amp_list,f_list,phase_list):
        j=10  # 多音扫频梳齿数
        new_ampl = amp_list[i*j : i*(j+1)]
        new_fl = f_list[i*j : i*(j+1)]
        new_phasel = phase_list[i*j : i*(j+1)]
        # new_ampl.append(amp_list[-i*j-6:i*j-1])
        # new_fl.append(f_list[-i*j-6:i*j-1])
        # new_phasel.append(phase_list[-i*j-6:i*j-1])
        # print(new_fl)
        ys = SBS_DSP.synthesize1(new_ampl, new_fl,
                                 self.parent.AWGInfo.ts, new_phasel)
        self.parent.AWGInfo.ys = ys
        wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
        self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
        self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave, ch=self.parent.AWGInfo.ChannelNum)
        if self.parent.AWGInfo.AWG_Status:
            # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
            #                                     channel=self.parent.AWGInfo.ChannelNum)
            self.parent.AWGHandle.play()

    def DonePump(self):
        '''
        两种方式，扫频与正常
        :return:
        '''
        AWG_framerate = 64e9  # AWG采样率
        self.parent.AWGHandle.set_fs(fs=AWG_framerate)
        if self.pumpdesignsetBtu.isChecked():
            if self.plusFreq.isChecked():
                self.parent.AWGInfo.f_list+=self.parent.AWGInfo.BWFreq
            if self.minusFreq.isChecked():
                self.parent.AWGInfo.f_list-=self.parent.AWGInfo.BWFreq

            f_list = self.parent.AWGInfo.f_list
            amp_list = self.parent.AWGInfo.amp_list
            phase_list = self.parent.AWGInfo.phase_list
            ts=self.parent.AWGInfo.ts
            CF = self.parent.AWGInfo.CFFreq
            BW = self.parent.AWGInfo.BWFreq
            DF = self.parent.AWGInfo.DFFreq
            if self.sweepFreq.isChecked():
                '''
                扫描方式：
                1.正常生成频梳，利用矩形滤波器决定AWG发送数据
                '''
                self.timer.stop()
                start = time.time()
                for i in range(int(len(f_list)/5)):

                #     t = Timer(1.0, self.sweep_Pump(i,amp_list,f_list,phase_list))
                #     t.start()

                #     M=10            #总共10根梳齿扫频，根据每次经验值推算
                #     j=int(M/2)
                    j=5
                    new_ampl=amp_list[i*j:i*j+10]
                    new_fl=f_list[i*j:i*j+10]
                    new_phasel=phase_list[i*j:i*j+10]
                    # new_ampl.append(amp_list[-i*j-6:i*j-1])
                    # new_fl.append(f_list[-i*j-6:i*j-1])
                    # new_phasel.append(phase_list[-i*j-6:i*j-1])
                    print(new_fl)
                    ys = SBS_DSP.synthesize1(new_ampl,new_fl,
                                             self.parent.AWGInfo.ts, new_phasel)
                    self.parent.AWGInfo.ys = ys
                    wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
                    self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
                    self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,ch=self.parent.AWGInfo.ChannelNum)
                    if self.parent.AWGInfo.AWG_Status:
                        # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                        #                                     channel=self.parent.AWGInfo.ChannelNum)
                        self.parent.AWGHandle.play()
                    time.sleep(0.3)

                end = time.time()
                print("循环运行时间:%.2f秒" % (end - start))
                self.timer.start(0)
            else:
                self.timer.stop()
                # 预反馈部分
                # if len(f_list)>1:todo:长度不匹配，后期改
                #     amp_list = self.pre_amp_seq(BW, DF)

                # ts = np.linspace(0, t_AWG, N_AWG, endpoint=False)
                ys = SBS_DSP.synthesize1(amp_list, f_list, ts, phase_list)
                self.parent.AWGInfo.f_list = f_list
                self.parent.AWGInfo.amp_list = amp_list
                self.parent.AWGInfo.phase_list = phase_list
                self.parent.AWGInfo.ts = ts
                self.parent.AWGInfo.ys = ys
                wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
                self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
                self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                                                    ch=self.parent.AWGInfo.ChannelNum)
                if self.parent.AWGInfo.AWG_Status:
                    # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                    #                                     channel=self.parent.AWGInfo.ChannelNum)
                    self.parent.AWGHandle.play()

                FFT_y, Fre = SBS_DSP.get_fft(ys, AWG_framerate)
                self.parent.AWGInfo.FFT_y = FFT_y
                self.parent.AWGInfo.Fre = Fre
                # Lorenz拟合
                Tb = 10 * 10 ** 6  # 10~30Mhz布里渊线宽
                omega_sbs = 7e9  # 布里渊平移量
                f_measure = np.arange(CF - 2 * BW - omega_sbs, CF + 2 * BW - omega_sbs, 10 ** 6)
                self.parent.AWGInfo.f_measure = f_measure
                total_lorenz = SBS_DSP.add_lorenz(f_measure, amp_list * 0.008, f_list, Tb)

                self.parent.AWGInfo.gb = total_lorenz



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
        self.plot_data = self.pw.addPlot(left='Amp', bottom='Freq(Hz)', title='SBSGain')

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

    def plot3(self,gain_on_off,freq_data):
        self.plot_data.clear()
        r_color1 = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])
        self.plot_data.plot(freq_data,gain_on_off,pen=r_color1)
        self.plot_data.showGrid(x=True,y=True)


class LightCtrl(QtWidgets.QGroupBox):
    '''
    激光器控制模块
    '''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('LightWave Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        # 激光器控制面板
        LightWidget = QtWidgets.QGroupBox()
        LightWidget.setFlat(True)
        LightWidget.setAlignment(QtCore.Qt.AlignLeft)

        self.StartWave = QtWidgets.QLineEdit()
        self.StartWave.setPlaceholderText('Start_C Band')
        StartCalidator = QtGui.QDoubleValidator(self)
        StartCalidator.setRange(1530, 1630)
        StartCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        StartCalidator.setDecimals(4)
        self.StartWave.setValidator(StartCalidator)

        self.EndWave=QtWidgets.QLineEdit()
        self.EndWave.setPlaceholderText('End_C Band')
        EndCalidator=QtGui.QDoubleValidator(self)
        EndCalidator.setRange(1530,1630)
        EndCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        EndCalidator.setDecimals(4)
        self.EndWave.setValidator(EndCalidator)

        self.StartFreq=QtWidgets.QLineEdit()
        self.StartFreq.setPlaceholderText('Start_Freq_193414.489GHz')
        SFCalidator=QtGui.QDoubleValidator(self)
        SFCalidator.setRange(183921.753,195942.783) #GHz,精确到1MHz
        SFCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        SFCalidator.setDecimals(3)
        self.StartFreq.setValidator(SFCalidator)

        self.EndFreq=QtWidgets.QLineEdit()
        self.EndFreq.setPlaceholderText('End_Freq_addBW')
        EFCalidator=QtGui.QDoubleValidator(self)
        EFCalidator.setRange(183921.753,195942.783) #GHz,精确到1MHz
        EFCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        EFCalidator.setDecimals(3)
        self.EndFreq.setValidator(EFCalidator)

        self.BWFreq=QtWidgets.QLineEdit()
        self.BWFreq.setPlaceholderText('Freq_BW')
        BWCalidator=QtGui.QDoubleValidator(self)
        BWCalidator.setRange(0.3,8) #GHz
        BWCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        BWCalidator.setDecimals(3)
        self.BWFreq.setValidator(BWCalidator)


        self.Power = QtWidgets.QLineEdit()
        self.Power.setPlaceholderText('0~20dBm')
        PowerCalidator = QtGui.QDoubleValidator(self)
        PowerCalidator.setRange(0, 30)
        PowerCalidator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        # PowerCalidator.setDecimals(2)
        self.Power.setValidator(PowerCalidator)
        self.ActiveBtu = QtWidgets.QPushButton('Active')
        self.ActiveBtu.setStyleSheet(
            '''QPushButton{background:rgb(170,200,50);}QPushButton:hover{background:yellow;}''')
        self.ActiveBtu.setMaximumSize(200, 200)
        self.ActiveBtu.setCheckable(True)
        self.enterBtu = QtWidgets.QPushButton('Enter')
        self.enterBtu.setChecked(False)

        LightLayout = QtWidgets.QGridLayout()
        # LightLayout.setSpacing(0)
        LightLayout.addWidget(QtWidgets.QLabel('StartWave：'), 0, 0)
        LightLayout.addWidget(self.StartWave, 0, 1)
        LightLayout.addWidget(QtWidgets.QLabel('nm  '), 0, 2)
        LightLayout.addWidget(QtWidgets.QLabel('EndWave: '),0,3)
        LightLayout.addWidget(self.EndWave,0,4)
        LightLayout.addWidget(QtWidgets.QLabel('nm '),0,5)
        LightLayout.addWidget(QtWidgets.QLabel('StartFreq: '),1,0)
        LightLayout.addWidget(self.StartFreq,1,1)
        LightLayout.addWidget(QtWidgets.QLabel('GHz '),1,2)
        LightLayout.addWidget(QtWidgets.QLabel('EndFreq: '),1,3)
        LightLayout.addWidget(self.EndFreq,1,4)
        LightLayout.addWidget(QtWidgets.QLabel('GHz '),1,5)
        LightLayout.addWidget(QtWidgets.QLabel('Freq_BW: '),2,0)
        LightLayout.addWidget(self.BWFreq,2,1)
        LightLayout.addWidget(QtWidgets.QLabel('GHz '),2,2)
        LightLayout.addWidget(QtWidgets.QLabel('Power:'), 2, 3)
        LightLayout.addWidget(self.Power, 2, 4)
        LightLayout.addWidget(QtWidgets.QLabel('dBm  '), 2, 5)

        LightLayout.addWidget(self.enterBtu, 3, 0,1,2)
        LightLayout.addWidget(self.ActiveBtu, 3, 3,1,2)
        LightWidget.setLayout(LightLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addStretch(1)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(LightWidget)
        self.setLayout(mainLayout)

        self.clicked.connect(self.check)
        self.enterBtu.clicked.connect(self.setupLight)
        self.ActiveBtu.clicked.connect(self.activeF)

        self.StartWave.textChanged.connect(self.setupWaveFill)
        # self.StartFreq.textChanged.connect(self.setupFreqFill)
        self.EndWave.textChanged.connect(self.setupEF)
        # self.EndFreq.textChanged.connect(self.setupEW)
        self.BWFreq.textChanged.connect(self.setupAll)


    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.LightHandle):
            self.setChecked(True)
            self.parent.LightCtrl.setCheckable(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No LightWave is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.LightCtrl.setChecked(False)

    def setupAll(self):
        C_speed = 299792458  # m/s
        BW=siEval(self.BWFreq.text())
        self.StartWave.setText(str(1550))
        self.EndWave.setText(str(round(C_speed/(BW+C_speed/1550),4)))

    def setupEF(self):
        C_speed=299792458  # m/s
        EndW=siEval(self.EndWave.text())
        SFreq=siEval(self.StartFreq.text())
        EFreq=siEval(self.EndFreq.text())
        self.EndFreq.setText(str(round(C_speed/EndW,3)))


    def setupWaveFill(self):
        C_speed=299792458  # m/s
        # wave='nm'
        # freq='GHz'
        SWave=siEval(self.StartWave.text())
        self.EndWave.setText(str(SWave))
        self.StartFreq.setText(str(round(C_speed/SWave,3)))
        self.EndFreq.setText(str(round(C_speed/SWave,3)))


    def setupLight(self):
        if (self.parent.testModeAction.isChecked() or self.parent.LightHandle):
            self.setChecked(True)
            self.parent.LightCtrl.setCheckable(True)
            if siEval(self.BWFreq.text())==0:
                self.parent.LightHandle.setupLight(power=float(self.Power.text()), wavelength=float(self.StartWave.text()))
            else:
                self.parent.LightHandle.sweepLight(waveStart=float(self.StartWave.text()),
                                                   waveEnd=float(self.EndWave.text()),
                                                   speed=200)

        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No LightWave is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.LightCtrl.setChecked(False)

    def activeF(self):
        api_light.LightSCPI.active(self)


class EDFACtrl(QtWidgets.QGroupBox):
    '''光信号EDFA控制栏'''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
        self.setTitle('EDFA Ctrl')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        EDFA1 = QtWidgets.QGroupBox()
        EDFA1.setTitle('EDFA1')
        EDFA1.setFlat(True)
        EDFA1.setAlignment(QtCore.Qt.AlignTop)
        EDFA1Layout = QtWidgets.QGridLayout()
        EDFA1Layout.setAlignment(QtCore.Qt.AlignTop)

        self.addressEDFA1 = QtWidgets.QLabel()

        self.setPower1 = QtWidgets.QWidget()
        self.setPower1Fill = QtWidgets.QLineEdit('5')
        self.setPower1UnitSel = QtWidgets.QComboBox()
        self.setPower1UnitSel.addItems(['dBm', 'mW'])
        self.setPower1UnitSel.setCurrentIndex(0)

        setPower1Layout = QtWidgets.QHBoxLayout()
        setPower1Layout.addWidget(QtWidgets.QLabel('SetPower'))
        setPower1Layout.addWidget(self.setPower1Fill)
        setPower1Layout.addWidget(self.setPower1UnitSel)
        self.setPower1.setLayout(setPower1Layout)

        self.P1slider = QtWidgets.QSlider()
        self.P1slider.setOrientation(QtCore.Qt.Horizontal)
        self.P1slider.setMaximum(20)
        self.P1slider.setMinimum(0)
        self.P1slider.setValue(5)
        # self.P1slider.setSingleStep(0.01)
        self.P1slider.setTickInterval(0.01)
        self.enterBtu1 = QtWidgets.QPushButton('Enter')
        self.activeBtu1 = QtWidgets.QPushButton('Active')
        self.activeBtu1.setCheckable(True)
        self.activeBtu1.setStyleSheet('''QPushButton{background:rgb(170,200,50);}QPushButton:hover{background:red;}''')

        EDFA1Layout.addWidget(QtWidgets.QLabel('Inst_COM:'), 0, 0)
        EDFA1Layout.addWidget(self.addressEDFA1, 0, 1, 1, 3)
        EDFA1Layout.addWidget(self.setPower1, 1, 0, 1, 3)
        EDFA1Layout.addWidget(self.P1slider, 3, 0, 1, 3)
        EDFA1Layout.addWidget(self.enterBtu1, 4, 0, 1, 1)
        EDFA1Layout.addWidget(self.activeBtu1, 4, 2, 1, 1)
        EDFA1.setLayout(EDFA1Layout)

        EDFA2 = QtWidgets.QGroupBox()
        EDFA2.setTitle('EDFA2')
        EDFA2.setFlat(True)
        EDFA2.setAlignment(QtCore.Qt.AlignTop)
        EDFA2Layout = QtWidgets.QGridLayout()
        EDFA2Layout.setAlignment(QtCore.Qt.AlignTop)

        self.addressEDFA2 = QtWidgets.QLabel()

        self.setPower2 = QtWidgets.QWidget()
        self.setPower2Fill = QtWidgets.QLineEdit('5')
        self.setPower2UnitSel = QtWidgets.QComboBox()
        self.setPower2UnitSel.addItems(['dBm', 'mW'])
        self.setPower2UnitSel.setCurrentIndex(0)

        setPower2Layout = QtWidgets.QHBoxLayout()
        setPower2Layout.addWidget(QtWidgets.QLabel('SetPower'))
        setPower2Layout.addWidget(self.setPower2Fill)
        setPower2Layout.addWidget(self.setPower2UnitSel)
        self.setPower2.setLayout(setPower2Layout)

        self.P2slider = QtWidgets.QSlider()
        self.P2slider.setOrientation(QtCore.Qt.Horizontal)
        self.P2slider.setMaximum(20)
        self.P2slider.setMinimum(0)
        self.P2slider.setValue(5)
        self.P2slider.setTickInterval(0.01)

        self.enterBtu2 = QtWidgets.QPushButton('Enter')
        self.activeBtu2 = QtWidgets.QPushButton('Active')
        self.activeBtu2.setCheckable(True)
        self.activeBtu2.setStyleSheet('''QPushButton{background:rgb(170,200,50);}QPushButton:hover{background:red;}''')

        EDFA2Layout.addWidget(QtWidgets.QLabel('Inst_COM:'), 0, 0)
        EDFA2Layout.addWidget(self.addressEDFA2, 0, 1, 1, 3)
        EDFA2Layout.addWidget(self.setPower2, 1, 0, 1, 3)
        EDFA2Layout.addWidget(self.P2slider, 3, 0, 1, 3)
        EDFA2Layout.addWidget(self.enterBtu2, 4, 0, 1, 1)
        EDFA2Layout.addWidget(self.activeBtu2, 4, 2, 1, 1)
        EDFA2.setLayout(EDFA2Layout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(EDFA1)
        mainLayout.addWidget(EDFA2)
        self.setLayout(mainLayout)

        self.setPower1Fill.textChanged.connect(self.EDFAChangeFun)
        self.P1slider.valueChanged.connect(self.EDFAChangeFun)
        self.setPower2Fill.textChanged.connect(self.EDFAFillChangeFun)
        self.P2slider.valueChanged.connect(self.EDFAChangeFun)
        self.clicked.connect(self.check)
        self.enterBtu1.clicked.connect(self.enterFun1)
        self.enterBtu2.clicked.connect(self.enterFun2)
        self.activeBtu1.clicked.connect(self.activeFun1)
        self.activeBtu2.clicked.connect(self.activeFun2)

    def check(self):
        if (self.parent.testModeAction.isChecked() or self.parent.EDFA1Handle or self.parent.EDFA2Handle):
            self.setChecked(True)
            self.parent.EDFACtrl.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No EDFA is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.EDFACtrl.setChecked(False)
        # self.parent.EDFACtrl.print_info()

    def EDFAChangeFun(self):

        self.setPower1Fill.setText(str(self.P1slider.value()))
        self.setPower2Fill.setText(str(self.P2slider.value()))
        EDFA1_status, EDFA1_Power = api_val.val_edfa1power(self.setPower1Fill.text(),
                                                           self.setPower1UnitSel.currentText())
        EDFA2_status, EDFA2_Power = api_val.val_edfa2power(self.setPower2Fill.text(),
                                                           self.setPower2UnitSel.currentText())
        self.parent.EDFAInfo.EDFA1power = EDFA1_Power
        self.parent.EDFAInfo.EDFA2power = EDFA2_Power

    def EDFAFillChangeFun(self):
        self.P1slider.setValue(int(self.setPower1Fill.text()))
        self.P2slider.setValue(int(self.setPower2Fill.text()))
        EDFA1_status, EDFA1_Power = api_val.val_edfa1power(self.setPower1Fill.text(),
                                                           self.setPower1UnitSel.currentText())
        EDFA2_status, EDFA2_Power = api_val.val_edfa2power(self.setPower2Fill.text(),
                                                           self.setPower2UnitSel.currentText())
        self.parent.EDFAInfo.EDFA1power = EDFA1_Power
        self.parent.EDFAInfo.EDFA2power = EDFA2_Power

    def enterFun1(self):
        api_edfa.EDFA1Set(EDFA1Handle=self.parent.EDFA1Handle, power=self.parent.EDFAInfo.EDFA1power)

    def activeFun1(self):
        if (self.parent.testModeAction.isChecked or self.parent.EDFA1Handle or self.parent.EDFA2Handle):
            self.setChecked(True)
            api_edfa.Active1(self.parent.EDFA1Handle)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No EDFA is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.EDFACtrl.setChecked(False)

    def enterFun2(self):
        api_edfa.EDFA2Set(EDFA2Handle=self.parent.EDFA2Handle, power=self.parent.EDFAInfo.EDFA2power)

    def activeFun2(self):
        if (self.parent.testModeAction.isChecked or self.parent.EDFA1Handle or self.parent.EDFA2Handle):
            self.setChecked(True)
            api_edfa.Active2(self.parent.EDFA2Handle)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No EDFA is connected!')
            msg.exec_()
            self.setChecked(False)
            self.parent.EDFACtrl.setChecked(False)


class Feedback(QtWidgets.QGroupBox):
    '''
    反馈算法
    1.带内平整度计算显示:目标带宽内，最大最小差值
    2.均方误差：与目标波形均方误差
    4.收敛方式：
        反馈次数
        均方误差
    '''
    # btu_map = QtWidgets.QPushButton('Mapping')
    # btu_map.setCheckable(True)
    # btu_map.setStyleSheet('''QPushButton:hover{background:yellow;}''')

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent

        self.setTitle('FB_Algorithm')
        self.setAlignment(QtCore.Qt.AlignLeft)

        # 反馈算法监控系数
        FBWidget = QtWidgets.QGroupBox()
        FBWidget.setFlat(True)
        FBWidget.setAlignment(QtCore.Qt.AlignLeft)

        # 需要显示收敛方式，均方误差实时显示（颜色标记升降）；反馈次数显示
        self.MSE = QtWidgets.QLineEdit()
        self.MSE.setPlaceholderText('MSEDisplay')
        self.FBnum = QtWidgets.QLineEdit()
        self.FBnum.setPlaceholderText('FB_Number')
        self.activeBtu = QtWidgets.QPushButton('Run')
        self.activeBtu.setStyleSheet('''QPushButton{background:rgb(170,200,50);}QPushButton:hover{background:red;}''')
        self.activeBtu.setMaximumSize(400, 400)
        self.activeBtu.setCheckable(True)
        self.backBtu = QtWidgets.QPushButton('Original')
        self.back = QtWidgets.QLineEdit()
        self.back.setPlaceholderText('NONE_PUMP')
        self.bfsBtu = QtWidgets.QPushButton('S_BFS&FWHM')
        self.bfs = QtWidgets.QLineEdit()
        self.bfs.setPlaceholderText('bfs_GHz')
        self.alpha = QtWidgets.QLineEdit()
        self.alpha.setPlaceholderText('alpha=1')
        self.linew=QtWidgets.QLineEdit()
        self.linew.setPlaceholderText('L_W_MHz')
        self.smoothindx=QtWidgets.QLineEdit()
        self.smoothindx.setPlaceholderText('smooth_i=301')
        self.width_peak=QtWidgets.QLineEdit()
        self.width_peak.setPlaceholderText('width=500')
        self.rel_height=QtWidgets.QLineEdit()
        self.rel_height.setPlaceholderText('height=0.1')
        self.min_base_indx=QtWidgets.QLineEdit()
        self.min_base_indx.setPlaceholderText('base=0')

        self.modFB = QtWidgets.QComboBox()
        self.modFB.addItems(api_val.FB_modList)
        self.modFBDispaly = QtWidgets.QLineEdit()

        self.ManualBtu=QtWidgets.QPushButton('Manual')
        self.ManualBtu.setStyleSheet('''QPushButton:hover{background:yellow;}''')
        self.btu_map=QtWidgets.QPushButton('Mapping')
        self.btu_map.setCheckable(True)
        self.btu_map.setStyleSheet('''QPushButton:hover{background:yellow;}''')
        self.btu_dfFB=QtWidgets.QPushButton('DF_FB')
        self.btu_dfFB.setStyleSheet('''QPushButton:hover{background:yellow;}''')

        FBLayout = QtWidgets.QGridLayout()
        FBLayout.setAlignment(QtCore.Qt.AlignLeft)
        FBLayout.addWidget(QtWidgets.QLabel('MSE:'), 0, 0, 1, 1)
        FBLayout.addWidget(self.MSE, 0, 1, 1, 1)
        FBLayout.addWidget(QtWidgets.QLabel('FB_Num:'), 1, 0, 1, 1)
        FBLayout.addWidget(self.FBnum, 1, 1, 1, 1)
        FBLayout.addWidget(self.backBtu, 0, 4, 1, 1)
        FBLayout.addWidget(self.back, 1, 4, 1, 1)
        FBLayout.addWidget(self.bfsBtu, 0, 5, 1, 1)
        FBLayout.addWidget(self.alpha, 0, 6, 1, 1)
        FBLayout.addWidget(self.bfs, 1, 5, 1, 1)
        FBLayout.addWidget(self.linew,1,6,1,1)
        FBLayout.addWidget(self.activeBtu, 0, 7, 2, 1)
        FBLayout.addWidget(self.ManualBtu,2,1,1,1)
        FBLayout.addWidget(self.btu_map,2,4,1,1)
        FBLayout.addWidget(self.smoothindx,2,2,1,1)
        FBLayout.addWidget(self.min_base_indx,2,3,1,1)
        FBLayout.addWidget(self.width_peak,2,5,1,1)
        FBLayout.addWidget(self.rel_height,2,6,1,1)
        FBLayout.addWidget(self.btu_dfFB,2,7,1,1)
        FBLayout.addWidget(QtWidgets.QLabel('Mod_Switch:'), 0, 2)
        FBLayout.addWidget(self.modFB, 0, 3)
        FBLayout.addWidget(self.modFBDispaly, 1, 2, 1, 2)
        self.setLayout(FBLayout)

        self.modFB.currentIndexChanged[int].connect(self.switch_mod)
        self.backBtu.clicked.connect(self.getBack)
        self.activeBtu.clicked.connect(self.FB_Function)
        self.bfsBtu.clicked.connect(self.getBFS)
        self.ManualBtu.clicked.connect(self.Manual_Fun)
        self.btu_map.clicked.connect(self.mapping_Fun)
        self.btu_dfFB.clicked.connect(self.dfFB_Fun)

        self.bfs.textChanged.connect(self.set_update)
        self.linew.textChanged.connect(self.set_update)
        self.alpha.textChanged.connect(self.set_update)
        self.smoothindx.textChanged.connect(self.set_update)
        self.width_peak.textChanged.connect(self.set_update)
        self.min_base_indx.textChanged.connect(self.set_update)

        # self.BGS_freq = []
        # self.BGS_amp = []
        # self.bfs_value = 7.15e3

    def dfFB_Fun(self):
        freq_design_seq = self.parent.AWGInfo.f_list
        freq = self.parent.AWGInfo.freq_FB
        gain_offset = self.parent.AWGInfo.gain_on_off_FB
        BFS=self.parent.AWGInfo.bfs
        FWHM=self.parent.AWGInfo.gamma_b
        new_freq_design=df_feedback(freq_design_seq,freq,gain_offset,BFS,FWHM)
        self.parent.AWGInfo.f_list=new_freq_design
        # AWGCtrl.DonePump(self)
        f_list=new_freq_design
        amp_list = self.parent.AWGInfo.amp_list
        phase_list = self.parent.AWGInfo.phase_list
        ts = self.parent.AWGInfo.ts
        ys = SBS_DSP.synthesize1(amp_list, f_list, ts, phase_list)

        wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
        self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
        self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                                           ch=self.parent.AWGInfo.ChannelNum)
        if self.parent.AWGInfo.AWG_Status:
            # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
            #                                     channel=self.parent.AWGInfo.ChannelNum)
            self.parent.AWGHandle.play()
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No AWG is connected!')
            msg.exec_()

    def mapping_Fun(self):
        if self.btu_map.isChecked():
            if self.parent.PNAHandle:
                self.parent.AWGInfo.map=1
            else:
                msg = Shared.MsgError(self, 'No Instrument!', 'No PNAN5225A is connected!')
                msg.exec_()
                self.btu_map.setCheckable(True)
        else:
            self.parent.AWGInfo.map=0

    def set_update(self):
        if self.linew.text():
            self.parent.AWGInfo.gamma_b=float(self.linew.text())      #手动设置线宽
        if self.bfs.text():
            self.parent.AWGInfo.bfs=float(self.bfs.text())
        if self.alpha.text():
            self.parent.AWGInfo.alpha=float(self.alpha.text())
        if self.smoothindx.text():
            self.parent.AWGInfo.smooth=int(self.smoothindx.text())
        if self.width_peak.text():
            self.parent.AWGInfo.width_peak=int(self.width_peak.text())
            # print(self.parent.AWGInfo.width_peak)
        if self.rel_height.text():
            self.parent.AWGInfo.rel_height_peak=float(self.rel_height.text())
        if self.min_base_indx.text():
            self.parent.AWGInfo.min_base_indx=int(self.min_base_indx.text())


    def search_index(self, f_seq, f_measure):
        # 功能：找到f_seq在f_measure中最接近位置(差的绝对值最小)的索引f_index
        # PS : 当前默认每个点都能找到，如果范围不对应可能会出现隐藏bug
        f_index = np.zeros(f_seq.size, dtype=int)
        idx_seq = 0
        find_num = 0
        idx_min = 0
        idx_max = -1  # 默认梳齿不是f_measure最后一个元素
        while find_num < f_seq.size:
            freq_slide = abs(f_measure[idx_min: idx_max] - f_seq[idx_seq])
            find_idx = np.argmin(freq_slide) + idx_min
            f_index[idx_seq] = find_idx
            find_num += 1
            if idx_seq < 0:
                idx_seq = -idx_seq
                idx_max = find_idx  # 更新搜索右边界
            else:
                idx_min = find_idx  # 更新搜索左边界
                idx_seq = -(idx_seq + 1)
        return f_index


    def expected_gain(self, f_index, measure_brian, type_filter):
        # 3db带宽范围：fmax - fmin + FWHM（半峰全宽）
        # 2版：均值取fmax - fmin范围内，最后算泵浦对应位置
        len_seq = len(f_index)

        if type_filter == 'Rectangle':
            # expected_gain_sam = np.ones(len_seq) * np.mean(brian_measure_sam)
            expected_gain_sam = np.ones(len_seq) * np.mean(measure_brian[f_index[1]:f_index[-2]])
        elif type_filter == 'Triangle':
            mb_min = max(np.min(measure_brian), 0)
            mb_max = np.max(measure_brian)
            if len_seq % 2 == 0:
                expected_seq1 = np.linspace(mb_min, mb_max, len_seq // 2)
                expected_seq2 = np.linspace(mb_max, mb_min, len_seq // 2)
            else:
                expected_seq1 = np.linspace(mb_min, mb_max, len_seq // 2 + 1)
                expected_seq2 = np.linspace(mb_max, mb_min, len_seq // 2 + 1)
                expected_seq2 = np.delete(expected_seq2, 0)
            expected_gain_sam = np.hstack((expected_seq1, expected_seq2))
        else:
            print('非法字符，请检查type_filter')
            expected_gain_sam = None
        return expected_gain_sam

    def lorenz(self, omega, omega_B, gamma_B):
        # 系数简化版
        # 输入：频率-omega；omega_B-布里渊增益最大点（BFS）；gamma_B-布里渊线宽
        # 输出：Lorenz型的增益因子g_B * g_0 * L_eff/A_eff
        gain_max = 10
        gamma_b22 = (gamma_B / 2) ** 2
        gain_lorenz = gain_max * gamma_b22 / ((omega - omega_B) ** 2 + gamma_b22)
        return gain_lorenz

    def corre_filter(self, measure_brian, gamma_B):
        # 功能：洛伦兹互相关去噪，修改线宽gamma_B影响分辨率
        x = np.linspace(-3 * 10 ** 3, 3 * 10 ** 3, 1000)  # 扫频范围，单位MHz
        ref_brian = self.lorenz(x, 0, gamma_B)
        corr = np.correlate(measure_brian, ref_brian, 'same')
        index_max = measure_brian.argmax()
        corr_refine = corr / corr.max() * np.mean(measure_brian[index_max - 5:index_max + 5])
        return corr_refine

    def bfs_correct(self, f_seq, f_measure, measure_brian, gamma_B=15):
        # 功能：洛伦兹互相关滤波取最值得到较准确整体BFS(单位：MHz)，精度取决于f_measure
        # 前提：观察窗口内有SBS增益且只有一个最大值)
        f_resolution = f_measure[1] - f_measure[0]
        amp_measure = self.corre_filter(measure_brian, gamma_B / f_resolution)
        cfp = np.median(f_seq)
        cf = f_measure[amp_measure.argmax()]
        bfs = cfp - cf
        return bfs

    def getBack(self):
        if (self.parent.testModeAction.isChecked()):
            self.back.clear()
            self.back.setPlaceholderText('Test!!! NONE')
        else:
            if (self.parent.PNAHandle):
                freq_BG_Signal, amp_BG_Signal = self.parent.PNAHandle.pna_acquire(measName=self.parent.PNAInfo.Scale)
                self.parent.AWGInfo.BJ_freq = freq_BG_Signal
                self.parent.AWGInfo.BJ_amp = amp_BG_Signal
                # self.BGS_amp=savgol_filter(amp_BG_Signal,51, 3, mode='nearest')
                self.back.clear()
                self.back.setPlaceholderText('Well Done!!!')
            else:
                self.back.clear()
                self.back.setPlaceholderText('Check PNA!')

    def peak_analysis(self,freq, gain_on_off):
        # 函数功能：峰值分析，具体包括通过开关增益计算主峰频率、增益、半高全宽FWHM,基线
        # 输入：测量频率(单位GHz)，开关增益
        # 输出：主峰BFS(默认中心频率15GHz),峰值，FWHM,基线(常数)
        freq = np.array(freq, dtype='float64')
        f_resolution = float(freq[1] - freq[0])  # 频率分辨率(GHz)
        # peaks, _ = find_peaks(gain_on_off, width=500, rel_height=0.1)  # 寻峰
        gain_on_off = np.array(gain_on_off)
        max_peak = np.max(gain_on_off)
        peaks, _ = find_peaks(gain_on_off, height=[max_peak - 1, max_peak])  # 寻峰

        prominences = peak_prominences(gain_on_off, peaks)[0]  # 计算峰高
        idx_main_peak = prominences.argmax()  # 找主峰
        BFS = self.parent.AWGInfo.CFFreq/1e9 - freq[peaks[idx_main_peak]]  # 求BFS(单位GHz)，默认中心频率15GHz
        main_peak_gain = prominences[idx_main_peak]  # 主峰峰值
        baseline = max(gain_on_off[peaks]) - main_peak_gain  # 求基线

        results_half = peak_widths(gain_on_off, peaks, rel_height=0.5)  # tuple{0：宽度;1：高度;2:xmin;3:xmax}
        FWHM_main_peak = results_half[0][idx_main_peak] * 1e3 * f_resolution  # 主峰半高全宽(单位MHz)

        return BFS, main_peak_gain, FWHM_main_peak, baseline

    def getBFS(self):
        # 功能：按下"BFS",计算单频泵浦的BFS和半高全宽
        if (self.parent.testModeAction.isChecked()):
            self.back.clear()
            self.back.setPlaceholderText('Test!!! NONE')
        else:
            if (self.parent.PNAHandle):
                freq_single_comb, amp_single_comb = self.parent.PNAHandle.pna_acquire(
                    measName=self.parent.PNAInfo.Scale)  # todo:改为本地已存单频泵浦增益数据
                freq_single_comb = freq_single_comb/1e9  # 单位GHz
                amp_single_comb = amp_single_comb - self.parent.AWGInfo.BJ_amp

                amp_single_comb = savgol_filter(amp_single_comb, 301, 3)  # 3阶SG平滑
                BFS, main_peak_gain, FWHM_main_peak, baseline = self.peak_analysis(freq_single_comb, amp_single_comb)  # 获取峰值分析参数
                self.parent.AWGInfo.bfs = BFS  # SBS平移量单位GHz
                self.parent.AWGInfo.gamma_b=FWHM_main_peak   # 单频线宽单位MHz
                self.parent.AWGInfo.baseline=baseline
                self.bfs.clear()
                self.linew.clear()
                self.bfs.setPlaceholderText('bfs='+str(round(self.parent.AWGInfo.bfs,1)) + 'GHz')
                self.linew.setPlaceholderText('线宽='+str(round(self.parent.AWGInfo.gamma_b,1))+'MHz')
            else:
                self.bfs.clear()
                self.bfs.setPlaceholderText('Check PNA!')


    def FB_Function(self, status):
        mod_index = self.modFB.currentIndex()
        print('alpha=',self.parent.AWGInfo.alpha)

        mod_shape = self.parent.AWGInfo.mod_sel
        if status:
            if (self.parent.testModeAction.isChecked()):
                self.activeBtu.setCheckable(True)
            else:
                # 仿真反馈触发
                self.activeBtu.setCheckable(True)
                # mod_index=2,以反馈次数作为收敛量
                if mod_index == 2:
                    FB_num = int(self.modFBDispaly.text())
                    print(FB_num)
                    i = 1
                    for _ in range(FB_num):
                        """当前反馈为实时反馈FB_num次结束，等待时间长且容易卡死
                        todo：
                        方案1：改为手动单次反馈
                        方案2：修改时延函数"""
                        freq_design_seq = self.parent.AWGInfo.f_list
                        print('freq_design_seq', len(freq_design_seq))
                        amp_design_seq = self.parent.AWGInfo.amp_list
                        freq_measure, amp_measure = self.parent.PNAHandle.pna_acquire(
                            measName=self.parent.PNAInfo.Scale)
                        amp_measure = amp_measure - self.parent.AWGInfo.BJ_amp  # 计算开关增益
                        amp_measure = savgol_filter(amp_measure, 301, 3)  # 单位MHz；300点3阶SG平滑去噪
                        baseline = peak_analysis(freq=freq_measure / 1e9, gain_on_off=amp_measure)
                        amp_measure = amp_measure - baseline  # 开关增益减去基线
                        measure_max = amp_measure.max()
                        amp_measure = amp_measure / measure_max  # 最大值归一化

                        f_index = self.search_index(freq_design_seq - self.parent.AWGInfo.bfs * 1e9, freq_measure)  # 搜索时减去BFS
                        print('f_index',len(f_index))
                        expected_amp_sam = self.expected_gain(f_index, amp_measure, 'Rectangle')
                        amp_measure_sam = np.array([amp_measure[j] for j in f_index])  # 最接近频梳频率的采样点增益
                        print('amp_design_seq', len(amp_design_seq),'expected_amp_sam',len(expected_amp_sam),'amp_measure_sam',len(amp_measure_sam))
                        amp_design_seq_new = mlt.change_amp_seq(amp_design_seq, expected_amp_sam, amp_measure_sam, 1,self.parent.AWGInfo.alpha)
                        amp_design_seq_new = mlt.normalize_amp_seq(amp_design_seq_new,freq_design_seq,self.parent.AWGInfo.phase_list)

                        self.parent.AWGInfo.amp_list = amp_design_seq_new
                        print('new amp_design_seq =', amp_design_seq_new)

                        ys = SBS_DSP.synthesize1(amp_design_seq_new,
                                                 self.parent.AWGInfo.f_list,
                                                 self.parent.AWGInfo.ts,
                                                 self.parent.AWGInfo.phase_list)
                        self.parent.AWGInfo.ys = ys
                        wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
                        self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
                        # self.parent.AWGHandle.clear_all_wfm()
                        # wfmID = self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                        #                                            ch=self.parent.AWGInfo.ChannelNum)
                        # self.parent.AWGHandle.play(wfmID=wfmID, ch=self.parent.AWGInfo.ChannelNum)
                        self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                                                           ch=self.parent.AWGInfo.ChannelNum)
                        if self.parent.AWGInfo.AWG_Status:
                            # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                            #                                     channel=self.parent.AWGInfo.ChannelNum)
                            self.parent.AWGHandle.play()

                        self.FBnum.setText(str(i))
                        # 预留设备设置时间10ms
                        time.sleep(10)
                        i += 1
                    self.FBnum.setText(str(i - 1) + '  Done !!!')
                    # self.activeBtu.setCheckable(False)
                elif mod_index == 1:
                    # 范围在0-1
                    '''
                    1.PNA抽取数据与目标波形（自身均值作为等长度数列）
                    2.离线对50组数据进行GA或TS迭代
                    3.与最开始的目标波形做均方误差(目前还是用带内平整度（）)
                    4.直到收敛
                    '''
                    MES = float(self.modFBDispaly.text())
                    print(MES)
                    ant_Num=50
                    freq_measure=[]
                    amp_measure=[]
                    for a in range(ant_Num):
                        freq_measure[a], amp_measure[a]=self.parent.PNAHandle.pna_acquire()

                else:
                    pass

    def switch_mod(self):
        mod_index = self.modFB.currentIndex()

        if mod_index == 1:
            self.modFBDispaly.clear()
            self.modFBDispaly.setPlaceholderText('MSE')

        elif mod_index == 2:
            self.modFBDispaly.clear()
            self.modFBDispaly.setPlaceholderText('FB_Num.')

    def Manual_Fun(self):
        self.parent.ManualFB_Fun.exec_()



class VNAMonitor(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        pg.setConfigOptions(leftButtonPan=False)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        # self.pgPlot = pg.PlotWidget(title='PNA Monitor')
        self.pgPlot = pg.MultiPlotWidget()
        self.plot_data = self.pgPlot.addPlot(left='RF_Power(dB)', bottom='Freq(Hz)', title='RF_Spectrum')
        self.plot_btn = QtWidgets.QPushButton('Replot', self)
        self.export_btn = QtWidgets.QPushButton('export', self)
        self.plot_btn.clicked.connect(self.plot)
        self.export_btn.clicked.connect(self.export)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.plot_btn)
        self.btn_layout.addWidget(self.export_btn)

        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.pgPlot)
        self.v_layout.addLayout(self.btn_layout)

        self.setLayout(self.v_layout)

        # self.data=np.empty()
        # self.timer_start()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.plot)
        self.timer.start(1500)
        # 设置计时间隔并启动(1000ms == 1s)
        self.map_len=1

    def timer_start(self):
        if self.parent.PNAHandle:
            # PNACtrl.setChecked(True)
            PNACtrl.InitialF
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.plot)
            self.timer.start(1000)
        else:
            pass

    def plot(self):
        # self.timer.stop()
        self.plot_data.clear()
        if self.parent.Display == 1:
            freq, result = self.parent.PNAHandle.pna_acquire(measName=self.parent.PNAInfo.Scale)
            if self.parent.AWGInfo.map*self.map_len==1:
                if len(result)==len(self.parent.AWGInfo.BJ_amp):
                    gain_on_off=result-self.parent.AWGInfo.BJ_amp
                    gain_on_off=savgol_filter(gain_on_off,self.parent.AWGInfo.smooth,3)
                    self.map_len=1
                    if self.parent.AWGInfo.min_base_indx == 0:
                        baseline = peak_analysis(freq=freq / 1e9, gain_on_off=gain_on_off)

                        gain_on_off_offset=gain_on_off-baseline
                    else:
                        gain_on_off_offset = gain_on_off-min(gain_on_off)
                    # gain_on_off_offset.tolist()
                else:
                    msg = Shared.MsgError(self, 'Note!!', '请重新采集背景信号！')
                    msg.exec_()
                    # self.map_len=0
                    # Feedback.btu_map.setChecked(True)
                    gain_on_off_offset = result
            else:
                gain_on_off_offset=result

            self.plot_data.plot(freq, gain_on_off_offset, pen='b')
            self.parent.AWGInfo.freq_FB=freq
            self.parent.AWGInfo.gain_on_off_FB=gain_on_off_offset
            self.plot_data.showGrid(x=True, y=True)
            # self.timer.start(1000)
        else:
            pass

    def export(self):
        '''[频率，幅值]写入csv '''
        # todo：把相位也读取保存
        today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        default_path = os.path.join(r"D:\Documents\项目", today_date)
        default_name = '\\pump_IL_cp'
        self.mkdir(default_path)
        self.filepath, type = QtWidgets.QFileDialog.getSaveFileName(self, "文件保存", default_path + default_name,
                                                                    'csv(*.csv)')  # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        pump_lists_designed = pd.DataFrame(
            {'freq_list': self.parent.AWGInfo.freq_FB, 'amp_list': self.parent.AWGInfo.gain_on_off_FB})
        pump_lists_designed.to_csv(self.filepath, index=False, sep=',')  # 将DataFrame存储为csv,index表示是否显示行名，default=True


    def mkdir(self, path):
        isExists = os.path.exists(path)
        if not isExists:
            # 如果不存在则创建目录
            # 创建目录操作函数
            os.makedirs(path)
            print(path + ' 创建成功')
            return True
        else:
            # 如果目录存在则不创建，并提示目录已存在
            print(path + ' 目录已存在')
            return False


    def off(self):
        self.pgPlot.clearMouse()

def peak_analysis(freq,gain_on_off):
    # 函数功能：峰值分析，具体包括通过开关增益计算主峰频率、增益、半高全宽FWHM,基线
    # 输入：测量频率(单位GHz)，开关增益
    # 输出：主峰BFS(默认中心频率15GHz),峰值，FWHM,基线(常数)
    freq = np.array(freq, dtype='float64')
    f_resolution = float(freq[1] - freq[0])  # 频率分辨率(GHz)
    # peaks, _ = find_peaks(gain_on_off, width, rel_height)  # 寻峰
    gain_on_off = np.array(gain_on_off)
    max_peak = np.max(gain_on_off)
    peaks, _ = find_peaks(gain_on_off, height=[max_peak-1,max_peak])  # 寻峰

    prominences = np.array(peak_prominences(gain_on_off, peaks)[0])  # 计算峰高
    idx_main_peak = prominences.argmax()  # 找主峰
    # BFS = 15 - freq[peaks[idx_main_peak]]  # 求BFS(单位GHz)，默认中心频率15GHz 可将15GHz换为输入变量
    main_peak_gain = prominences[idx_main_peak]  # 主峰峰值
    baseline = max(gain_on_off[peaks]) - main_peak_gain  # 求基线

    # results_half = peak_widths(gain_on_off, peaks, rel_height=0.5)  # tuple{0：宽度;1：高度;2:xmin;3:xmax}
    # FWHM_main_peak = results_half[0][idx_main_peak]*1e3*f_resolution  # 主峰半高全宽(单位MHz)

    # return BFS, main_peak_gain, FWHM_main_peak, baseline
    return baseline

def df_feedback(freq_design_seq, freq, gain_offset, BFS, FWHM):
    # 功能：通过左右区间积分，在自然线宽范围内微调梳齿频率间隔（待验证）
    # 输入：梳齿频率freq_design_seq(Hz), 开关增益的频率freq(Hz)和校准基线后的开关响应gain_offset(dB)
    # BFS  # 读取单频测量所得BFS，单位GHz
    # FWHM  # 读取单频测量所得FWHM，单位MHz

    # 边缘梳齿频率不变，只改中间
    freq_design_seq_sam = freq_design_seq[1:-1]
    new_freq_design = freq_design_seq

    # print('freq_design_seq_sam =', freq_design_seq_sam + BFS*1e9)
    f_index = mlt.search_index(freq_design_seq_sam - BFS * 1e9, freq)  # 搜索时减去BFS,freq_design_seq和freq单位相同(Hz)
    # print('find freq =', freq[f_index])

    ratio = 0.4  # 加窗点数/FWHM对应点数
    n_dots = int(ratio * (f_index[1] - f_index[0]))  # 半区间取点个数
    sample_array = np.array([gain_offset[i - n_dots:i + n_dots + 1] for i in f_index])
    left_list = np.hstack((np.ones(n_dots) / n_dots, np.zeros(n_dots + 1)))
    left_measure_sam = np.dot(sample_array, left_list)
    right_list = np.hstack((np.zeros(n_dots + 1), np.ones(n_dots) / n_dots))
    right_measure_sam = np.dot(sample_array, right_list)
    temp = (0.5 - left_measure_sam / (left_measure_sam + right_measure_sam))
    offset_f = temp * FWHM
    new_freq_design[1:-1] = freq_design_seq_sam - offset_f * 1e6
    return new_freq_design