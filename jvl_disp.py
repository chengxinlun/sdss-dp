import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location
from code.core.util.io import create_directory


f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
rmid_list = pickle.load(f)
f.close()
for each in rmid_list:
    try:
        lag = np.loadtxt(os.path.join(Location.root, "result", "revmap",
                                      str(each), "rm.txt"))[:, 2]
    except Exception as reason:
        continue
    # Dirs for result
    plotDir = os.path.join("plot", "revmap", "jvl")
    fileDir = os.path.join("result", "revmap", "jvl")
    create_directory(plotDir)
    create_directory(fileDir)
    # Plot
    fig = plt.figure()
    plt.hist(lag, bins=50)
    fig.savefig(os.path.join(Location.root, plotDir, str(each) + ".png"))
    plt.close()
    # Statistics
    h = np.histogram(lag, bins=50)
    stat = np.array([h[1][h[0].argmax()], np.std(lag)])
    if stat[0] < stat[1] or stat[0] < h[1][h[0].argmin()] + 1.0 * stat[1]:
        stat = np.array([0.0, 0.0])
    np.savetxt(os.path.join(Location.root, fileDir, str(each) + ".txt"), stat)
