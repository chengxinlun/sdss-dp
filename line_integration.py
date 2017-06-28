#!/usr/bin/env python
# -*- coding:utf-8 -*-
import numpy as np
from code.fitting.LmCF import LmCF
from code.fitting.LmHO import LmHO


def line_inte(cf_para, ho_para):
    cf_dict = LmCF(4000.0, 1.0, 2.0).integrate(cf_para)
    ho_dict = LmHO().integrate(ho_para)
    return np.array([cf_dict["cont"], cf_dict["fe2"], ho_dict["hbeta"],
                     ho_dict["o3"]])
