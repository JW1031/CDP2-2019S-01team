import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy import signal
import os
import glob
from matplotlib import rc
import io
import cv2
rc("font", size=6, weight='bold')
#%%
def time_stft_psd_plot(fs, NFFT, var, time):
    f_var, Pxx_den_var = signal.welch(var, fs, nperseg=len(x),
                                      scaling='density')  # Estimate Power Spectral Density using Welch’s method.
    mean_var = np.mean(10 * np.log10(Pxx_den_var))  # Compute mean of PSD in [dB].
    mean_varvar = [mean_var, mean_var]
    f_mean = [min(f_var), max(f_var)]

    my_x_ticks_1 = np.arange(0, 800, 200)  # Set axis-ticks.
    my_x_ticks_2 = np.arange(0, 800, 200)  # If use different dataset,
    my_x_ticks_3 = np.arange(-240, 0, 30)  # these may need to be changed.

    fig, (ax1) = plt.subplots(nrows=1, ncols=1)

    pxx, freq, bins, im = ax1.specgram(var, NFFT=NFFT, mode='psd', noverlap=0, scale='dB', Fs=fs, vmin=-125, vmax=-15,
                                       cmap='gray')  # Plot spectrogram.
    ax1.set_xlabel('Time [s]', fontweight='bold')
    ax1.set_ylabel('Frequency [Hz]', fontweight='bold')
    ax1.set_xticks(my_x_ticks_2)
    plt.xticks(fontsize=6)
    return ax1


def ax_to_ndarray(ax, **kwargs):

    ax.axis('off')
    ax.figure.canvas.draw()
    trans = ax.figure.dpi_scale_trans.inverted()
    bbox = ax.bbox.transformed(trans)

    buff = io.BytesIO()
    plt.savefig(buff, format='png', dpi=ax.figure.dpi, bbox_inches=bbox, **kwargs)
    buff.seek(0)
    im = plt.imread(buff)
    return im

#%%


os.chdir('D:/Capstone/20190109/1.12')
work_path = os.getcwd() # set path
qry = work_path + '/*.csv'
files = glob.glob(qry) # get files

save_path = 'C:/Users/tkddj/PycharmProjects/Capstone/data'


#%%
for fn in files:
    filename = fn.rstrip('.csv')
    data = pd.read_csv(fn, names=['id', 'x', 'y', 'z', 'ts'])

    x = data['x']
    y = data['y']
    z = data['z']

    t = data['ts']

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    z_mean = np.mean(z)

    x = x - x_mean # Extracted by the mean
    y = y - y_mean
    z = z - z_mean

    t = (t-t[0])/1000 # Convert timestamp to [s]

    fs = 100 # Sampling rate
    NFFT = 2*fs # Number of samples used in each window for FFT. We set two seconds window.
    ax = time_stft_psd_plot(fs, NFFT, x, t)
    ay = time_stft_psd_plot(fs, NFFT, y, t)
    az = time_stft_psd_plot(fs, NFFT, z, t)
    x_img = ax_to_ndarray(ax)[:,:,0]
    y_img = ax_to_ndarray(ay)[:,:,0]
    z_img = ax_to_ndarray(az)[:,:,0]
    RGB_xyz = np.zeros(shape=[x_img.shape[0], x_img.shape[1], 3])
    RGB_xyz[:, :, 0] = x_img
    RGB_xyz[:, :, 1] = y_img
    RGB_xyz[:, :, 2] = z_img
    RGB_xyz = (RGB_xyz*255).astype('uint8')
    filename = fn.rstrip('.csv').split('\\')
    filename = filename[len(filename) - 1]
    cv2.imwrite(save_path + '/' + filename +'.png', RGB_xyz)
    plt.close('all')