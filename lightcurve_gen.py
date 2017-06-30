# -*- coding: utf-8 -*-
import os
import pickle
import logging
import logging.config
from code.core.location import Location
from code.core.util.io import create_directory


# Reading the fit result
def fit_read(rmid, mjd):
    try:
        f_data = open(os.path.join(Location.root, Location.mc, str(rmid),
                                   str(mjd) + ".pkl"), "rb")
        res_list = pickle.load(f_data)
        cont_res = res_list[0]
        line_res = res_list[1]
        f_data.close()
    except Exception:
        err_str = str(rmid) + " " + str(mjd) + ": fitting not found"
        logger = logging.getLogger("root")
        logger.error(err_str)
        return []
    return [cont_res, line_res]


# Write list to file
def lc_write(fname, lc, lc_e, mjdr, lc_dir):
    llc_file = open(os.path.join(lc_dir, fname), 'w')
    for i in range(len(lc)):
        llc_file.write(str(mjdr[i]) + " " + str(lc[i]) + " " + str(lc_e[i]) +
                       "\n")
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
    felc_e = []
    hblc = []
    hblc_e = []
    o3lc = []
    o3lc_e = []
    clc = []
    clc_e = []
    mjd_real = []
    fail = 0
    for each_day in mjd_list:
        mc_res = fit_read(rmid, each_day)
        if mc_res == [] or mc_res[0] == [] or mc_res[1] == []:
            fail += 1
            continue
        clc.append(mc_res[0][0])
        felc.append(mc_res[0][1])
        hblc.append(mc_res[0][2])
        o3lc.append(mc_res[0][3])
        clc_e.append(mc_res[1][0])
        felc_e.append(mc_res[1][1])
        hblc_e.append(mc_res[1][2])
        o3lc_e.append(mc_res[1][3])
        mjd_real.append(each_day)
        if fail > 0.5 * len(mjd_list):
            raise Exception("too many day missing")
    # Generate lightcurve files
    lc_write("fe2.txt", felc, felc_e, mjd_real, lc_dir)
    lc_write("hbeta.txt", hblc, hblc_e, mjd_real, lc_dir)
    lc_write("o3.txt", o3lc, o3lc_e, mjd_real, lc_dir)
    lc_write("cont.txt", clc, clc_e, mjd_real, lc_dir)


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
