import pexpect
import epics
import hypothesis.strategies as st
from hypothesis.strategies import composite
def valid_analog_outs(size):
    return st.lists(st.floats(min_value=0.001, max_value=10.00), min_size=size, max_size=size)

def valid_digital_outs(size):
    return st.lists(st.integers(min_value=0, max_value=1), min_size=size, max_size=size)

def valid_stopcount():
    return st.integers(min_value=10, max_value=400)

def valid_memblock_a_o():
    return st.floats(min_value=-400, max_value=400)
    
def valid_buffer_size():
    return st.integers(min_value=10, max_value=4000)

def c400_bias_out_1000():
    return st.integers(min_value=0, max_value=1000)

def c400_bias_out_2000():
    return st.integers(min_value=0, max_value=2000)

def valid_int_time():
    return st.floats(min_value=1e-5, max_value=0.99)

def c400_pulse_period():
    return st.integers(min_value=1, max_value=1000000)

def c400_pulse_width():
    return st.integers(min_value=1, max_value=1000000)

def data_stop_range():
    return st.integers(min_value=100, max_value=2000)

@composite
def f460buff_and_stop(draw):
    buf = draw(st.integers(min_value=1000, max_value=10000))
    stopvalue = draw(st.integers(min_value=500, max_value=buf-1))

    return (buf, stopvalue)