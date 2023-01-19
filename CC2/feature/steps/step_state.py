from behave import step
from hamcrest import assert_that, equal_to
from typing import Optional, Tuple
import requests
import json
import socket
import time


def get_status_pack(info) -> Optional[Tuple[str, str]]:
    """
    Trigger Message and get status from OCPP Charge point
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8001))
    time.sleep(10)
    message = "tm sn"
    sock.sendall(message.encode())
    time.sleep(3)
    sock.shutdown(socket.SHUT_WR)
    data = sock.recv(1024)
    try:
        status_pack = json.loads(data.decode())
    except:
        return None
    
    assert len(status_pack["message"]["notificationStatus"]) >= 3
    return status_pack["message"]["notificationStatus"][1][info], status_pack["message"]["notificationStatus"][2][info]

def set_charging_state(state):
    url = None
    if state == 'B':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=0&Relay15=0&Relay7=0&Relay8=0'
    elif state == 'C':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=0&Relay15=0&Relay7=1&Relay8=1'
    elif state == 'A':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=1&Relay15=1'
    retry = 0
    assert url is not None, "undefined state"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"
    time.sleep(5)


@step('the current state is {state}')
def step_the_current_state_is(context, state):
    set_charging_state(state)

@step('trigger fault {fault}')
def trigger_fault(context, fault):
    url = None
    if fault == 'residue current':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay13=1&Relay14=1'
    elif fault == 'shorted diode':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay5=1&Relay6=1'
    elif fault == 'contactor welded close':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay11=1&Relay12=1'
    retry = 0
    assert url is not None, "undefined fault"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"
    time.sleep(10)

@step('EV switch to {state}')
def step_EV_switch_to(context, state):
    set_charging_state(state)

@step('the EVSE should switch to state {state}')
def step_the_EVSE_should_switch_to_state(context, state):
    if state == 'B':
        expect_status = 'SuspendedEV'
    elif state == 'C':
        expect_status = 'Charging'
    elif state == 'A':
        expect_status = 'Available'
    elif state == 'F':
        expect_status = 'Faulted'
    elif state == 'SuspendedEVSE':
        expect_status = 'SuspendedEVSE'
    elif state == 'Finishing':
        expect_status = 'Finishing'
    result = get_status_pack("status")
    print(result)
    assert result is not None
    assert_that(result[0], equal_to(expect_status), 'connector 1')
    assert_that(result[1], equal_to(expect_status), 'connector 2')

@step('error code should be {error}')
def error_code_should_be(context, error):
    result = get_status_pack("vendor_error_code")
    print(result)
    assert result is not None
    assert_that(result[0], equal_to(error), 'connector 1')
    assert_that(result[1], equal_to(error), 'connector 2')
    
@step('reset to state A')
def reset_to_state_A(context):
    url = "http://192.168.17.123/current_state.json?pw=admin&Relay13=0&Relay14=0&Relay5=0&Relay6=0&Relay11=0&Relay12=0&Relay7=0&Relay8=0&Relay2=1&Relay15=1"
    retry = 0
    assert url is not None, "undefined fault"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1      
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"
    time.sleep(3)

@step('reset test station')
def reset_test_station(context):
    url = "http://192.168.17.123/current_state.json?pw=admin&SetAll=0"
    retry = 0
    assert url is not None, "undefined fault"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"

@step('wait for test station to start up')
def wait_for_test_station_to_start_up(context):
    while True:
        result = get_status_pack("status")
        if result == None:
            time.sleep(20)
            continue
        else:
            break

@step('wait for {seconds}')
def wait_for(context, seconds):
    time.sleep(int(seconds))

