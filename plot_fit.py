#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import os
import matplotlib.pyplot as plt
from code.fitting.cont import ContSdss
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow
from code.core.location import Location
from code.core.dataio.specio import get_spec


def plot_fit(rmid, mjd):
    # Loading original data
    ff_path = "data/calib/pt/" + str(rmid) + "-" + str(mjd) + ".pkl"
    w, f, e = get_spec(ff_path)
    # Plotting original data
    plt.plot(w, f)
    # Loading fitting result
    f_data = open(os.path.join(Location.root, Location.fitting, str(rmid),
                               str(mjd) + ".pkl"), "rb")
    res_list = pickle.load(f_data)
    cont_init = res_list[0:9]
    line_init = res_list[9:]
    # Construct models from fitting result
    cont = Fe2V(*cont_init[0:6]) + ContSdss(*cont_init[6:])
    line = Hbeta2(*line_init[0:9]) + Narrow(*line_init[9:13]) + \
        Narrow(*line_init[13:17]) + Narrow(*line_init[17:21]) + \
        Narrow(*line_init[21:])
    # Plotting fitting result
    plt.plot(w, cont(w))
    plt.plot(w, line(w) + cont(w))
    # Saving plotting
    fig_file = os.path.join(Location.root, Location.fitting_plot, str(rmid))
    plt.savefig(fig_file, format="png")
    plt.close()
