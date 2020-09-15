
from PIL import Image
import numpy as np
from float2hex import *
import os


def make_mif(file_path="d:/Domerectpy.mif"):
    img_pil = Image.open("resize_img.png")
    w, h = img_pil.size
    img_pil = np.array(img_pil).astype(np.float32)
    img_pil = img_pil / 255.  # 归一化
    print(img_pil.shape)
    r = np.reshape(img_pil[:, :, 0], w * h)
    g = np.reshape(img_pil[:, :, 1], w * h)
    b = np.reshape(img_pil[:, :, 2], w * h)

    headfile = '''DEPTH = 65536;
WIDTH = 32;
ADDRESS_RADIX = HEX;
DATA_RADIX = HEX;
CONTENT
BEGIN
'''
    # red 通道
    mif = open(os.path.join(file_path, "r_32bit.mif"), "w")
    mif.writelines(headfile)
    for i in range(0, w * h):
        mif.writelines(str(hex(i)[2:]))
        mif.writelines(':')
        mif.writelines(str(float2hex(r[i])[2:]))
        mif.writelines(';')
        mif.writelines('\n')
    mif.write('END;')
    # green 通道
    mif = open(os.path.join(file_path, "g_32bit.mif"), "w")
    mif.writelines(headfile)
    for i in range(0, w * h):
        mif.writelines(str(hex(i)[2:]))
        mif.writelines(':')
        mif.writelines(str(float2hex(g[i])[2:]))
        mif.writelines(';')
        mif.writelines('\n')
    mif.write('END;')
    # blue通道
    mif = open(os.path.join(file_path, "b_32bit.mif"), "w")
    mif.writelines(headfile)
    for i in range(0, w * h):
        mif.writelines(str(hex(i)[2:]))
        mif.writelines(':')
        mif.writelines(str(float2hex(b[i])[2:]))
        mif.writelines(';')
        mif.writelines('\n')
    mif.write('END;')


if __name__ == '__main__':
    make_mif()