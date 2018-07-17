from ctypes import *
from dwfconstants import *
from scipy.signal import welch
import time
from math import*
import matplotlib.pyplot as plt
import sys
import numpy as np

# Loading library for connecting to device
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")
# Declare ctype variables
IsInUse = c_bool()
dev0 = c_int(0)             # device 0: outputs 1 signal, 2 inputs
dev1 = c_int(0)             # device 1: 1 input only
cdevices = c_int()

def acquire_samples(device, channel, sampling_rate, nSamples):
# Acquire samples from device, channel and for however many samples
    cSamples = 0; cLost = c_int(); cCorrupted = c_int(); fLost = 0; fCorrupted = 0; cAvailable = c_int()
    sts = c_byte(); rgpy = [0.0] * nSamples
    # set up acquisition for device 0 channel 0
    dwf.FDwfAnalogInChannelEnableSet(device, channel, c_bool(True))      # Enable Analog in channel
    dwf.FDwfAnalogInChannelRangeSet(device, channel, c_double(0.1))      # Configure channel range
    dwf.FDwfAnalogInAcquisitionModeSet(device, acqmodeRecord)            # Perform acquisition for length of time RecordLengthSet
    dwf.FDwfAnalogInFrequencySet(device, sampling_rate)                          # Set sample rate of device
    dwf.FDwfAnalogInChannelOffsetSet(device, channel, c_double(0.0))     # Configure offset for channel
    # Define RecordLengthSet
    dwf.FDwfAnalogInRecordLengthSet(device, c_double(float(nSamples) / sampling_rate.value))
    dwf.FDwfAnalogInConfigure(device, c_bool(True), c_bool(True))
    time.sleep(0.3)                 # Wait for acquisition to settle
    # Temporary samples array
    tmpSamples = (c_double * int(nSamples))()  # creates array
    while cSamples < nSamples:
        dwf.FDwfAnalogInStatus(device, c_bool(True), byref(sts))
        if cSamples == 0 and (sts == DwfStateConfig or sts == DwfStatePrefill or sts == DwfStateArmed):
            # Acquisition not yet started.
            continue
        dwf.FDwfAnalogInStatusRecord(device, byref(cAvailable), byref(cLost), byref(cCorrupted))
        cSamples += cLost.value
        if cLost.value:
            fLost = 1
        if cCorrupted.value:
            fCorrupted = 1
        if cAvailable.value == 0:
            print("third if")
            continue
        if cSamples + cAvailable.value > nSamples:
            cAvailable = c_int(nSamples - cSamples)
        # get samples
        dwf.FDwfAnalogInStatusData(device, channel, byref(tmpSamples, cSamples * 8), cAvailable)
        cSamples += cAvailable.value
    if fLost:
        print(
        "Samples were lost! Reduce frequency")
    if cCorrupted:
        print(
        "Samples could be corrupted! Reduce frequency")
    # Save the values
    for i in range(0, nSamples):
        rgpy[i] = tmpSamples[i]
    # dwf.FDwfAnalogInConfigure(device, c_bool(False), c_bool(False))
    # dwf.FDwfAnalogInChannelEnableSet(device, channel, c_bool(False))
    return rgpy

def plot_response(values, sampling_rate, nSamples):
    plt.plot(values)
    plt.show()

    np.savetxt('1500Hz_comb.txt', values, delimiter=',')

    print("RMS:", np.sqrt(np.mean(np.square(values))))

    sampling_rate = sampling_rate.value
    num_samples = nSamples
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

    freqarr = [100 * (i + 1) for i in range(15)]
    reference_values = [0.0 for i in range(len(freqarr))]
    for i in range(len(freqarr)):
        start = int((freqarr[i] - 30) / bin_size)
        stop = int((freqarr[i] + 30) / bin_size)
        reference_values[i] = max(yf[start:stop])

    print(reference_values)
    plt.plot(xf, yf)
    plt.show()

# START SCRIPT -----------------------------------------------------------------------------
# Show Devices Available
# Declare string variables
serialnum = create_string_buffer(16)
# Print DWF version
version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: ", version.value)
# Enumerate and print device information
dwf.FDwfEnum(c_int(0), byref(cdevices))
print("Number of Devices: ", str(cdevices.value))
for i in range(0, cdevices.value):
    dwf.FDwfEnumSN(c_int(i), serialnum)
    print("------------------------------")
    print("Device ", str(i), " : ")
    print(str(serialnum.value))
    dwf.FDwfEnumDeviceIsOpened(c_int(i), byref(IsInUse))
    # Define device by serial number
    dwf.FDwfDeviceOpen(c_int(i), byref(dev0))

print("------------------------------")
# Device 0: outputting signal from Device
if dev0.value == hdwfNone.value:
    print("failed to open 1st device")
    quit()
else:
    print("Device Connected! Waiting for signal...")

sampling_rate = c_double(20000)
nSamples = 20000
time.sleep(2)
values1 = acquire_samples(dev0, c_int(0), sampling_rate, nSamples)
values2 = acquire_samples(dev0, c_int(1), sampling_rate, nSamples)


for i in range(len(values1)):
    values1[i] = values[i]/0.059749
    values2[i] = values2[i]/0.059289         # used to be 0.05166  0.059289   SS: 0.04867

plot_response(values1, sampling_rate, nSamples)
plot_response(values2, sampling_rate, nSamples)