#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
# from code.fitting.cont import ContSdss
from astropy.modeling import models
from code.calib.splitspec import splitspec
from code.fitting.fe2 import Fe2V
from code.fitting.fitter import lmlsq
from code.core.dataio.specio import get_spec


if __name__ == "__main__":
    w, f, e = get_spec("data/calib/pt/776-56660.pkl")
    wavesplit = [[4200.0, 4300.0], [4450.0, 4750.0], [5100.0, 5500.0]]
    wf, ff, ef = splitspec(w, f, e, wavesplit)
    fem = Fe2V(0.0, 900.0, 1.0, 0.0, 900.0, 1.0)
    cf = models.PowerLaw1D(f[0], w[0],
                           - np.log(abs(f[-1]/f[0])) / np.log(abs(w[-1]/w[0])),
                           fixed={'x_0': True}) + models.Polynomial1D(3) + fem
    print(cf.parameters)
    res = lmlsq(cf, wf, ff, ef, 100000)
    print(res.parameters)
