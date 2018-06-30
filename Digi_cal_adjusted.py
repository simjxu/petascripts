from json import dumps
from bottle import route, run, response
from ctypes import *
from dwfconstants import *
import time
import sys
from math import*
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch
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

def get_reference_values(collected_samples, freqarr, sampling_rate, num_samples, axis):

    # Plot the waveform
    plt.plot(collected_samples)
    plt.show()

    # Calculate spectrum
    xf = np.linspace(0.0, sampling_rate / 2, num_samples // 2)
    _, yf = welch(
        collected_samples,
        sampling_rate,
        nperseg=num_samples,
        noverlap=0,
        window='flattop',
        scaling='spectrum'
    )
    yf = np.sqrt(2 * yf) * len(yf)
    yf = yf[:len(xf)]
    yf = 2.0 / num_samples * np.abs(yf)

    # Plot the spectrum
    plt.plot(xf, yf)
    plt.show()

    # Determine the maximum at each frequency in frequency array
    reference_values = [0.0 for i in range(len(freqarr))]
    # reference_values = dict()
    bin_size = sampling_rate / num_samples
    # Divide by Reference 832M1 Sensitivities -----
    if axis == 1:
        volt = 0.049382
    elif axis == 2:
        volt = 0.049076
    else:
        volt = 0.051660
    for i in range(len(freqarr)):
        start = int((freqarr[i] - 30) / bin_size)
        stop = int((freqarr[i] + 30) / bin_size)
        reference_values[i] = max(yf[start:stop])/volt
        # reference_values[str(i)] = max(yf[start:stop])/volt
        # print(freqarr[i], ":", max(yf[start:stop])/volt)
    # plt.plot(xf, yf)
    # plt.show()
    return reference_values

@route('/calibrate/<sensor>/<frequency:int>')
def calibrate_at_frequency(sensor, frequency):
    if sensor == "LSM6DS3":
        sampling_rate = c_double(20000)
        nSamples = 16384
    elif sensor == "832M1":
        sampling_rate = c_double(20000)
        nSamples = 16384
    else:
        resp = {"message": "Sensor name entered incorrectly"}
        return dumps(resp)

    # BEGIN ACQUISITION ----------------------------------------------
    print("Acquiring data...")
    dwf.FDwfAnalogInConfigure(dev0, c_bool(True), c_bool(True))  # Configures devices to be on
    dwf.FDwfAnalogInConfigure(dev1, c_bool(True), c_bool(True))
    time.sleep(1)  # Wait for signal to settle...
    # Acquire samples, Device 0 Channel 0
    dev0chan0_values = acquire_samples(dev0, c_int(0), sampling_rate, nSamples)
    # # Acquire samples, Device 0 Channel 1
    # dev0chan1_values = acquire_samples(dev0, c_int(1), sampling_rate, nSamples)
    # # Acquire samples, Device 1 Channel 0
    # dev1chan0_values = acquire_samples(dev1, c_int(0), sampling_rate, nSamples)

    # GET REFERENCE VAL ----------------------------------------------
    print("Getting reference values...")
    reference_values1 = get_reference_values(dev0chan0_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=nSamples, axis=3)
    reference_values2 = get_reference_values(dev0chan0_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=nSamples, axis=3)
    reference_values3 = get_reference_values(dev0chan0_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=nSamples, axis=3)

    print("Dumping response...")
    # resp = {
    #     "message": "Shaker is now running at %s." % (freqstring),
    #     "reference_values x": reference_values1,
    #     "reference_values y": reference_values2,
    #     "reference_values z": reference_values3
    # }
    resp = {
        "message": "Shaker is now running at %s." % (freqstring),
        "reference_rms": {"x": reference_values1, "y": reference_values2, "z": reference_values3}
    }
    return dumps(resp)

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
# RUN BOTTLE SCRIPT ================================================
run(host='localhost', port=8080)
