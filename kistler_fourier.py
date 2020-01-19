import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import get_window


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


hard_path = 'C:/Users/Kirill/Desktop/Stab_records/all/after'
path_setter(hard_path)
file_dir_list = [(p, f) for p, d, f in os.walk(os.getcwd())]
file_list = []
for p, f in file_dir_list:
    for i in f:
        if '.txt' in i:
            file_list.append(p + '\\' + i)
print(file_list)
writer = pd.ExcelWriter('../kistler_fourier.xlsx')


def core(file, axis):
    data = np.loadtxt(file, skiprows=1)[:, axis]
    fs = 1000
    # Get real amplitudes of FFT (only in positive frequencies)
    '''
    while True:
        trigger = input('Применить окно Хеннинга? y/n \n').lower()
        if trigger == 'y':
            m = len(data)
            w = get_window('hann', m)
            fft_vals = np.absolute(np.fft.rfft(data * w))
            break
        elif trigger == 'n':
            fft_vals = np.absolute(np.fft.rfft(data))
            break
    '''
    m = len(data)
    w = get_window('hann', m)
    fft_vals = np.absolute(np.fft.rfft(data * w))

    # Get frequencies for amplitudes in Hz
    fft_freq = np.fft.rfftfreq(len(data), 1.0/fs)

    # Define bands
    bands = {'0-0.3': (0.016, 0.3), '0.3-1': (0.3, 1.0), '1-7': (1.0, 7.0)}

    # Take the mean of the fft amplitude for each band
    band_fft = dict()
    freq_ix_list = []
    max_peak_list = []
    for band in bands:
        freq_ix = np.where((fft_freq >= bands[band][0]) & (fft_freq <= bands[band][1]))[0]
        print("------------------------------------------------------")
        freq_ix_list.append(freq_ix)
        max_magn_for_band = np.max(fft_vals[freq_ix])
        band_fft[band] = max_magn_for_band
        max_peak_ix = np.where(fft_vals == max_magn_for_band)
        max_peak_list.append(fft_freq[max_peak_ix])

    freq_ix_cum = np.concatenate(freq_ix_list)

    df = pd.DataFrame(columns=['freq', 'magn'])
    df['freq'] = [fft_freq[ix] for ix in freq_ix_cum]
    df['magn'] = [fft_vals[ix] for ix in freq_ix_cum]

    ax = df.plot.line(x='freq', y='magn', legend=False)
    ax.set_xlabel("Frequencies [Hz]")
    ax.set_ylabel("Magnitude")

    inf = file.split('\\')[-1].split(' ')
    pref = inf[-1][0:3]
    eyes = int(pref[-1]) % 2
    if eyes == 1:
        pref = 'EC_'
    elif eyes == 0:
        pref = 'EO_'

    f_name = '{0:s}{1:s}_Axis_{2:s}'.format(pref, file.split('\\')[-1],
            'X' if axis == 1 else ('Y' if axis == 2 else 'Unknown axis'))
    ax.set_title(f_name)

    ax.xaxis.set_major_locator(plt.MultipleLocator(0.5))
    plt.grid(True)
    ax.plot()

    plt.savefig(f_name + '.png')
    # plt.show()
    return max_peak_list


def main(files):
    result_df_list = []
    col = ''
    for file in files:
        for i in range(1, 2, 1):
            ls = core(file, i)
            if i == 1:
                col = 'X'
            elif i == 2:
                col = 'Y'
            line = file.split('\\')[-1]
            suff = '_processed'
            result_df_list.append(pd.DataFrame([ls], columns=['0-0.3_' + col + suff, '0.3-1_' + col + suff, '1-7_' + col + suff], index=[line]))
    pd.concat(result_df_list, axis=0).to_excel(writer, sheet_name='Fourier', index=True)
    writer.save()


if __name__ == '__main__':
    main(file_list)

