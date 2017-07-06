import os
import numpy as np
import matplotlib.pyplot as plt
from code.core.location import Location


dcf_sum = os.path.join(Location.root, "result/revmap/dcf")
for each in os.listdir(dcf_sum):
    dcf_file = os.path.join(dcf_sum, each)
    dcf_data = np.loadtxt(dcf_file)
    t = dcf_data[:, 0]
    t_m_sig = dcf_data[:, 1]
    t_p_sig = dcf_data[:, 2]
    dcf = dcf_data[:, 3]
    dcf_m_err = dcf_data[:, 4]
    dcf_p_err = dcf_data[:, 5]
    fig = plt.figure()
    plt.errorbar(t, dcf, yerr=[dcf_m_err, dcf_p_err],
                 xerr=[t_m_sig, t_p_sig])
    plot_file = os.path.join(Location.root, "plot/revmap/dcf",
                             each.replace("txt", "png"))
    fig.savefig(plot_file)
    plt.close()
    max_index = dcf.argmax()
    t_max = t[max_index]
    t_max_m_sig = t_m_sig[max_index]
    t_max_p_sig = t_p_sig[max_index]
    sum_file = open(os.path.join(dcf_sum, "total.txt"), "a")
    sum_file.write(str(each.split(".")[0]) + " " + str(t_max) + " " +
                   str(t_max_m_sig) + " " + str(t_max_p_sig) + "\n")
    sum_file.close()
