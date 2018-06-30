import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

file = open("data.txt", 'r')
datain = file.read().split("\n")

values = [0 for i in range(len(datain))]
for i in range(len(datain)):
    values[i] = float(datain[i])

# reader = csv.reader(open("data.txt", "r"), delimiter=",")
# x = list(reader)
# values = np.array(x).astype("float")
# values = values[0]

print("length:", len(values))
print("RMS:", np.sqrt(np.mean(np.square(values))))

# Zval = [0.75, 0.88, 1.02, 1.1, 0.97, 0.94, 1.14, 0.94, 0.92, 1.01, 1.02, 0.97, 0.87, 0.83, 1.12]
# Zval = [0.75, 0.88, 1.02, 1.1, 0.97, 0.94, 1.14, 0.94, 0.92, 1.01, 1.02, 0.97, 0.87, 0.83, 0.86]

freqarr = [100*(i+1) for i in range(15)]
sampling_rate = 6664
num_samples = len(values)
xf = np.linspace(0.0, sampling_rate / 2, num_samples // 2)
_, yf = welch(
    values,
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

reference_values = [0.0 for i in range(len(freqarr))]
for i in range(len(freqarr)):
    start = int((freqarr[i] - 30) / bin_size)
    stop = int((freqarr[i] + 30) / bin_size)
    reference_values[i] = max(yf[start:stop])

print(reference_values)

plt.plot(xf, yf)
plt.show()

# ratio = [0.0 for i in range(len(freqarr))]
# for i in range(len(freqarr)):
#     ratio[i] = Zval[i]/reference_values[i]
#
# print(ratio)
# # Plot the spectrum
# plt.plot(xf, yf)
# plt.show()
#
# plt.plot(freqarr, ratio)
# plt.ylim(0,1.3)
# plt.show()

