import numpy as np
import matplotlib.pyplot as plt

# Q = 0.7
# f0 = 1700

def func(w, q, f0):
    num = (f0 ** 4 - f0 ** 2 * w ** 2) ** 2 + (f0 ** 3 * w / q) ** 2
    den = ((f0 ** 2 - w ** 2) ** 2 + (f0 * w / q) ** 2) ** 2

    return np.sqrt(num / den)

Q = 0.7
f0 = 1700

freqarr = [100.0*(i+1) for i in range(15)]
curve = [0.0 for i in range(15)]
curve2 = [0.0 for i in range(15)]

idx = 0
for f in freqarr:
    curve[idx] = np.sqrt(  pow( pow( pow(f0, 2)-pow(f, 2), 2)+pow((f0*f/Q), 2) , 2)  /
                          ( pow(pow(f0, 4)-pow(f0, 2)*pow(f, 2), 2) + pow(pow(f0, 3)*f/Q, 2) )   )

    curve2[idx] = func(f, Q, f0)
    idx += 1

plt.plot(freqarr, curve)
plt.show()

plt.plot(freqarr, curve2)
plt.show()