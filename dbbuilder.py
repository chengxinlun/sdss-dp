#!/usr/bin/env python
# -*- coding: utf-8 -*-
import code.core.dataio.specio as s
import code.calib.ptcalib as ec
import code.visual.plotspec as p
from code.calib.splitspec import splitspec
from code.core.dataio.rawio import get_rm_list, get_source_info
import numpy as np


def calib_and_out(rmid, mjd):
    w, f, e = ec.ptcalib(rmid, mjd)
    fn = str(rmid) + "-" + str(mjd) + ".pkl"
    w, f, e = splitspec(w, f, e, [np.array([4000.0, 5500.0])])
    s.save_spec(w, f, e, "data/calib/pt", fn)
    fd = "plot/spectra/" + str(rmid)
    fn = str(mjd) + ".png"
    p.plotspec(w, f, filedir=fd, filename=fn)


if __name__ == "__main__":
    rm_list = get_rm_list()
    for each in rm_list:
        mjd_list = get_source_info(each).mjd
        for day in mjd_list:
            try:
                calib_and_out(each, day)
            except Exception as reason:
                print(str(each) + "-" + str(day) + ": Failed " + str(reason))
