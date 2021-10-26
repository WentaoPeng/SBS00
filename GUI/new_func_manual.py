'''新增模块函数，待加入Panels.py
todo:模块功能*3
1.能够手动调节幅值比例(输入输出框1，set按钮1)
2.能够手动调节梳齿间隔(输入输出框2，set按钮2)
3.能够通过反馈，用增益/梳齿频移补偿器件不理想带来的波动(输入输出框1、2，反馈按钮1、2)
'''
import json
import multi_Lorenz_2_triangle as mlt
import numpy as np

def manual_lists():
    # 功能：手动调节复制比例或梳齿间隔
    if unset:  # todo: 如果用户未设置序列参数
        freq_seq = None
        amp_seq = self.pre_amp_seq(BW, DF)  # todo:改成预反馈的输出
        amp_seq_list = amp_seq.tolist()  # numpy转list
        str_amp_seq = str(amp_seq_list)  # list转string  todo:str_amp_seq显示在界面输入输出框中
        freq_seq_list = amp_seq.tolist()  # numpy转list
        str_freq_seq = str(freq_seq_list)  # list转string  todo:str_freq_seq显示在界面输入输出框中
    #     todo：为防止输出过长无法显示，增加复制文本功能，以便在界面外修改
    else:  # 如果用户手动更新了参数
        amp_seq = json.loads(str_amp_seq)  # string转list todo:str_amp_seq在界面输入输出框中读取
        freq_seq = json.loads(str_freq_seq)  # string转list todo:str_freq_seq在界面输入输出框中读取
    return



def df_feedback(freq_design_seq, freq, gain_offset, BFS, FWHM):
    # 功能：通过左右区间积分，在自然线宽范围内微调梳齿频率间隔（待验证）
    # 输入：梳齿频率freq_design_seq(Hz), 开关增益的频率freq(Hz)和校准基线后的开关响应gain_offset(dB)
    # BFS  # 读取单频测量所得BFS，单位GHz
    # FWHM  # 读取单频测量所得FWHM，单位MHz

    # 边缘梳齿频率不变，只改中间
    freq_design_seq_sam = freq_design_seq[1:-1]
    new_freq_design = freq_design_seq

    # print('freq_design_seq_sam =', freq_design_seq_sam + BFS*1e9)
    f_index = mlt.search_index(freq_design_seq_sam + BFS*1e9, freq)  # 搜索时减去BFS,freq_design_seq和freq单位相同(Hz)
    # print('find freq =', freq[f_index])

    ratio = 0.4  # 加窗点数/FWHM对应点数
    n_dots = int(ratio * (f_index[1] - f_index[0]))  # 半区间取点个数
    sample_array = np.array([gain_offset[i - n_dots:i + n_dots+1] for i in f_index])
    left_list = np.hstack((np.ones(n_dots) / n_dots, np.zeros(n_dots+1)))
    left_measure_sam = np.dot(sample_array, left_list)
    right_list = np.hstack((np.zeros(n_dots + 1), np.ones(n_dots) / n_dots))
    right_measure_sam = np.dot(sample_array, right_list)
    temp = (0.5-left_measure_sam/(left_measure_sam+right_measure_sam))
    offset_f = temp*FWHM
    new_freq_design[1:-1] = freq_design_seq_sam - offset_f*1e3
    return new_freq_design

