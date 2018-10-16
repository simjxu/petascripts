import requests
import time
import json
import numpy as np
from scipy.signal import welch
import matplotlib.pyplot as plt
import scipy.io as sio

file = open('data.txt', 'r')
pts = file.read().split("\n")
print(len(pts))
datapoints = [float(i) for i in pts]

# plt.plot(datapoints)
# plt.show()

print("RMS:", np.sqrt(np.mean(np.square(datapoints))))
freq = [100 * (i+1) for i in range(15)]
reference_value = [0.0 for i in range(15)]
for i in range(1):
    extract_data = datapoints
    num_samples = len(extract_data)

    sampling_rate = 6664

    xf = np.linspace(0.0, sampling_rate / 2, num_samples // 2)
    _, yf = welch(
        extract_data,
        sampling_rate,
        nperseg=num_samples,
        noverlap=0,
        window='flattop',
        scaling='spectrum'
    )

    yf = np.sqrt(2 * yf) * len(yf)
    yf = yf[:len(xf)]
    yf = 2.0 / num_samples * np.abs(yf)
    bin_size = sampling_rate / num_samples

for i in range(15):
    start = int((freq[i] - 30) / bin_size)
    stop = int((freq[i] + 30) / bin_size)
    reference_value[i] = max(yf[start:stop])

print(reference_value)
plt.plot(xf, yf)
# plt.ylim([0.5, 0.6])
plt.show()