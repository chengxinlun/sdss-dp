import os
import pickle
import logging
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location


# Read from lightcurve
def read_lc(rmid):


# Normalization, that is, dividing hbeta
def norm_f(rmid):
    try:
        flux_a, error_a = aver(rmid)
        if flux_a == [] or error_a == []:
            raise Exception("Error")
    except Exception:
        logger = logging.getLogger("root")
        logger.error("Error", str(rmid) + ": completely empty")
        return []
    # [0]: Fe2, [1]: O3, [2]:Hbeta
    flux_n = flux_a / flux_a[2]
    error_n = (flux_a * error_a[2] + error_a * flux_a[2]) / \
        (flux_a[2] * flux_a[2])
    return [flux_n, error_n]


# Fe2 vs O3 plot
fe2 = []
fe2_e = []
o3 = []
o3_e = []
s = []
# Valid source list
f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
source_list = pickle.load(f)
f.close()
for each in source_list:
    flux_n, error_n = norm_f(each)
    if flux_n == [] or error_n == []:
        continue
    fe2.append(flux_n[0])
    fe2_e.append(error_n[0])
    o3.append(flux_n[1])
    o3_e.append(error_n[1])
    s.append(each)
plt.errorbar(fe2, o3, xerr=fe2_e, yerr=o3_e, linestyle='none')
plt.xlabel("Relative FeII")
plt.ylabel("Relative OIII")
plt.show()
plt.scatter(fe2, o3)
plt.xlabel("Relative FeII")
plt.ylabel("Relative OIII")
plt.show()
