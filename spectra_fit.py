#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from code.fitting.cont import ContSdss
from code.calib.splitspec import splitspec
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow
from code.fitting.fitter import lmlsq
from code.core.dataio.specio import get_spec
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def cffit(w, f, e):
    wavesplit = [[4200.0, 4300.0], [4450.0, 4750.0], [5100.0, 5500.0]]
    wf, ff, ef = splitspec(w, f, e, wavesplit)
    fem = Fe2V(0.0, 900.0, 1.0, 0.0, 900.0, 1.0)
    cf = ContSdss(ff[0], wf[0],
                  - np.log(abs(f[-1]/f[0])) / np.log(abs(w[-1]/w[0])), 0.0, 0.0,
                  0.0, 0.0, fixed={'x_0': True}) + fem
    res = lmlsq(cf, wf, ff, ef, 100000)
    return res.parameters


def hofit(w, f, e, cfres):
    cf = ContSdss(*cfres[:7]) + Fe2V(*cfres[6:-1])
    ff = f - cf(w)
    hbeta = Hbeta2(10.0, 0.0, 500.0, 40.0, 0.0, 1800.0, 40.0, 0.0, 1800.0,
                   bounds={'n_a': [0.0, 50.0], 'n_s': [-1000.0, 1000.0],
                           'n_w': [0.0, 1200.0], 'w1_a': [0.0, 50.0],
                           'w1_s': [-1000.0, 1000.0], 'w1_w': [1200.0, 20000.0],
                           'w2_a': [0.0, 50.0], 'w2_s': [-1000.0, 1000.0],
                           'w2_w': [1200.0, 20000.0]})
    o3 = Narrow(20.0, 0.0, 500.0, 5008.22, fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [0.0, 1200.0]}) + \
        Narrow(20.0, 0.0, 500.0, 4960.36, fixed={'c': True}, bounds={
            'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [0.0, 1200.0]})
    hdelta = Narrow(10.0, 0.0, 1500.0, 4102.73, fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [1200.0, 20000.0]})
    hgamma = Narrow(20.0, 0.0, 500.0, 4346.42, fixed={'c': True}, bounds={
        'a': [0.0, 50.0], 's': [-1000.0, 1000.0], 'w': [1200.0, 20000.0]})
    all_lines = hbeta + o3 + hdelta + hgamma
    res = lmlsq(all_lines, w, ff, e, 100000)
    return res.parameters


if __name__ == "__main__":
    w, f, e = get_spec("data/calib/pt/782-56660.pkl")
    cont_res = cffit(w, f, e)
    line_res = hofit(w, f, e, cont_res)
    print(cont_res.parameters)
    print(line_res.parameters)
    plt.plot(w, f)
    plt.plot(w, cont_res(w))
    plt.plot(w, line_res(w))
    plt.savefig("782-56660.png")
