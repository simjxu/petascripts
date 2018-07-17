from scipy.optimize import curve_fit
import numpy as np
import math
import matplotlib.pyplot as plt


def func(w, q, f0):
    num = (f0 ** 4 - f0 ** 2 * w ** 2) ** 2 + (f0 ** 3 * w / q) ** 2
    den = ((f0 ** 2 - w ** 2) ** 2 + (f0 * w / q) ** 2) ** 2

    return np.sqrt(num / den)

# xdata = [100 * (i+1) for i in range(15)]
# ydata = [1.01,0.961,1.032,0.959,0.959,0.978,0.956,0.964,0.954,0.87,0.87,0.94,0.925,0.89,0.878]

# X axis
# xdata = [100,200,300,400,500,1400,1500]
# ydata = [1,1,1.01,1.01,1.02,0.92,0.91]

# xdata = [100,200,300,400,500,1400,1500]
# ydata = [1,1,0.99,0.99,0.98,0.92,0.9]

# # Z axis
# xdata = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
# ydata = [1,0.96,0.96,1,0.98,0.98,0.97,0.97,0.92,0.92,0.89,0.96,0.96,0.88,0.85]
xdata = [100,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
ydata = [1,0.94,0.91,0.88,0.85,0.80,0.79,0.74,0.78,0.74,0.7,0.66]



popt, pcov = curve_fit(
    func,
    xdata,
    ydata,
    bounds = ([0.2,1000], [0.9, 5000]),
    method = 'trf'
)

print(popt)

newpts = np.linspace(0, 1500, 150)
newvals = [0.0 for i in range(len(newpts))]
for i in range(len(newvals)):
    newvals[i] = func(newpts[i], popt[0], popt[1])
    # newvals[i] = func(newpts[i], 0.7, 2200)

plt.plot(xdata, ydata, 'o', color='g')
plt.plot(newpts, newvals)
plt.show()

# # With Q and f0
# Q = 0.67
# f0 = 1245.16
# newpts = np.linspace(0, 1500, 150)
# newvals = [0.0 for i in range(len(newpts))]
# for i in range(len(newvals)):
#     newvals[i] = func(newpts[i], Q, f0)
#     # newvals[i] = func(newpts[i], 0.7, 2200)
#
# plt.plot(xdata, ydata, 'o', color='g')
# plt.plot(newpts, newvals)
# plt.ylim([0.5, 1])
# plt.show()
#
