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
        super(LightSCPI, self).__init__(host,port,timeout)
        if reset:
            self.write('*rst')
            self.write('*opc?')


    def sweepLight(self,waveStart,waveEnd,speed):
        '''针对于大带宽调控，进行PUMP路载波扫频方法；频率精确到0.0001nm
        1.单音扫频
        2.多音扫频
        如何配合AWG反馈振幅？
        '''
        self.write(f'wav:swe:star {waveStart}nm')
        self.write(f'wav:swe:stop {waveEnd}nm')
        self.write('wav:swe:mode CONT')
        #可选择三种模式 STEP步进   MAN手动   CONT连续
        self.write('wav:swe:cycl 1000')  #循环次数
        #步进速度
        self.write(f'wav:swe:spe {speed}nm/s') #max200nm/s min 5--【m/s
        self.write('wav:swe:step 5nm')  #min0.0001nm

        self.write('wav:swe STAR')  #STOP STAR PAUS CONT状态
        self.query('*opc?')


    def setupLight(self,power,wavelength):
        # Wave=wavelength*1e9
        self.write(f'sour0:wav {wavelength}nm')
        self.write('sour0:pow:unit 0')
        self.write(f'sour0:pow {power}')
        self.query('*opc?')

    def active(self):
        self.write('trig0:optp dis')