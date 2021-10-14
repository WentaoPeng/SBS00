'''新增模块函数，待加入Panels.py
todo:界面显示开关增益，更新单频泵浦参数计算方法'''
from scipy.signal import savgol_filter, find_peaks, peak_widths, peak_prominences
import matplotlib.pyplot as plt

def peak_analysis(freq,gain_on_off):
    # 函数功能：峰值分析，具体包括通过开关增益计算主峰频率、增益、半高全宽FWHM,基线
    # 输入：测量频率(单位GHz)，开关增益
    # 输出：主峰BFS(默认中心频率15GHz),峰值，FWHM,基线(常数)
    f_resolution = float(freq[1] - freq[0])  # 频率分辨率(GHz)
    peaks, _ = find_peaks(gain_on_off, width=500, rel_height=0.1)  # 寻峰

    prominences = peak_prominences(gain_on_off, peaks)[0]  # 计算峰高
    idx_main_peak = prominences.argmax()  # 找主峰
    BFS = 15 - freq[peaks[idx_main_peak]]  # 求BFS(单位GHz)，默认中心频率15GHz todo:可将15GHz换为输入变量
    main_peak_gain = prominences[idx_main_peak]  # 主峰峰值
    baseline = max(gain_on_off[peaks]) - main_peak_gain  # 求基线

    results_half = peak_widths(gain_on_off, peaks, rel_height=0.5)  # tuple{0：宽度;1：高度;2:xmin;3:xmax}
    FWHM_main_peak = results_half[0][idx_main_peak]*1e3*f_resolution  # 主峰半高全宽(单位MHz)

    return BFS, main_peak_gain, FWHM_main_peak, baseline


def cal_gain_on_off(freq,gain_data, BJ):
    # 功能：减去底噪，得到校准基线后的开关增益
    # freq为PNA测量频率，单位Hz
    freq = freq / 1e9  # 转单位为GHz

    gain_on_off = gain_data - BJ  # 减底噪

    gain_on_off = savgol_filter(gain_on_off, 301, 3)  # 3阶SG平滑

    if need_new_parameter:  # 如果未进行单频参数测量
        BFS, main_peak_gain, FWHM_main_peak, baseline = peak_analysis(freq, gain_on_off)  # 获取峰值分析参数 todo:其他参数保存后显示到界面
        need_new_parameter = False  # todo:找到设置 True 的位置，以重新测量数据
    else:
        baseline = None  # todo:从内存读取参数

    gain_on_off_offset = gain_on_off - baseline
    return gain_on_off_offset



if __name__ == '__main__':
    freq, gain_data= None  # 测量频率(单位Hz)和增益(dB)，todo：读取自PNA或本地内存
    BJ = None  # 测量底噪(dB) todo：读取自PNA或本地内存
    gain_offset = cal_gain_on_off(freq, gain_data, BJ)
    plt.plot(freq, gain_offset, label='gain_offset')
    plt.xlabel("Freq(GHz)")
    plt.ylabel("Gain_offset(DB)")

    # plt.plot(freq[peaks], gain_offset[peaks], "x")  # 标记峰值  todo:可考虑画在开关增益中，验证程序是否正确寻峰

    plt.legend()
    plt.show()