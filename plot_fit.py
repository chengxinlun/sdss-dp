#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pickle
import os
import matplotlib.pyplot as plt
from code.core.util.io import create_directory
from code.calib.splitspec import splitspec
from code.fitting.cont import ContSdss
from code.fitting.fe2 import Fe2V
from code.fitting.hbeta import Hbeta2
from code.fitting.narrow import Narrow
from code.core.location import Location
from code.core.dataio.specio import get_spec


def plot_fit(rmid, mjd, num_err):
    try:
        # Loading original data
        ff_path = "data/calib/pt/" + str(rmid) + "-" + str(mjd) + ".pkl"
        w, f, e = get_spec(ff_path)
        w, f, e = splitspec(w, f, e, [[4000.0, 5500.0]])
        # Loading fitting result
        f_data = open(os.path.join(Location.root, Location.fitting, str(rmid),
                                   str(mjd) + ".pkl"), "rb")
        res_list = pickle.load(f_data)
        cont_init = res_list[0]
        line_init = res_list[1]
        # Construct models from fitting result
        fe_param = cont_init[3:]
        fe = Fe2V(*fe_param)
        cont = ContSdss(*cont_init[0:3])
        line = Hbeta2(*line_init[0:9]) + Narrow(*line_init[9:13]) + \
            Narrow(*line_init[13:17]) + Narrow(*line_init[17:21]) + \
            Narrow(*line_init[21:])
        # Plotting fitting result
        plt.plot(w, line(w))
        plt.plot(w, cont(w))
        plt.plot(w, fe(w))
        plt.plot(w, line(w) + cont(w) + fe(w))
    except Exception as e:
        print(str(e))
    # Saving plotting
    plt.plot(w, f)
    fig_file = os.path.join(Location.fitting_plot, str(rmid))
    create_directory(fig_file)
    fig_file = os.path.join(Location.root, fig_file, str(mjd) + ".png")
    plt.savefig(fig_file, format="png")
    plt.close()
    return num_err


if __name__ == "__main__":
    '''
    mjd_list = [56660, 56664, 56669, 56683, 56686, 56697, 56713, 56715, 56717,
                56720, 56722, 56726, 56739, 56745, 56747, 56749, 56751, 56755,
                56768, 56772, 56780, 56782, 56783, 56795, 56799, 56804, 56808,
                56813, 56825, 56829, 56833, 56837]
    f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
    rmid_list = pickle.load(f)
    f.close()
    for each_source in rmid_list:
        num_err = []
        for each_day in mjd_list:
            try:
                num_err = plot_fit(each_source, each_day, num_err)
            except Exception:
                num_err.append(each_day)
        print(str(each_source) + ": " + str(len(num_err)))
        print(num_err)
    '''
    plot_fit(320, 56660, [])
