#! encoding = utf-8
from math import pi
import operator
from pyqtgraph import siEval

AWGCHANNELSET={0:1,
               1:2,
               2:3,
               3:4}

def _compare(num1, op, num2):
    ''' An comparison operator generator '''

    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq}

    return ops[op](num1, num2)

def val_edfa1power(power_text,power_unit):
    '''
    小功率EDFA
    :param power: 输入功率文本
    :param power_unit: 单位
    :return: 实际功率
    '''
    if power_text:
        power_num=siEval(power_text+power_unit)
    else:
        return 0,0
    # 需要判断单位是什么
    if power_unit=='dBm':
        code,power=val_float(power_num, safe=[('>=', 0), ('<=', 10)],
                               warning=[('>', 10), ('<=', 20)])
    else:
        code, power = val_float(power_num, safe=[('>=', 0), ('<=', 0.0099)],
                                warning=[('>', 0.0099), ('<=', 0.0999)])

    return code,power


def val_edfa2power(power_text, power_unit):
    '''
    大功率EDFA
    :param power: 输入功率文本
    :param power_unit: 单位
    :return: 实际功率
    '''
    if power_text:
        power_num = siEval(power_text + power_unit)
    else:
        return 0, 0
    if power_unit=='dBm':
        code,power=val_float(power_num, safe=[('>=', 0), ('<=', 35)],
                               warning=[('>', 35), ('<=', 40)])
    else:
        code, power = val_float(power_num, safe=[('>=', 0), ('<=', 3.1623)],
                                warning=[('>', 3.1623), ('<=', 10)])
    return code, power

def val_awgCW_mod_freq(freq_text, freq_unit_text):
    ''' Validate frequency input.
        Arguments
            freq_text: str, modulation frequency user input
            freq_unit_text: str, modulation frequency unit
        Safe range: [0, 20e9] Hz
        Warning range: (20e9, 25e9] Hz
    '''

    if freq_text:   # if not empty string
        freq_num = siEval(freq_text + freq_unit_text)
    else:
        return 0, 0

    code, freq = val_float(freq_num, safe=[('>=', 0), ('<=', 20e9)],
                           warning=[('>', 20e9), ('<=', 25e9)])
    return code, freq

def val_awgBW_mod_freq(freq_text,freq_unit_text):
    '''
    Validate frequency input.
    :param freq_text: str,modulation frequency user input
    :param freq_unit_text: str,modulation frequuency unit
    :return:
    '''
    if freq_text:   # if not empty string
        freq_num = siEval(freq_text + freq_unit_text)
    else:
        return 0, 0

    code, freq = val_float(freq_num, safe=[('>=', 0), ('<=', 8e9)],
                           warning=[('>', 8e9), ('<=', 10e9)])
    return code, freq

def val_awgDF_mod_freq(freq_text,freq_unit_text):
    '''

    :param freq_text: str, modulation frequency user input
    :param freq_unit_text: str, modulation frequency unit
    :return:
    '''
    if freq_text:  # if not empty string
        freq_num = siEval(freq_text + freq_unit_text)
    else:
        return 0, 0

    code, freq = val_float(freq_num, safe=[('>=', 0), ('<=', 50e6)],
                           warning=[('>', 50e6), ('<=', 100e6)])
    return code, freq

def val_float(text, safe=[], warning=[]):
    ''' General validator for int number.
        Comparison operators can be passed through safe & warning
        Each comparison list contains tuples of (op, num)
    '''

    try:
        number = float(text)
        # 1st test if the number is in the safe range
        boolean = True
        for op, num in safe:
            boolean *= _compare(number, op, num)
        if boolean:
            code = 2
        else:
            boolean = True
            for op, num in warning:
                boolean *= _compare(number, op, num)
            if boolean:
                code = 1
            else:
                code = 0
        return code, number
    except ValueError:
        return 0, 0