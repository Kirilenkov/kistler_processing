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


hard_path = 'C:/Users/Kirill/Desktop/kistler/main'
path_setter(hard_path)
file_dir_list = [(p, f) for p, d, f in os.walk(os.getcwd())]
file_list = []
for p, f in file_dir_list:
    for i in f:
        if '.txt' in i:
            file_list.append(p + '\\' + i)
print(file_list)


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
    for band in bands:
        freq_ix = np.where((fft_freq >= bands[band][0]) & (fft_freq <= bands[band][1]))[0]
        print("------------------------------------------------------")
        freq_ix_list.append(freq_ix)
        max_magn_for_band = np.max(fft_vals[freq_ix])
        band_fft[band] = max_magn_for_band
        max_peak_ix = np.where(fft_vals == max_magn_for_band)
        print(fft_freq[max_peak_ix])

    freq_ix_cum = np.concatenate(freq_ix_list)

    df = pd.DataFrame(columns=['freq', 'magn'])
    df['freq'] = [fft_freq[ix] for ix in freq_ix_cum]
    df['magn'] = [fft_vals[ix] for ix in freq_ix_cum]

    ax = df.plot.line(x='freq', y='magn', legend=False)
    ax.set_xlabel("Frequencies [Hz]")
    ax.set_ylabel("Magnitude")
    ax.set_title('Name: {0:s}, Axis: {1:s}'
                 .format(file.split('/')[-1], 'X' if axis == 1 else ('Y' if axis == 2 else 'Unknown axis')))
    ax.xaxis.set_major_locator(plt.MultipleLocator(0.5))
    plt.grid(True)
    ax.plot()
    plt.show()


def main(files):
    for file in files:
        for i in range(1, 2, 1):
            core(file, i)


if __name__ == '__main__':
    main(file_list)

