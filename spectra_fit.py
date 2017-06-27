#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import logging.config
import warnings
import pickle
import matplotlib.pyplot as plt
from lmfit import report_fit
from code.calib.splitspec import splitspec
from code.fitting.LmCF import LmCF
from code.fitting.LmHO import LmHO
from code.fitting.fitter import conggrad
from code.core.dataio.specio import get_spec
from code.core.location import Location
from code.core.util.io import create_directory
# from code.core.util.parallel import para_return


def cffit(w, f, e, initial):
    wavesplit = [[4200.0, 4300.0], [4450.0, 4750.0], [5100.0, 5500.0]]
    wf, ff, ef = splitspec(w, f, e, wavesplit)
    cf = LmCF(wf[0], ff[0], ff[-1], initp=initial)
    res = conggrad(cf, wf, ff, ef, 10000)
    report_fit(res)
    return res.params


def hofit(w, f, e, cf_res, initial):
    ws, fs, es = splitspec(w, f, e, [[4750, 5100.0]])
    ff = fs - LmCF(4200.0, 1.0, 2.0).eval(cf_res, ws)
    ho = LmHO(initp=initial)
    res = conggrad(ho, ws, ff, es, 10000)
    report_fit(res)
    return res.params


def spectra_fit(rmid, mjd, isMc=False, cont_init=None, line_init=None, w=None,
                f=None, e=None):
    if w is None and f is None and e is None:
        try:
            w, f, e = get_spec("data/calib/pt/" + str(rmid) + "-" + str(mjd) +
                               ".pkl")
            w, f, e = splitspec(w, f, e, [[4000.0, 5500.0]])
        except Exception:
            logger = logging.getLogger("root")
            logger.error(str(rmid) + " " + str(mjd) + ": spectra not found.")
            return []
    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        cont_res = cffit(w, f, e, cont_init)
        line_res = hofit(w, f, e, cont_res, line_init)
        if not isMc:
            save_fit(rmid, mjd, [cont_res, line_res], w, f)
            return []
        else:
            return [cont_res, line_res, w, f]


def save_fit(rmid, mjd, res_list, w, f):
    save_location = os.path.join(Location.fitting, str(rmid))
    create_directory(save_location)
    f = open(os.path.join(Location.root, save_location, str(mjd) + ".pkl"),
             "wb")
    pickle.dump([each.parameters for each in res_list], f)
    f.close()


'''
if __name__ == "__main__":
    logging.config.fileConfig("process_log.conf")
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    args = [(each, each_mjd, False, None, None, None, None, None)
            for each in source_list for each_mjd in mjd_list]
    res = para_return(spectra_fit, args, num_thread=100)
'''
f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
source_list = pickle.load(f)
f.close()
for each in source_list:
    cf, ho, w, f = spectra_fit(each, 56660, isMc=True)
    cff = LmCF(4000.0, 1.0, 2.0).eval(cf, w)
    hof = LmHO().eval(ho, w)
    plt.plot(w, f)
    plt.plot(w, cff + hof)
    plt.plot(w, cff)
    plt.show()
    plt.close()
