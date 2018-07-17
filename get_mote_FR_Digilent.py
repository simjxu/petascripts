import requests
import time
from dwfconstants import *
import sys
import numpy as np

# location_id = input("Enter location id:  ")
location_id = 3441
num_meas = 60

# Go to inspect element, on the machine you are interested in, and choose the something like "37"
# Use https://curl.trillworks.com/ to convert

cookies = {
    '_ga': 'GA1.2.1207267595.1529618946',
    'mp_6236728f0c61399bdb15b5a17d1fbf1c_mixpanel': '^%^7B^%^22distinct_id^%^22^%^3A^%^20^%^22assembler^%^40petasense.com^%^22^%^2C^%^22^%^24initial_referrer^%^22^%^3A^%^20^%^22https^%^3A^%^2F^%^2Fapp.petasense.com^%^2F^%^22^%^2C^%^22^%^24initial_referring_domain^%^22^%^3A^%^20^%^22app.petasense.com^%^22^%^7D',
    'session': '.eJxFz8FrwjAUx_F_ZeTsoa0KQ9hhW7Ki7L3Skil5l-JiNU0aBVtXG_F_X-dlp3f48b7wubFyf65awxb7bdNWE1bWO7a4sadvtmAkRUB5GIC_zpUVg_L5VElyZPVUhQ-fbQqT8cIo63qybpZxnUD6dcXgrpCIAXmegEeHftlDWBvwhVVBx0q-GeXVXPlVA-l4pRjILueYiFkm9RQ5zDAp6iwtPMnGoIdAnmrk4kob0SNfWeK7cRt_gooxhRd2n7Ct7uqfqtxqfbocu4cknrC2atv6dCxdNfzL-NizeYTh0CkPPb1HUSbX7vNPm-bdqI5gs2rINjVYMn_1S1udH00WP7P7LylGaGk.Dh_XWw.8x8itfiFtdhMXJLM-nmxDjVE8m4',
}

headers = {
    'Pragma': 'no-cache',
    'Origin': 'https://app.petasense.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://app.petasense.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}




# ------------------------ END INPUTS --------------------------

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

def connect_to_Digilent():
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

def acquire_RMS(device, channel, sampling_rate, nSamples):
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
    return np.sqrt(np.mean(np.square(rgpy)))

def set_freq_amp(device, channel, freq, amp):
    dwf.FDwfAnalogOutNodeEnableSet(device, channel, AnalogOutNodeCarrier, c_bool(True))
    dwf.FDwfAnalogOutNodeFunctionSet(device, channel, AnalogOutNodeCarrier, funcSine)
    dwf.FDwfAnalogOutNodeFrequencySet(device, channel, AnalogOutNodeCarrier, c_double(freq))
    dwf.FDwfAnalogOutNodeAmplitudeSet(device, channel, AnalogOutNodeCarrier, c_double(amp))
    dwf.FDwfAnalogOutConfigure(device, channel, c_bool(True))  # TURNS ON SIG GEN.
    time.sleep(1)  # Offset settling time

def shaker_table(freq):
    # SET THIS FIRST!
    oneg_reference_rms = 0.01

    amp = 0.1
    set_freq_amp(dev0, c_int(0), freq, amp)
    gvalue = acquire_RMS(dev0, c_int(0), c_double(20000), 20000)/0.01045

    while gvalue > 1.01 or gvalue < 0.99:
        gvalue = acquire_RMS(dev0, c_int(0), c_double(20000), 20000) / 0.01045
        print(gvalue)
        if gvalue > 1.01:
            print("gvalue=", gvalue, "decreasing voltage")
            if gvalue - 1.00 < 0.2:
                amp -= 0.002
            else:
                amp -= 0.05
            set_freq_amp(dev0, c_int(0), freq, amp)

        elif gvalue < 0.99:
            print("gvalue=", gvalue, "increasing voltage")
            if 1.00 - gvalue < 0.2:
                # increase voltage
                amp += 0.002
            else:
                amp += 0.05
            set_freq_amp(dev0, c_int(0), freq, amp)
        else:
            print("value achieved:", freq, amp)

def signal_off(channel):
    if channel == 0:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(0), c_bool(False))
    elif channel == 1:
        dwf.FDwfAnalogOutConfigure(dev0, c_int(1), c_bool(False))

# Connect to the shaker table
connect_to_Digilent()

request_url = 'https://api.petasense.com/webapp/vibration-data/' + str(location_id) + \
              '/broadband-trend?amp_type=acceleration&axis=z&channel_type=high_bandwidth&feature=rms'
spectrum_url = 'https://api.petasense.com/webapp/vibration-data/2132431/spectrum?amp_type=acceleration&axis=z&channel_type=low_bandwidth&measurement_location_id=2841'
broadband_info = requests.get(request_url, headers=headers, cookies=cookies)
broadband_info = broadband_info.json()

current_last_measurement = broadband_info['last_measurement_time']
print(current_last_measurement)

meas_ids = broadband_info['trend_data']['measurement_id']
last_id = str(meas_ids[-1])
print(last_id)

# frequencies = [(i+1)*100.0 for i in range(15)]
frequencies = [(i+1)*100.0 for i in range(num_meas)]


rms_values = [0.0 for i in range(num_meas)]
i = 0
for f in frequencies:
    print("running frequency:", f)
    no_newmeas = True

    # Set frequency to shaker table
    shaker_table(f)
    time.sleep(2)

    # Check the website for the last measurement time, save it
    broadband_info = requests.get(request_url, headers=headers, cookies=cookies)
    broadband_info = broadband_info.json()
    current_last_measurement = broadband_info['last_measurement_time']
    print("current last measurement:", current_last_measurement)

    while no_newmeas:
        broadband_info = requests.get(request_url, headers=headers, cookies=cookies)
        broadband_info = broadband_info.json()
        new_measurement = broadband_info['last_measurement_time']
        print("new measurement:", new_measurement)

        if new_measurement != current_last_measurement:
            print("new measurement found")
            # Check if frequency is in range
            meas_ids = broadband_info['trend_data']['measurement_id']
            last_id = str(meas_ids[-1])
            spectrum_url = 'https://api.petasense.com/webapp/vibration-data/' + last_id + \
                           '/spectrum?amp_type=acceleration&axis=z&channel_type=high_bandwidth&measurement_location_id=' + \
                           str(location_id)
            spectrum_info = requests.get(spectrum_url, headers=headers, cookies=cookies)
            spectrum_info = spectrum_info.json()
            spectrum = spectrum_info['spectrum_data']['mag']
            farray = spectrum_info['spectrum_data']['freq']
            mag_max_arg = np.argmax(spectrum)

            # Get RMS
            waveform_url = 'https://api.petasense.com/webapp/vibration-data/' + last_id + \
                           '/waveform?amp_type=acceleration&axis=z&channel_type=high_bandwidth&measurement_location_id=' + \
                           str(location_id)
            waveform_info = requests.get(waveform_url, headers=headers, cookies=cookies)
            waveform_info = waveform_info.json()
            curr_rms = waveform_info['broadband_features']['rms']
            print("current rms", curr_rms)

            if farray[mag_max_arg] >= f-15 or farray[mag_max_arg] <= f+15:
                rms_values[i] = curr_rms
                i += 1
                no_newmeas = False
            else:
                current_last_measurement = new_measurement
                time.sleep(10)
                print("woke up from 10second sleep")

        else:
            time.sleep(10)
            print("woke up from 10 second sleep")

print(rms_values)
signal_off(0)