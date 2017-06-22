from code.core.dataio.specio import get_spec
from code.calib.splitspec import splitspec
from code.fitting.LmCF import LmCF
from code.fitting.fitter import conggrad
from lmfit import report_fit
import matplotlib.pyplot as plt

w, f, e = get_spec("data/calib/pt/782-56660.pkl")
wp, fp, ep = splitspec(w, f, e, [[4000.0, 5500.0]])
wf, ff, ef = splitspec(w, f, e, [[4200.0, 4300.0], [4450.0, 4750.0],
                                 [5100.0, 5500.0]])
cf = LmCF(wp[0], fp[0], fp[-1])
res = conggrad(cf, wf, ff, ef, 10000)
report_fit(res)
fit_res = res.params
plt.plot(wp, fp)
plt.plot(wp, cf.eval(fit_res, wp))
plt.show()
