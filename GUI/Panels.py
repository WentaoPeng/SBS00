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
        self.InstEnable.setText('ON'if self.parent.AWGInfo.AWG_Status else 'OFF')
        self.ChannelNum.setText(str(self.parent.AWGInfo.ChannelNum))
        self.DACset.setText(str(self.parent.AWGInfo.DAC_index))
        self.ShapeStatus.setText(self.parent.AWGInfo.mod_index)
        self.CWSet.setText(str(self.parent.AWGInfo.CFFreq)+'Hz')
        self.BWSet.setText(str(self.parent.AWGInfo.BWFreq)+'Hz')
        self.DFSet.setText(str(self.parent.AWGInfo.DFFreq)+'Hz')
        self.Amplitude.setText(str(self.parent.AWGInfo.AWGPower)+'Mv')


    def refresh_fun(self):
        if self.parent.testModeAction.isChecked() or  (not self.parent.AWGHandle):
            pass
        else:
            self.addressText.setText(self.parent.AWGInfo.instName)
            self.InstEnable.setText('ON'if self.parent.AWGInfo.AWG_Status else 'OFF')
            self.ChannelNum.setText(str(self.parent.AWGInfo.ChannelNum))
            self.DACset.setText(str(self.parent.AWGInfo.DAC_index))
            self.ShapeStatus.setText(self.parent.AWGInfo.mod_index)
            self.CWSet.setText(str(self.parent.AWGInfo.CFFreq)+'Hz')
            self.BWSet.setText(str(self.parent.AWGInfo.BWFreq)+'Hz')
            self.DFSet.setText(str(self.parent.AWGInfo.DFFreq)+'Hz')
            self.Amplitude.setText(str(self.parent.AWGInfo.AWGPower)+'Mv')

    def show_InstMoreInfo(self):
        # 待扩展
        return

    def err_msg(self):
        '''AWG反馈错误信息'''
        if self.parent.AWGHandle:
            self.parent.AWGInfo.errMsg=api_awg.M9502A.err_check()
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
        # pCenter=QtGui.QDoubleValidator()
        # pCenter.setRange(0,40*10**9)
        # pCenter.setNotation(QtGui.QDoubleValidator.StandardNotation)
        # pCenter.setDecimals(2)
        self.CenterFreqFill=QtWidgets.QLineEdit('10')
        # self.CenterFreqFill.setText('10')
        # self.CenterFreqFill.setValidator(pCenter)
        # self.CenterFreqFill = QtWidgets.QLineEdit.setValidator(pdouble)
        self.CenterFreqUnitSel = QtWidgets.QComboBox()
        self.CenterFreqUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.CenterFreqUnitSel.setCurrentIndex(3)
        CenterFreqLayout = QtWidgets.QHBoxLayout()
        CenterFreqLayout.addWidget(QtWidgets.QLabel('CenterFreq'))
        CenterFreqLayout.addWidget(self.CenterFreqFill)
        CenterFreqLayout.addWidget(self.CenterFreqUnitSel)
        self.CenterFreq.setLayout(CenterFreqLayout)

        self.BandWidth = QtWidgets.QWidget()
        # pBand=QtGui.QDoubleValidator()
        # pBand.setRange(0,8*10**9)
        # pBand.setNotation(QtGui.QDoubleValidator.StandardNotation)
        # pBand.setDecimals(2)
        self.BandWidthFill = QtWidgets.QLineEdit('200')
        # self.BandWidthFill.setText('200')
        # self.BandWidthFill.setValidator(pBand)
        self.BandWidthUnitSel = QtWidgets.QComboBox()
        self.BandWidthUnitSel.addItems(['Hz', 'KHz', 'MHz', 'GHz'])
        self.BandWidthUnitSel.setCurrentIndex(2)
        BandWidthLayout = QtWidgets.QHBoxLayout()
        BandWidthLayout.addWidget(QtWidgets.QLabel('BandWidth'))
        BandWidthLayout.addWidget(self.BandWidthFill)
        BandWidthLayout.addWidget(self.BandWidthUnitSel)
        self.BandWidth.setLayout(BandWidthLayout)

        self.CombFreq = QtWidgets.QWidget()
        # pComb=QtGui.QDoubleValidator()
        # pComb.setRange(1,10**9)
        self.CombFreqFill = QtWidgets.QLineEdit('10')
        # self.CombFreqFill.setValidator(pComb)
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
                                                           'Manual Input (0mV to 1000mV)',self.parent.AWGInfo.AWGPower, 0, 1000, 1)
        if okay:
            if self.parent.testModeAction.isChecked():
                pass
            else:
                self.parent.AWGInfo.AWGPower=target_Power
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
        mod_index=self.PumpModeSel.currentText()
        self.parent.AWGInfo.mod_index=mod_index
        print(mod_index)
        # DAC选择
        DAC_index=self.DACset.text()
        self.parent.AWGInfo.DAC_index=DAC_index
        print(DAC_index)
        # 通道选择
        Channel_N=self.channelNumset.currentText()
        self.parent.AWGInfo.ChannelNum=Channel_N
        print(Channel_N)
        CF_status,CF_freq=api_val.val_awgCW_mod_freq(self.CenterFreqFill.text(),
                                                   self.CenterFreqUnitSel.currentText())
        BW_status,BW_freq=api_val.val_awgBW_mod_freq(self.BandWidthFill.text(),
                                                     self.BandWidthUnitSel.currentText())
        DF_status,DF_freq=api_val.val_awgDF_mod_freq(self.CombFreqFill.text(),
                                                     self.CombFreqUnitSel.currentText())
        self.CenterFreqFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(CF_status)))
        self.BandWidthFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(BW_status)))
        self.CombFreqFill.setStyleSheet('border:1px solid {:s}'.format(Shared.msgcolor(DF_status)))

        self.parent.AWGInfo.CFFreq=CF_freq
        self.parent.AWGInfo.BWFreq=BW_freq
        self.parent.AWGInfo.DFFreq=DF_freq





    def DesignPump(self):



        AWG_framerate = 64 * 10 ** 9 # AWG采样率
        Df = 1 * 10 ** 6
        # FM_AWG = AWG_framerate / 2.56   # AWG最高分析频率
        N_AWG = int(AWG_framerate / Df)
        t_AWG = N_AWG * (1 / AWG_framerate)
        CF=self.parent.AWGInfo.CFFreq
        BW=self.parent.AWGInfo.BWFreq
        DF=self.parent.AWGInfo.DFFreq

        if self.PumpModeSel.currentIndex==0:
            f_list,amp_list,phase_list=SBS_DSP.square_filter(CF,BW,DF)
        elif self.PumpModeSel.currentIndex==1:
            f_list,amp_list,phase_list=SBS_DSP.triangle_filter(CF,BW,DF)
        else:
            f_list,amp_list,phase_list=SBS_DSP.square_filter(CF,BW,DF)
            # f_list,amp_list,phase_list=SBS_DSP.Band_stop_filter(CF,BW,DF,signal_BW=5*10**9)

        ts=np.linspace(0,t_AWG,N_AWG,endpoint=False)

        ys=SBS_DSP.synthesize1(amp_list,f_list,ts,phase_list)
        print(f_list)
        print(self.parent.AWGInfo.CFFreq)
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示符号

        plt.figure()
        plt.subplot(211)
        plt.plot(ts, ys, 'b')
        plt.xlabel("t（毫秒）")
        plt.ylabel("S(t)幅值")
        plt.title("叠加信号图")
        # plt.show()

        # fs,hz=get_fft(ys,N_FPGA)
        fs, hz = SBS_DSP.get_fft(ys, N_AWG)
        # angle_fs = np.angle(np.abs(np.abs(fft(ys))/N_FPGA))
        # angle_hz=np.arange(len(ys))
        plt.subplot(212)
        plt.xlim(9500, 10500)
        plt.plot(hz, fs, 'g')
        # plt.subplot(313)
        # plt.plot(angle_fs,angle_fs,'p')
        plt.xlabel("F（MHz）")
        plt.ylabel("A归一化")
        plt.title("PUMP频梳")
        plt.savefig('triangle.png')
        plt.show()


class OSACtrl(QtWidgets.QGroupBox):
    '''
    光谱仪控制显示
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


class EDFA1Ctrl(QtWidgets.QGroupBox):
    '''小信号EDFA控制栏'''

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
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

    def __init__(self, parent):
        QtWidgets.QGroupBox.__init__(self, parent)
        self.parent = parent
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
