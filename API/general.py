#! encoding = utf-8
import visa
import pyvisa
import os.path
from pyvisa.resources.usb import USBInstrument
from pyvisa.resources.tcpip import TCPIPInstrument


def list_inst():
    '''
    查询可用仪器列表
    :return:
    '''
    try:
        rm = visa.ResourceManager()
    except OSError:
        return [], 'Cannot open VISA Library!'

    # 获取可用设备地址
    inst_list = list(rm.list_resources())
    inst_list.sort()
    inst_dict = {}
    for inst in inst_list:
        try:
            # 打开每台仪器获取信息
            temp = rm.open_resource(inst, read_termination='\r\n')
            text=temp.query('IDN?')
            inst_dict[inst]=text.strip()
            # 如果是GPIB，查询名称
            if int(temp.interface_type) == 1:
                text = temp.query('IDN?')
                inst_dict[inst] = text.strip()
            else:
                inst_dict[inst] = inst
            # 关闭设备
            temp.close()
        except:
            inst_dict[inst] = 'Visa IO Error'

    inst_str = 'Detected Instrument:\n'
    if inst_dict:
        for inst in inst_list:
            inst_str = inst_str + '{:s}\t{:s}\n'.format(inst, inst_dict[inst])
    else:
        inst_str = 'No instrument available. Check your connection/driver.'

    return inst_list, inst_str


def open_inst(inst_address):
    '''
    通过地址打开对应设备
    :param inst_address:
    :return:
    '''

    if inst_address == 'N.A.':
        return None
    else:
        try:
            rm = visa.highlevel.ResourceManager()
            inst_handle = rm.open_resource(inst_address)
            return inst_handle
        except:
            return None


def close_inst(*inst_handle):
    '''
    关闭所有连接设备
    :param inst_handle:
    :return:
    '''
    status = False

    for inst in inst_handle:
        if inst:
            try:
                inst.close()
            except:
                status = True
        else:
            pass
    return status