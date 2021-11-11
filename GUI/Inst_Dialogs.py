#! encoding = utf-8
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui
from GUI import SharedWidgets as Shared
from API import general as api_gen
from API import AWGapi as api_awg
from API import PNAapi as api_pna
from API import LightAPI as api_light
import re
from GUI import Panels as panels_fun
from scipy.signal import savgol_filter, find_peaks, peak_widths, peak_prominences
import SBS_DSP
from pyqtgraph import siFormat
import pyqtgraph as pg


class selectInstDialog(QtWidgets.QDialog):
    '''
    设备通信方式选择，利用VISA结合NI MAX自动搜索设备ip及COM地址
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(400, 400)
        self.setWindowTitle('Select Inst_Port')

        refreshButton = QtGui.QPushButton('Refresh Available Instrument List')
        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))

        self.availableInst = QtWidgets.QLabel()
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtWidgets.QWidget()
        selInstLayout = QtWidgets.QFormLayout()
        self.selAWG = QtWidgets.QComboBox()
        self.selAWG.addItems(['N.A.'])
        self.selAWG.addItems(instList)
        self.selPNA = QtWidgets.QComboBox()
        self.selPNA.addItems(['N.A.'])
        self.selPNA.addItems(instList)
        self.selEDFA1 = QtWidgets.QComboBox()
        self.selEDFA1.addItems(['N.A.'])
        self.selEDFA1.addItems(instList)
        self.selEDFA2 = QtWidgets.QComboBox()
        self.selEDFA2.addItems(['N.A.'])
        self.selEDFA2.addItems(instList)
        self.selLight = QtWidgets.QComboBox()
        self.selLight.addItems(['N.A.'])
        self.selLight.addItems(instList)

        selInstLayout.addRow(QtWidgets.QLabel('AWG'), self.selAWG)
        selInstLayout.addRow(QtWidgets.QLabel('PNA'), self.selPNA)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA1'), self.selEDFA1)
        selInstLayout.addRow(QtWidgets.QLabel('EDFA2'), self.selEDFA2)
        selInstLayout.addRow(QtWidgets.QLabel('LightWave'), self.selLight)

        selInst.setLayout(selInstLayout)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.availableInst, 0, 0, 1, 2)
        mainLayout.addWidget(refreshButton, 1, 0, 1, 2)
        mainLayout.addWidget(selInst, 2, 0, 1, 2)
        mainLayout.addWidget(cancelButton, 3, 0)
        mainLayout.addWidget(acceptButton, 3, 1)

        self.setLayout(mainLayout)

        refreshButton.clicked.connect(self.refresh)
        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

    def refresh(self):
        '''
        刷新设备列表
        :return:
        '''
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        item_count = self.selAWG.count()

        for i in range(item_count - 1):
            self.selAWG.removeItem(1)
            self.selPNA.removeItem(1)
            self.selEDFA1.removeItem(1)
            self.selEDFA2.removeItem(1)
            self.selLight.removeItem(1)
        self.selAWG.addItems(instList)
        self.selPNA.addItems(instList)
        self.selEDFA1.addItems(instList)
        self.selEDFA2.addItems(instList)
        self.selLight.addItems(instList)


    def accept(self):
        # 关闭旧的设备连接
        api_gen.close_inst(self.parent.AWGHandle,
                           self.parent.PNAHandle,
                           self.parent.LightHandle,
                           self.parent.EDFA1Handle,
                           self.parent.EDFA2Handle,)
        # 开启新的设备连接
        AWGIP=re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',str(self.selAWG.currentText()),re.S)
        PNAIP=re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])',str(self.selPNA.currentText()),re.S)
        LightIP = re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', str(self.selLight.currentText()), re.S)

        self.parent.AWGHandle = api_awg.M9502A(AWGIP)
        self.parent.PNAHandle = api_pna.PNASCPI(PNAIP)
        self.parent.LightHandle = api_light.LightSCPI(LightIP)
        self.parent.EDFA1Handle = api_gen.open_inst(self.selEDFA1.currentText())
        self.parent.EDFA2Handle = api_gen.open_inst(self.selEDFA2.currentText())

        self.done(True)

class manualInstDialog(QtWidgets.QDialog):
    '''
    手动输入设备IP
    '''
    def __init__(self,parent):
        QtWidgets.QDialog.__init__(self,parent)
        self.parent=parent
        self.setMinimumSize(200,200)
        self.setWindowTitle('Manual Input Inst_IP')
        self.awgip='192.168.1.102'
        self.pnaip='192.168.1.100'
        self.lightip='192.168.1.101'

        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))

        ManualInst=QtWidgets.QWidget()
        ManualInstLayout=QtWidgets.QFormLayout()
        self.AWGIP=QtWidgets.QWidget()
        self.AWGIPFill=QtWidgets.QLineEdit()
        self.AWGIPFill.setInputMask("000.000.000.000")
        self.AWGIPFill.setText("192.168.1.102")

        self.PNAIP=QtWidgets.QWidget()
        self.PNAIPFill=QtWidgets.QLineEdit()
        self.PNAIPFill.setInputMask("000.000.000.000")
        self.PNAIPFill.setText("192.168.1.100")

        self.LightIP=QtWidgets.QWidget()
        self.LightIPFill=QtWidgets.QLineEdit()
        self.LightIPFill.setInputMask("000.000.000.000")
        self.LightIPFill.setText("192.168.1.101")

        ManualInstLayout.addRow("AWG_IP",self.AWGIPFill)
        ManualInstLayout.addRow("PNA_IP",self.PNAIPFill)
        ManualInstLayout.addRow("LightIP",self.LightIPFill)

        ManualInst.setLayout(ManualInstLayout)

        mainLayout=QtWidgets.QGridLayout()
        mainLayout.addWidget(ManualInst,0,0,2,1)
        mainLayout.addWidget(acceptButton,3,1)
        mainLayout.addWidget(cancelButton,3,0)
        self.setLayout(mainLayout)

        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

        # 更新后台ip
        self.AWGIPFill.textChanged.connect(self.updateIP)
        self.PNAIPFill.textChanged.connect(self.updateIP)
        self.LightIPFill.textChanged.connect(self.updateIP)

    def updateIP(self):
        self.awgip=self.AWGIPFill.text()
        self.pnaip=self.PNAIPFill.text()
        self.lightip=self.LightIPFill.text()

    def accept(self):
        if self.awgip=='N.A.':
            self.done(True)
            return None
        else:
            try:
                self.parent.AWGHandle=api_awg.M9502A(self.awgip,reset=True)
                print(self.parent.AWGHandle)
                self.done(True)
            except:
                return None

        if self.pnaip=='N.A.':
            self.done(True)
            return None

        else:
            try:
                self.parent.PNAHandle=api_pna.PNASCPI(self.pnaip,reset=True)
                print(self.parent.PNAHandle)
                self.done(True)
            except:
                return None

        if self.lightip=='N.A.':
            self.done(True)
            return None
        else:
            try:
                self.parent.LightHandle=api_light.LightSCPI(self.lightip,reset=True)
                print(self.parent.LightHandle)
                self.done(True)
            except:
                return None

        self.done(True)

class manualFB_list(QtWidgets.QDialog):
        '''
        显示反馈后的amp-list以及freq-list
        并且可以修改
        '''
        def __init__(self,parent):
            QtWidgets.QDialog.__init__(self,parent)
            self.parent=parent

            self.setupUI()

            self.freq_data=[]
            self.gain_on_off_offset=[]
            self.btu_display.clicked.connect(self.data_setup)
            self.btu_save.clicked.connect(self.data_save)
            self.btu_accept.clicked.connect(self.manual_Fun)
            self.btu_map.clicked.connect(self.mapping_Fun)
            self.btu_cancel.clicked.connect(self.reject)
            self.btu_save_data.clicked.connect(self.save_data)

        def save_data(self):
            pass

        def mapping_Fun(self):
            if self.btu_map.isChecked():
                if self.parent.PNAHandle:
                    self.parent.AWGInfo.map=1
                else:
                    msg = Shared.MsgError(self, 'No Instrument!', 'No PNAN5225A is connected!')
                    msg.exec_()
                    self.btu_map.setCheckable(True)
            else:
                self.parent.AWGInfo.map=0
            # # 功能：减去底噪，得到校准基线后的开关增益
            # if self.parent.PNAHandle:
            #     BJ=self.parent.AWGInfo.BJ_amp
            #
            #     self.freq_data,gain_data=self.parent.PNAHandle.pna_acquire(
            #             measName=self.parent.PNAInfo.Scale)
            #     # freq为PNA测量频率，单位Hz
            #     freq = self.freq_data / 1e9  # 转单位为GHz
            #
            #     gain_on_off = gain_data - BJ  # 减底噪
            #
            #     gain_on_off = savgol_filter(gain_on_off, 301, 3)  # 3阶SG平滑
            #     BFS, main_peak_gain, FWHM_main_peak, baseline = self.peak_analysis(freq, gain_on_off)
            #     self.gain_on_off_offset = gain_on_off - baseline
            #     #显示
            #     panels_fun.FcombDisplay.plot3(self.gain_on_off_offset,self.freq_data)
            #
            # else:
            #     msg = Shared.MsgError(self, 'No Instrument!', 'No PNAN5225A is connected!')
            #     msg.exec_()

        def manual_Fun(self):
            if self.parent.AWGHandle:
                ys = SBS_DSP.synthesize1(self.parent.AWGInfo.amp_list, self.parent.AWGInfo.f_list
                                         , self.parent.AWGInfo.ts, self.parent.AWGInfo.phase_list)
                wavefile = (ys - min(ys)) / (max(ys) - min(ys)) - 0.5
                self.parent.AWGInfo.AWGwave = np.ones(len(wavefile)) * wavefile
                self.parent.AWGHandle.download_wfm(wfmData=self.parent.AWGInfo.AWGwave,
                                                   ch=self.parent.AWGInfo.ChannelNum)
                if self.parent.AWGInfo.AWG_Status:
                    # self.parent.AWGHandle.set_amplitude(amplitude=self.parent.AWGInfo.AWGPower,
                    #                                     channel=self.parent.AWGInfo.ChannelNum)
                    self.parent.AWGHandle.play()
            else:
                msg = Shared.MsgError(self, 'No Instrument!', 'No AWG is connected!')
                msg.exec_()

        def data_save(self):
            col_num=self.list_table.columnCount()
            row_num=self.list_table.rowCount()
            new_arry=np.empty(shape=(col_num,row_num))
            for col in range(col_num):
                for row in range(row_num):
                        new_arry[col][row]=float(self.list_table.item(row,col).text())

            self.parent.AWGInfo.amp_list=new_arry[0]
            self.parent.AWGInfo.f_list=new_arry[1]*1e9
            self.parent.AWGInfo.phase_list=new_arry[2]
            # print(self.parent.AWGInfo.f_list)

        def data_setup(self):
            '''
            更新页面数据
            :return:
            '''
            self.list_table.blockSignals(True)
            amp_list= self.parent.AWGInfo.amp_list
            f_list=self.parent.AWGInfo.f_list/1e9    #GHz显示
            phase_list=self.parent.AWGInfo.phase_list
            arry=np.array([amp_list,f_list,phase_list])
            # print(arry,arry[1],arry[2],arry[1][2])
            self.list_table.setRowCount(len(amp_list))
            for column in range(3):
                for row in range(len(amp_list)):
                    self.list_table.setItem(row,column,QtWidgets.QTableWidgetItem(format(arry[column][row],'.6f')))
                    # self.list_table.item(row, column).setTextAlignment(QtCore.AlignHCenter | QtCore.AlignVCenter)
            self.list_table.update()
            self.list_table.blockSignals(False)


        def setupUI(self):
            self.setMinimumSize(1200,1200)
            self.setWindowTitle('MaunalFB Amp/Freq List')
#             显示，BFS，FWHM，amp_list,freq_list,phase_list
            self.list_table=QtWidgets.QTableWidget(self)
            self.btu_display=QtWidgets.QPushButton('Display')
            self.btu_save=QtWidgets.QPushButton('Save')
            self.btu_accept=QtWidgets.QPushButton('Accept')
            self.btu_cancel=QtWidgets.QPushButton('Cancel')
            self.btu_map=QtWidgets.QPushButton('Mapping')
            self.btu_map.setCheckable(True)
            self.btu_map.setStyleSheet('''QPushButton:hover{background:yellow;}''')
            self.btu_save_data=QtWidgets.QPushButton('Save_MD')
            self.spaceItem=QtWidgets.QSpacerItem(20,20,QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
            self.vbox=QtWidgets.QVBoxLayout()
            self.vbox.addWidget(self.btu_display)
            self.vbox.addWidget(self.btu_save)
            self.vbox.addWidget(self.btu_accept)
            self.vbox.addWidget(self.btu_map)
            self.vbox.addWidget(self.btu_save_data)
            self.vbox.addWidget(self.btu_cancel)
            self.vbox.addSpacerItem(self.spaceItem)
            self.txt=QtWidgets.QLabel()
            self.txt.setMinimumHeight(50)
            self.vbox2=QtWidgets.QVBoxLayout()
            self.vbox2.addWidget(self.list_table)
            self.vbox2.addWidget(self.txt)
            self.hbox=QtWidgets.QHBoxLayout()
            self.hbox.addLayout(self.vbox2)
            self.hbox.addLayout(self.vbox)
            self.setLayout(self.hbox)
            # self.list_table.horizontalHeader().setFixedHeight(50)
            # self.list_table.setVerticalScrollBar(QtCore.Qt.ScrollBarAlwaysOn)
            self.list_table.setColumnCount(3)
            # self.list_table.setShowGrid(False)
            self.list_table.setHorizontalHeaderLabels(['Amp_list','Freq_list(GHz)','Phase_list'])
            self.list_table.horizontalHeader().setSectionsClickable(False)
            # self.list_table.horizontalHeader().setStyleSheet('QHeaderView::section{background:}')
            # self.show()

class viewInstDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)

        self.setMinimumSize(400, 400)
        self.setWindowTitle('View Instrument Status')

class CloseSelInstDialog(QtWidgets.QDialog):
    '''
    关闭设备
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(400,400)
        self.setWindowTitle('Close Instrument')

        inst=QtWidgets.QWidget()
        self.awgToggle=QtWidgets.QCheckBox()
        self.pnaToggle=QtWidgets.QCheckBox()
        self.EDFA1Toggle=QtWidgets.QCheckBox()
        self.EDFA2Toggle=QtWidgets.QCheckBox()
        self.LightToggle=QtWidgets.QCheckBox()

        instLayout=QtWidgets.QFormLayout()
        instLayout.addRow(QtWidgets.QLabel('Instrument'),QtWidgets.QLabel('Status'))

        if self.parent.AWGHandle:
            self.awgToggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('AWG'),self.awgToggle)
        else:
            self.awgToggle.setCheckState(False)

        if self.parent.PNAHandle:
            self.pnaToggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('PNA'),self.pnaToggle)
        else:
            self.pnaToggle.setCheckState(False)

        if self.parent.EDFA1Handle:
            self.EDFA1Toggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('EDFA1'),self.EDFA1Toggle)
        else:
            self.EDFA1Toggle.setCheckState(False)

        if self.parent.EDFA2Handle:
            self.EDFA2Toggle.setCheckState(True)
            instLayout.addRow(QtWidgets.QLabel('EDFA2'),self.EDFA2Toggle)
        else:
            self.EDFA2Toggle.setCheckState(False)

        inst.setLayout(instLayout)

        okButton=QtWidgets.QPushButton(Shared.btn_label('complete'))
        mainLayout=QtWidgets.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(QtWidgets.QLabel('No command will be sent before you hit the accept button'))
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        okButton.clicked.connect(self.accept)

    def close_inst_handle(self,inst_handle,check_state):

        if check_state and inst_handle:
            api_gen.close_inst(inst_handle)
            return None
        else:
            return inst_handle

    def accept(self):
        if self.awgToggle.isChecked() and self.parent.AWGHandle:
            self.parent.AWGHandle=self.close_inst_handle(self.parent.AWGHandle,
                                                         self.awgToggle.isChecked())
        if self.pnaToggle.isChecked() and self.parent.PNAHandle:
            self.parent.PNAHandle=self.close_inst_handle(self.parent.PNAHandle,
                                                        self.pnaToggle.isChecked())

        self.parent.EDFA1Handle=self.close_inst_handle(self.parent.EDFA1Handle,
                                                       self.EDFA1Toggle.isChecked())
        self.parent.EDFA2Handle=self.close_inst_handle(self.parent.EDFA2Handle,
                                                       self.EDFA2Toggle.isChecked())
        if self.LightToggle.isChecked() and self.parent.LightHandle:
            self.parent.LightHandle=self.close_inst_handle(self.parent.LightHandle,
                                                        self.LightToggle.isChecked())

        self.parent.Display==0
        self.close()

class AWGInfoDialog(QtWidgets.QDialog):
    '''AWG设置窗口'''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
