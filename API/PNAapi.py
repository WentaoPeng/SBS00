#! encoding = utf-8
import pyvisa
import sys
import os.path
import time
import numpy as np
import socketscpi

"""
TODO:
1.通过ip访问
2.读取网分数据，并显示
    可调节显示范围，自动寻找增益范围
    自动调节扫描点数
    可设置平均系数
    可设置IF 分辨频率
    可设置探测光功率
3.自检
"""


class PNASCPI(socketscpi.SocketInstrument):

    def __init__(self, host, port=5025, timeout=10, reset=False):
        super().__init__(host, port, timeout)
        if reset:
            self.write('*rst')
            self.query('*opc?')

        self.write('system:fpreset')
        self.query('*opc?')
        self.write('display:window1:state on')

    def configure(self, **kwargs):
        """
        分开多函数执行
        :param kwargs: startFreq  endFreq  numpoints
        ifBW  power  meas
        :return:分发函数
        """
        for key, value in kwargs.items():
            if key == 'startFreq':
                self.set_startFreq(value)
            elif key == 'endFreq':
                self.set_endFreq(value)
            elif key == 'numpoints':
                self.set_numpoints(value)
            elif key == 'ifBw':
                self.set_ifBW(value)
            elif key == 'power':
                self.set_power(value)
            elif key == 'avgpoints':
                self.set_avgpoints(value)
            else:
                return KeyError(
                    f'Invalid keyword argument:"{key}"'
                )
        self.err_check()

    def set_startFreq(self, start):
        self.write(f'SENS:FREQ:STAR {start}')

    def set_endFreq(self, end):
        self.write(f'SENS:FREQ:STOP {end}')

    def set_numpoints(self, numpoints):
        self.write(f'SENS:SWE:POIN {numpoints}')

    def set_ifBW(self, ifBW):
        self.write(f'SENS:FOM:RANG:SEGM:BWID {ifBW}')

    def set_power(self, power):
        self.write(f'SOUR:POW1 {power}')

    def allmeas(self):
        self.write('DISP:WIND:TRAC:Y:AUTO')
        self.query('*opc?')

    def set_avgpoints(self, avgvalue):
        self.write(f'SENSe1:AVERage:Count {avgvalue}')
        # self.write(f'SENS:SWE:POIN {avgvalue}')
        self.write('SENS:AVER ON')
        self.query('*opc?')


    def set_Smoothing(self,Btn):
        if Btn:
            self.write(f'CALC:SMO ON')
        else:
            self.write(f'CALC:SMO OFF')

    def PNA_setup(self, measName=['S21']):
        """
        :param kwargs:针对初始化enter，
        主要设置S11 S12 S21 S22 window1
        measName，measParm
        :return:
        """
        # if not isinstance(measName, list):
        #     raise TypeError('measName and measParam must be lists of strings, even when defining only one measurement.')

        self.write('system:fpreset')
        self.query('*opc?')
        self.write('display:window1:state on')
        # self.write('calc1:par:def "S21",S21')
        # self.write('disp:wind1:trac1:feed S21')
        self.write(f'calculate:parameter:define:ext "{measName}","{measName}"')
        self.write(f'display:window1:trace1:FEED "{measName}"')
        self.write('DISP:WIND:TRAC:Y:AUTO')

    def pna_acquire(self, measName='S21'):
        """Acquires frequency and measurement data from selected measurement on VNA for plotting."""
        if not isinstance(measName, str):
            raise TypeError('measName must be a string.')
        # Select measurement to be transferred.
        self.write(f'calculate1:parameter:select "{measName}"')

        # Format data for transfer.
        self.write('format:border swap')
        self.write('format real,64')  # Data type is double/float64, not int64.
        # hold
        # self.write('SENS:SWE:MODE HOLD')
        # Acquire measurement data.
        # self.write('calculate1:data? fdata')
        meas = self.binblockread(cmd='calculate1:data? fdata', datatype='d')
        self.query('*opc?')

        # Acquire frequency data.
        # self.write('calculate1:x?')
        freq = self.binblockread(cmd='calculate1:x?', datatype='d')
        self.query('*opc?')
        # Continuous
        # self.write('SENS:SWE:MODE CONTinous')

        return freq, meas
