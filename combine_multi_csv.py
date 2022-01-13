# 读取与指定文件开头相同的csv文件，并水平合并

import glob
import os
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks, peak_widths, peak_prominences
from PyQt5 import QtWidgets,QtGui

class MainForm(QtWidgets.QWidget):
    def __init__(self, name='MainForm'):
        super(MainForm, self).__init__()
        self.setWindowTitle(name)
        # self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.resize(600, 400)  # 设置窗体大小
        # btn 1
        self.btn_chooseDir = QtWidgets.QPushButton(self)
        self.btn_chooseDir.setObjectName("btn_chooseDir")
        self.btn_chooseDir.setText("选择文件")

        # 设置布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.btn_chooseDir)
        self.setLayout(layout)

        # 设置信号
        self.btn_chooseDir.clicked.connect(self.slot_btn_chooseDir)

    def slot_btn_chooseDir(self):
        plt.style.use('seaborn-whitegrid')

        # input_path = os.getcwd()  # 获取当前文件夹地址
        # input_path = r'D:\Documents\5G项目\2021-12-30\chip3-2-1226'  # 手动输入目标文件夹地址
        default_path = r'D:\Documents\5G项目'  # 默认目标文件夹地址
        input_path, datatype = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', default_path, 'csv(*.csv)')
        # print(input_path)
        filedir, filename = os.path.split(input_path)
        print(filedir, filename)
        feature_name = filename.split('_')[0]
        print(feature_name)
        file_counter = 0

        all_files = glob.glob(os.path.join(filedir, f'{feature_name}*.csv'))
        all_data_frames = []
        for file in all_files:
            data_frame = pd.read_csv(file, index_col=False, header=0, sep=',')
            filename_str = os.path.basename(file)[:-4]
            if 'BW' not in filename_str:
                data_frame['freq_list'] = data_frame['freq_list'] / 1E9  # 横坐标 Hz -> GHz
                xlabel_str = 'Frequency(GHz)'
            else:
                filename_str_split = filename_str.split('_')
                CF_str = filename_str_split[1]
                CF = float(CF_str[2:-1])
                print('CF', CF)
                data_frame['freq_list'] = CF - data_frame['freq_list'] / 1E9  # 横坐标转换为BFS(GHz)
                xlabel_str = 'BFS(GHz)'
            data_frame.columns = [xlabel_str] + list(data_frame.columns)[1:-1]+[filename_str]  # 最后一列以文件名命名
            plt.plot(data_frame[xlabel_str], data_frame[filename_str])
            all_data_frames.append(data_frame)
            file_counter += 1
        data_frame_concat = pd.concat(all_data_frames, axis=1)  # axis=1-平行拼接
        output_path = os.path.join(filedir, f'combine_{feature_name}_{str(file_counter)}_files.csv')
        data_frame_concat.to_csv(output_path, index=False)

        plt.xlabel(xlabel_str)
        plt.ylabel('PNA(dB)')
        plt.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainForm()
    window.show()

    sys.exit(app.exec_())