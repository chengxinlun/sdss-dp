#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import pickle
import logging
import numpy as np
from code.core.location import Location
from code.core.dataio.dataio import get_spec
from code.core.util.parallel import para_return
from spectra_fit.py import spectra_fit


def noise_gene(flux, error):
    noise_t = [np.random.normal(flux[i], error[i], 100) for i in len(flux)]
    noise_t = np.array(noise_t)
    return np.transpose(noise_t)


def mcee(rmid, mjd):
    try:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                           ".pkl")
        # Loading fitting result
        f_data = open(os.path.join(Location.root, Location.fitting, str(rmid),
                                   str(mjd) + ".pkl"), "rb")
        res_list = pickle.load(f_data)
        cont_init = res_list[0:9]
        line_init = res_list[9:]
        f_data.close()
        # Noise generation
        f_with_e = noise_gene(f, e)
        # Wrapping for parallel computation
        args = [(rmid, mjd, True, cont_init, line_init, w, each, e,)
                for each in f_with_e]
        res = para_return(spectra_fit, args, num_thread=100)
        res = [each for each in res if each != []]
        num_parameters = len(res[0])
        res_std = []
        for each in xrange(num_parameters):
            temp = res[:, each]
            res_std.append(np.std(temp))
        return res_std
    except Exception as e:
        logger = logging.getLogger("root")
        logger.error("Error", exc_info=sys.exc_info())
        sys.exc_clear()
        return []


if __name__ == "__main__":
    logging.config.fileConfig("process_log.conf")
    f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
    source_list = pickle.load(f)
    f.close()
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
