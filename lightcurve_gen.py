# -*- coding: utf-8 -*-
import os
import pickle
import logging
import logging.config
import numpy as np
from code.core.location import Location
from code.core.dataio.specio import get_spec
from code.core.util.io import create_directory
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow


# Reading the fit result
def fit_read(rmid, mjd):
    try:
        f_data = open(os.path.join(Location.root, Location.fitting, str(rmid),
                                   str(mjd) + ".pkl"), "rb")
        res_list = pickle.load(f_data)
        cont_res = res_list[0]
        line_res = res_list[1]
        f_data.close()
    except Exception:
        err_str = str(rmid) + " " + str(mjd) + ": fitting not found"
        logger = logging.getLogger("root")
        logger.error(err_str)
        print(err_str)
        return []
    return [cont_res, line_res]


# Integration
def intg(cont_res, line_res, wmin, wmax):
    x = np.arange(wmin, wmax, 0.1)
    # FeII
    fe_m = Fe2V(*cont_res[3:])
    fe_d = fe_m(x)
    fe_f = np.trapz(fe_d, x)
    # Hbeta
    hb_m = Hbeta2(*line_res[0:9])
    hb_d = hb_m(x)
    hb_f = np.trapz(hb_d, x)
    # OIII model, data and flux
    o3_m = Narrow(*line_res[9:13])
    o3_d = o3_m(x)
    o3_f = np.trapz(o3_d, x)
    return [fe_f, hb_f, o3_f]


# Processing line mc result into data for output
def llc_data(rmid, mjd):
    res = fit_read(rmid, mjd)
    if res == []:
        return []
    else:
        fef, hbf, o3f = intg(res[0], res[1], 4000.0, 5500.0)
        return [str(mjd) + "    " + str(fef), str(mjd) + "    " + str(hbf),
                str(mjd) + "    " + str(o3f)]


# Processing continuum into data for output
def clc_data(rmid, mjd):
    try:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                           ".pkl")
    except Exception:
        raise Exception("continuum not found")
    idx = (np.abs(w - 5100.0)).argmin()  # Nearnest index to wavelength 5100A
    return str(mjd) + "    " + str(f[idx]) + "    " + str(e[idx])


# Write list to file
def lc_write(fname, lc, lc_dir):
    llc_file = open(os.path.join(lc_dir, fname), 'w')
    for each in lc:
        llc_file.write(each + "\n")
    llc_file.close()


# Generate lightcurve files for each source
def lc_gen(rmid):
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    lc_dir = os.path.join(Location.root, "result/lightcurve", str(rmid))
    create_directory(lc_dir)
    # Check if too many days are empty
    felc = []
    hblc = []
    o3lc = []
    clc = []
    lfail = 0
    cfail = 0
    for each_day in mjd_list:
        try:
            allc = llc_data(rmid, each_day)
            felc.append(allc[0])
            hblc.append(allc[1])
            o3lc.append(allc[2])
        except Exception:
            lfail = lfail + 1
        try:
            clc.append(clc_data(rmid, each_day))
        except Exception:
            cfail = cfail + 1
        if lfail > 0.5 * len(mjd_list) or cfail > 0.5 * len(mjd_list):
            raise Exception("too many day missing")
    # Generate lightcurve files
    lc_write("fe2.txt", felc, lc_dir)
    lc_write("hbeta.txt", hblc, lc_dir)
    lc_write("o3.txt", o3lc, lc_dir)


# Generate all lightcurve file
logging.config.fileConfig("lc_log.conf")
# Valid source list
f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
source_list = pickle.load(f)
f.close()
for each in source_list:
    try:
        lc_gen(each)
    except Exception:
        logger = logging.getLogger("root")
        logger.error("Error", str(each) + ": lightcurve generation failure")
    print(str(each) + " lc generation finished")
