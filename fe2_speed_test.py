from code.fitting.fe2 import Fe2V
import numpy as np
import time

x = np.linspace(4000.0, 5500.0, num=3000)
fe2 = Fe2V(0.0, 900.0, 1.0, 0.0, 900.0, 1.0)
start = time.clock()
y = fe2(x)
print(time.clock() - start)
print(y)
