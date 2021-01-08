import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob,os
'''
20210107实验数据绘图
'''
# CW10=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\10.csv',skiprows=6,nrows=40000)
# CW11=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\11.csv',skiprows=6,nrows=40000)
# CW12=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\12.csv',skiprows=6,nrows=40000)
# CW13=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\13.csv',skiprows=6,nrows=40000)
# CW14=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\14.csv',skiprows=6,nrows=40000)
# CW15=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\15.csv',skiprows=6,nrows=40000)
# CW16=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\16.csv',skiprows=6,nrows=40000)
# CW17=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\17.csv',skiprows=6,nrows=40000)
# CW18=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\18.csv',skiprows=6,nrows=40000)
# CW19=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\19.csv',skiprows=6,nrows=40000)
# CW20=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\20.csv',skiprows=6,nrows=40000)
#
# BG=pd.read_csv('C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S\\BG.csv',skiprows=6,nrows=40000)

# data=r'C:\\Users\\Wentao Peng\\OneDrive - stu2019.jnu.edu.cn\\组会报告\\实验数据\\Experimental data\\20210107\\New folder\\S'
path=r'C:\Users\Wentao Peng\OneDrive - stu2019.jnu.edu.cn\组会报告\实验数据\Experimental data\20210107\New folder\S'
files=glob.glob(os.path.join(path,"*.csv"))
print(files)

dl=[]
for f in files:
    dl.append(pd.read_csv(f,skiprows=6,nrows=40000))

print(dl)

r_color = np.random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k', 'd', 'l', 's'])

N=len(dl)-1
i=0
for _ in range(N):
    plt.figure(1)
    open_off=dl[i]['S21(DB)']-dl[-1]['S21(DB)']
    plt.plot(dl[-1]['Freq(Hz)']/(10**9),open_off,label='PUMP'+str(i))
    plt.xlabel("Freq(GHz)")
    plt.ylabel("S21(DB)")
    i+=1
plt.show()