import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll
import time
from util import epics_util as util

class Tester(object):
    
    def __init__(self, path):
        self.path = path #path to i2g and config param upto the actual name
        #self.proc = ''
        #print self.path
        self.proc = pexpect.spawn(self.path)

        # memory_check = self.proc.expect(["Out of memory", pexpect.TIMEOUT, pexpect.EOF], timeout=3)
        # #print "mem check: " + str(memory_check)
        # if memory_check == 0:
        #     cycle = pexpect.spawn('curl "http://admin:1234@192.168.100.36/script?run002=run"')
        #     time.sleep(30)


    
    def kill_pexpect(self):
        #self.proc.close(force=True)
        self.proc.close()
        util.blowout_pvs()
    



