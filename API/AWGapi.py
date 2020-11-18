#! encoding = utf-8
import pyvisa
import visa
import os.path
import socketscpi
"""
TODO:
1.针对M9502A创建SCPI类
"""
Shape_MODE_LIST = ['Rectangle', 'Triangle', 'Band Stop']

class M9502A(socketscpi.SocketInstrument):

    '''
    Generic class for controlling Keysight M9502A AWG.


    '''
    def __init__(self,host,port=5025,timeout=10,reset=False):
        super().__init__(host,port,timeout)
        if reset:
            self.write('*rst')
            self.query('*opc?')
        # Query all settings from AWG and store them as class attributes
        self.dacMode = self.query('inst:dacm?').strip()
        self.memDiv = 1
        self.fs = float(self.query('frequency:raster?').strip())
        self.effFs = self.fs / self.memDiv
        self.func = self.query('func:mode?').strip()
        self.refSrc = self.query('roscillator:source?').strip()
        self.refFreq = float(self.query('roscillator:frequency?').strip())
        self.amp1 = float(self.query('voltage1?'))
        self.amp2 = float(self.query('voltage2?'))
        self.amp3 = float(self.query('voltage3?'))
        self.amp4 = float(self.query('voltage4?'))

        # Initialize waveform format constants and populate them with check_resolution()
        self.gran = 256
        self.minLen = 1280
        self.binMult = 127
        self.binShift = 0

    # def configure(self, dacMode='single', memDiv=1, fs=64e9, refSrc='axi', refFreq=100e6, amp1=300e-3, amp2=300e-3, amp3=300e-3, amp4=300e-3, func='arb'):
    def configure(self, **kwargs):
        """
        Sets basic configuration for M8195A and populates class attributes accordingly.
        Keyword Arguments:
            dacMode (str): DAC operation mode. ('single', 'dual', 'four', 'marker', 'dcd', 'dcmarker')
            memDiv (int): Clock/memory divider rate. (1, 2, 4)
            fs (float): AWG sample rate.
            refSrc (str): Reference clock source. ('axi', 'int', 'ext')
            refFreq (float): Reference clock frequency.
            amp1/2/3/4 (float): Output amplitude in volts pk-pk. (min=75 mV, max=1 V)
            func (str): AWG mode, either arb or sequencing. ('arb', 'sts', 'stsc')
        """

        # Stop output on all channels before doing anything else
        for ch in range(1, 5):
            self.stop(ch=ch)

        # Check to see which keyword arguments the user sent and call the appropriate function
        for key, value in kwargs.items():
            if key == 'dacMode':
                self.set_dacMode(value)
            elif key == 'memDiv':
                self.set_memDiv(value)
            elif key == 'fs':
                self.set_fs(value)
            elif key == 'refSrc':
                self.set_refSrc(value)
            elif key == 'refFreq':
                self.set_refFreq(value)
            elif key == 'amp1':
                self.set_amplitude(value, channel=1)
            elif key == 'amp2':
                self.set_amplitude(value, channel=2)
            elif key == 'amp3':
                self.set_amplitude(value, channel=3)
            elif key == 'amp4':
                self.set_amplitude(value, channel=4)
            elif key == 'func':
                self.set_func(value)
            else:
                raise KeyError(
                    f'Invalid keyword argument: "{key}"')  # raise KeyError('Invalid keyword argument. Use "dacMode", "memDiv", "fs", "refSrc", "refFreq", "amp1/2/3/4", or "func".')

        self.err_check()

    def set_amplitude(self,amplitude=500,channel=1):


    def ramp_down(start,stop):
        n=start
        while n>stop:
            n=n-1
            yield n

    def ramp_up(start,stop):
        n=start
        while n<stop:
            n=n+1
            yield n