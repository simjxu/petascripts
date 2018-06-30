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
def custom_waveform(freqarr, shiftarr, amplitude, simulated_sampling_rate, time_length):
    # choose some high number for simulated sampling rate, we will create 0.01 seconds worth, or whatever time_length is
    # Define the waveform for 100Hz - 1500Hz ------------------------------
    simulated_num_samples = int(simulated_sampling_rate * time_length)
    rgdSamples = (c_double * simulated_num_samples)()
    # For a 100-1500Hz section, e.g., each cycle will be time_length seconds long
    # Sample rate = frequency * number of samples
    print(len(rgdSamples))
    for t in range(simulated_num_samples):
        sumfreq = 0
        for j in range(len(freqarr)):
            sumfreq += amplitude * sin(2 * pi * freqarr[j] * t / simulated_sampling_rate + shiftarr[j])
        rgdSamples[t] = sumfreq

    # t = [i / simulated_sampling_rate for i in range(simulated_num_samples)]
    # plt.plot(t, rgdSamples)
    # plt.show()
    #
    # longersample = [0.0 for i in range(len(rgdSamples))]
    # for i in range(len(longersample)):
    #     longersample[i] = rgdSamples[i]
    # xf = np.linspace(0.0, simulated_sampling_rate / 2, len(longersample) // 2)
    # _, yf = welch(
    #     longersample,
    #     simulated_sampling_rate,
    #     nperseg=len(longersample),
    #     noverlap=0,
    #     window='flattop',
    #     scaling='spectrum'
    # )
    # yf = np.sqrt(2 * yf) * len(yf)
    # yf = yf[:len(xf)]
    # yf = 2.0 / len(longersample) * np.abs(yf)
    #
    # plt.plot(xf, yf)
    # plt.show()

    return rgdSamples
def generate_samples(device, channel, rgdSamples, time_length):
    dwf.FDwfAnalogOutNodeEnableSet(device, channel, AnalogOutNodeCarrier, c_bool(True))
    dwf.FDwfAnalogOutNodeFunctionSet(device, channel, AnalogOutNodeCarrier, funcCustom)
    dwf.FDwfAnalogOutNodeDataSet(device, channel, AnalogOutNodeCarrier, rgdSamples, c_int(len(rgdSamples)))
    dwf.FDwfAnalogOutNodeFrequencySet(device, channel, AnalogOutNodeCarrier, c_double(1 / time_length))
    dwf.FDwfAnalogOutNodeAmplitudeSet(device, channel, AnalogOutNodeCarrier, c_double(1))
    dwf.FDwfAnalogOutConfigure(device, channel, c_bool(True))  # TURNS ON SIG GEN.
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
# ------------ END acquire_samples() -------------------------------------------------------
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
    shiftarr1500 = [1.31,-0.685,0.41,0.5,0.2,0.14,0.3,-0.605,0.66,-0.91,0.015,3.24,-1.06,2.315,0.25]
    shiftarr3000 = [3.0600, 3.5100, 1.0250, -0.1510, 2.6330, 4.0420, 0.0820, -0.2070, 2.9800, 0.2200,
                    2.7100, 2.1300, 1.6100, 1.7300, 1.6600]
    shiftarr4000 = [2.7500, 2.1000, 1.0800, 1.0900, 1.7600, 3.6200, -1.7500, 0.6400, 4.0300, 0.9200]
    shiftarr5000 = [3.5900, 1.5600, 1.2000, 1.8000, 1.4600, 3.3300, -1.2000, 1.3900, 3.9500, 0.2100]
    shiftarr6000 = [3.5500, 3.3600, 1.6200, -1.1100, 1.3700, 0.7800, 1.4700, 3.5700, 0.9100, 1.1500]

    if frequency <= 1500:
        shiftarr = shiftarr1500; amp = 0.15; freqstring = "100-1500Hz"
        # freqarr = [113, 198, 295, 423, 510, 625, 710, 815, 950, 1050, 1100, 1215, 1310, 1445, 1500]
        # freqarr = [113, 198, 295]
        freqarr = [198]

    elif 1500 < frequency <= 3000:
        shiftarr = shiftarr3000; amp = 0.2; freqstring = "1600-3000Hz"
        freqarr = [100 * (i + 1) + 1500 for i in range(len(shiftarr1500))]
    elif 3000 < frequency <= 4000:
        shiftarr = shiftarr4000; amp = 0.25; freqstring = "3100-4000Hz"
        freqarr = [100 * (i + 1) + 3000 for i in range(len(shiftarr1500))]
    elif 4000 < frequency <= 5000:
        shiftarr = shiftarr5000; amp = 0.3; freqstring = "4100-5000Hz"
        freqarr = [100 * (i + 1) + 4000 for i in range(len(shiftarr1500))]
    elif 5000 < frequency <= 6000:
        shiftarr = shiftarr6000; amp = 0.25; freqstring = "5100-6000Hz"
        freqarr = [100 * (i + 1) + 5000 for i in range(len(shiftarr1500))]
    else:
        resp = {"message": "Frequency entered is not available"}
        return dumps(resp)
    # BEGIN SIGNAL GEN -----------------------------------------------
    print("Generating signal...")
    rgdSamples = custom_waveform(freqarr, shiftarr, amplitude=amp, simulated_sampling_rate=10000, time_length=1)
    generate_samples(dev0, c_int(0), rgdSamples, time_length=1)
    # BEGIN ACQUISITION ----------------------------------------------
    print("Acquiring data...")
    dwf.FDwfAnalogInConfigure(dev0, c_bool(True), c_bool(True))  # Configures devices to be on
    dwf.FDwfAnalogInConfigure(dev1, c_bool(True), c_bool(True))
    time.sleep(1)  # Wait for signal to settle...
    # Acquire samples, Device 0 Channel 0
    dev0chan0_values = acquire_samples(dev0, c_int(0), sampling_rate, nSamples)
    # Acquire samples, Device 0 Channel 1
    dev0chan1_values = acquire_samples(dev0, c_int(1), sampling_rate, nSamples)
    # Acquire samples, Device 1 Channel 0
    dev1chan0_values = acquire_samples(dev1, c_int(0), sampling_rate, nSamples)

    # GET REFERENCE VAL ----------------------------------------------
    print("Getting reference values...")
    reference_values1 = get_reference_values(dev0chan0_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=nSamples, axis=1)
    reference_values2 = get_reference_values(dev0chan1_values, freqarr, sampling_rate=sampling_rate.value,
                                             num_samples=nSamples, axis=2)
    reference_values3 = get_reference_values(dev1chan0_values, freqarr, sampling_rate=sampling_rate.value,
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
@route('/signal/<frequency:int>')
def set_filter_signal(frequency):
    amp = 0.25          # Need to get 0.5V p2p
    dwf.FDwfAnalogOutNodeEnableSet(dev0, c_int(1), AnalogOutNodeCarrier, c_bool(True))
    dwf.FDwfAnalogOutNodeFunctionSet(dev0, c_int(1), AnalogOutNodeCarrier, funcSine)
    dwf.FDwfAnalogOutNodeFrequencySet(dev0, c_int(1), AnalogOutNodeCarrier, c_double(frequency))
    dwf.FDwfAnalogOutNodeAmplitudeSet(dev0, c_int(1), AnalogOutNodeCarrier, c_double(amp))
    dwf.FDwfAnalogOutConfigure(dev0, c_int(1), c_bool(True))  # TURNS ON SIG GEN.
    time.sleep(1)       # Offset settling time
    resp = {
        "message": "Set to %s Frequency and  %.3f volts Amplitude" % (frequency, amp)
    }
    return dumps(resp)
# Turn off the source output on the signal generator
@route('/signal_off/<channel:int>')
def signal_off(channel):
    if channel == 0:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(0), c_bool(False))
    elif channel == 1:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(1), c_bool(False))
    resp = {
        "message": "Signal generator turned off for channel %s" % (channel)
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
    if str(serialnum.value) == "b'SN:210321A67C47'":
        dwf.FDwfDeviceOpen(c_int(i), byref(dev0))
    if str(serialnum.value) == "b'SN:210321A678D7'":
        dwf.FDwfDeviceOpen(c_int(i), byref(dev1))
print("------------------------------")
# Device 0: outputting signal from Device
if dev0.value == hdwfNone.value:
    print("failed to open 1st device")
    quit()
elif dev1.value == hdwfNone.value:
    print("failed to open 2nd device")
    quit()
else:
    print("Device Connected! Waiting for signal...")
# RUN BOTTLE SCRIPT ================================================
run(host='localhost', port=8080)