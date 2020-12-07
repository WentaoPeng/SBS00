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
class PNAN5225A(socketscpi.SocketInstrument):
    '''
    PNAN5225A
    重置指令
    访问设备并返回指定参数，并保存为类属性
    '''
    def __init__(self,host,port,timeout,reset=False):
        super().__init__(host,port,timeout)
        if reset:
            self.write('*rst')
            self.query('*opc?')
        # 访问设备并返回指定参数，并保存为类属性
        self.AVERageNUM=self.query('').strip()