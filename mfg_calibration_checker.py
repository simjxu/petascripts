import numpy as np
import matplotlib.pyplot as plt
import csv
import sklearn
from sklearn.neighbors import LocalOutlierFactor

#
# def normalize(cal_array):
#     return 0
#
# def check_calibration(mote_model, axis, MEMS_array, ANLG_array=None):
#     if mote_model == 'VM1':
#         if ANLG_array != None:
#             print("VM1 should not have analog values")
#         else:
#             # Check range of values before normalizing
#
#             # Normalize
#             norm_array = normalize(MEMS_array)
#
#             # Run LoF anomaly detection
#
#             # Check variance
#
#
# check_calibration('VM1', [1,2,3], [1,2,3,4])



num_meas = 60
file = open("data/P14-VM2.txt", 'r')
device_ids = file.read().split("\n")

reader = csv.reader(open("data/acc_832_z_14.csv", "r"), delimiter=",")
x = list(reader)
acc__z = np.array(x).astype("float")

dev__z = np.zeros(acc__z.shape)

plt.plot(acc__z)
plt.show()

# normalize
for i in range(len(device_ids)):
    avg = np.average(acc__z[i,0:10])
    acc__z[i, :] = acc__z[i, :]/avg
    # plt.plot(acc__z[i, :])

    if i != 0:
        dev__z[i, :] = acc__z[i, :]-acc__z[i-1, :]
        plt.plot(dev__z[i, :])

plt.show()



# Separate out the good from bad
X = np.copy(dev__z)
# np.delete(X, [6, 17, 21, 23, 30, 31, 48], axis=0)


LOF = LocalOutlierFactor.LocalOutlierFactor
clf = LOF(n_neighbors=20)
y_pred = clf.fit_predict(X)
dec_func = clf.decision_function(X)
print(dec_func.shape)
for i in range(len(device_ids)):
    print(device_ids[i], ':', dec_func[i], ':', y_pred[i])



# Check to make sure first frequency values (100-900Hz) in range


# Check variance of the first frequency values (100-900Hz)


#