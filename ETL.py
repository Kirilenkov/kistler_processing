import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

default_msg = 'Enter the full path to the folder with the log files: \n'


def path_setter(link, message=default_msg, stage=False):
    if message[-1] != '\n':
        message += '\n'
    try:
        os.chdir(link)
    except FileNotFoundError:
        if not stage:
            print('Hard path not found')
        else:
            print('Cannot find the specified path')
        path_setter(input(message), message=message, stage=True)
