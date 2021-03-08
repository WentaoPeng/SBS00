#! encoding=utf_8
import pyvisa
import visa
import os.path
import socketscpi
"""
TODO:
1.针对LightWave扫频控制，改变pump载波中心频率
2.实现控制LightWave基本功能
"""

class LightSCPI(socketscpi.SocketInstrument):
    '''
    Keysight LightWave Ctrl

    '''
    def __init__(self,host,port=5025,timeout=10,reset=False):
        super(LightSCPI, self).__init__(hsot,port,timeout)
        if reset:
            self.write('*rst')
            self.write('*opc?')


    def sweepLight(self,powerList,waveStart,waveEnd,speed):
        '''针对于大带宽调控，进行PUMP路载波扫频方法；频率精确到0.0001nm
        1.单音扫频
        2.多音扫频
        如何配合AWG反馈振幅？
        '''



    def setupLight(self,power,wavelength):
        Wave=wavelength*1e9
        self.write(f'sour0:wav:freq {Wave}')
        self.write(f'sour0:pow:att {power}')
        self.query('*opc?')

    def active(self):
        self.write('trig1:optp dis')