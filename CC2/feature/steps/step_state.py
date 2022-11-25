from behave   import given, when, then
from hamcrest import assert_that, equal_to, is_not
import requests
import json
import socket
import time

def get_status_pack():
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
    res = ""
    data = sock.recv(1024)
    try:
        status_pack = json.loads(data.decode())
    except:
        return None
    
    return (status_pack["ntstatus"][1]["status"], status_pack["ntstatus"][2]["status"])
    

@given('the current state is {state}')
def step_the_current_state_is(context, state):
    if state == 'B':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=0&Relay8=0'
    elif state == 'C':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=1&Relay8=1'
    retry = 0
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"    
                
@when('EV switch to {state}')
def step_EV_switch_to(context, state):
    if state == 'B':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=0&Relay8=0'
    elif state == 'C':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay7=1&Relay8=1'
    retry = 0
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"

@then('the EVSE should switch to state {state}')
def step_the_EVSE_should_switch_to_state(context, state):
    if state == 'B':
        expect_status = 'SuspendedEV'
    elif state == 'C':
        expect_status = 'Charging'
    result = get_status_pack()
    assert result is not None
    assert_that(result[0], equal_to(expect_status), 'connector 1')
    assert_that(result[1], equal_to(expect_status), 'connector 2')
        
    
