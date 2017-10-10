from epics import caget, caput, poll, PV, ca
import time
import pexpect


def pv_check(pv, value):
    poll(evt=1.0, iot=1.01)
    pv_value = pv.get(use_monitor=False)
    if isclose(pv_value, value):
    #if pv.get() == value:
        #print "value is correct: " + str(pv.get())
        #print "value is " + str(value) + " actual is " + str(pv_value)
        return True
    else:
        t0 = time.time()
        #pv.put(value)
        poll(evt=1.e-5, iot=0.01)
        while not isclose(pv_value, value):
            pv.put(value)
            poll(evt=1.0, iot=1.01)
            pv_value = pv.get(use_monitor=False)
            #poll(evt=1.0, iot=1.01)
            if time.time() - t0 > 10:
                #current = pv.get(use_monitor=False)
                current = pv.get(use_monitor=False)
                print ("setting " + pv.pvname + " timed out, set value was " + str(value) + " actual value was: " + str(current))
                return False
            else:
                pass
        print "value is " + str(value) + " actual is " + str(pv_value)
        return True

def caput_check(name, value):
    t0 = time.time()
    
    while caget(name) != value:
        caput(name, value)
        poll(evt=1.e-5, iot=0.01)
        if time.time() - t0 > 10:
            print "did not set"
            return False
    return True

def put_check(pv, value):
    #pv.get(use_monitor=False)
    #pv.get()
    poll(evt=0.1, iot=0.1)
    pv.put(value)
    #poll(evt=1.0, iot=1.01)
    #print pv.get()
    #pv.put(value)
    #poll(evt=0.5, iot=0.25)
    #poll(evt=1.0, iot=1.01)
    #time.sleep(1)
    return pv_check(pv, value)

def check_fuzzy(pvname, value, envelope):
    pv_value = caget(pvname)
    under  = -1*value*envelope + value
    over = value*envelope + value

    t0 = time.time()
    while pv_value < under or pv_value > over:
        if time.time() - t0 > 10:
            raise ValueError("setting " + pvname + " timed out, value was " + str(value))
            return False
        else:
            if pv_value >= under or pv_value <= over:
                return True
    return True

def put_fuzzy(pvname, value, envelope):
    caput(pvname, value)
    return check_fuzzy(pvname, value, envelope)

def check_device(device_name, proc):
    connect = proc.expect(
            [pexpect.TIMEOUT, pexpect.EOF, 'Announce\(\) success: '+str(device_name)], timeout=15)
    
    if connect == 2:
        return True
    else:
        print "check_device fail"
        print proc.after
        print proc.before
        return False
        
        
def blowout_pvs():
    #epics.ca.clear_channel(pv_name.chid) 
    ca.finalize_libca()
    # ctx = ca.current_context()
    # pvs = []
    # for x in ca._cache[ctx]:
    #     pvs.append(x)
    # for pv in pvs:
    #     ca._cache[ctx].pop(pv)
    # print ctx


def isclose(a, b, rel_tol=0.01, abs_tol=0.0):
    if type(a) == str or type(b) ==  str:
        return a == b 
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    #return a == b 

def expect(proc, regex=[], timeout=5):
    expect_params = [pexpect.TIMEOUT, pexpect.EOF, "Out of memory"] + regex
    
    result = proc.expect(expect_params, timeout)
    #print "result is " + str(result) 
    if result == 2:
        cycle = pexpect.spawn('curl "http://admin:1234@192.168.100.36/script?run002=run"')
        time.sleep(30)

        return proc.expect([pexpect.TIMEOUT, pexpect.EOF]+regex, timeout)
    else:
        return result