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
    error = fd[:, 2]
    return [mjd_list, flux, error]


# Filter out invalid result
def filt(mjd_list, flux, error):
    n0i = np.nonzero(flux)
    norm_mjdl = mjd_list[n0i]
    norm_flux = flux[n0i]
    norm_error = error[n0i]
    if len(norm_flux) < 0.5 * len(mjd_list):
        return [[], [], []]
    else:
        return [norm_mjdl, norm_flux, norm_error]


# Intersection
def inter(mjdl_list, fl_list, err_list):
    mjd_list = mjdl_list[0]
    for each in mjdl_list:
        mjd_list = np.intersect1d(mjd_list, each)
    flux = []
    error = []
    for each in range(len(mjdl_list)):
        inter_i = np.nonzero(np.in1d(mjdl_list[each], mjd_list))
        flux.append(fl_list[inter_i])
        error.append(err_list[inter_i])
    flux = np.array(flux)
    error = np.array(error)
    return [mjd_list, flux, error]


# Get hb, o3
def ave(rmid):
    hbl = filt(*read_lc(rmid, "hbeta"))
    o3l = filt(*read_lc(rmid, "o3"))
    fel = filt(*read_lc(rmid, "fe2"))
    a_hb = np.mean(hbl[1])
    e_hb = np.mean(hbl[2])
    a_o3 = np.mean(o3l[1])
    e_o3 = np.mean(o3l[2])
    a_fe = np.mean(fel[1])
    e_fe = np.mean(fel[2])
    r_o3 = a_o3 / a_hb
    r_fe = a_fe / a_hb
    r_o3_e = (a_o3 * e_hb + e_o3 * a_hb) / (a_hb * a_hb)
    r_fe_e = (a_fe * e_hb + e_fe * a_hb) / (a_hb * a_hb)
    return [r_o3, r_fe, r_o3_e, r_fe_e]


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
    plt.errorbar(data_list[:, 0], data_list[:, 1], xerr=data_list[:, 2],
                 yerr=data_list[:, 3], linestyle='none', color='blue', fmt='o')
    plt.xlim([0.0, 2.5])
    plt.ylim([0.0, 25.0])
    plt.xlabel("Relative OIII")
    plt.ylabel("Relative FeII")
    plt.show()
