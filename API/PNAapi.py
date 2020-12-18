#! encoding = utf-8
import pyvisa
import sys
import os.path
import time
import numpy as np
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
class PNASCPI():

    def __init__(self,visaAddress):
        self.OpenConnection(visaAddress)
        return

    def write(self, CommandString):
        self._Instrument.write(CommandString)
        return

    def query(self, QueryString):
        ret = self._Instrument.query(QueryString)
        return ret

    def OpenConnection(self, InstVisaAddr):
        if InstVisaAddr == 'N.A.':
            return None
        else:
            try:
                self._rm=pyvisa.ResourceManager()
                self._Instrument=self._rm.open_resource(InstVisaAddr)
                # self.IDNString=self.query('*IDN')
                return
            except:
                return None

    def InstName(self):
        instName=self.query('*IDN')
        return instName

    def binblockread(self, dtype=np.int8, debug=False):
        """Read data with IEEE 488.2 binary block format

        The waveform is formatted as:
        #<x><yyy><data><newline>, where:
        <x> is the number of y bytes. For example, if <yyy>=500, then <x>=3.
        NOTE: <x> is a hexadecimal number.
        <yyy> is the number of bytes to transfer. Care must be taken
        when selecting the data type used to interpret the data.
        The dtype argument used to read the data must match the data
        type used by the instrument that sends the data.
        <data> is the curve data in binary format.
        <newline> is a single byte new line character at the end of the data.
        """

        # Read # character, raise exception if not present.
        if self.socket.recv(1) != b'#':
            raise BinblockError('Data in buffer is not in binblock format.')

        # Extract header length and number of bytes in binblock.
        headerLength = int(self.socket.recv(1).decode('latin_1'), 16)
        numBytes = int(self.socket.recv(headerLength).decode('latin_1'))

        if debug:
            print('Header: #{}{}'.format(headerLength, numBytes))

        rawData = bytearray(numBytes)
        buf = memoryview(rawData)

        # While there is data left to read...
        while numBytes:
            # Read data from instrument into buffer.
            bytesRecv = self.socket.recv_into(buf, numBytes)
            # Slice buffer to preserve data already written to it.
            buf = buf[bytesRecv:]
            # Subtract bytes received from total bytes.
            numBytes -= bytesRecv
            if debug:
                print('numBytes: {}, bytesRecv: {}'.format(
                    numBytes, bytesRecv))

        # Receive termination character.
        term = self.socket.recv(1)
        if debug:
            print('Term char: ', term)
        # If term char is incorrect or not present, raise exception.
        if term != b'\n':
            print('Term char: {}, rawData Length: {}'.format(
                term, len(rawData)))
            raise BinblockError('Data not terminated correctly.')

        # Convert binary data to NumPy array of specified data type and return.
        return np.frombuffer(rawData, dtype=dtype)

    def PNA_setup(self,start=10e6,stop=20e9,numPoints=20001,ifBw=1e3,dwell=1e-3,measName=['meas1'],measParam=['S11'],avgpoions=0):
        """Sets up basic S parameter measurement(s).

        Configures measurements and traces in a single window, sets start/stop
        frequency, number of points, IF bandwidth, and dwell time from preset state.
        vna=self.parent.PNAHandle
        """

        if not isinstance(measName, list) and not isinstance(measParam, list):
            raise TypeError('measName and measParam must be lists of strings, even when defining only one measurement.')

        # vna.write('system:fpreset')
        # vna.query('*opc?')
        # vna.write('display:window1:state on')

        # Order of operations: 1-Define a measurement. 2-Feed measurement to a trace on a window.
        # t = 1
        # for m, p in zip(measName, measParam):
        #     vna.write(f'calculate1:parameter:define "{m}","{p}"')
        #     vna.write(f'display:window1:trace{t}:feed "{m}"')
        #     t += 1

        self.write('SYST:PRES')
        self.write('DISPLAY:WINDOW1:STATE ON')
        # 设置traceS21
        self.write(f'calculate:parameter:define:ext "{measName}","{measParam}"')
        self.write(f'display:window1:trace1:FEED "{measName}"')

        self.write(f'sense1:frequency:start {start}')
        self.write(f'sense1:frequency:stop {stop}')
        self.write(f'sense1:sweep:points {numPoints}')
        self.write(f'sense1:sweep:dwell {dwell}')
        self.write(f'sense1:bandwidth {ifBw}')
        self.write(f'SENSe1:AVERage:Count{avgpoions}')
        self.write('SENS:AVER ON')
        self.query('*opc?')

    def pna_acquire(self,measName='meas1'):
        """Acquires frequency and measurement data from selected measurement on VNA for plotting."""
        if not isinstance(measName, str):
            raise TypeError('measName must be a string.')
        # Select measurement to be transferred.
        self.write(f'calculate1:parameter:select "{measName}"')

        # Format data for transfer.
        self.write('format:border swap')
        self.write('format real,64')  # Data type is double/float64, not int64.

        # Acquire measurement data.
        self.write('calculate1:data? fdata')
        meas = self.binblockread(dtype=np.float64)
        self.query('*opc?')

        # Acquire frequency data.
        self.write('calculate1:x?')
        freq = self.binblockread(dtype=np.float64)
        self.query('*opc?')

        return freq, meas

    def CloseConnection(self):
        """ Close the connection to the VNA and release all resources """
        self._Instrument.close()
        self._rm.close()
        return

