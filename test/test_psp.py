import sys
import time
import threading
import logging
import pytest
import numpy as np
import psp
from conftest import test_pvs, pvbase

if sys.version_info.major >= 3:
    long = int

logger = logging.getLogger(__name__)


def setup_pv(pvname, connect=True):
    pv = psp.PV(pvname)
    if connect:
        pv.connect(timeout=1.0)
    return pv


def test_server_start(server):
    pass


@pytest.mark.timeout(10)
@pytest.mark.parametrize('pvname', test_pvs)
def test_connect_and_disconnect(pvname):
    logger.debug('test_create_and_clear_channel %s', pvname)
    pv = setup_pv(pvname)
    assert pv.isconnected
    pv.disconnect()


@pytest.mark.timeout(10)
@pytest.mark.parametrize('pvname', test_pvs)
def test_get(pvname):
    logger.debug('test_get_data %s', pvname)
    pv = setup_pv(pvname)
    value = pv.get()
    assert value is not None


@pytest.mark.timeout(10)
@pytest.mark.parametrize('pvname', test_pvs)
def test_put_get(pvname):
    logger.debug('test_put_get %s', pvname)
    pv = setup_pv(pvname)
    old_value = pv.get()
    pv_type = type(old_value)
    logger.debug('%s is of type %s', pvname, pv_type)
    if pv_type in (int, long, float):
        new_value = old_value + 1
    elif pv_type == str:
        new_value = "putget"
    elif pv_type == tuple:
        new_value = tuple([1] * len(old_value))
    logger.debug('caput %s %s', pvname, new_value)
    pv.put(new_value, timeout=1.0)
    assert pv.get() == new_value


@pytest.mark.timeout(10)
@pytest.mark.parametrize('pvname', test_pvs)
def test_monitor(pvname):
    logger.debug('test_subscribe %s', pvname)
    pv = setup_pv(pvname)
    old_value = pv.get()
    pv_type = type(old_value)
    pv.monitor()
    logger.debug('%s is of type %s', pvname, pv_type)
    if pv_type in (int, long, float):
        new_value = old_value + 1
    elif pv_type == str:
        new_value = "putmon"
    elif pv_type == tuple:
        new_value = tuple([1] * len(old_value))
    logger.debug('caput %s %s', pvname, new_value)
    pv.put(new_value)
    n = 0
    while n < 10 and pv.value != new_value:
        time.sleep(0.1)
        n += 1
    assert pv.value == new_value


@pytest.mark.timeout(10)
@pytest.mark.parametrize('pvname', test_pvs)
def test_misc(pvname):
    logger.debug('test_misc %s', pvname)
    pv = setup_pv(pvname)
    assert isinstance(pv.host(), str)
    assert isinstance(pv.state(), int)
    assert isinstance(pv.count, int)
    assert isinstance(pv.type(), str)
    assert isinstance(pv.rwaccess(), int)


@pytest.mark.timeout(10)
def test_waveform():
    logger.debug('test_waveform')
    pv = setup_pv(pvbase + ":WAVE")
    # Do as a tuple
    pv.use_numpy = False
    val = pv.get()
    assert isinstance(val, tuple)
    assert len(val) == pv.count
    # Do as a np.ndarray
    pv.use_numpy = True
    val = pv.get()
    assert isinstance(val, np.ndarray)
    assert len(val) == pv.count


@pytest.mark.timeout(10)
def test_threads():
    logger.debug('test_threads')

    def some_thread_thing(pvname):
        psp.utils.ensure_context()
        pv = setup_pv(pvname)
        val = pv.get()
        assert isinstance(val, tuple)

    pvname = pvbase + ":WAVE"
    thread = threading.Thread(target=some_thread_thing, args=(pvname,))
    thread.start()
    thread.join()
