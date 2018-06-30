import numpy as np
import csv
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def func(w, q, f0):
    num = (f0 ** 4 - f0 ** 2 * w ** 2) ** 2 + (f0 ** 3 * w / q) ** 2
    den = ((f0 ** 2 - w ** 2) ** 2 + (f0 * w / q) ** 2) ** 2

    return np.sqrt(num / den)

num_meas = 15
file = open("data/P14-IDs.txt", 'r')
device_ids = file.read().split("\n")

reader = csv.reader(open("data/acc_lsm_x_14.csv", "r"), delimiter=",")
x = list(reader)
acc_832m1_x = np.array(x).astype("float")

reader = csv.reader(open("data/acc_lsm_y_14.csv", "r"), delimiter=",")
x = list(reader)
acc_832m1_y = np.array(x).astype("float")

reader = csv.reader(open("data/acc_lsm_z_14.csv", "r"), delimiter=",")
x = list(reader)
acc_832m1_z = np.array(x).astype("float")

Q_f0 = np.matrix([[0.0 for col in range(2)] for row in range(len(device_ids))])

xdata = [100,200,300,400,500,1400,1500]
ydata = [1,1,0.99,0.99,0.98,-1, -1]

for i in range(len(device_ids)):

    ydata[6] = acc_832m1_z[i, -1]
    ydata[5] = acc_832m1_z[i, -1] - (1 - acc_832m1_z[i, -1])*0.15

    print(ydata[6])

    popt, pcov = curve_fit(
        func,
        xdata,
        ydata,
        bounds=([0.2, 1000], [0.9, 5000]),
        method='trf'
    )

    Q_f0[i, 0] = popt[0]
    Q_f0[i, 1] = popt[1]

# print(Q_f0)