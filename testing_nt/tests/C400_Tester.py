import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll, camonitor
import time
from util import epics_util as util
from tests.Tester import Tester


class C400_Tester(Tester):

    def __init__(self, path, test_name):
        if test_name == 'epics':
            self.path = path
        else:
            self.path = path + str(test_name)
        Tester.__init__(self, self.path)
        self.status = PV('status')
        poll(evt=1.0, iot=0.51)
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

    def accumulate_mode(self):
        data = []
        check = util.expect(self.proc, ["C1"])
        count = PV('in_counts_3')
        low_3 = PV('low_limit_3')
        trig_buffer = PV('trig_buffer', auto_monitor=False)
        int_time = PV('analog_out_period')
        accum_mode = PV('accum_mode')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)

        util.put_check(low_3, 0.0)
        util.put_check(trig_buffer, 1000)
        int_time.put(10e-5)
        poll(evt=1.e-5, iot=0.01)

        def getCount(pvname, value, **kw):
            data.append(value)

        count.add_callback(getCount)

        time.sleep(1)

        def run(mode):

            util.put_check(accum_mode, mode)
            time.sleep(1)

            init.put(1)
            poll(evt=1.e-5, iot=0.01)
            t0 = time.time()
            while time.time() - t0 < 5:
                poll(evt=1.e-5, iot=0.01)
            init.put(0)
            poll(evt=1.e-5, iot=0.01)

        run(0)
        if len(data) > 10:
            non_accum = data[-1] - data[-6]
        else:
            print "didnt get data"
            return False
        run(1)
        if len(data) > 10:
            accum = data[-1] - data[-6]
        else:
            print "didnt get data 2nd time"
            return False

        # teardown
        util.put_check(accum_mode, 0)
        print data
        return non_accum, accum, data[0]

    def buffering(self, value):
        check = util.expect(self.proc, ["C1"])
        count3 = PV('in_counts_3')
        low3 = PV('low_limit_3')
        trig_buffer = PV('trig_buffer', auto_monitor=False)
        int_time = PV('analog_out_period')
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)
        data = []
        #camonitor('trig_buffer')
        def getCount1(pvname, value, **kw):
            data.append(value)

        util.put_check(low3, 0.0)
        util.put_check(trig_buffer, value)
        util.put_fuzzy('analog_out_period', 10e-5, 0.05)

        print "set value " + str(value)
        print "buffer value " + str(trig_buffer.get())
        #time.sleep(5)
        #print "buffer value " + str(trig_buffer.get())

  
        count3.add_callback(getCount1)
        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()
        while time.time() - t0 < 5:

            poll(evt=1.e-5, iot=0.01)

        run1 = len(data)

        return run1

    def burst_size(self, value):
        check = util.expect(self.proc, ["C1"])
        data = []
        print check
        print self.proc.after
        count = PV('in_counts_3')
        trig_mode = PV('trig_mode')
        low3 = PV('low_limit_3')
        int_time = PV('analog_out_period')
        trig_burst = PV('trig_burst', auto_monitor=False)
        trig_buffer = PV('trig_buffer', auto_monitor=False)
        init = PV('initiate')
        poll(evt=1.e-5, iot=0.01)
        util.put_check(trig_mode, 0)
        low3.put(0.0)
        int_time.put(10e-4)
        util.put_check(trig_buffer, value)
        util.put_check(trig_burst, value)
        print trig_burst.get(), trig_buffer.get(), trig_mode.get(), value
        poll(evt=1.e-5, iot=0.01)

        def getCount(pvname, value, **kw):
            if value != 0:
                data.append(value)
        print trig_buffer.get(use_monitor=False)
        print trig_burst.get(use_monitor=False)
        time.sleep(1)
        count.add_callback(getCount)
        print len(data)
        init.put(1)
        t0 = time.time()
        while time.time() - t0 < 5:

            poll(evt=1.e-5, iot=0.01)
        data_length = len(data)
        # teardown
        print len(data)
        print len(data)
        print len(data)

        util.put_check(trig_burst, 0)
        util.put_check(trig_buffer, 0)  
        #print data
        return data_length

    def io(self, value1, value2):
        check = util.expect(self.proc, ["C1"])
        init = PV('initiate')
        low1, low2, low3, low4 = PV('low_limit_1'), PV(
            'low_limit_2'), PV('low_limit_3'), PV('low_limit_4')
        poll(evt=1.e-5, iot=0.01)
        util.put_check(low1, 0.0)
        util.put_check(low2, 0.0)
        util.put_check(low3, 0.0)
        util.put_check(low4, 0.0)

        count1, count2, count3, count4 = PV('in_counts_1'), PV(
            'in_counts_2'), PV('in_counts_3'), PV('in_counts_4')

        rate1, rate2, rate3, rate4 = PV('analog_in_rate_1'), PV(
            'analog_in_rate_2'), PV('analog_in_rate_3'), PV('analog_in_rate_4')

        bias1_in, bias2_in, bias3_in, bias4_in = PV('analog_in_bias_1'), PV(
            'analog_in_bias_2'), PV('analog_in_bias_3'), PV('analog_in_bias_4')

        bias1_out, bias2_out, bias3_out, bias4_out = PV('analog_out_bias_1'), PV(
            'analog_out_bias_2'), PV('analog_out_bias_3'), PV('analog_out_bias_4')


        init.put(1)

        poll(evt=1.0, iot=0.01)

        util.put_check(bias1_out, value1)
        util.put_check(bias2_out, value2)

        counts = [count1.get(), count2.get(), count3.get(), count4.get()]
        rates = [rate1.get(), rate2.get(), rate3.get(), rate4.get()]
        bias_ins = [bias1_in.get(), bias2_in.get(), bias3_in.get(), bias4_in.get()]
        bias_outs = [bias1_out.get(), bias2_out.get(), bias3_out.get(), bias4_out.get()]

        
        return [counts, rates, bias_ins, bias_outs]

    def set_integration(self, value):
        check = util.expect(self.proc, ["C1"])
        int_time = PV('analog_out_period', auto_monitor=False)
        util.put_check(int_time, value)
        print int_time.get()
        print int_time.get()
        print "before| intended: " + str(value) + " actual: " +str(int_time.get()) + " close check: " + str(util.isclose(value, int_time.get(use_monitor=False)))
        return int_time.get()

    def integration_test(self):
        data = []
        check = util.expect(self.proc, ["C1"])
        count = PV('in_counts_3')
        trig_mode, low3, low4, trig_buffer, int_time, init = PV('trig_mode'), PV('low_limit_3'), PV(
            'low_limit_4'), PV('trig_buffer'), PV('analog_out_period'), PV('initiate')
        trig_mode.put(1)
        low3.put(0.0)
        low4.put(0.0)
        util.put_check(trig_buffer, 1000)
        #util.put_fuzzy('analog_out_period', 10e-5, 0.01)
        int_time.put(10e-5)
        poll(evt=1.e-5, iot=0.01)

        def getCount(pvname, value, **kw):
            data.append(value)

        count.add_callback(getCount)

        init.put(1)
        print trig_mode.get(), low3.get(), low4.get(), trig_buffer.get(), int_time.get()
        print count.value
        print count.get()
        poll(evt=2.0, iot=2.01)
        print count.value
        print count.get()
        fast = count.value

        int_time.put(10e-3)

        t1 = time.time()
        # while caget('analog_out_period') != 10e-3:
        #     if time.time() - t1 > 20:
        #         return "integration period is not being set"
        #     else:
        #         pass

        init.put(1)
        time.sleep(5)

        slow = count.value

        if slow and fast:
            print slow, fast
            return slow / (fast + 0.01 * fast), slow / (fast - 0.01 * fast)

        else:
            print slow, fast
            return False

    def discriminator_limits(self):
        check = util.expect(self.proc, ["C1"])
        polarity3, polarity4, trig_buffer, int_time, init = PV('digital_out_polarity_3'), PV(
            'digital_out_polarity_4'), PV('trig_buffer'), PV('analog_out_period'), PV('initiate')
        util.put_check(trig_buffer, 1000)
        int_time.put(10e-4)
        poll(evt=1.e-5, iot=0.01)

        count3 = PV('in_counts_3')
        count4 = PV('in_counts_4')
        low_limit3 = PV('low_limit_3')
        low_limit4 = PV('low_limit_4')
        high_limit3 = PV('high_limit_3')
        high_limit4 = PV('high_limit_4')

        util.put_check(low_limit3, 1.0)
        util.put_check(low_limit4, 1.0)
        util.put_check(polarity3, 1)
        util.put_check(polarity4, 1)
        util.put_check(high_limit3, 5.0)
        util.put_check(high_limit4, 5.0)
        poll(evt=1.e-5, iot=0.01)

        setting = self.proc.expect(
            [pexpect.TIMEOUT, 'Error setting C400'], timeout=1)
        if setting == 1:

            polarity3.put(1)
            polarity4.put(1)

        data = []
        data2 = []

        def getCount(pvname, value, **kw):
            data.append(value)

        def getCount2(pvname, value, **kw):
            data2.append(value)

        count3.add_callback(getCount)
        count4.add_callback(getCount2)
        poll(evt=1.e-5, iot=0.01)
        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()
        while time.time() - t0 < 3:
            poll(evt=1.e-5, iot=0.01)

        util.put_check(low_limit3, 0.0)

        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()
        while time.time() - t0 < 3:
            poll(evt=1.e-5, iot=0.01)

        return sum(data), sum(data2)

    def polarity(self):
        data = []
        # if lowerlimit is 0, polarity cant change?
        check = util.expect(self.proc, ["C1"])
        pols = {1: PV('digital_out_polarity_1'), 2: PV('digital_out_polarity_2'), 3: PV(
            'digital_out_polarity_3'), 4: PV('digital_out_polarity_4')}
        low1 = PV('low_limit_1')
        low2 = PV('low_limit_2')
        low3 = PV('low_limit_3')
        low4 = PV('low_limit_4')

        util.put_check(low1, 0.05)
        util.put_check(low2, 0.05)
        util.put_check(low3, 0.05)
        util.put_check(low4, 0.05)

        util.put_check(pols[1], 1)
        util.put_check(pols[2], 1)
        util.put_check(pols[3], 1)
        util.put_check(pols[4], 1)

        for i in range(1, 5):
            data.append(pols[i].get())

        util.put_check(pols[1], 0)
        util.put_check(pols[2], 0)
        util.put_check(pols[3], 0)
        util.put_check(pols[4], 0)

        for i in range(1, 5):
            data.append(pols[i].get())

        # print caget('digital_out_polarity_1'), caget('digital_out_polarity_2'), caget('digital_out_polarity_3'), caget('digital_out_polarity_4')
        # print caget('low_limit_1'), caget('low_limit_2'), caget('low_limit_3'), caget('low_limit_4')
        # print caget('high_limit_1'), caget('high_limit_2'),
        # caget('high_limit_3'), caget('high_limit_4')

        # teardown
        util.put_check(pols[1], 1)
        util.put_check(pols[2], 1)
        util.put_check(pols[3], 1)
        util.put_check(pols[4], 1)

        return sum(data)

    def pulse(self, period, width):
        data = []

        check = util.expect(self.proc, ["C1"])
        pulse_period, pulse_width, p_enable1, p_enable2, p_enable3, p_enable4 = PV('pulse_period'), PV('pulse_width'), PV(
            'digital_out_pulse_enable_1'), PV('digital_out_pulse_enable_2'), PV('digital_out_pulse_enable_3'), PV('digital_out_pulse_enable_4')
        poll(evt=1.0, iot=1.01)

        print p_enable1.get(), p_enable2.get(), p_enable3.get(), p_enable4.get(), pulse_period.get(), pulse_width.get()
        # util.put_check(p_enable1, 1)
        # util.put_check(p_enable2, 1)
        # util.put_check(p_enable3, 1)
        # util.put_check(p_enable4, 1)
        # util.put_check(pulse_period, period)
        # util.put_check(pulse_width, width)

        pulse_period.put(period)
        pulse_width.put(width)
        p_enable1.put(1)
        p_enable2.put(1)
        p_enable3.put(1)
        p_enable4.put(1)

        print p_enable1.get(), p_enable2.get(), p_enable3.get(), p_enable4.get(), pulse_period.get(), pulse_width.get()

    
        # teardown
        # util.put_check(pulse_period, 100)
        # util.put_check(pulse_width, 1)
        # util.put_check(p_enable1, 0)
        # util.put_check(p_enable2, 0)
        # util.put_check(p_enable3, 0)
        # util.put_check(p_enable4, 0)

        
        return [pulse_period.get(), pulse_width.get()]

    def start_stop(self, stop):
        data = []
        check = util.expect(self.proc, ["C1"])
        count, trig_mode, trig_buffer, int_time, low3, init = PV('in_counts_3'), PV(
            'trig_mode'), PV('trig_buffer'), PV('analog_out_period'), PV('low_limit_3'), PV('initiate')

        stop_state = PV('stopped_state')
        running_state = PV('running_state')
        poll(evt=0.5, iot=0.5)
        util.put_check(trig_mode, 1)
        util.put_check(low3, 0.0)
        util.put_check(trig_buffer, 0)
        int_time.put(10e-5)
        poll(evt=1.0, iot=1.01)

        #print trig_mode.get(), low3.get(), int_time.get(), trig_buffer.get()
        def getCount(pvname, value, **kw):
            if len(data) >= stop-1:
                init.put(0)
                poll(evt=0.1, iot=0.1)        
            #poll(evt=0.001, iot=0.001)
            
            data.append(value)


        count.add_callback(getCount)
        poll(evt=1.0, iot=1.01)

        init.put(1)
        poll(evt=0.5, iot=0.5)
        t0 = time.time()
        while len(data) < stop:
            poll(evt=1.e-5, iot=0.01)
            if time.time() - t0 >= 100:
                print "didnt reach stop count"
                break
        #poll(evt=0.1, iot=0.1)        
        #init.put(0)
        poll(evt=0.1, iot=0.1)
        #print trig_buffer.get(), low3.get(), trig_mode.get()
        pre_sleep = len(data)
        poll(evt=2.5, iot=0.5)
        time.sleep(5)
        post_sleep = len(data)
        print stop
        print pre_sleep, post_sleep
        return [pre_sleep, post_sleep]

    def state(self):
        check = util.expect(self.proc, ["C1"])
        running_state = PV('running_state')
        paused_state = PV('paused_state')
        stopped_state = PV('stopped_state')

        return [running_state.value, paused_state.value, stopped_state.value]

    def trigger_modes(self):
        data = []
        check = util.expect(self.proc, ["C1"])
        start_trig, pause_trig, stop_trig, trig_mode, trig_burst = PV('trig_source_start'), PV(
            'trig_source_pause'), PV('trig_source_stop'), PV('trig_mode'), PV('trig_burst')
        poll(evt=0.5, iot=0.5)
        util.put_check(start_trig, 0)
        util.put_check(pause_trig, 0)
        util.put_check(stop_trig, 0)
        util.put_check(trig_mode, 0)

        for i in range(0, 4):
            puti = util.put_check(start_trig, i)

            for j in range(0, 4):
                bad = 0
                putj = util.put_check(pause_trig, j)

                for k in range(0, 4):
                    if j == k and k != 0:
                        util.put_check(stop_trig, k)
                        bad = self.proc.expect(
                            [pexpect.TIMEOUT, "Error setting C400 configuration"], timeout=5)

                        if bad == 1:
                            putk = True
                        else:
                            putk = False
                    else:
                        putk = util.put_check(stop_trig, k)

                    if puti and putk and putj:
                        data.append(True)
                    else:
                        data.append(False)
                util.put_check(stop_trig, 0)

        for i in range(0, 7):

            util.put_check(trig_mode, i)
            time.sleep(1)
            data.append(trig_mode.get() == i)
        # teardown

        util.put_check(trig_mode, 1)
        util.put_check(trig_burst, 0)
        print data
        if all(x == True for x in data):
            return True
        else:
            # print data
            return False
