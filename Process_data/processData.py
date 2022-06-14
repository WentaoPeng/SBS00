import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob,os
from scipy.signal import savgol_filter

r_color = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])
def plot1(dl,dlB,name):
    """
    幅频响应计算
    """
    N=len(dl)
    i=0
    Freq=[]
    pumpF=np.linspace(10,20,11,endpoint=True)
    for _ in range(N):
        plt.figure(1)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)  # 去掉上边框
        ax.spines['right'].set_visible(False)  # 去掉右边框
        amp=dl[i]['S21(DB)']-dlB[i]['S21(DB)']
        # amp=amp-min(amp)
        # amp1=amp/4.34/0.09999999999999998/0.06/max(amp/4.34/0.09999999999999998/0.06)
        plt.plot(dl[i]['Freq(Hz)'] / (10 ** 9), savgol_filter(amp, 53, 10, mode='nearest'),
                    label=name[i])

        am=pd.DataFrame(savgol_filter(amp, 53, 10, mode='nearest'))
        am.to_csv('D:/OneDrive-stuJnu/OneDrive - stu2019.jnu.edu.cn/协同工作/数据分析/DATA/20210729/amp.csv')
        # print(amp1,dl[i]['Freq(Hz)'])
        # 平滑
        # plt.plot(dl[i]['Freq(Hz)'] / (10 ** 9),
        #          savgol_filter(amp-min(amp), 51, 3, mode='nearest'),
        #          label=name[i])
        # plt.title("Single Frequency Comb Control of SBS_MPF",fontsize=15, fontweight='bold')

        # BW=np.argwhere(amp1=0.5)
        # print(BW)
        # 斯托克斯
        # max_indx=np.argmax(amp)
        # Freq.append(dl[i]['Freq(Hz)'][max_indx]/(10**9))
        # FSBS=list(map(lambda x: x[0]-x[1],zip(pumpF,Freq)))
        # meanFSBS=np.mean(FSBS)
        #反斯托克斯
        # min_indx=np.argmin(amp)
        # Freq.append(dl[i]['Freq(Hz)'][min_indx]/(10**9))
        # Anti_FSBS=list(map(lambda x: x[0]-x[1],zip(pumpF,Freq)))
        # Anti_meanFSBS=np.mean(Anti_FSBS)
        # 显示最小值最大值点坐标
        # plt.plot(dl[i]['Freq(Hz)'][min_indx],dl[i]['S21(DB)'][min_indx],'ks')
        # show_min='['+str(dl[i]['Freq(Hz)'][min_indx])+' '+str(dl[i]['S21(DB)'][min_indx])+']'
        # plt.annotate(show_min,xytext=(dl[i]['Freq(Hz)'][min_indx],dl[i]['S21(DB)'][min_indx]),
        #              xy=(dl[i]['Freq(Hz)'][min_indx],dl[i]['S21(DB)'][min_indx]))

        plt.title("Amplitude Response", fontsize=15, fontweight='bold')
        plt.xlabel("Freqence(GHz)", fontsize=13, fontweight='bold')
        plt.ylabel("RF_Power(DB)", fontsize=13, fontweight='bold')
        plt.legend(loc='best', numpoints=1,ncol=1)
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=9, fontweight='bold')  # 设置图例字体的大小和粗细
        # plt.savefig(name[i] + ".svg", format="svg")
        phash = np.mod(dl[i]['S21(DEG)'] - dlB[i]['S21(DEG)'] + 180, 360) - 180

        # plt.plot(dl[-1]['Freq(Hz)']/(10**9),phash,
        #          label=name[j])
        # 平滑
        df=pd.DataFrame(savgol_filter(phash, 53, 10, mode='nearest'))
        df.to_csv('D:/OneDrive-stuJnu/OneDrive - stu2019.jnu.edu.cn/协同工作/数据分析/DATA/20210729/phash.csv')
        plt.plot(dl[i]['Freq(Hz)'] / (10 ** 9), savgol_filter(phash, 53, 10, mode='nearest'),
                 label=name[i])
        plt.title("Phase Response", fontsize=15, fontweight='bold')
        plt.xlabel("Freqence(GHz)", fontsize=13, fontweight='bold')
        plt.ylabel("RF_Power(DB)", fontsize=13, fontweight='bold')
        plt.legend(loc='best', numpoints=1, ncol=1)
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=12, fontweight='bold')  # 设置图例字体的大小和粗细

        i+=1
        # plt.show()
    # plt.xlim(3.88, 4.5)
    # plt.ylim(0, 15)
    plt.savefig(name[0]+".svg", format="svg")
    plt.show()
    # plt.figure(2)
    # plt.plot(Anti_FSBS)
    # plt.show()
    # print(Freq)
    # print("mean_SBS平移量：",Anti_meanFSBS)

def plot_phash(dl,dlB,name):
    """
    相频响应计算
    """
    N=len(dl)
    j=0
    for _ in range(N):
        plt.figure(2)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)  # 去掉上边框
        ax.spines['right'].set_visible(False)  # 去掉右边框

        phash=np.mod(dl[j]['S21(DEG)']-dlB[0]['S21(DEG)']+180,360)-180

        # plt.plot(dl[-1]['Freq(Hz)']/(10**9),phash,
        #          label=name[j])
        # 平滑
        plt.plot(dl[j]['Freq(Hz)']/(10**9),savgol_filter(phash,53,10, mode= 'nearest'),
                 label=name[j])
        plt.title("Phase Response", fontsize=15, fontweight='bold')
        plt.xlabel("Freqence(GHz)", fontsize=13, fontweight='bold')
        plt.ylabel("RF_Power(DB)", fontsize=13, fontweight='bold')
        plt.legend(loc='best', numpoints=1, ncol=1)
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=12, fontweight='bold')  # 设置图例字体的大小和粗细
        # plt.savefig(name[j] + "phase.svg", format="svg")
        j+=1
        # plt.show()

    # plt.xlim(6.98,7.09)
    # plt.ylim()
    # plt.legend()
    plt.savefig(name[0]+"phase.svg", format="svg")
    plt.show()

def file_name(file_dir):
    # 读取文件名
    L=[]
    for root, dirs, files in os.walk(file_dir,topdown=False):
        # print('root_dir:', root)  # 当前目录路径
        # print('sub_dirs:', dirs)  # 当前路径下所有子目录
        for file in files:
                L.append(os.path.splitext(file)[0])
        print('files:', L)  # 当前路径下所有非目录子文件
    return L

def plot_odd(dl,name):
    """
    仅仅画图
    :param dl:
    :return:
    """
    N = len(dl)
    i = 0
    for _ in range(N):
        plt.figure(1)
        ax = plt.gca()
        ax.spines['top'].set_visible(False)  # 去掉上边框
        ax.spines['right'].set_visible(False)  # 去掉右边框
        plt.plot(dl[i]['Freq(Hz)'] / (10 ** 9), dl[i]['S21(DB)']-min(dl[i]['S21(DB)']),
                 label=name[i])
        plt.title("Radio spectrum ",fontsize=15, fontweight='bold')
        plt.xlabel("Freqence(GHz)", fontsize=13, fontweight='bold')
        plt.ylabel("RF_Power(DB)", fontsize=13, fontweight='bold')
        plt.legend(loc='best', numpoints=1,ncol=1)
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=10, fontweight='bold')  # 设置图例字体的大小和粗细
        i+=1
    plt.xlim(6.89, 7.21)
    plt.ylim(0, 3.5)
    plt.savefig("300MHz三角形电谱图.svg", format="svg")
    plt.show()

def dat_csv(path,path_new):
    filelist = os.listdir(path)  # 目录下所有的文件列表
    print(filelist)
    for files in filelist:
        yuan_path = os.path.join(path, files)
        file_name = os.path.splitext(files)[0]  # 文件名
        Newdir = os.path.join(path_new, str(file_name) + '.csv')
        data = []
        with open(yuan_path, 'rb') as df:
            for line in df:
                data.append(list(line.strip().split()))
        dataset = pd.DataFrame(data)
        dataset.to_csv(Newdir, index=None)

if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 如果要显示中文字体,则在此处设为：SimHei   英文Arial
    plt.rcParams['axes.unicode_minus'] = False  # 显示负号

    '''
    Mark\
    path1:20210107实验数据绘图 单频调控范围证明
    path2:20210107实验数据绘图 50MHz三角形验证调控范围
    path3:20210107实验数据绘图 14G局部
    path4:20210106实验数据绘图 开关增益（较好）
    path5:20210107实验数据绘图 矩形带宽改变s  三角形带宽改变t
    path6:20210106实验数据绘图 矩形   三角形
    
    path7:0107  针对三角形带宽从30-120   300MHz尝试突破另外画图
    
    path8:0107 针对矩形带宽从30-120MHz
    path9:单梳齿
    path10:电谱图绘制宽波段
    path11:高精度光谱图
    path12:冲击300MHz三角形
    
    path13: 反斯托克斯 用的是14cm长波导（插损16dB）中心波长调控
    path14：单梳 反斯托克斯
    '''
    # path1=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\CW\Signal'
    # path1=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\CW\T'
    # path1=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\CW\CW14G'
    # path1=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210106\KG'
    # path1=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\S'
    # path1 = r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210106\S'
    # path7=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\T_BW_14GDf=3M'
    # path8=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\S_BW_14GDf=3M'
    # path9=r'C:\Users\Wentao Peng\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\T_BW_14GDf=3M'
    # pathB=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\T_BJ'
    # pathB=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\CW\Signal_BJ'
    # path10=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\电谱图'
    # dat11=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109高精度光谱仪dat'
    # path11=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109高精度光谱仪csv'
    # path13=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210113\P24.3abs'
    # path14=r'C:\Users\Wentao Peng\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210113\SOLO'
    # pathB=r'C:\Users\Wentao Peng\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\T_BJ'
    # 将dat转换为csv
    # dat_csv(dat11,path11)
    #  2021-3-26
    # path1=r'D:\OneDrive-stuJnu\OneDrive - stu2019.jnu.edu.cn\协同工作\数据分析\DATA\2021-3-26\20210326\一级=120MHz，BW=250MHz'
    # pathB=r'D:\OneDrive-stuJnu\OneDrive - stu2019.jnu.edu.cn\协同工作\数据分析\DATA\2021-3-26\20210326\DBBJ'
    # path12=r'C:\Users\DELL\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210109\T_300MHz'
    path1=r'D:\OneDrive-stuJnu\OneDrive - stu2019.jnu.edu.cn\协同工作\数据分析\DATA\20210729\ZBD'
    pathB=r'D:\OneDrive-stuJnu\OneDrive - stu2019.jnu.edu.cn\协同工作\数据分析\DATA\20210729\ZBDBJ'
    files=glob.glob(os.path.join(path1,"*.csv"))
    filesB = glob.glob(os.path.join(pathB, "*.csv"))
    name=file_name(path1)
    # nameB=file_name(pathB)
    # print(files)
    # print(name)
    # print(nameB)
    dl=[]
    for f in files:
        dl.append(pd.read_csv(f,skiprows=6,nrows=40000))
    print(dl)

    dlB=[]
    for f in filesB:
        dlB.append(pd.read_csv(f, skiprows=6, nrows=40000))
    print(dlB)
    plot1(dl,dlB,name)
    # plot_phash(dl,dlB,name)
    # plot_odd(dl,name)