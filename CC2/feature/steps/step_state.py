from behave import given, when, then
from hamcrest import assert_that, equal_to
from typing import Optional, Tuple
import requests
import json
import socket
import time


def get_status_pack() -> Optional[Tuple[str, str]]:
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
    return status_pack["message"]["notificationStatus"][1]["status"], status_pack["message"]["notificationStatus"][2]["status"]

def set_charging_state(state):
    url = None
    if state == 'F':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay11=1&Relay12=1'
    if state == 'B':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=0&Relay8=0'
    elif state == 'C':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=1&Relay8=1'
    retry = 0
    assert url is not None, "undefined state"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"

@given('the current state is {state}')
def step_the_current_state_is(context, state):
    set_charging_state(state)   
                
@when('EV switch to {state}')
def step_EV_switch_to(context, state):
    set_charging_state(state)

@then('the EVSE should switch to state {state}')
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
    result = get_status_pack()
    assert result is not None
    assert_that(result[0], equal_to(expect_status), 'connector 1')
    assert_that(result[1], equal_to(expect_status), 'connector 2')
