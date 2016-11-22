#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import pickle
from code.core.location import Location
from code.core.dataio.rawio import get_rm_list
from code.core.dataio.specio import get_spec


if __name__ == "__main__":
    tot = get_rm_list()
    valid = []
    for each in tot:
        try:
            w, f, e = get_spec("data/calib/pt/" + str(each) + "-56660.pkl")
            if max(w) > 5490.0 and min(w) < 4010.0:
                valid.append(each)
        except Exception:
            continue
    f = open(os.path.join(Location.root, "data", "source_list.pkl"), "wb")
    pickle.dump(valid, f)
    f.close()
