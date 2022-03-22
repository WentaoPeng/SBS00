import pyvisa
import visa
import math
import serial.tools.list_ports
import socketscpi
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import  QApplication, QWidget

from PyQt5.QtCore import   QTime, QTimer

# model_number = 'AEDFA-37-R-NC'
# serial_number = '15060901'
# Baud Rate = 19200
# COM5(series 2)


class EDFASCPI():
    def __init__(self, com_serial):
        """Initialization aims to get back the configurations"""
        # 1) initialization
        self.COM_serial = com_serial
        self.num_output = self.query(self.COM_serial, ':READ:CH:POW:OUT?', 'int')  # the total number of Output Power.
        print('the total number of Output Power:', self.num_output)

        self.num_cur = self.query(self.COM_serial, ':READ:CH:CUR?', 'int')  # the total number of Current.
        print('the total number of Current:', self.num_cur)

        self.ctrl_mode = self.query(self.COM_serial, ':READ:MODE:NAMES?', 'str')  # returns “ACC” as the available mode.
        print('the available mode:', self.ctrl_mode)

        self.min_acc = self.query(self.COM_serial, ':READ:DRIV:MIN:ACC:CH1?', 'float')  # returns the minimum setpoint value.
        self.max_acc = self.query(self.COM_serial, ':READ:DRIV:MAX:ACC:CH1?', 'float')  # returns the maximum setpoint value.
        print('setpoint value span:', f'[{self.min_acc}-{self.max_acc}] mA')

        # 2) Get the value of threshold level and check the Alarm status.
        # As the setpoint is OFF initially, loss of SEED power occurs.
        # The device operate normally until the SEED power is higher than the threshold level.
        self.seed_threshold = self.query(self.COM_serial, ':THRES:POW:IN:LEV:SET1?',
                                 'float')  # returns the SEED power threshold level.
        print('seed_threshold:', self.seed_threshold)
        self.loss_seed_power = self.query(self.COM_serial, ':SENS:THRES:ALARM:POW:IN:LOS:CH1?',
                                  'int')  # return “1” means the loss of SEED power.
        print('loss_seed_power:', self.loss_seed_power)

        return
    def EDFA1Set(self, value):
        # 4) To set the setpoint from initial value to 750mA.
        self.loss_seed_power = self.query(self.COM_serial, ':SENS:THRES:ALARM:POW:IN:LOS:CH1?',
                                  'int')  # return “1” means the loss of SEED power.
        self.output_state = self.query(self.COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
        if (not self.loss_seed_power) and self.output_state:
            self.set_point(self.COM_serial, ':DRIV:ACC:CUR:CH1 ', value)
        return

    def query_EDFA1_Power(self, unit):
        output_power = self.query(self.COM_serial, ':SENS:POW:OUT:CH1?', 'float')  # 读取当前输出功率
        if unit == 'mW':
            return output_power
        elif unit == 'dBm':
            if not output_power:
                return -50
            return 10 * math.log10(output_power)
        else:
            print('单位错误！')
            return None

    def Active1(self, state):
        # 3) Turn on the SEED and Laser.
        self.output_state = self.query(self.COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
        print('output_state:', self.output_state)
        while self.output_state != 1:
            self.set_point(self.COM_serial, ':DRIV:ACC:STAT:CH1 ', 1)  # 输出端口使能
            self.output_state = self.query(self.COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
            print('output_state:', self.output_state)

        value = 0+state*1
        if self.output_state == 1:  # 确认输出使能
            self.set_point(self.COM_serial, ':DRIV:MCTRL ', value)  # 1-输出打开, 0-输出关闭
        return

    def EDFA2Set(EDFA2Handle,power):
        return

    def Active2(EDFA2Handle):
        return

    def answer_by(self, datatype='str'):
        answer = self.COM_serial.readline()
        trans_answer = answer.decode()
        if datatype == 'str':
            pass
        else:
            if datatype == 'float':
                trans_answer = float(trans_answer)
            elif datatype == 'int':
                trans_answer = int(trans_answer)
            else:
                print('No such type！Default string')
        return trans_answer

    def query(self, opt_serial, instruction, answer_type='str'):
        # 询问状态并返回指定格式的响应
        # 视情况可增设最小时延
        opt_serial.write(instruction.encode() + b'\n')
        return self.answer_by(answer_type)

    def set_point(self, opt_serial, instruction, value):
        opt_serial.write(instruction.encode() + str(value).encode() + b'\n')


if __name__ == '__main__':
    def answer_by(datatype='str'):
        answer = COM_serial.readline()
        # 此处可加入超时警告
        trans_answer = answer.decode()
        if datatype == 'str':
            pass
        else:
            if datatype == 'float':
                trans_answer = float(trans_answer)
            elif datatype == 'int':
                trans_answer = int(trans_answer)
            else:
                print('No such type！Default string')
        return trans_answer


    def inquiry(opt_serial, instruction, answer_type='str'):
        # 询问状态并返回指定格式的响应
        # 视情况可增设最小时延
        opt_serial.write(instruction.encode()+b'\n')
        return answer_by(answer_type)


    def set_point(opt_serial, instruction, value):
        opt_serial.write(instruction.encode()+str(value).encode()+b'\n')

    # 检查端口并确保其打开
    plist = list(serial.tools.list_ports.comports())
    if len(plist) <= 0:
        print("没有发现端口!")
    else:
        plist_1 = list(plist[1])
        serialName = plist_1[0]
        COM_serial = serial.Serial(serialName, 19200, timeout=60)
        print("可用端口名>>>", COM_serial.name)
        print('端口打开:', COM_serial.isOpen())

        # 1) initialization
        num_output = inquiry(COM_serial, ':READ:CH:POW:OUT?', 'int')  # the total number of Output Power.
        print('the total number of Output Power:', num_output)

        num_cur = inquiry(COM_serial, ':READ:CH:CUR?', 'int')  # the total number of Current.
        print('the total number of Current:', num_cur)

        ctrl_mode = inquiry(COM_serial, ':READ:MODE:NAMES?', 'str')  # returns “ACC” as the available mode.
        print('the available mode:', ctrl_mode)

        min_acc = inquiry(COM_serial, ':READ:DRIV:MIN:ACC:CH1?', 'float')  # returns the minimum setpoint value.
        max_acc = inquiry(COM_serial, ':READ:DRIV:MAX:ACC:CH1?', 'float')  # returns the maximum setpoint value.
        print('setpoint value span:', f'[{min_acc}-{max_acc}] mA')

        # 2) Get the value of threshold level and check the Alarm status.
        # As the setpoint is OFF initially, loss of SEED power occurs.
        # The device operate normally until the SEED power is higher than the threshold level.
        seed_threshold = inquiry(COM_serial, ':THRES:POW:IN:LEV:SET1?', 'float')  # returns the SEED power threshold level.
        print('seed_threshold:', seed_threshold)
        loss_seed_power = inquiry(COM_serial, ':SENS:THRES:ALARM:POW:IN:LOS:CH1?', 'int')  # return “1” means the loss of SEED power.
        print('loss_seed_power:', loss_seed_power)

        # 3) Turn on the SEED and Laser.
        output_state = inquiry(COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
        print('output_state:', output_state)
        while output_state != 1:
            set_point(COM_serial, ':DRIV:ACC:STAT:CH1 ', 1)  # 输出端口使能
            output_state = inquiry(COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
            print('output_state:', output_state)

        if output_state == 1:
            set_point(COM_serial, ':DRIV:MCTRL ', 0)  # 输出打开

        # 4) To set the setpoint from initial value to 750mA.
        loss_seed_power = inquiry(COM_serial, ':SENS:THRES:ALARM:POW:IN:LOS:CH1?', 'int')  # return “1” means the loss of SEED power.
        output_state = inquiry(COM_serial, ':DRIV:ACC:STAT:CH1?', 'int')  # 检查准备状态指令  1-ENABLED,2-BUSY
        if (not loss_seed_power) and output_state:
            set_point(COM_serial, ':DRIV:ACC:CUR:CH1 ', 750)

        # 5) Monitor the value of Output Power.
        current = inquiry(COM_serial, ':DRIV:ACC:CUR:CH1?', 'float')  # 读取当前设置电流
        print('current:', current)

        output_power = inquiry(COM_serial, ':SENS:POW:OUT:CH1?', 'float')  # 读取当前输出功率
        print('output_power:', output_power, 'mW')
        print('output_power:', 10*math.log10(output_power), 'dbm')

