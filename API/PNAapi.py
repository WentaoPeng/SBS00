#! encoding = utf-8
import pyvisa
import os.path
import socketscpi
# This program provides a socket interface to Keysight test equipment.
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
def PNA_setup(vna,start=10e6,stop=20e9,numPoints=20001,ifBw=1e3,dwell=1e-3,measName=['meas1'],measParam=['S11']):
    """Sets up basic S parameter measurement(s).

    Configures measurements and traces in a single window, sets start/stop
    frequency, number of points, IF bandwidth, and dwell time from preset state.
    vna=self.parent.PNAHandle
    """

    if not isinstance(measName, list) and not isinstance(measParam, list):
        raise TypeError('measName and measParam must be lists of strings, even when defining only one measurement.')

    vna.write('system:fpreset')
    vna.query('*opc?')
    vna.write('display:window1:state on')

    # Order of operations: 1-Define a measurement. 2-Feed measurement to a trace on a window.
    t = 1
    for m, p in zip(measName, measParam):
        vna.write(f'calculate1:parameter:define "{m}","{p}"')
        vna.write(f'display:window1:trace{t}:feed "{m}"')
        t += 1

    vna.write(f'sense1:frequency:start {start}')
    vna.write(f'sense1:frequency:stop {stop}')
    vna.write(f'sense1:sweep:points {numPoints}')
    vna.write(f'sense1:sweep:dwell {dwell}')
    vna.write(f'sense1:bandwidth {ifBw}')

def pna_acquire(vna,measName='meas1'):
    """Acquires frequency and measurement data from selected measurement on VNA for plotting."""
    if not isinstance(measName, str):
        raise TypeError('measName must be a string.')

    # Select measurement to be transferred.
    vna.write(f'calculate1:parameter:select "{measName}"')

    # Format data for transfer.
    vna.write('format:border swap')
    vna.write('format real,64')  # Data type is double/float64, not int64.

    # Acquire measurement data.
    vna.write('calculate1:data? fdata')
    meas = vna.binblockread(dtype=np.float64)
    vna.query('*opc?')

    # Acquire frequency data.
    vna.write('calculate1:x?')
    freq = vna.binblockread(dtype=np.float64)
    vna.query('*opc?')

    return freq, meas
