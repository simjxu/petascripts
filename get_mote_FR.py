import requests
import time
import json
import numpy as np
import vxi11 as vx

#4006
location_id = input("Enter location id:  ")

# To avoid Socket timeout
def get_new_connection():
    osc_ip = "169.254.1.5"
    try:
        osc = vx.Instrument(osc_ip)
        osc.open()
    except:
        print("unable to connect, restart oscilloscope and try again")
        return None

    return osc

# Makes connection to oscilloscope
# @memoize
def connect_osc():
    osc = get_new_connection()

    if osc is None:
        return None

    # Set Language
    osc.write("SYSTEM:LANGUAGE ENGLISH")

    # Set osc variable
    # Setting the AC Coupling
    osc.write("CHANnel1:COUPling AC")

    # Setting The BandWidth limit
    osc.write(":CHANnel1:BWLimit 20M ")

    # Setting Channel Probe
    print("Setting the Channel Probe")
    osc.write("CHANNEL1:PROBe 1")
    print("Channel Probe set to 1")

    osc.write(":RUN")
    osc.write("SOURCE1:OUTPUT1:STATE OFF")
    # Make Sure that the source output is Off (Shaker-Table Safety)
    return osc

# Retrieving Vrms from the O-scope
def get_vrms(osc, channel):
    time.sleep(0.1)
    osc.write(str(channel) + ":DISPlay ON")
    osc.write("MEASure:STATistic:ITEM VRMS," + str(channel))
    vrms = osc.ask("MEASure:STATistic:ITEM? CURRENT,VRMS ")
    return vrms

def set_display_scale(osc, channel, vscale, hscale):

    v_scale = str(vscale)
    osc.write(str(channel)+":SCALE " + str(v_scale))  # v/div

    h_scale = str(hscale)
    osc.write("TIMEBASE:MAIN:SCALE " + str(h_scale))  # s/div

    time.sleep(0.001)
    osc.write(":RUN")

def signal_off():
    osc = connect_osc()
    osc.write("SOURCE1:OUTPUT1:STATE OFF")
    osc.write("SOURCE2:OUTPUT2:STATE OFF")

def shaker_table(freq):
    # Connect to the Oscilloscope
    osc = connect_osc()
    # Checks if the Oscilloscope is connected, if not returns the error

    freq_array = [100*(i+1) for i in range(15)]
    amp_i_array = [0.19, 0.21, 0.23, 0.25, 0.27, 0.3, 0.33, 0.35, 0.38, 0.4, 0.45, 0.43, 0.475, 0.5, 0.52]

    # For every single test, we are starting at 0.3V
    amp_i = amp_i_array[freq_array.index(freq)]
    osc.write("SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE " + str(amp_i))

    # Adjust window
    if freq <= 250:
        set_display_scale(osc, "CHANNEL1", 0.02, 0.01)
    elif freq <= 550:
        set_display_scale(osc, "CHANNEL1", 0.02, 0.005)
    elif freq <= 1050:
        set_display_scale(osc, "CHANNEL1", 0.02, 0.002)
    elif freq <= 1600:
        set_display_scale(osc, "CHANNEL1", 0.02, 0.001)

    # Set Signal generator frequency
    osc.write("SOURCE2:FREQUENCY:FIXED " + str(freq))
    osc.write("SOURCE2:OUTPUT2:STATE ON")

    gvalue = float(get_vrms(osc, "CHANNEL1"))/0.012

    while gvalue > 1.01 or gvalue < 0.99:
        time.sleep(1)
        gvalue = float(get_vrms(osc, "CHANNEL1"))/0.012
        if gvalue > 1.01:
            print("decreasing voltage")
            if gvalue-1.00 < 0.2:
                amp_i -= 0.005
            else:
                amp_i -= 0.01
            osc.write("SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE " + str(amp_i))

        elif gvalue < 0.99:
            print("increasing voltage")
            if 1.00 - gvalue < 0.2:
                # increase voltage
                amp_i += 0.005
            else:
                amp_i += 0.01
            osc.write("SOURCE2:VOLTAGE:LEVEL:IMMEDIATE:AMPLITUDE " + str(amp_i))
        else:
            print("value achieved:", freq, amp_i)


# Go to inspect element, on the machine you are interested in, and choose the something like "37"
# Use https://curl.trillworks.com/ to convert

cookies = {
    '_ga': 'GA1.2.354410958.1484069253',
    'session': '.eJw9z0FrgzAYxvGvMnLuwaQtDGGHQTRk7H3FopXkIp06TGxaULvOlH73pT3s-vDnB8-N1N9jN_UknsdLtyK1aUl8Iy9fJCbAkw3anc2KYQGh1tqWv-jbAfnAFMsj8BBBJdea5x5YvoBNQ1tusgq8KnKqHNBMKK9FcAp5BVcuKCQDh1bz3iif9hl_D72MskIfMyEjdCWFaudCM4BvDdhg89RiJcNeboPMtM2vqkq2yFKrbHLVAt7IfUUOzWx-uvrQNOfLaX4-oSsyddNkzqd66Jb_Z8j2Bv3HUQs1o5MUTRQhh-WzSjzYYUa_d8gez7AH29CHfpm68WkS-kruf_vwZXw.DgG_VA.7G5cdR3Ae9rk8pOnx9AqzSp3pLk',
    'mp_6236728f0c61399bdb15b5a17d1fbf1c_mixpanel': '^%^7B^%^22distinct_id^%^22^%^3A^%^20^%^22assembler^%^40petasense.com^%^22^%^2C^%^22^%^24initial_referrer^%^22^%^3A^%^20^%^22^%^24direct^%^22^%^2C^%^22^%^24initial_referring_domain^%^22^%^3A^%^20^%^22^%^24direct^%^22^%^7D',
}

headers = {
    'Pragma': 'no-cache',
    'Origin': 'https://app.petasense.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://app.petasense.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}

request_url = 'https://api.petasense.com/webapp/vibration-data/' + str(location_id) + \
              '/broadband-trend?amp_type=acceleration&axis=z&channel_type=low_bandwidth&feature=rms'
spectrum_url = 'https://api.petasense.com/webapp/vibration-data/2132431/spectrum?amp_type=acceleration&axis=z&channel_type=low_bandwidth&measurement_location_id=2841'
broadband_info = requests.get(request_url, headers=headers, cookies=cookies)
broadband_info = broadband_info.json()

current_last_measurement = broadband_info['last_measurement_time']
print(current_last_measurement)

meas_ids = broadband_info['trend_data']['measurement_id']
last_id = str(meas_ids[-1])
print(last_id)

frequencies = [(i+1)*100.0 for i in range(15)]
rms_values = [0.0 for i in range(15)]
i = 0
for f in frequencies:
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
                           '/spectrum?amp_type=acceleration&axis=z&channel_type=low_bandwidth&measurement_location_id=' + \
                           str(location_id)
            spectrum_info = requests.get(spectrum_url, headers=headers, cookies=cookies)
            spectrum_info = spectrum_info.json()
            spectrum = spectrum_info['spectrum_data']['mag']
            farray = spectrum_info['spectrum_data']['freq']
            mag_max_arg = np.argmax(spectrum)

            # Get RMS
            waveform_url = 'https://api.petasense.com/webapp/vibration-data/' + last_id + \
                           '/waveform?amp_type=acceleration&axis=z&channel_type=low_bandwidth&measurement_location_id=' + \
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

print("RMS values:", rms_values)
signal_off()

a = input("Press Enter to end")
print(a)
