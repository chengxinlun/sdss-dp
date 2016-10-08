#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
# from code.fitting.cont import ContSdss
from astropy.modeling import models
from code.fitting.fe2 import Fe2V
from code.core.dataio.specio import get_spec


if __name__ == "__main__":
    w, f, e = get_spec("data/calib/pt/776-56660.pkl")
    fem = Fe2V(9.11188866e+01, 1.47695698e+04, 2.24485311e+00, 1.34039084e+01,
               -1.61586601e+02, -1.28818455e+00, bounds={"l1_i_r": [0.0, 50.0],
                                                         "n3_i_r": [0.0, 50.0]})
    cf = models.PowerLaw1D(1.34758852e+01, 4.20046037e+03, 7.96224578e-01) + fem
    ff = cf(w)
    plt.errorbar(w, f, yerr=e)
    plt.plot(w, ff)
    plt.show()
