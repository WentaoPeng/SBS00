__author__ = """Wentao Peng"""
__email__ = 'wentaopeng@stu2019.jnu.edu.cn'
__version__ = '2020'

# ! encoding = utf-8

import sys
from PyQt5 import QtWidgets
import GUI.MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = GUI.MainWindow.MainWindow()
    window.show()
    # window.showNormal()  # 高分辨率显示
    # window.showMaximized()  # 字体适应最大化屏幕缩放

    sys.exit(app.exec_())
