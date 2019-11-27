import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

path = 'C:/Users/Kirill/Desktop/kistler/main'
os.chdir(path)
kis_file = path + '/' + 'without_outliers_alphas_0.01_0.01_Kirill 004.txt'


def main(file):
    dataX = np.loadtxt(file, skiprows=1)[:, 1]
    fs = 1000

    # Get real amplitudes of FFT (only in positive frequencies)
    fft_vals = np.absolute(np.fft.rfft(dataX))

    # Get frequencies for amplitudes in Hz
    fft_freq = np.fft.rfftfreq(len(dataX), 1.0/fs)

    # Define bands
    bands = {'0-0.3': (0.0, 0.3), '0.3-1': (0.3, 1.0), '1-7': (1.0, 7.0)}

    # Take the mean of the fft amplitude for each band
    band_fft = dict()
    for band in bands:
        freq_ix = np.where((fft_freq >= bands[band][0])
                           & (fft_freq <= bands[band][1]))[0]
        band_fft[band] = np.mean(fft_vals[freq_ix])

    df = pd.DataFrame(columns=['band', 'value'])
    df['band'] = bands.keys()
    df['value'] = [band_fft[band] for band in bands]
    ax = df.plot.bar(x='band', y='value', legend=False)
    ax.set_xlabel("Stab band")
    ax.set_ylabel("Mean band Amplitude")
    ax.plot()
    plt.show()


if __name__ == '__main__':
    main(kis_file)
