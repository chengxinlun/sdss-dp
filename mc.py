#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
import numpy as np
from code.core.dataio.dataio import get_spec
from code.core.util.parallel import para_return
from spectra_fit.py import spectra_fit


def noise_gene(flux, error):
    noise_t = [np.random.normal(flux[i], error[i], 100) for i in len(flux)]
    noise_t = np.array(noise_t)
    return np.transpose(noise_t)


def mcee(rmid, mjd, cont_init, line_init):
    try:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                           ".pkl")
        f_with_e = noise_gene(f, e)
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
