import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll
import time
from util import epics_util as util
from tests.Tester import Tester
from hypothesis import given
import hypos


class M10_Tester(Tester):

    def __init__(self, path, test_name):
        if test_name == 'epics':
            self.path = path
        else:
            self.path = path + str(test_name)
        Tester.__init__(self, self.path)
        self.data1 = []
        self.data2 = []
        self.stop = 101
        self.status = PV('status')
        if test_name == 'epics':
            self.connected = True
        else:
            self.connected = self.status.get() in (0, 3)

        start_time = time.time()
        while not self.connected:
            print str(self.status.get()) + "not connected yet"
            self.connected = self.status.get() in (0, 3)
            poll(evt=1.0, iot=0.51)
            if time.time() - start_time >= 60:
                self.connected = False
                print "timed out"
                break

    # def io(self):

    #     init = PV('initiate')
    #     d_outs = {1: PV('digitalOut1'), 2: PV('digitalOut2'),
    #               3: PV('digitalOut3'), 4: PV('digitalOut4')}
    #     d_ins = {1: PV('digitalIn1'), 2: PV('digitalIn2'),
    #              3: PV('digitalIn3'), 4: PV('digitalIn4')}
    #     a_ins = {1: PV('analogIn1'), 2: PV('analogIn2')}
    #     a_outs = {1: PV('analogOut1'), 2: PV('analogOut2')}
    #     poll(evt=1.e-5, iot=0.01)
    #     d_i = []
    #     a_i = []
    #     d_o = []
    #     a_o = []

    #     init.put(1)
    #     poll(evt=1.e-5, iot=0.01)
    #     for i in range(0, 4):
    #         d_o.append(util.put_check(d_outs[i + 1], 1))
    #         d_i.append(util.pv_check(d_ins[i + 1], 1))

    #     for i in range(0, 2):
    #         a_o.append(util.put_check(a_outs[i + 1], i))
    #         a_i.append(a_ins[i + 1].get() != None)

    #     print d_o
    #     return [x for sublist in [d_i, a_i, d_o, a_o] for x in sublist]

    def get_analog_ins(self):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')

        a_ins = {1: PV('analogIn1'), 2: PV('analogIn2')}
        a_i = []

        poll(evt=1.e-5, iot=0.01)

        for i in range(0, 2):
            a_i.append(a_ins[i + 1].get() != None)

        return a_i

    def set_analog_outs(self, value):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')
        a_outs = {1: PV('analogOut1'), 2: PV('analogOut2')}
        a_outs[1].connect()
        a_outs[2].connect()
        poll(evt=1.0, iot=0.01)

        util.put_check(a_outs[1], value[0])
        poll(evt=1.e-5, iot=0.01)
        util.put_check(a_outs[2], value[1])
        poll(evt=1.e-5, iot=0.01)

        output = [a_outs[1].get(), a_outs[2].get()]
        return output

    def get_digital_ins(self):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')

        d_ins = {1: PV('digitalIn1'), 2: PV('digitalIn2'),
                 3: PV('digitalIn3'), 4: PV('digitalIn4')}
        d_i = []
        poll(evt=1.e-5, iot=0.01)

        for i in range(0, 4):
            d_i.append(d_ins[i + 1].get() != None)

        print d_i
        return d_i

    def set_digital_outs(self, value):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')
        d_outs = {1: PV('digitalOut1'), 2: PV('digitalOut2'),
                  3: PV('digitalOut3'), 4: PV('digitalOut4')}
        poll(evt=1.0, iot=0.01)
        for i in range(4):
            util.put_check(d_outs[i + 1], value[i])
        return [v.get() for v in d_outs.values()]

    def init(self):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')

        a_in_1 = PV('analogIn1')
        poll(evt=1.e-5, iot=0.01)

        before_init = a_in_1.get()

        init.put(1)
        poll(evt=1, iot=1)

        after_init = a_in_1.get()

        return before_init, after_init

    def abort(self):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            return False

        init = PV('initiate')
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

    # def getData1(pvname, value, **kw):
    #     if value != 0:
    #         self.data1.append(value)

    # def getData2(pvname, value, **kw):
    #     if value != 0:
    #         self.data2.append(value)

    def stopcount(self):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            print self.proc.before
            print self.proc.after
            return False

        def getData1(pvname, value, **kw):
            if value != 0:
                self.data1.append(value)

        def getData2(pvname, value, **kw):
            if value != 0:
                self.data2.append(value)

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
        if util.put_check(stop_count, self.stop):
            init.put(1)
            t0 = time.time()
            while time.time() - t0 < 10:
                poll(evt=1.e-5, iot=0.01)
        else:
            print "Stopcount not set"
            return False

        buffered_run = len(self.data1)
        print self.data1
        print len(self.data1)
        return buffered_run

    def stopcount_value(self, value):
        if util.expect(self.proc, ["A1"]) != 3:
            print "did not connect"
            print self.proc.before
            print self.proc.after
            return False

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
        while time.time() - t0 < 10:
            poll(evt=1.e-5, iot=0.01)
        run = len(data1)

        return run

    def memory_test(self, value):
        util.expect(self.proc)
        # if not self.connected:
        #     print "Device not connected"
        #     return False

        #proc2 = pexpect.spawn(self.path)
        aout1 = PV('analogOut1')
        ain1 = PV('analogIn1')
        poll(evt=1.0, iot=1.01)
        #aout2 = PV('analogOut2')
        print ain1.get()

        # aout2.put(value)
        poll(evt=1.0, iot=1.01)
        # proc2.close(force=True)
        return value
