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
values = acquire_samples(dev0, c_int(0), sampling_rate, nSamples)

for i in range(len(values)):
    values[i] = values[i]/0.04867         # used to be 0.05166  0.05881   SS: 0.04867

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

freqarr = [100*(i+1) for i in range(15)]
reference_values = [0.0 for i in range(len(freqarr))]
for i in range(len(freqarr)):
    start = int((freqarr[i] - 30) / bin_size)
    stop = int((freqarr[i] + 30) / bin_size)
    reference_values[i] = max(yf[start:stop])

print(reference_values)
plt.plot(xf, yf)
plt.show()

# Zval = [0.57, 0.95, 0.9, 0.9, 0.65, 0.49, 0.51, 0.42, 0.44, 0.97, 0.66, 0.72, 0.8, 0.81, 1.16]
# newval = [0.5592703247269647, 0.95487620082305358, 0.89092940278817589, 0.92037696058224105, 0.66861508060960884, 0.52253411176432263, 0.56069145157158962, 0.48244009241912056, 0.51498871510448441, 1.1024332095606051, 0.75774679250775634, 0.85645002314836338, 1.1178021322937142, 1.1711074895224816, 1.7154831066303717]
#
# ratio = [0.0 for i in range(len(freqarr))]
# for i in range(len(freqarr)):
#     ratio[i] = Zval[i]/newval[i]
#
# plt.plot(xf, yf)
# plt.show()