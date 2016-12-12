#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pickle
import logging
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location
from code.core.util.io import create_directory
from code.core.dataio.specio import get_spec
from code.core.util.parallel import para_return
from spectra_fit import spectra_fit


def noise_gene(flux, error):
    noise_t = [np.random.normal(flux[i], error[i], 100)
               for i in xrange(len(flux))]
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
        logger.error(str(rmid) + str(mjd) + ": fitting result not found")
        return []
    # Noise generation
    f_with_e = noise_gene(f, e)
    # Wrapping for parallel computation
    args = [(rmid, mjd, True, cont_init, line_init, w, each, e,)
            for each in f_with_e]
    # Parallel computation
    res = para_return(spectra_fit, args, num_thread=100)
    # Filtering out empty(failed) fitting
    res = [each for each in res if each != []]
    # Exception of insufficient data
    if len(res) < 80:
        logger = logging.getLogger("root")
        logger.error(str(rmid) + " " + str(mjd) +
                     ": insufficient number of Monte Carlo runs")
        return []
    # Final result
    num_parameters = len(res[0])
    res_std = []
    for each in xrange(num_parameters):
        temp = res[:, each]
        res_std.append(np.std(temp))
    return res_std


if __name__ == "__main__":
    logging.config.fileConfig("mc_log.conf")
    '''
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
            res_std = mcee(each, each_day)
            res_file = open(os.path.join(Location.root, res_dir,
                                         str(each_day) + ".pkl"))
            pickle.dump(res_std, res_file)
            res_file.close()
    '''
    res_std = mcee(177, 56660)
    print(res_std)
