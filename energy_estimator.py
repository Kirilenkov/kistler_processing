import pandas as pd
import os

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


hard_path = 'C:/Users/Kirill/Desktop/Stab_records/velocity'
path_setter(hard_path)
file_dir_list = [(p, f) for p, d, f in os.walk(os.getcwd())]
file_list = []
for p, f in file_dir_list:
    for i in f:
        if '.txt' in i:
            file_list.append(p + '\\' + i)
print(file_list)
writer = pd.ExcelWriter('../Energy.xlsx')
