import scipy
import numpy as np

from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt

if __name__=='__main__':
    AWG_framerate = 64 * 10 ** 9  # AWG采样率
    FM_AWG = AWG_framerate / 2.56  # AWG最高分析频率
    Df = 1 * 10 ** 6
    N_AWG = int(AWG_framerate / Df)
    ys = np.loadtxt('AWG_cos_triangle150M17G.txt')
    fft_ys = np.abs(np.abs(fft(ys)) / N_AWG)
    fft_ys = scipy.fft.fft(ys)
    fft_ys1 = abs(fft_ys)
    fft_ys2 = abs(fft_ys1 / N_AWG)
    fft_ys3 = fft_ys2[range(int(N_AWG / 2))]
    Fs = np.arange(len(ys))

    plt.figure()
    plt.plot(Fs,fft_ys2)
    plt.show()