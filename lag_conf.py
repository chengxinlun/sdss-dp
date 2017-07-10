import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location


f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
rmid_list = pickle.load(f)
f.close()
# Omit list
oList = [331, 370, 382, 421, 548, 618, 644, 649, 669, 768, 776, 790, 792, 824,
         840]
sn = []
for each in rmid_list:
    try:
        if each in oList:
            raise Exception("Omitted")
        lag = np.loadtxt(os.path.join(Location.root, "result", "revmap", "jvl",
                                      str(each) + ".txt"))
        if lag[1] == 0.0:
            raise Exception("Unphysical lag")
    except Exception as reason:
        continue
    sn.append(lag[0] / lag[1])
    print(each)
sn = np.array(sn)
print(len(sn))
plt.hist(sn, bins=20)
plt.xlabel("Lag/error")
plt.show()
