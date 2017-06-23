import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location


# Read from lightcurve
def read_lc(rmid, line):
    fd = np.loadtxt(os.path.join(Location.root, Location.lightcurve, str(rmid),
                                 line + ".txt"))
    mjd_list = fd[:, 0]
    flux = fd[:, 1]
    return [mjd_list, flux]


# Filter out invalid result
def filt(mjd_list, flux):
    n0i = np.nonzero(flux)
    norm_mjdl = mjd_list[n0i]
    norm_flux = flux[n0i]
    if len(norm_flux) < 0.5 * len(mjd_list):
        return [[], []]
    else:
        return [norm_mjdl, norm_flux]


# Intersection
def inter(mjdl_list, fl_list):
    mjd_list = mjdl_list[0]
    for each in mjdl_list:
        mjd_list = np.intersect1d(mjd_list, each)
    flux = []
    for each in range(len(mjdl_list)):
        inter_i = np.nonzero(np.in1d(mjdl_list[each], mjd_list))
        flux.append(fl_list[inter_i])
    flux = np.array(flux)
    return [mjd_list, flux]


# Get hb, o3
def ave(rmid):
    hbl = filt(*read_lc(rmid, "hbeta"))
    o3l = filt(*read_lc(rmid, "o3"))
    fel = filt(*read_lc(rmid, "fe2"))
    a_hb = np.mean(hbl[1])
    a_o3 = np.mean(o3l[1])
    a_fe = np.mean(fel[1])
    r_o3 = a_o3 / a_hb
    r_fe = a_fe / a_hb
    return [r_o3, r_fe]


if __name__ == "__main__":
    f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
    source_list = pickle.load(f)
    f.close()
    data_list = []
    for each in source_list:
        try:
            temp = ave(each)
            print(temp)
            data_list.append(temp)
        except Exception:
            continue
    data_list = np.array(data_list)
    plt.scatter(data_list[:, 0], data_list[:, 1])
    plt.xlim([0.0, 2.5])
    plt.ylim([0.0, 25.0])
    plt.xlabel("Relative OIII")
    plt.ylabel("Relative FeII")
    plt.show()
