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
        for ch in range(1, 4):
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

    def set_dacMode(self, dacMode='single'):
        """
        Sets and reads DAC mode for the M8195A using SCPI commands.
        Args:
            dacMode (str): DAC operation mode. ('single', 'dual', 'four', 'marker', 'dcd', 'dcmarker')
        """

        if dacMode not in ['single', 'dual', 'four', 'marker', 'dcd', 'dcmarker']:
            raise ValueError("'dacMode' must be 'single', 'dual', 'four', 'marker', 'dcd', or 'dcmarker'.")

        self.write(f'inst:dacm {dacMode}')
        self.dacMode = self.query('inst:dacm?').strip().lower()

        def set_memDiv(self, memDiv=1):
            """
            Sets and reads memory divider rate using SCPI commands.
            Args:
                memDiv (int): Clock/memory divider rate. (1, 2, 4)
            """

            if memDiv not in [1, 2, 4]:
                raise ValueError('Memory divider must be 1, 2, or 4.')
            self.write(f'instrument:memory:extended:rdivider div{memDiv}')
            self.memDiv = int(self.query('instrument:memory:extended:rdivider?').strip().split('DIV')[-1])

    def set_fs(self, fs=65e9):
        """
        Sets and reads sample rate using SCPI commands.
        Args:
            fs (float): AWG sample rate.
        """

        if not isinstance(fs, (int, float)) or fs <= 0:
            raise ValueError('Sample rate must be a positive floating point value.')
        self.write(f'frequency:raster {fs}')
        self.fs = float(self.query('frequency:raster?').strip())
        self.effFs = self.fs / self.memDiv

        def set_func(self, func='arb'):
            """
            Sets and reads AWG function using SCPI commands.
            Args:
                func (str): AWG mode, either arb or sequencing. ('arb', 'sts', 'stsc')
            """

            if func.lower() not in ['arb', 'sts', 'stsc']:
                raise ValueError("'func' argument must be 'arb', 'sts', 'stsc'")
            self.write(f'func:mode {func}')
            self.func = self.query('func:mode?').strip()

    def set_refSrc(self, refSrc='axi'):
        """
        Sets and reads reference source using SCPI commands.
        Args:
            refSrc (str): Reference clock source. ('axi', 'int', 'ext')
        """

        if refSrc.lower() not in ['axi', 'int', 'ext']:
            raise ValueError("'refSrc' must be 'axi', 'int', or 'ext'")
        self.write(f'roscillator:source {refSrc}')
        self.refSrc = self.query('roscillator:source?').strip()

    def set_refFreq(self, refFreq=100e6):
        """
        Sets and reads reference frequency using SCPI commands.
        Args:
            refFreq (float): Reference clock frequency.
        """

        if not isinstance(refFreq, float) or refFreq <= 0:
            raise ValueError('Reference frequency must be a positive floating point value.')
        self.write(f'roscillator:frequency {refFreq}')
        self.refFreq = float(self.query('roscillator:frequency?').strip())

    def set_amplitude(self,amplitude=500,channel=1):
        return
        if channel not in  [1,2,3,4]:
            raise AWGError('\'channel\'must be 1,2,3,or4.')
        if not isinstance(amplitude,float)and not isinstance(amplitude,int):
            raise AWGError('\'amplitudu\'must be a floating point value.')
        if amplitude>1000 or amplitude<0:
            raise AWGError('\'amplitude\'must be between 0 and 1V.')
        self.write(f'voltage{channel}{amplitude}')
        exec(f"self.amp{channel}=float(self.query('voltage{channel}?'))")

    def sanity_check(self):
        """Prints out user-accessible class attributes."""

        print('Sample rate:', self.fs)
        print('DAC Mode:', self.dacMode)
        print('Function:', self.func)
        print('Ref source:', self.refSrc)
        print('Ref frequency:', self.refFreq)
        print('Amplitude CH 1:', self.amp1)
        print('Amplitude CH 2:', self.amp2)
        print('Amplitude CH 3:', self.amp3)
        print('Amplitude CH 4:', self.amp4)

    def download_wfm(self, wfmData, ch=1, name='wfm', *args, **kwargs):
        """
        Defines and downloads a waveform into the segment memory.
        Assigns a waveform name to the segment. Returns segment number.
        Args:
            wfmData (NumPy array): Waveform samples (real or complex floating point values).
            ch (int): Channel to which waveform will be downloaded.
            name (str): Optional name for waveform.
            # sampleMkr (int): Index of the beginning of the sample marker.
            # syncMkr (int): Index of the beginning of the sync marker.

        Returns:
            (int): Segment number of the downloaded waveform. Use this as the waveform identifier for the .play() method.
        """

        # Stop output before doing anything else
        self.write('abort')
        wfm = self.check_wfm(wfmData)
        length = len(wfmData)

        # Initialize waveform segment, populate it with data, and provide a name
        segment = int(self.query(f'trace{ch}:catalog?').strip().split(',')[-2]) + 1
        self.write(f'trace{ch}:def {segment}, {length}')
        self.binblockwrite(f'trace{ch}:data {segment}, 0, ', wfm)
        self.write(f'trace{ch}:name {segment},"{name}_{segment}"')

        # Use 'segment' as the waveform identifier for the .play() method.
        return segment

    def check_wfm(self, wfmData):
        """
        HELPER FUNCTION
        Checks minimum size and granularity and returns waveform with
        appropriate binary formatting.

        See pages 273-274 in Keysight M8195A User's Guide (Edition 13.0,
        October 2017) for more info.
        Args:
            wfmData (NumPy array): Unscaled/unformatted waveform data.

        Returns:
            (NumPy array): Waveform data that has been scaled and
                formatted appropriately for download to AWG
        """

        # If waveform length doesn't meet granularity or minimum length requirements, repeat the waveform until it does
        repeats = wraparound_calc(len(wfmData), self.gran, self.minLen)
        wfm = np.tile(wfmData, repeats)
        rl = len(wfm)
        if rl < self.minLen:
            raise error.AWGError(f'Waveform length: {rl}, must be at least {self.minLen}.')
        if rl % self.gran != 0:
            raise error.GranularityError(f'Waveform must have a granularity of {self.gran}.')

        # Apply the binary multiplier, cast to int16, and shift samples over if required
        return np.array(self.binMult * wfm, dtype=np.int8) << self.binShift

    def delete_segment(self, wfmID=1, ch=1):
        """
        Deletes specified waveform segment.
        Args:
            wfmID (int): Waveform identifier, used to select waveform to be deleted.
            ch (int): AWG channel from which the segment will be deleted.
        """

        # Argument checking
        if type(wfmID) != int or wfmID < 1:
            raise socketscpi.SockInstError('Segment ID must be a positive integer.')
        if ch not in [1, 2, 3, 4]:
            raise socketscpi.SockInstError('Channel must be 1, 2, 3, or 4.')
        self.write('abort')
        self.write(f'trace{ch}:del {wfmID}')

    def clear_all_wfm(self):
        """Clears all segments from segment memory."""
        self.write('abort')
        for ch in range(1, 5):
            self.write(f'trace{ch}:del:all')

    def play(self, wfmID=1, ch=1):
        """
        Selects waveform, turns on analog output, and begins continuous playback.
        Args:
            wfmID (int): Waveform identifier, used to select waveform to be played.
            ch (int): AWG channel out of which the waveform will be played.
        """

        self.write(f'trace:select {wfmID}')
        self.write(f'output{ch} on')
        self.write('init:cont on')
        self.write('init:imm')

    def stop(self, ch=1):
        """
        Turns off analog output and stops playback.
        Args:
            ch (int): AWG channel to be deactivated.
        """

        self.write(f'output{ch} off')
        self.write('abort')

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
    def read_power_toggle(self):
        # 获取设备状态
        try:
            text=self.query(':OUTP?')
            status=bool(int(text.strip()))
            return status
        except:
            return False


class AWGError(Exception):
    """AWG Exception class"""
    pass