import vxi11 as vx
import numpy as np
import requests
import time
from ctypes import *


def get_new_connection():
    osc_ip = "169.254.1.5"
    try:
        osc = vx.Instrument(osc_ip)
        osc.open()
    except:
        print("unable to connect, restart oscilloscope and try again")
        return None

    return osc

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

def get_reading():
    osc.write(":STOP")
    osc.write("WAV:SOUR CHAN1")
    osc.write("WAV:MODE RAW")
    osc.write("WAV:FORM BYTE")
    osc.write("WAV:STAR 1")
    osc.write("WAV:STOP 1000")

    data = (c_byte*1000)()
    data = osc.ask(":WAV:DATA?")
    # data = osc.ask("MEASure:STATistic:ITEM? CURRENT,VRMS ")
    return data

osc = connect_osc()
data = get_reading()
for i in range(len(data)):
    print(data[i])
print(get_reading())
