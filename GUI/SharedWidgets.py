#! encoding = utf-8

from PyQt5 import QtGui, QtCore, QtWidgets
import random
from math import ceil
import numpy as np


BUTTONLABEL = {'confirm':['Lets do it', 'Go forth and conquer', 'Ready to go',
                          'Looks good', 'Sounds about right'],
               'complete':['Nice job', 'Sweet', 'Well done', 'Mission complete'],
               'accept':['I see', 'Gotcha', 'Okay', 'Yes master'],
               'reject':['Never mind', 'I changed my mind', 'Cancel', 'I refuse'],
               'error':['Oopsy!', 'Something got messed up', 'Bad']
                }



def btn_label(btn_type):
    ''' Randomly generate a QPushButton label.
        Arguments
            btn_type: str
        Returns
            label: str
    '''

    try:
        a_list = BUTTONLABEL[btn_type]
        return a_list[random.randint(0, len(a_list)-1)]
    except KeyError:
        return 'A Button'





def msgcolor(status_code):
    ''' Return message color based on status_code.
        0: fatal, red
        1: warning, gold
        2: safe, green
        else: black
    '''

    if not status_code:
        return '#D63333'
    elif status_code == 1:
        return '#FF9933'
    elif status_code == 2:
        return '#00A352'
    else:
        return '#000000'