import pyaudio
import numpy as np
from math import*
import matplotlib.pyplot as plt

#
volume = [0.036956521739130443,0.05555555555555556,0.04857142857142857,0.054838709677419356,0.052795031055900624,
          0.06296296296296297,0.08585858585858587,0.09340659340659341,0.12686567164179105,0.16666666666666669,
          0.14655172413793105,0.1931818181818182,0.19767441860465118,0.1847826086956522,0.23611111111111113]

# # Get rid of low frequencies
# volume = [0, 0, 0, 0, 0,
#           0, 0, 0, 0, 0,
#           0.3,0.3,0.3, 0.3, 0.3]

duration = 5   # in seconds, may be float
fs = 50000       # sampling rate, Hz, must be integer

p = pyaudio.PyAudio()

# # For single tone frequency
# f = 440.0        # sine frequency, Hz, may be float
# # generate samples, note conversion to float32 array
# samples = volume*(np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)
#
# print(type(samples))

# For 100-1500Hz combine frequency
freqarr = [100.0*(i+1) for i in range(15)]
shiftarr = [-0.34,-0.685,0.41,0.505,0.195,0.145,1.455,-0.605,0.66,-0.91,0.015,2.875,-1.45,2.32,0.25]
shiftarr = [0,0,0,0,0,0,0,0,0,0,1.625,0.705,-0.2,2.305,-1.3]
timearr = np.arange(fs*duration)*(1/fs)

samples = np.sin(2 * np.pi * np.arange(fs*duration)*0/fs).astype(np.float32)
for j in range(len(freqarr)):
    samples += volume[j] * np.sin(2 * np.pi * np.arange(fs*duration)*freqarr[j]/fs + shiftarr[j]).astype(np.float32)

# plt.plot(samples)
# plt.show()

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

# play. May repeat with different volume values (if done interactively)
while True:
    stream.write(samples)

# stream.stop_stream()
# stream.close()
#
# p.terminate()