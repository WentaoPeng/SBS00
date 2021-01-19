#! encoding = utf-8

from PyQt5 import QtGui, QtCore, QtWidgets
import random
from API import validators as api_val
from API import AWGapi as api_awg

from math import ceil
import numpy as np

BUTTONLABEL = {'confirm': ['Lets do it', 'Go forth and conquer', 'Ready to go',
                           'Looks good', 'Sounds about right'],
               'complete': ['Nice job', 'Sweet', 'Well done', 'Mission complete'],
               'accept': ['I see', 'Gotcha', 'Okay', 'Yes master'],
               'reject': ['Never mind', 'I changed my mind', 'Cancel', 'I refuse'],
               'error': ['Oopsy!', 'Something got messed up', 'Bad']
               }


def btn_label(btn_type):
    ''' Randomly generate a QPushButton label.
        Arguments
            btn_type: str
        Returns
            label: str
    '''

    try:
        a_list = BUTTONLABEL[btn_type]
        return a_list[random.randint(0, len(a_list) - 1)]
    except KeyError:
        return 'A Button'


class AWGInfo():
    '''AWG信息'''

    def __init__(self):
        self.instName = 'AWG M9502A'
        self.ChannelNum = 0
        self.CFFreq = 10 * 10 ** 9
        self.BWFreq = 200 * 10 ** 6
        self.DFFreq = 10 * 10 ** 6
        self.AWG_Status =False
        self.mod_index = 0
        self.mod_sel = ''
        self.DAC_index = 0
        self.ChannelNum = 1
        self.AWGPower = 500
        self.errMsg = ''
        self.Address = '192.168.1.101'
        # 设计波形参数
        self.ts = 0
        self.ys = 0
        self.AWGwave=0
        self.FFT_y = 0
        self.Fre = 0
        self.gb = 0
        self.f_measure = 0
        # 频率及幅值列表
        self.f_list=[]
        self.amp_list=[]
        self.phase_list=[]

    def full_info_query(self, AWGHandle):
        '''采集设备信息'''
        if AWGHandle:
            self.instName = AWGHandle.resource_name
            self.AWG_Status = api_awg.M9502A.read_power_toggle
            self.errMsg = ''
        else:
            self.instName = 'No Instrument'


class PNAInfo():
    '''PNA信息'''

    def __init__(self):
        self.instName = ''
        self.Scale=''
        self.AvgPoints=0
        self.Power=0
        self.SweepPoints=0
        self.StartFerq=10**7
        self.EndFerq=50*10**9


    def full_info_query(self, PNAHandle):
        if PNAHandle:
            self.instName = PNAHandle.resource_name
        else:
            self.instName='NoInstrument'

class MsgError(QtGui.QMessageBox):
    ''' Error message box '''

    def __init__(self, parent, title_text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)

class InstStatus(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, code):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(str(code))
        self.setWindowTitle('Instrument Communication Failure!')


class LightInfo():
    '''Lightwave信息'''

    def __init__(self):
        self.instName = ''
        self.instInterface = ''
        self.instInterfaceNum = 0

    def full_info_query(self, LightHandle):
        if LightHandle:
            self.instName = LightHandle.resource_name
            self.instInterface = str(LightHandle.interface_type)
            self.instInterfaceNum = LightHandle.interface_number


class EDFAInfo():
    '''EDFA1 信息'''

    def __init__(self):
        self.instName = ''
        self.instInterface = ''
        self.instInterfaceNum = 0
        self.EDFA1power=0
        self.EDFA2power=0

    def full_info_query(self, EDFA1Handle):
        if EDFA1Handle:
            self.instName = EDFA1Handle.resource_name
            self.instInterface = str(EDFA1Handle.interface_type)
            self.instInterfaceNum = EDFA1Handle.interface_number


class AWGChannelBox(QtWidgets.QComboBox):
    '''AWG通道选取'''

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        bandList = []

        for key in api_val.AWGCHANNELSET:
            msg = 'Channel:{:d}'.format(api_val.AWGCHANNELSET[key])
            bandList.append(msg)
        self.addItems(bandList)
        self.setCurrentIndex(4)


def msgcolor(status_code):
    ''' Return message color based on status_code.
        0: fatal, red
        1: warning, gold
        2: safe, green
        else: black
    '''

    if not status_code:
        return '#D63333'
    elif status_code == 1:
        return '#FF9933'
    elif status_code == 2:
        return '#00A352'
    else:
        return '#000000'
