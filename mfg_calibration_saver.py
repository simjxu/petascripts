import os
import requests
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# Go to inspect element, on the machine you are interested in, and choose the something like "37"
# Use https://curl.trillworks.com/ to convert

cookies = {
    '_ga': 'GA1.2.1207267595.1529618946',
    'mp_6236728f0c61399bdb15b5a17d1fbf1c_mixpanel': '^%^7B^%^22distinct_id^%^22^%^3A^%^20^%^22assembler^%^40petasense.com^%^22^%^2C^%^22^%^24initial_referrer^%^22^%^3A^%^20^%^22https^%^3A^%^2F^%^2Fapp.petasense.com^%^2F^%^22^%^2C^%^22^%^24initial_referring_domain^%^22^%^3A^%^20^%^22app.petasense.com^%^22^%^7D',
    'session': '.eJw9z0FrgzAYxvGvMnLuwdoKo7DTUmVl7ytKNOS9iLN2JjEtVDsxpd99roddH3h-8L-z6nRth47tTnU_tCtW6SPb3dnLF9uxVBwN8bgjXnji1qMsLXI7E8-2YGwI4cGBP1hKqAe-n8FDoJaNeDMr8x2gzzvwuU4TNaEre-LoUkmOXKmVgQ0kpUNvIzJoUXQ9JFlIorNo9qFyyiuRBRBma-RHRzKbwGczOAhQLl9vt5R8bEjYCUN4Y48Vq5tR_7RV3TSX23l8lqxXbGiHQV_OlW3n_zKQsQFXRGBgJHHQ-B4EYGL7KRdRFiNKNZFoInQqIpm7P_02tNenydav7PELQ0Rn5A.DhVflQ.E_OBfeEy4ZGjpNn5vklkIiIRvfE',
}

headers = {
    'Pragma': 'no-cache',
    'Origin': 'https://mfg.petasense.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://mfg.petasense.com/',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache',
}

# Get the list of device ids
file = open("data/P14-VM2.txt", 'r')
device_ids = file.read().split("\n")
num_ids = len(device_ids)
# num_meas = 15
num_meas = 60
acc_x = np.zeros((num_ids, num_meas))
acc_y = np.zeros((num_ids, num_meas))
acc_z = np.zeros((num_ids, num_meas))

for i in range(num_ids):
    request_url = 'https://api.petasense.com/mfgapp/calibration/report?device_id=' + str(device_ids[i])
    calibration_info = requests.get(request_url, headers=headers, cookies=cookies)
    calibration_info = calibration_info.json()

    for j in range(num_meas):
        # acc_x[i, j] = calibration_info['data_lsm6ds3']['rms']['x'][j]
        # acc_y[i, j] = calibration_info['data_lsm6ds3']['rms']['y'][j]
        # acc_z[i, j] = calibration_info['data_lsm6ds3']['rms']['z'][j]
        try:
            acc_x[i, j] = calibration_info['data_832m1']['rms']['x'][j]
        except:
            print(device_ids[i])
        acc_y[i, j] = calibration_info['data_832m1']['rms']['y'][j]
        acc_z[i, j] = calibration_info['data_832m1']['rms']['z'][j]

    print(i, "files complete")

# np.savetxt('data/acc_lsm_x_14.csv', acc_x, fmt='%.18e', delimiter=',')
# np.savetxt('data/acc_lsm_y_14.csv', acc_y, fmt='%.18e', delimiter=',')
# np.savetxt('data/acc_lsm_z_14.csv', acc_z, fmt='%.18e', delimiter=',')

np.savetxt('data/acc_832_x_14.csv', acc_x, fmt='%.18e', delimiter=',')
np.savetxt('data/acc_832_y_14.csv', acc_y, fmt='%.18e', delimiter=',')
np.savetxt('data/acc_832_z_14.csv', acc_z, fmt='%.18e', delimiter=',')