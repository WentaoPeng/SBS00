#! encoding = utf-8
import pyvisa
import os.path

def list_inst():
    '''
    查询可用仪器列表
    :return:
    '''
    try:
        rm=pyvisa.highlevel.ResourceManager()
    except OSError:
        return [],'Cannot open VISA Library!'

    #获取可用设备地址
