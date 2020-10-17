#! encoding = utf-8
import pyvisa
import os.path


def list_AWGinst():
    '''
    AWG通过USB通信
    :return:
    '''
    try:
        rm = pyvisa.highlevel.ResourceManager()
    except OSError:
        return [], 'Cannot open VISA Library!'

    # 获取可用设备地址
    inst_list = list(rm.list_resources())
    inst_list.sort()
    inst_dict = {}
    for inst in inst_list:
        try:
            temp = rm.open_resource(inst, read_termination='\r\n')
            if int(temp.interface_type) == 1:
                text = temp.query('IDN?')
                inst_dict[inst] = text.strip()
            else:
                inst_dict[inst] = inst
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
