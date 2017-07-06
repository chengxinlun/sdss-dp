import os
import pickle
import logging
from code.core.location import Location
from code.revmap.jvl import rm_single


f = open(os.path.join(Location.root, "data/source_list.pkl"), "rb")
mjd_list = pickle.load(f)
f.close()
logging.config.fileConfig("revmap_log.conf")
for each in mjd_list:
    pipein, pipeout = os.pipe()
    newpid = os.fork()
    if newpid == 0:
        try:
            rm_single(each, nthread=100)
        except Exception as reason:
            logger = logging.getLogger("root")
            logger.error(str(each) + ": " + str(reason))
        finally:
            fin = "Finished"
            os.write(pipeout, fin.encode())
            os._exit()
    else:
        ret = os.read(pipein, 64).decode()
        os.wait()
