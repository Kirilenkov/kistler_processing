import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.signal import get_window

path = 'C:/Users/Kirill/Desktop/kistler/main'
os.chdir(path)
kis_file = path + '/' + 'without_outliers_alphas_0.01_0.01_Ksenia_EC_002.txt'


def main(file):
    data = np.loadtxt(file, skiprows=1)[:, 1]
    fs = 1000
    # Get real amplitudes of FFT (only in positive frequencies)
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

    """
    df = pd.DataFrame(columns=['band', 'value'])
    df['band'] = bands.keys()
    df['value'] = [band_fft[band] for band in bands]
    print(df)
    ax = df.plot.bar(x='band', y='value', legend=False)
    ax.set_xlabel("Stab band")
    ax.set_ylabel("Max band Magnitude")
    """
    df = pd.DataFrame(columns=['freq', 'magn'])
    df['freq'] = [fft_freq[ix] for ix in freq_ix_cum]
    df['magn'] = [fft_vals[ix] for ix in freq_ix_cum]

    ax = df.plot.line(x='freq', y='magn', legend=False)
    ax.set_xlabel("Frequencies [Hz]")
    ax.set_ylabel("Magnitude")
    print(plt.xticks())

    ax.plot()
    plt.show()


if __name__ == '__main__':
    main(kis_file)
