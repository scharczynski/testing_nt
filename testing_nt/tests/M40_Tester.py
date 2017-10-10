import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll
import time
from util import epics_util as util
from tests.Tester import Tester

class M40_Tester(Tester):

    def __init__(self, path, test_name):
        
        self.path = path + str(test_name)
        Tester.__init__(self, self.path)
        self.data1 = []
        self.data2 = []
        self.stop = 99
        self.status = PV('status')
        self.connected = self.status.get() in (0, 3)

        start_time = time.time()
        while not self.connected:
            print "not connected yet"
            self.connected = self.status.get() in (0, 3)
            poll(evt=5.0, iot=1.51)
            if time.time - start_time >= 60:
                self.connected = False
                break

    
    def io(self):  
        if not self.connected:
            print "Device not connected"
            return False

        d_o = []
        a_o = []
        d_i = []
        a_i = []
        d_outs = {1:PV('digitalOut1'), 2:PV('digitalOut2'), 3:PV('digitalOut3'), 4:PV('digitalOut4'),
            5:PV('digitalOut5'), 6:PV('digitalOut6'), 7:PV('digitalOut7'), 8:PV('digitalOut8')}
        d_ins = {1:PV('digitalIn1'), 2:PV('digitalIn2'), 3:PV('digitalIn3'), 4:PV('digitalIn4'),
            5:PV('digitalIn5'), 6:PV('digitalIn6'), 7:PV('digitalIn7'), 8:PV('digitalIn8')}
        a_outs = {1:PV('analogOut1'), 2:PV('analogOut2'), 3:PV('analogOut3'), 4:PV('analogOut4'),
            5:PV('analogOut5'), 6:PV('analogOut6'), 7:PV('analogOut7'), 8:PV('analogOut8')}
        a_ins = {1:PV('analogIn1'), 2:PV('analogIn2'), 3:PV('analogIn3'), 4:PV('analogIn4'),
            5:PV('analogIn5'), 6:PV('analogIn6'), 7:PV('analogIn7'), 8:PV('analogIn8'),}
        poll(evt=1.e-5, iot=0.01)

        for i in range(0,8):
            d_o.append(util.put_check(d_outs[i+1], 1))
            a_o.append(util.put_check(a_outs[i+1], i))
            d_i.append(util.pv_check(d_ins[i+1], 1))
            a_i.append(a_ins[i+1].get() != None)
            

        return [x for sublist in [d_i, a_i, d_o, a_o] for x in sublist]

    def set_digital_outs(self, values):
        initial_check = util.expect(self.proc, ["A1"])
        d_outs = {1:PV('digitalOut1'), 2:PV('digitalOut2'), 3:PV('digitalOut3'), 4:PV('digitalOut4'),
            5:PV('digitalOut5'), 6:PV('digitalOut6'), 7:PV('digitalOut7'), 8:PV('digitalOut8')}
        poll(evt=1.e-5, iot=0.01)
        for i in range(0, 8):
            util.put_check(d_outs[i+1], values[i])
        return [v.get() for v in d_outs.values()]

    def set_analog_outs(self, values):
        initial_check = util.expect(self.proc, ["A1"])
        a_outs = {1:PV('analogOut1'), 2:PV('analogOut2'), 3:PV('analogOut3'), 4:PV('analogOut4'),
            5:PV('analogOut5'), 6:PV('analogOut6'), 7:PV('analogOut7'), 8:PV('analogOut8')}
        poll(evt=1.0, iot=0.01)

        for i in range(0, 8):
           util.put_check(a_outs[i+1], values[i])
        
        return [v.get() for v in a_outs.values()]
    
    def get_digital_ins(self):
        initial_check = util.expect(self.proc, ["A1"])
        d_i = []
        d_ins = {1:PV('digitalIn1'), 2:PV('digitalIn2'), 3:PV('digitalIn3'), 4:PV('digitalIn4'),
            5:PV('digitalIn5'), 6:PV('digitalIn6'), 7:PV('digitalIn7'), 8:PV('digitalIn8')}
        poll(evt=1.e-5, iot=0.01)

        for i in range(0, 8):
            d_i.append(d_ins[i+1].get() != None)
        
        return d_i

    def get_analog_ins(self):
        initial_check = util.expect(self.proc, ["A1"])
        a_i = []
        a_ins = {1:PV('analogIn1'), 2:PV('analogIn2'), 3:PV('analogIn3'), 4:PV('analogIn4'),
            5:PV('analogIn5'), 6:PV('analogIn6'), 7:PV('analogIn7'), 8:PV('analogIn8'),}
        poll(evt=1.e-5, iot=0.01)

        for i in range(0, 8):
            a_i.append(a_ins[i+1].get() != None)
        
        return a_i


    def enable_stopcount(self):
        initial_check = util.expect(self.proc, ["A1"])
        stop = 100
        data1 = []
        data2 = []

        def getData1(pvname, value, **kw):
            if value != 0:
                data1.append(value)

        def getData2(pvname, value, **kw):
            if value != 0:
                data2.append(value)

        analog1 = PV('analogIn1')
        stop_count = PV('outStopCount')
        init = PV('initiate')
        analog2 = PV('analogIn2')
        poll(evt=1.e-5, iot=0.01)
        analog1.wait_for_connection()
        analog2.wait_for_connection()
        init.wait_for_connection()
        stop_count.wait_for_connection()

        analog1.add_callback(getData1)

        if util.put_check(stop_count, stop):
            init.put(1)
            t0 = time.time()
            while time.time() -t0 < 30:           
                poll(evt=1.e-5, iot=0.01)
        else:
            print "Stopcount not set"
            return False

        buffered_run = len(data1)
        analog2.add_callback(getData2)

        time.sleep(2)
        if util.put_check(stop_count, -1):
            init.put(1)
            t0 = time.time()
            while time.time() -t0 < 30:           
                poll(evt=1.e-5, iot=0.01)
        else:
            print "Stopcount not set 2nd time"
            return False

        unbuffered_run = len(data2)

        return buffered_run, unbuffered_run

    def init(self):
        initial_check = util.expect(self.proc, ["A1"])
        init =  PV('initiate')

        a_in_1 = PV('analogIn1')
        poll(evt=1.e-5, iot=0.01)

        before_init = a_in_1.get()

        init.put(1)
        poll(evt=1, iot=1)

        after_init = a_in_1.get()

        return before_init, after_init

    def abort(self):
        initial_check = util.expect(self.proc, ["A1"])
        init =  PV('initiate')
        data = []
        a_in_1 = PV('analogIn1')
        poll(evt=1.e-5, iot=0.01)

        def getData1(pvname, value, **kw):
            if value != 0:
                data.append(value)

        a_in_1.add_callback(getData1)
        poll(evt=1.e-5, iot=0.01)

        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()

        while time.time() - t0 < 10:
            poll(evt=1.e-5, iot=0.01)
            if len(data) >= 50:
                init.put(0)

        time.sleep(2)

        return len(data)   

    def stopcount_value(self, value):
        initial_check = util.expect(self.proc, ["A1"])
        data1 = []
        def getData1(pvname, value, **kw):
            if value != 0:
                data1.append(value)

        analog1 = PV('analogIn1')
        stop_count = PV('outStopCount')
        init = PV('initiate')
        analog2 = PV('analogIn2')
        poll(evt=1.e-5, iot=0.01)
        analog1.wait_for_connection()
        analog2.wait_for_connection()
        init.wait_for_connection()
        stop_count.wait_for_connection()

        util.put_check(stop_count, value)
        analog1.add_callback(getData1)
        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()
        while time.time() -t0 < 10:           
            poll(evt=1.e-5, iot=0.01)

        run = len(data1)
        
        return run