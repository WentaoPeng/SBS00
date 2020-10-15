# encoding=utf-8

def query_inst_name(motorHandle):
    '''
    查询设备名称
    :param motorHandle:
    :return:
    '''

    try:
        text = motorHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def move(motorHandle, step):
    '''
    步进
    :param motorHandle:
    :param step:
    :return:
    '''
    motorHandle.write('1PA+{:d}\n'.format(step))
