import pexpect
from epics import caget, caput, PV, ca, get_pv, pv, poll, _PVmonitors_
import time
from util import epics_util as util
from tests.Tester import Tester
import epics


class F460_Tester(Tester):

    def __init__(self, path, test_name):
        if test_name == 'epics':
            self.path = path
        else:
            self.path = path + str(test_name)
        Tester.__init__(self, self.path)
        self.status = PV('status')
        if test_name == 'epics':
            self.connected = True
        else:
            t0 = time.time()
            while self.status.get() not in (0, 3):
                poll(evt=1.e-5, iot=0.01)
                if time.time() - t0 > 10:
                    print "status bad " + str(self.status.get())
                    break
            check = util.check_device('F1', self.proc)
            state_check = self.status.get() in (0, 2)
            self.connected = check and state_check

    def stress_test(self):
        if not self.connected:
            print "Device not connected"
            return False
        trig_stop = PV('stop_trigger_source')

        for i in range(0, 10):
            trig_stop.put(i % 2)
            trig_stop.get()
            poll(evt=0.01, iot=0.01)
            expect = self.proc.expect([pexpect.TIMEOUT, pexpect.EOF, 'Announce\(\) success', 'fail', 'memory'], timeout=0.1)
            print self.proc.after
            print i%2
            if expect in (3,4):
                return self.proc.after, self.proc.before
        return "passed all"

    def buffer_mode(self, value):
        data = []

        if not self.connected:
            print "Device not connected"
            return False

        time.sleep(1)

        acquisition_mode = PV('acquisition_mode')
        buffered_mode = PV('buffered_acquisition')
        stopcount = PV('stop_count')
        current1 = PV('current_in_1')
        init = PV('initiate')
        acquisition_mode.put(1)
        poll(evt=1.0, iot=1.0)
        buffered_mode.put(1)
        poll(evt=1.0, iot=1.0)
        stopcount.put(value)
    
        poll(evt=1.0, iot=1.0)
        buff1 = buffered_mode.get()

        def getCount(pvname, value, **kw):
            data.append(value)

        current1.add_callback(getCount)
        init.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()
        while time.time() - t0 < 4:
            poll(evt=1.e-5, iot=0.01)

        return len(data)

    def burst_size(self, value):
        print self.connected
        data = []
        if not self.connected:
            print "Device not connected"
            return False
        
        acquisition_mode = PV('acquisition_mode')
        buffered_mode = PV('buffered_acquisition')
        burst_count = PV('burst_count')

        acquisition_mode.put(1)
        poll(evt=1.e-5, iot=0.01)
        buffered_mode.put(1)
        poll(evt=1.e-5, iot=0.01)
        t0 = time.time()

        burst_count.put(value)
        poll(evt=0.01, iot=0.01)
        connect = self.proc.expect([pexpect.TIMEOUT, pexpect.EOF, 'Announce\(\) success'], timeout=1)

        output = burst_count.get()

        burst_count.put(0, wait=True)
        poll(evt=1.0, iot=1.01)

        return output

    def burst2(self, value): 
        #connect = self.proc.expect([pexpect.TIMEOUT, pexpect.EOF, 'Announce\(\) success'], timeout=1)
        if not self.connected:
            print "Device not connected"
            return False
        burst = PV('burst_count')
        poll(evt=1.01, iot=1.01)
        util.put_check(burst, value)
        poll(evt=1.0, iot=1.01)
        caput('burst_count', value)
        # while burst.get() != 100:
        #     burst.put(100)
        #     poll(evt=1.0, iot=1.01)
        return burst.get()

    def io(self):
        if not self.connected:
            print "Device not connected"
            return False
        init, ai1, ai2, ci1, ci2, ci3, ci4 = PV('initiate'), PV('analog_in_1'), PV('analog_in_2'), PV('current_in_1'), PV('current_in_2'), PV('current_in_3'), PV('current_in_4')
        comp1, comp2, comp3, comp4, bias = PV('channel_in_1'), PV('channel_in_2'), PV('channel_in_3'), PV('channel_in_4'), PV('bias_in')
        
        init.put(1)
        poll(evt=1.0, iot=1.01)

        return ai1, ai2, ci1, ci2, ci3, ci4, comp1, comp2, comp3, comp4, bias
    def trigger_stop(self):
        if not self.connected:
            print "Device not connected"
            return False
        #time.sleep(5)
        data = []
        stop_trig = PV('stop_trigger_source')
        acquisition_mode = PV('acquisition_mode')
        buff_mode = PV('buffered_acquisition')
        stopcount = PV('stop_count')
        poll(evt=1.e-5, iot=0.01)
        # stopcount.put(0)
        # poll(evt=1.e-5, iot=0.01)
        # buff_mode.put(0)
        # poll(evt=1.e-5, iot=0.01)
        # print util.put_check(stopcount, 0)
        # print stopcount.get()
        # print util.put_check(buff_mode, 0)
        # print buff_mode.get()
        poll(evt=1.e-5, iot=0.01)
        print "starting setup is, acquisition: " + str(acquisition_mode.get()) + " stoptrig: " + str(stop_trig.get())

        acquisition_mode.put(0)
        poll(evt=1.e-5, iot=0.01)
        # buff_mode.put(1)
        # poll(evt=1.e-5, iot=0.01)
        # stopcount.put(1000)
        # poll(evt=1.e-5, iot=0.01)

        #stop_trig.put(1)
        util.put_check(stop_trig, 1)
        print "trig1: " + str(stop_trig.get())
        poll(evt=1.0, iot=1.01)
        print "trig2: " + str(stop_trig.get())
        data.append(stop_trig.get() == 1)
        time.sleep(3)
        print "trig3: " + str(stop_trig.get())

        #stop_trig.put(0)
        util.put_check(stop_trig, 0)
        poll(evt=1.0, iot=1.01)

        data.append(stop_trig.get() == 0)
        time.sleep(3)
        print "trig4: " + str(stop_trig.get())
        return data

    def trigger_start(self):
        if not self.connected:
            print "Device not connected"
            return False
        data = []
        start_trig = PV('start_trigger_source')
        acquisition_mode = PV('acquisition_mode')
        poll(evt=1.e-5, iot=0.01)
        print "starting setup is, acquisition: " + str(acquisition_mode.get()) + " stoptrig: " + str(start_trig.get())
        
        acquisition_mode.put(0)
        poll(evt=1.e-5, iot=0.01)

        #start_trig.put(1)
        util.put_check(start_trig, 1)
        print "trig1: " + str(start_trig.get())
        poll(evt=1.0, iot=1.01)
        print "trig2: " + str(start_trig.get())
        data.append(start_trig.get() == 1)
        time.sleep(3)
        print "trig3: " + str(start_trig.get())

        #start_trig.put(0)
        util.put_check(start_trig, 0)
        poll(evt=1.0, iot=1.01)

        data.append(start_trig.get() == 0)
        time.sleep(3)
        print "trig4: " + str(start_trig.get())
        return data

    def trigger_pause(self):
        if not self.connected:
            print "Device not connected"
            return False
        data = []
        pause_trig = PV('pause_trigger_source')
        acquisition_mode = PV('acquisition_mode')
        poll(evt=1.e-5, iot=0.01)
        print "starting setup is, acquisition: " + str(acquisition_mode.get()) + " stoptrig: " + str(pause_trig.get())

        acquisition_mode.put(0)
        poll(evt=1.e-5, iot=0.01)

        #pause_trig.put(1)
        util.put_check(pause_trig, 1)
        print "trig1: " + str(pause_trig.get())
        poll(evt=1.0, iot=1.01)
        print "trig2: " + str(pause_trig.get())
        data.append(pause_trig.get() == 1)
        time.sleep(3)
        print "trig3: " + str(pause_trig.get())

        #pause_trig.put(0)
        util.put_check(pause_trig, 0)
        poll(evt=1.0, iot=1.01)

        data.append(pause_trig.get() == 0)
        time.sleep(3)
        print "trig4: " + str(pause_trig.get())
        return data
    
    def gate_polarity(self):
        if not self.connected:
            print "Device not connected"
            return False
        data = []
        gate = PV('bnc_start_gate')
        poll(evt=0.1, iot=0.1)
        gate.put(1)
       # util.put_check(gate, 1)
        poll(evt=0.1, iot=0.1)
        data.append(gate.get()==1)
        
        print gate.get()
        gate.put(0)
        poll(evt=0.1, iot=0.1)
        data.append(gate.get()==0)
        print data
        print gate.get()
        return data

    def input_range(self):
        if not self.connected:
            print "Device not connected"
            return False
        data = []
        range1 = PV('range_1')
        range2 = PV('range_2')
        range3 = PV('range_3')
        range4 = PV('range_4')
        poll(evt=0.1, iot=0.1)

        for i in range(0, 4):
            range1.put(i)
            range2.put(i)
            range3.put(i)
            range4.put(i)
            poll(evt=1.1, iot=1.1)

            data.append(range1.get()==i)
            data.append(range2.get()==i)
            data.append(range3.get()==i)
            data.append(range4.get()==i)

        return data


    def acquisition_modes(self):
        if not self.connected:
            print "Device not connected"
            return False
        data = []
        acquisition_mode = PV('acquisition_mode')
        burst_count = PV('burst_count')
        poll(evt=0.1, iot=0.1)
        print acquisition_mode.get()
        for i in range(0, 6):

            #acquisition_mode.put(i)
            util.put_check(acquisition_mode, i)
            if i == 5:
                util.put_check(burst_count, 0)
            #util.put_check(acquisition_mode, i)
            poll(evt=0.1, iot=0.1)
            print acquisition_mode.get()
            if acquisition_mode.get() == i:
                data.append(True)
            else:
                data.append(False)
        print data
        #teardown
        #acquisition_mode.put(0)
        #util.put_check(acquisition_mode, 1)
        acquisition_mode.put(1)
        print acquisition_mode.get()
        util.put_check(acquisition_mode, 0)
        #acquisition_mode.put(0)
        print acquisition_mode.get()
        poll(evt=1.0, iot=1.0)
        return data


    def config_options(self):
        data = []
        # connect = self.proc.expect([pexpect.TIMEOUT, pexpect.EOF, 'Announce\(\) success'], timeout=5)
        if not self.connected:
            print "Device not connected"
            return False

        start_trig = PV('start_trigger_source')
        pause_trig = PV('pause_trigger_source')
        stop_trig = PV('stop_trigger_source')
        acquisition_mode = PV('acquisition_mode')
        bnc_start_gate = PV('bnc_start_gate')
        range_1 = PV('range_1')
        range_2 = PV('range_2')
        range_3 = PV('range_3')
        range_4 = PV('range_4')
        #burst_count = PV('burst_count')

        
        
        # acquisition_mode.put(0)
        # start_trig.put(0)
        # pause_trig.put(0)
        # stop_trig.put(0)
       

        util.put_check(acquisition_mode, 0)
        util.put_check(start_trig, 0)
        util.put_check(pause_trig, 0)
        util.put_check(stop_trig, 0)

        poll(evt=2.0, iot=2.0)
        print acquisition_mode.get()
        print start_trig.get()
        print pause_trig.get()
        print stop_trig.get()

        for i in range(0, 2):
            #start_trig.put(i)
            print "i: " + str(i)
            time.sleep(0.1)
            
            start_trig.put(i)
            poll(evt=1, iot=1)
            if start_trig.get() == i:
                data.append(True)
            else:
                data.append(False)
            #data.append(util.pv_check(start_trig, i))
     

            for j in range(0, 2):
                print "j: " + str(j)
                pause_trig.put(j)
                poll(evt=1, iot=1)
                if pause_trig.get() == j:
                    data.append(True)
                else:
                    data.append(False)
                #data.append(util.pv_check(pause_trig, j))
                

                for k in range(0, 2):
                    
                    print "k: " + str(k)
                    stop_trig.put(k)
                    bad = self.proc.expect(
                            [pexpect.TIMEOUT, "Error setting C400 configuration"], timeout=2)
                    poll(evt=1.0, iot=1.0)
                    #caput('stop_trigger_source', k)
                    #time.sleep(0.1)

                    # if k == j and j != 0:

                    #     poll(evt=1.0, iot=1.0)
                    #     print self.proc.after
                    #     if bad == 1:
                    #         data.append(True)
                    #     else:
                    #         data.append(False)
                    # elif 
                    if stop_trig.get() == k:
                        data.append(True)
                    else:
                        data.append(False)
                        #data.append(util.pv_check(stop_trig, k))

                stop_trig.put(0)
                poll(evt=1, iot=1)
            pause_trig.put(0)
            poll(evt=1, iot=1)
        print data
        print "doing modes"
        for i in range(0, 6):
            acquisition_mode.put(i)
            poll(evt=1.0, iot=1.0)
            if acquisition_mode.get() == i:
                data.append(True)
            else:
                data.append(False)
            # caput('acquisition_mode', i)
            # time.sleep(1)
            # if caget('acquisition_mode') != i:
            #     data.append(False)
            # else:
            #     data.append(True)
        print "doing bnc"
        # for i in range(0, 2):
        #     bnc_start_gate.put(i)
        #     poll(evt=1.0, iot=1.0)
        #     if bnc_start_gate.get() == i:
        #         data.append(True)
        #     else:
        #         data.append(False)
        # print "doing ranges"
        # for i in range(0, 4):
        #     range_1.put(i)
        #     range_2.put(i)
        #     range_3.put(i)
        #     range_4.put(i)
        #     poll(evt=1.0, iot=1.1)
        #     if range_1.get() == i and range_2.get()==i and range_3.get()==i and range_4.get()==i:
        #         data.append(True)
        #     else:
        #         data.append(False)

        # teardown
        #util.put_check(burst_count, 0)
        #util.put_check(acquisition_mode, 1)
        #burst_count.put(-1)
        acquisition_mode.put(1)
        poll(evt=1.0, iot=1.1)
        print data

        return all(x == True for x in data)

    def version_numbers(self):

        if not self.connected:
            print "Device not connected"
            return False

        return caget('firmware_version'), caget('fpga_version'), caget('serial_number'), caget('software_rev'), caget('secondary_fpga_version'), caget('rpt_revision'), caget('hardware_revision')

    def initiate_abort(self, values):
        buff = values[0]
        stop = values[1]
        data = []
        if not self.connected:
            print "Device not connected"
            print self.status
            return False

        stopcount = PV('stop_count')
        acquisition_mode = PV('acquisition_mode')
        buffered_mode = PV('buffered_acquisition')
        current1 = PV('current_in_1')
        init = PV('initiate')
        poll(evt=1.0, iot=1.01)
        util.put_check(acquisition_mode, 1)
        poll(evt=1.e-5, iot=0.01)

        util.put_check(buffered_mode, 0)

        poll(evt=1.e-5, iot=0.01)

        util.put_check(stopcount, buff)

        poll(evt=1.e-5, iot=0.01)

        def getCount(pvname, value, **kw):
            #print value
            data.append(value)
        t0 = time.time()
        current1.add_callback(getCount)
        init.put(1)
        while time.time() - t0 < 15 and len(data) < stop:
            poll(evt=0.5, iot=0.01)
            print len(data)
        final_val = data[-1]
        init.put(0)
        poll(evt=1.e-5, iot=0.01)
        time.sleep(5)
        return util.isclose(final_val, data[-1])  

    
    def memory_test(self, value):
        if not self.connected:
            print "device not"
            return False
        #proc2 = pexpect.spawn(self.path)

        #aout2.put(value)
        poll(evt=1.0, iot=1.01)
        #proc2.close(force=True)
        return value