import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll, camonitor
import time
import re
from util import epics_util as util
from tests.Tester import Tester


class Config_Tester(Tester):

    def __init__(self, path, test_name):
        
        self.path = path + str(test_name)
        Tester.__init__(self, self.path)


    def bad_defaults(self):

        #self.proc.expect(['\[EXCEPTION[^:]*string', pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        util.expect(self.proc,['\[EXCEPTION[^:]*string'], 5)
        error = self.proc.after
        return error

    def broken_xml(self):
        #self.proc.expect(['\[EXCEPTION] Error parsing XML file', pexpect.EOF, pexpect.TIMEOUT], timeout=5)
        util.expect(self.proc, ['\[EXCEPTION] Error parsing XML file'], 5)
        found = self.proc.after
        return found

    def buffering_low(self):
        status = PV('status')
        start_time = time.time()
        while status.get() not in (0, 3):
            print str(status.get()) + "not connected yet"
            connected = status.get() in (0, 3)
            poll(evt=1.0, iot=0.51)
            if time.time() - start_time >= 60:
                connected = False
                print "timed out"
                break

        check = util.expect(self.proc, ["C1"])
        count3 = PV('in_counts_3')
        low_3 = PV('low_limit_3')
        low_4 = PV('low_limit_4')
        trig_buffer = PV('trig_buffer')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)
        data3 = []

        def getCount3(pvname, value, **kw):
            data3.append(value)

        if util.put_check(low_3, 0.0) and util.put_check(low_4, 0.0) and util.put_check(trig_buffer, 1000) and util.put_fuzzy('analog_out_period', 10e-5, 0.05):
            pass
        else:
            print "setting not taking place"
            return False, False

        count3.add_callback(getCount3)
        init.put(1)
        t0 = time.time()
        while time.time() - t0 < 3:

            poll(evt=1.e-5, iot=0.01)

        time.sleep(2)

        return len(data3)

    def buffering(self):
        poll(evt=1.9, iot=0.01)
        status = PV('status')
        poll(evt=1.9, iot=0.01)
        start_time = time.time()
        while status.get() not in (0, 3):
            print str(status.get()) + "not connected yet"
            print status.info
            print status
            connected = status.get() in (0, 3)
            poll(evt=1.0, iot=0.51)
            if time.time() - start_time >= 60:
                connected = False
                print "timed out"
                break

        print util.expect(self.proc, ["C1"])
        count3 = PV('in_counts_3')
        count4 = PV('in_counts_4')
        low_3 = PV('low_limit_3')
        low_4 = PV('low_limit_4')
        trig_buffer = PV('trig_buffer')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)
        data3 = []
        data4 = []

        def getCount3(pvname, value, **kw):
            data3.append(value)

        def getCount4(pvname, value, **kw):
            data4.append(value)

        if util.put_check(low_3, 0.0) and util.put_check(low_4, 0.0) and util.put_check(trig_buffer, 1000) and util.put_fuzzy('analog_out_period', 10e-5, 0.05):
            pass
        else:
            print "setting not taking place"
            return False, False

        t0 = time.time()
        time.sleep(1)
        count3.add_callback(getCount3)
        count4.add_callback(getCount4)
        poll(evt=1.e-5, iot=0.01)
        init.put(1)
        poll(evt=1.e-5, iot=0.01)   

        while time.time() - t0 < 3:

            poll(evt=1.e-5, iot=0.01)

        # end = self.proc.expect(
        #     ['Announce\(\) success', pexpect.TIMEOUT, pexpect.EOF], timeout=3)
        return len(data3), len(data4)

    def channel_limits(self, value):
        self.proc.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=3)


        test = [PV('test1'), PV('test2'), PV('test3')]

        rules = {test[0]:(1, 300), test[1]:(-300, -1), test[2]:(None, None)}
        poll(evt=1.e-5, iot=0.01)
        time.sleep(0.1)

        test[0].put(value)
        #c1 = self.proc.expect(['Limit violation', pexpect.TIMEOUT, pexpect.EOF], timeout=1)
        test[1].put(value)
        #c2 = self.proc.expect(['Limit violation', pexpect.TIMEOUT, pexpect.EOF], timeout=1)
        test[2].put(value)
        #c3 = self.proc.expect(['Limit violation', pexpect.TIMEOUT, pexpect.EOF], timeout=1)
        poll(evt=1.0, iot=0.01)
        results = []
        for i in test:
            if rules[i] == (None, None):
                results.append(util.isclose(i.get(),value))
            elif value >= rules[i][0] and value <= rules[i][1]:
                results.append(util.isclose(i.get(),value))
            else:
                results.append(util.isclose(i.get(), rules[i][0]) or util.isclose(i.get(), rules[i][1]))
        return results

    def check_limits(self, value):
        t3 = 1
        if value <= 300 and value >= 1:
            t1 = 1
            t2 = 0
        elif value >= -300 and value <= -1:
            t1 = 0
            t2 = 1
        else:
            t1 = 0
            t2 = 0
        return t1, t2, t3

    def check(self, value1, value2, tolerance):
        mod_plus = value1 + value1 * tolerance
        mod_minus = value1 - value1 * tolerance

        return (mod_plus >= value2 or mod_minus <= value2)

    def channel_scaling(self):
        status = PV('status')
        start_time = time.time()
        while status.get() not in (0, 3):
            print str(status.get()) + "not connected yet"
            connected = status.get() in (0, 3)
            poll(evt=1.0, iot=0.51)
            if time.time() - start_time >= 60:
                connected = False
                print "timed out"
                break

        check = util.expect(self.proc, ["A1"])
        normal = PV('cleanIn1')
        linear = PV('linearIn1')
        log = PV('logIn1')
        both_scaled = PV('bothScaled')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)

        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        time.sleep(2)

        base = normal.get()
        lin = linear.get()
        logged = log.get()
        both = both_scaled.get()

        print base, lin, logged, both

        return (self.check(lin, base * 2 + 10, 0.01) and self.check(logged, 10**base, 0.01) and self.check(both, 10 ** (base * 2 + 10), 0.01))

    def defaults(self):
        self.proc.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=3)
        a, b, c = caget('testA'), caget('testB'), caget('testC')
        return (a, b, c)

    def monitor_only(self):
        status = PV('status')
        start_time = time.time()
        while status.get() not in (0, 3):
            print str(status.get()) + "not connected yet"
            connected = status.get() in (0, 3)
            poll(evt=1.0, iot=0.51)
            if time.time() - start_time >= 60:
                connected = False
                print "timed out"
                break

        check = util.expect(self.proc, ["C1"])

        count3 = PV('in_counts_3')
        count4 = PV('in_counts_4')
        trig_mode = PV('trig_mode')
        low_3 = PV('low_limit_3')
        low_4 = PV('low_limit_4')
        trig_buffer = PV('trig_buffer')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)
        data3 = []
        data4 = []

        util.put_check(trig_mode, 1)
        util.put_check(low_3, 0.0)
        util.put_check(low_4, 0.0)
        util.put_check(trig_buffer, 1000)
        util.put_fuzzy('analog_out_period', 10e-5, 0.01)

        def getCount3(pvname, value, **kw):
            data3.append(value)

        def getCount4(pvname, value, **kw):
            data4.append(value)

        count3.add_callback(getCount3)
        count4.add_callback(getCount4)

        init.put(1)
        time.sleep(3)

        return len(data3), len(data4)

    def same_name(self):
        self.proc.expect('\[EXCEPTION[^:]*exists')

        error = self.proc.after
        before = self.proc.before

        # print " after "+ error

        expr = re.compile('\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}:\d{3}')
        clean = re.sub(expr, '', error).lstrip()
        return clean

    def same_wire(self, value):
        self.proc.expect([pexpect.TIMEOUT, pexpect.EOF], timeout=0.25)

        t1 = PV('wire1')
        t2 = PV('wire2')
        poll(evt=1.0, iot=0.01)

        t1.put(value, wait=True)
        time.sleep(1)

        return(t1.get(), t2.get())
