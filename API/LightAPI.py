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
    def __init__(self,host,port=5025):
        self.OpenConnection()
        return

    def write(self, CommandString):
        self._Instrument.write(CommandString)
        return

    def query(self, QueryString):
        ret = self._Instrument.query(QueryString)
        return ret

    def OpenConnection(self,InstVisaAddr):
        if InstVisaAddr == 'N.A.':
            return None
        else:
            try:
                self._rm=pyvisa.ResourceManager('c:/windows/system32/visa32.dll')
                self._Instrument=self._rm.open_resource(InstVisaAddr)
                # self.IDNString=self.Query('*IDN')
                return
            except:
                return None

    def setupLight(self,power,wavelength):
        Wave=wavelength*1e9
        self.write(f'sour0:wav:freq {Wave}')
        self.write(f'sour0:pow:att {power}')
        self.query('*opc?')

    def active(self):
        self.write('trig1:optp dis')