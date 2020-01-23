import pandas as pd
import numpy as np
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


hard_path = 'C:/Users/Kirill/Desktop/Stab_records/velocity/proc'
path_setter(hard_path)
file_dir_list = [(p, f) for p, d, f in os.walk(os.getcwd())]
file_list = []
for p, f in file_dir_list:
    for i in f:
        if '.txt' in i:
            file_list.append(p + '\\' + i)
writer = pd.ExcelWriter('Energy.xlsx')


def core(file, axis, skip, weight=60):
    data = np.loadtxt(file, skiprows=skip)[:, axis]
    total = 0
    for i in range(data.__len__() - 1):
        total += weight * abs(pow(data[i + 1], 2) - pow(data[i], 2))/2
    return total


def main(skip_num):
    pref = ''
    if skip_num == 1:
        pref += 'proc_'
    else:
        pref += 'raw_'
    axis = 'Unknown axis'
    name_prev = 'start'
    micro_df_list = []
    macro_df_list = []
    table = pd.DataFrame()
    for f in file_list:
        inf = f.split('\\')[-1].split(' ')
        suff = inf[-1][0:3]
        name = inf[0]
        trigg = int(suff[-1])
        eyes = trigg % 2
        if eyes == 1:
            suff += '_EC'
        elif eyes == 0:
            suff += '_EO'
        for i in range(1, 3):
            if i == 1:
                axis = 'X'
            elif i == 2:
                axis = 'Y'
            val = core(f, i, skip_num)
            snippet = pd.DataFrame(val, index=[name], columns=[pref + 'axis_' + axis + '_' + suff])
            if name != name_prev and name_prev != 'start':
                line = pd.concat(micro_df_list, axis=1, sort=True)
                print(line)
                macro_df_list.append(line)
                micro_df_list.clear()
            micro_df_list.append(snippet)
            name_prev = name
    table = pd.concat(macro_df_list, axis=0, sort=True)
    table.to_excel(writer, sheet_name=pref.upper() + 'Energy', index=True)
    writer.save()


if __name__ == '__main__':
    main(1)
