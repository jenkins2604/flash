from behave import step
from hamcrest import assert_that, equal_to
from subprocess import call
from typing import Optional, Tuple
import requests
import json
import socket
import time

def send_command_to_EV_simulator(url):
    retry = 0
    assert url is not None, "undefined fault"
    while retry < 3:
        resp = requests.get(url)
        if resp.status_code == 200:
            break
        else:
            retry += 1
    assert resp.status_code == 200, f"error connecting EV Simulator, status code {resp.status_code}"

def find_meter_value(msg, info):
    data = msg["sampled_value"]
    for items in data:
        if (items["measurand"] + items["phase"] if "phase" in items else items["measurand"]) == info:
            return items["value"] + items["unit"]
    return None

def get_status_pack(pack, info, connector_id=0) -> Optional[Tuple[str, str]]:
    """
    Trigger Message and get status from OCPP Charge point
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 8001))
    time.sleep(10)
    command = "StatusQuery"
    sock.sendall(command.encode())
    time.sleep(3)
    sock.shutdown(socket.SHUT_WR)
    full_msg = ''
    while True:
        data = sock.recv(1024)
        if len(data) <= 0:
            break
        full_msg += data.decode("utf-8")
    try:
        message = json.loads(full_msg)
    except:
        return None
    
    if pack == "energyMeter":
        return find_meter_value(message["message"][pack][connector_id]["sampled_value"], info)
    else:
        return message["message"][pack][connector_id][info]

def set_charging_state(state):
    url = None
    if state == 'B':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=0&Relay15=0&Relay7=0&Relay8=0'
    elif state == 'C':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=0&Relay15=0&Relay7=1&Relay8=1'
    elif state == 'A':
        url = 'http://192.168.17.123/current_state.json?pw=admin&Relay2=1&Relay15=1'
    send_command_to_EV_simulator(url)
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
    send_command_to_EV_simulator(url)
    time.sleep(1)

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
    status_1 = get_status_pack("notificationStatus", "status", 1)
    status_2 = get_status_pack("notificationStatus", "status", 2)
    assert_that(status_1, equal_to(expect_status), 'connector 1')
    assert_that(status_2, equal_to(expect_status), 'connector 2')

@step('error code should be {error}')
def error_code_should_be(context, error):
    status_1 = get_status_pack("notificationStatus", "error_code", 1)
    status_2 = get_status_pack("notificationStatus", "error_code", 2)
    assert_that(status_1, equal_to(error), 'connector 1')
    assert_that(status_2, equal_to(error), 'connector 2')

@step('vendor error code should be {error}')
def vendor_error_code_should_be(context, error):
    status_1 = get_status_pack("notificationStatus", "vendor_error_code", 1)
    status_2 = get_status_pack("notificationStatus", "vendor_error_code", 2)
    assert_that(status_1, equal_to(error), 'connector 1')
    assert_that(status_2, equal_to(error), 'connector 2')
    
@step('reset to state A')
def reset_to_state_A(context):
    url = "http://192.168.17.123/current_state.json?pw=admin&SetAll=16394"
    send_command_to_EV_simulator(url)
    time.sleep(3)

@step('reset test station')
def reset_test_station(context):
    url = "http://192.168.17.123/current_state.json?pw=admin&SetAll=0"
    send_command_to_EV_simulator(url)
    url = "http://192.168.17.123/current_state.json?pw=admin&SetAll=16394"
    send_command_to_EV_simulator(url)

@step('wait for test station to start up')
def wait_for_test_station_to_start_up(context):
    errc = call("../../check.sh")
    assert errc == 0, f"can not start test station, status code {errc}"

@step('wait for {seconds}')
def wait_for(context, seconds):
    time.sleep(int(seconds))

