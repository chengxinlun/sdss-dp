#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import logging.config
import warnings
import pickle
import numpy as np
from code.fitting.cont import ContSdss
from code.calib.splitspec import splitspec
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow
from code.fitting.fitter import lmlsq
from code.core.dataio.specio import get_spec
from code.core.location import Location
from code.core.util.io import create_directory
from code.core.util.parallel import para_return


def cffit(w, f, e, initial):
    wavesplit = [[4200.0, 4300.0], [4450.0, 4750.0], [5100.0, 5500.0]]
    wf, ff, ef = splitspec(w, f, e, wavesplit)
    # Set initial parameters if do not exist
    if initial is None:
        initial = [0.0, 900.0, 1.0, 0.0, 1200.0, 1.0, ff[0], wf[0],
                   - np.log(abs(f[-1]/f[0])) / np.log(abs(w[-1]/w[0]))]
    fem = Fe2V(*initial[0:6])
    cf = ContSdss(*initial[6:], fixed={'x_0': True}) + fem
    res = lmlsq(cf, wf, ff, ef, 100000)
    return res


def hofit(w, f, e, cf, initial):
    ff = f - cf(w)
    if initial is None:
        initial = [10.0, 0.0, 500.0, 40.0, 0.0, 1800.0, 40.0, 0.0, 1800.0,
                   20.0, 0.0, 500.0, 5008.22, 20.0, 0.0, 500.0, 4960.36,
                   10.0, 0.0, 1500.0, 4102.73, 20.0, 0.0, 1500.0, 4346.42]
    hbeta = Hbeta2(*initial[0:9],
                   bounds={'n_a': [0.0, 50.0], 'n_s': [-1000.0, 1000.0],
                           'n_w': [0.0, 1200.0], 'w1_a': [0.0, 50.0],
                           'w1_s': [-1000.0, 1000.0], 'w1_w': [1200.0, 20000.0],
                           'w2_a': [0.0, 50.0], 'w2_s': [-1000.0, 1000.0],
                           'w2_w': [1200.0, 20000.0]})
    o3 = Narrow(*initial[9:13], fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [0.0, 1200.0]}) + \
        Narrow(*initial[13:17], fixed={'c': True}, bounds={
            'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [0.0, 1200.0]})
    hdelta = Narrow(*initial[17:21], fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [1200.0, 20000.0]})
    hgamma = Narrow(*initial[21:], fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [1200.0, 20000.0]})
    all_lines = hbeta + o3 + hdelta + hgamma
    res = lmlsq(all_lines, w, ff, e, 100000)
    return res


def spectra_fit(rmid, mjd, isMc, cont_init, line_init, w, f, e):
    # try:
    if w is None and f is None and e is None:
        w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                               ".pkl")
        # with warnings.catch_warnings():
            # warnings.filterwarnings('error')
    cont_res = cffit(w, f, e, cont_init)
    line_res = hofit(w, f, e, cont_res, line_init)
    if not isMc:
        save_fit(rmid, mjd, [cont_res, line_res], w, f)
        return []
    else:
        return [cont_res.parameters, line_res.parameters]
    # except Exception as e:
        # logger = logging.getLogger("root")
        # logger.error("Error", exc_info=sys.exc_info())
        # sys.exc_clear()
    #     print(e.message)
    #     print(sys.exc_info())
    #     return []


def save_fit(rmid, mjd, res_list, w, f):
    save_location = os.path.join(Location.fitting, str(rmid))
    create_directory(save_location)
    f = open(os.path.join(Location.root, save_location, str(mjd) + ".pkl"),
             "wb")
    pickle.dump([each.parameters for each in res_list], f)
    f.close()


if __name__ == "__main__":
    '''
    logging.config.fileConfig("process_log.conf")
    f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
    source_list = pickle.load(f)
    f.close()
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    args = [(each, each_mjd, False, None, None, None, None, None)
            for each in source_list for each_mjd in mjd_list]
    res = para_return(spectra_fit, args, num_thread=100)
    '''
    res = spectra_fit(175, 56660, True, None, None, None, None, None)
    print(res)
