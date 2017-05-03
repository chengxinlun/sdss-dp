#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pickle
import logging
import numpy as np
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow
from code.core.location import Location
from code.core.util.io import create_directory
from code.core.dataio.specio import get_spec
from code.core.util.parallel import para_return
from spectra_fit import spectra_fit


def noise_gene(flux, error):
    noise_t = [np.random.normal(flux[i], np.abs(error[i]), 100)
               for i in range(len(flux))]
    noise_t = np.array(noise_t)
    return np.transpose(noise_t)


def mcee(rmid, mjd):
    try:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                           ".pkl")
    except Exception:
        logger = logging.getLogger("root")
        logger.error("Error", str(rmid) + " " + str(mjd) +
                     ": spectra not found")
        return []
    # Loading fitting result
    try:
        f_data = open(os.path.join(Location.root, Location.fitting, str(rmid),
                                   str(mjd) + ".pkl"), "rb")
        res_list = pickle.load(f_data)
        cont_init = res_list[0]
        line_init = res_list[1]
        f_data.close()
    except Exception:
        logger = logging.getLogger("root")
        logger.error(str(rmid) + " " + str(mjd) + ": fitting result not found")
        return []
    # Noise generation
    f_with_e = noise_gene(f, e)
    # Wrapping for parallel computation
    args = [(rmid, mjd, cont_init, line_init, w, each, e,) for each in f_with_e]
    # Parallel computation
    res = para_return(flux_integrate, args, num_thread=100)
    print(res)
    # Filtering out empty(failed) fitting
    res = [each for each in res if each != []]
    # Exception of insufficient Monte Carlo runs
    if len(res) < 80:
        logger = logging.getLogger("root")
        logger.error(str(rmid) + " " + str(mjd) +
                     ": insufficient number of Monte Carlo runs")
        return []
    # Final result
    num_parameters = len(res[0])
    res_ave = []
    res_std = []
    for each in range(num_parameters):
        temp = [every[each] for every in res]
        res_ave.append(np.mean(temp))
        res_std.append(np.std(temp))
    print(res_ave)
    print(res_std)
    return [res_ave, res_std]


def flux_integrate(rmid, mjd, cont_init, line_init, w, f, e):
    fitting_res = spectra_fit(rmid, mjd, True, cont_init, line_init, w, f, e)
    # Fitting failure, return no result
    if len(fitting_res) == 0:
        return []
    # FeII model, data and flux
    fe_m = Fe2V(*fitting_res[0][3:])
    fe_d = fe_m(w)
    fe_f = np.trapz(fe_d, w)
    # Hbeta model, data and flux
    hb_m = Hbeta2(*fitting_res[1][0:9])
    hb_d = hb_m(w)
    hb_f = np.trapz(hb_d, w)
    # OIII model, data and flux
    o3_m = Narrow(*fitting_res[1][9:13])
    o3_d = o3_m(w)
    o3_f = np.trapz(o3_d, w)
    return [fe_f, o3_f, hb_f]


if __name__ == "__main__":
    logging.config.fileConfig("mc_log.conf")
    f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
    source_list = pickle.load(f)
    f.close()
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    for each in source_list:
        res_dir = os.path.join(Location.mc, str(each))
        create_directory(res_dir)
        for each_day in mjd_list:
            print("Begin Monte Carlo for " + str(each) + " " + str(each_day))
            try:
                res_std = mcee(each, each_day)
            except Exception:
                logger = logging.getLogger("root")
                logger.error(str(each) + " " + str(each_day) + ": unexpected.")
                continue
            res_file = open(os.path.join(Location.root, res_dir,
                                         str(each_day) + ".pkl"), "wb")
            pickle.dump(res_std, res_file)
            res_file.close()
