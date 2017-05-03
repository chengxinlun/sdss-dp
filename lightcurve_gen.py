# -*- coding: utf-8 -*-
import os
import pickle
import logging
import logging.config
import numpy as np
from code.core.location import Location
from code.core.dataio.specio import get_spec
from code.core.util.io import create_directory


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
    print(mc_res)
    return mc_res


# Processing line mc result into data for output
def llc_data(rmid, mjd):
    mc_res = mc_read(rmid, mjd)
    if mc_res == []:
        raise Exception("mc result not found")
    else:
        hbeta_f = mc_res[0][2]
        hbeta_e = mc_res[1][2]
        return str(mjd) + "    " + str(hbeta_f) + "    " + str(hbeta_e)


# Processing continuum into data for output
def clc_data(rmid, mjd):
    try:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                           ".pkl")
    except Exception:
        raise Exception("continuum not found")
    idx = (np.abs(w - 5100.0)).argmin()  # Nearnest index to wavelength 5100A
    return str(mjd) + "    " + str(f[idx]) + "    " + str(e[idx])


# Generate lightcurve files for each source
def lc_gen(rmid):
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    lc_dir = os.path.join(Location.root, "result/lightcurve", str(rmid))
    create_directory(lc_dir)
    # Check if too many days are empty
    llc = []
    clc = []
    lfail = 0
    cfail = 0
    for each_day in mjd_list:
        try:
            llc.append(llc_data(rmid, each_day))
        except Exception:
            lfail = lfail + 1
        try:
            clc.append(clc_data(rmid, each_day))
        except Exception:
            cfail = cfail + 1
        if lfail > 0.5 * len(mjd_list) or cfail > 0.5 * len(mjd_list):
            raise Exception("too many day missing")
    # Generate lightcurve files
    llc_file = open(os.path.join(lc_dir, "hbeta.txt"), 'w')
    for each in llc:
        llc_file.write(each + "\n")
    llc_file.close()
    clc_file = open(os.path.join(lc_dir, "cont.txt"), 'w')
    for each in clc:
        clc_file.write(each + "\n")
    clc_file.close()


'''
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
'''
lc_gen(798)
