import SBS_DSP
import math
import numpy as np
import random
import scipy
from scipy.fftpack import fft, ifft

import matplotlib.pyplot as plt

PI2 = math.pi * 2


def FBFunction(amp_list):
    N = len(amp_list)
    # amp_list[N-1]=3
    amp_list[0] = 0.21549
    amp_list[1] = 0.14002
    amp_list[2] = 0.08018
    amp_list[3] = 0.14040
    amp_list[4] = 0.21536
    # amp_list[5]=0.8
    # amp_list[5:8]=0
    # amp_list[2]=2.3
    return amp_list


def FList(f_list, bandwith):
    # N=len(f_list)
    # for i in range(4,8):
    #     f_list[i]=
    # f_list[11]=14070*10**6
    # f_list[12]=14090*10**6
    f_list[-1] = f_list[-2] + bandwidth / 2
    f_list[0] = f_list[1] - bandwidth / 2

    return f_list - 0.2e9


if __name__ == '__main__':
    AWG_framerate = 64 * 10 ** 9  # AWG采样率
    Df = 1 * 10 ** 6
    FM_AWG = AWG_framerate / 2.56  # AWG最高分析频率
    # FM_FPGA = FPGA_framerate / 2.56  # FPGA最高分析频率
    N_AWG = int(AWG_framerate / Df)
    # N_FPGA = int(FPGA_framerate / Df)
    # N_FPGA=2**14
    t_AWG = N_AWG * (1 / AWG_framerate)
    # t_FPGA = N_FPGA * (1 / FPGA_framerate)
    center_F = 15 * 10 ** 9
    bandwidth = 30 * 10 ** 6
    df = 6 * 10 ** 6
    # f_list, amp_list, phase_list = SBS_DSP.square_filter(center_F, bandwidth, df)
    f_list, amp_list, phase_list = SBS_DSP.triangle_filter(center_F, bandwidth, df)
    f_list = FList(f_list, bandwidth)
    amp_list = FBFunction(amp_list)
    # f_list=FList(f_list)

    ts = np.linspace(0, t_AWG, N_AWG, endpoint=False)

    ys = SBS_DSP.synthesize1(amp_list, f_list, ts, phase_list)
    print(f_list)
    txt = SBS_DSP.get_awgfile(ys, center_F, bandwidth, df, shape=0)
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示符号

    plt.figure()
    plt.subplot(211)
    plt.plot(ts, ys, 'b')
    plt.xlabel("t（毫秒）")
    plt.ylabel("S(t)幅值")
    plt.title("叠加信号图")
    fs, hz = SBS_DSP.get_fft(ys, N_AWG)
    plt.subplot(212)
    plt.plot(hz, fs, 'g')
    plt.xlabel("F（MHz）")
    plt.ylabel("A归一化")
    plt.title("PUMP频梳")
    plt.savefig('triangle.png')
    plt.show()
