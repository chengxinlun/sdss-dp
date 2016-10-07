#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from code.fitting.cont import ContSdss
from code.fitting.fe2 import Fe2V
from code.fitting.fitter import lmlsq
from code.core.dataio.specio import get_spec


w, f, e = get_spec("data/calib/pt/776-56660.pkl")
contm = ContSdss(f[0], w[0],
                 - np.log(abs(f[-1]/f[0])) / np.log(abs(w[-1]/w[0])), 0.0, 0.0,
                 0.0, 0.0)
print(contm)
fem = Fe2V(0.0, 900.0, 1.0, 0.0, 900.0, 1.0)
cf = contm + fem
cf[0].x_0.fixed = True
print(cf)
print(cf[0].x_0.fixed)
res = lmlsq(cf, w, f, e, 100000)
print(res)
