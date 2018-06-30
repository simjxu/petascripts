import numpy as np
import matplotlib.pyplot as plt

def sum_sines(freqarr,shiftarr):
    time_signal = np.arange(0, 2, 0.0001)
    comb_signal = np.zeros(len(time_signal))
    for j in range(len(freqarr)):
        comb_signal += amp * np.sin(2 * np.pi * freqarr[j] * time_signal + shiftarr[j])
    return comb_signal

# freqarr = [100.0*(i+1) for i in range(15)]
freqarr = [1100,1200,1300,1400,1500]
# shiftarr = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
# shiftarr = [-0.34,-0.685,0.41,0.505,0.195,0.145,1.455,-0.605,0.66,-0.91,0.015,2.875,-1.45,2.32,0.25]
shiftarr = [1.1,0.7,-0.2,2.3,-1.3]

amp = 0.12

# Time and signal array
time_signal = np.arange(0,2,0.0001)
comb_signal = np.zeros(len(time_signal))

# Find optimal shift array
inc = 0.005
# for i in range(1):
for k in range(5):
    for i in range(len(shiftarr)):
        curr_max = np.max(np.abs(sum_sines(freqarr,shiftarr)))
        new_max = curr_max
        newshift = np.copy(shiftarr)
        newshift[i] += inc
        if np.max(np.abs(sum_sines(freqarr, newshift))) < curr_max:
            new_max = np.max(np.abs(sum_sines(freqarr, newshift)))
            while new_max < curr_max:
                curr_max = new_max
                newshift[i] += inc
                new_max = np.max(np.abs(sum_sines(freqarr, newshift)))
                if new_max > curr_max:
                    newshift[i] -= inc
        else:
            newshift = np.copy(shiftarr)
            newshift[i] -= inc
            if np.max(np.abs(sum_sines(freqarr, newshift))) < curr_max:
                new_max = np.max(np.abs(sum_sines(freqarr, newshift)))
                while new_max < curr_max:
                    curr_max = new_max
                    newshift[i] -= inc
                    new_max = np.max(np.abs(sum_sines(freqarr, newshift)))
                    if new_max > curr_max:
                        newshift[i] += inc
            else:
                newshift = np.copy(shiftarr)
        print("Newest max:", new_max)
        shiftarr = newshift
        print(shiftarr)


comb_signal = sum_sines(freqarr, shiftarr)

plt.plot(time_signal, comb_signal)
plt.show()