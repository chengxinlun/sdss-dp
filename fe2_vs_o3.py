import os
import pickle
import logging
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location


# Reading the mc result
def mc_read(rmid, mjd):
    filein_dir = os.path.join(Location.root, "result/mc", str(rmid),
                              str(mjd) + ".pkl")
    try:
        filein = open(filein_dir, "rb")
        mc_res = pickle.load(filein)
        filein.close()
    except Exception:
        logger = logging.getLogger("root")
        logger.error("Error", str(rmid) + " " + str(mjd) +
                     ": mc result not found")
        return []
    return mc_res


# Averaging the result
def aver(rmid):
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    flux = []
    error = []
    for each_day in mjd_list:
        mc_res = mc_read(rmid, each_day)
        if mc_res == []:
            continue
        else:
            flux.append(mc_res[0])
            error.append(mc_res[1])
    flux = np.array(flux)
    error = np.array(error)
    # Averaging
    # Weight of average: 1/e^2
    flux_a = []
    error_a = []
    for each in xrange(len(flux[0])):
        weight = 1.0 / (error[:, each] * error[:, each])
        flux_a.append(np.sum(flux[:, each] * weight) / np.sum(weight))
        error_a.append(np.sum(error[:, each] * weight) / np.sum(weight))
    return [np.array(flux_a), np.array(error_a)]


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
