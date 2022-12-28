import asyncio
import concurrent.futures
import logging
import random
import string
import json
from datetime import datetime, timedelta
from functools import partial

import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call_result, call
from ocpp.v16.enums import Action, AuthorizationStatus, AvailabilityType, RegistrationStatus, DataTransferStatus, \
    ChargingProfilePurposeType, ChargingProfileKindType, ResetType, ResetStatus, UpdateType, \
    GetCompositeScheduleStatus, MessageTrigger

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
pool = concurrent.futures.ThreadPoolExecutor()

class ChargePoint(CP):
    counter = 0

    # Variables used in switching charging profiles T5546
    profileFirst = True
    switchCounter = 0

    # Multiple SetChargingProfiles
    stack_level = 0

    # SendLocalList
    list_version = 0

    status_pack = {"message" : {"vendorId": "NA", "updateStatus": "NA", "notificationStatus": [{}, {}, {}]} }
    
    @on(Action.BootNotification)
    def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        if self.counter < 3:
            self.counter += 1
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=240,
                status=RegistrationStatus.accepted
            )
        else:
            return call_result.BootNotificationPayload(
                current_time=datetime.utcnow().isoformat(),
                interval=10,
                status=RegistrationStatus.accepted
            )

    @on(Action.Heartbeat)
    def on_heartbeat(self, **kwargs):
        return call_result.HeartbeatPayload(
            current_time=datetime.utcnow().isoformat(),
           )

    @on(Action.DataTransfer)
    def on_data_transfer(self, message_id, **kwargs):
        return call_result.DataTransferPayload(status=DataTransferStatus.unknownMessageId)

    @on(Action.DiagnosticsStatusNotification)
    def on_diagnostics_status_notification(self, **kwargs):
        return call_result.DiagnosticsStatusNotificationPayload()

    @on(Action.MeterValues)
    def on_meter_values(self, **kwargs):
        return call_result.MeterValuesPayload()

    @on(Action.Authorize)
    def on_authorize(self, id_tag, **kwargs):
        id_tag_info = {"status": AuthorizationStatus.accepted}
        return call_result.AuthorizePayload(id_tag_info=id_tag_info)

    @on(Action.StartTransaction)
    def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        id_tag_info = {"status": AuthorizationStatus.accepted}
        self.counter += 1
        return call_result.StartTransactionPayload(id_tag_info=id_tag_info, transaction_id=self.counter)

    @on(Action.StopTransaction)
    def on_stop_transaction(self, **kwargs):
        id_tag_info = {"status": AuthorizationStatus.accepted}
        return call_result.StopTransactionPayload(id_tag_info=id_tag_info)

    @on(Action.StatusNotification)
    def on_status_notification(self, connector_id, error_code, status, timestamp, **kwargs):
        
        new_status = call.StatusNotificationPayload(connector_id, error_code, status, timestamp, **kwargs)
        if len(self.status_pack["message"]["notificationStatus"]) > connector_id:
            self.status_pack["message"]["notificationStatus"][connector_id] = new_status.__dict__
        return call_result.StatusNotificationPayload()

    @on(Action.FirmwareStatusNotification)
    def on_firmware_status_notification(self, status, **kwargs):
        logging.info(status)
        if status != "Idle":
            self.status_pack["message"]["updateStatus"] = status
        return call_result.FirmwareStatusNotificationPayload()

    async def send_reserve_now(self, connector, tag, reservation, **kwargs):
        dt = datetime.utcnow()
        dt += timedelta(seconds=900)
        request = call.ReserveNowPayload(connector_id=connector, expiry_date=dt.isoformat(),
                                         id_tag=tag, reservation_id=reservation)
        response = await self.call(request)
        logging.info(response)

    async def send_cancel_reservation(self, reservation, **kwargs):
        request = call.CancelReservationPayload(reservation_id=reservation)
        response = await self.call(request)
        logging.info(response)

    async def send_change_availability_all_to_operative(self, **kwargs):
        request = call.ChangeAvailabilityPayload(connector_id=0, type=AvailabilityType.operative)
        response = await self.call(request)

    async def send_change_availability(self, **kwargs):
        request = call.ChangeAvailabilityPayload(connector_id=1, type=AvailabilityType.inoperative)
        response = await self.call(request)

    async def send_hardreset(self, **kwargs):
        request = call.ResetPayload(type=ResetType.hard)
        response = await self.call(request)
        logging.info(response)

    async def send_set_charging_profiles_limits_test(self, **kwargs):
        periods = []
        for i in range(10):
            p = {'limit': 6 + i % 20,
                 'startPeriod': 10 * i}
            periods.append(p)
        request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
            "chargingProfileId": self.stack_level,
            "stackLevel": self.stack_level,
            "chargingProfilePurpose": ChargingProfilePurposeType.txdefaultprofile,
            "chargingProfileKind": ChargingProfileKindType.relative,
            "chargingSchedule": {
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": periods
            }
        })
        self.stack_level += 1
        response = await self.call(request)

    # Switch between two charging profiles. (T5546)
    async def send_set_charging_profile(self, **kwargs):
        logging.info('sending charge profile')
        if self.profileFirst:
            self.profileFirst = False
            logging.info('profile one (%s)', self.switchCounter)
            request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
                "chargingProfileId": 123,
                "stackLevel": 1,
                # "recurrencyKind": RecurrencyKind.daily,
                "chargingProfilePurpose": ChargingProfilePurposeType.txdefaultprofile,
                "chargingProfileKind": ChargingProfileKindType.relative,
                "chargingSchedule": {
                    "chargingRateUnit": "A",
                    "chargingSchedulePeriod": [{
                        "limit": 10,
                        "numberPhases": 3,
                        "startPeriod": 0
                    }]
                }
            })
        else:
            self.profileFirst = True
            logging.info('profile two (%s)', self.switchCounter)
            self.switchCounter += 1
            request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
                "chargingProfileId": 123,
                "stackLevel": 1,
                # "recurrencyKind": RecurrencyKind.daily,
                "chargingProfilePurpose": ChargingProfilePurposeType.txdefaultprofile,
                "chargingProfileKind": ChargingProfileKindType.relative,
                "chargingSchedule": {
                    "chargingRateUnit": "A",
                    "chargingSchedulePeriod": [{
                        "limit": 6,
                        "numberPhases": 3,
                        "startPeriod": 0
                    }]
                }
            })

    async def send_get_composite_schedule(self, connector_id, duration, **kwargs):
        request = call.GetCompositeSchedulePayload(connector_id=connector_id, duration=duration)
        response = await self.call(request)
        logging.info(response)

    # Send a local list. Validates how many items can be sent in one go.
    async def send_locallist(self, **kwargs):
        if self.list_version == 0:
            update_type = UpdateType.full
        else:
            update_type = UpdateType.differential
        self.list_version += 1
        letters = string.ascii_uppercase
        authdata = []
        id_tag_info = {'status': AuthorizationStatus.accepted}
        for i in range(0, 5):
            id_tag = ''.join(random.choice(letters) for i in range(20))

            authdata.append({'idTag': id_tag, 'idTagInfo': id_tag_info})
        request = call.SendLocalListPayload(list_version=self.list_version,
                                            update_type=update_type,
                                            local_authorization_list=authdata)
        response = await self.call(request)

    async def send_unlock(self, connector_id, **kwargs):
        request = call.UnlockConnectorPayload(connector_id=connector_id)
        response = await self.call(request)
        if response.status == "UnlockFailed":
            logging.info('Unlock failed')

    async def send_set_charging_recurring_profile(self, **kwargs):
        logging.info('sending charge recurring profile')
        request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
            "chargingProfileId": 251645,
            "stackLevel": 0,
            "chargingProfilePurpose": ChargingProfilePurposeType.txdefaultprofile,
            "recurrencyKind": "Daily",
            "chargingProfileKind": ChargingProfileKindType.recurring,
            "chargingSchedule": {
                "duration": 86400,
                "startSchedule": datetime.utcnow().isoformat(),
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": [{
                    "startPeriod": 0,
                    "limit": 7.0,
                    "numberPhases": 3
                }, {
                    "startPeriod": 180,
                    "limit": 13.0,
                    "numberPhases": 3
                }]
            }
        })
        response = await self.call(request)
        logging.info(response)

    async def send_set_charging_relative_profile(self, **kwargs):
        logging.info('sending charge relative profile')
        request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
            "chargingProfileId": 486369,
            "stackLevel": 1,
            "chargingProfilePurpose": ChargingProfilePurposeType.txdefaultprofile,
            "chargingProfileKind": ChargingProfileKindType.relative,
            "chargingSchedule": {
                "duration": 120,
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": [{
                    "startPeriod": 0,
                    "limit": 14.0,
                    "numberPhases": 3
                }]
            }
        })
        response = await self.call(request)
        logging.info(response)

    async def send_set_charging_spike_profile(self, **kwargs):
        logging.info('sending charge spike profile')
        request = call.SetChargingProfilePayload(connector_id=1, cs_charging_profiles={
            "chargingProfileId": 599515,
            "stackLevel": 1,
            "transactionId": 369476,
            "chargingProfilePurpose": ChargingProfilePurposeType.txprofile,
            "chargingProfileKind": ChargingProfileKindType.absolute,
            "chargingSchedule": {
                "duration": 120,
                "startSchedule": datetime.utcnow().isoformat(),
                "chargingRateUnit": "A",
                "chargingSchedulePeriod": [{
                    "startPeriod": 0,
                    "limit": 15.0,
                    "numberPhases": 3
                }]
            }
        })
        response = await self.call(request)
        logging.info(response)

    async def send_set_charging_custom_profile(self, charging_profile, connector, **kwargs):
        logging.info("sending custom profile")
        request = call.SetChargingProfilePayload(connector_id=connector, cs_charging_profiles=charging_profile)
        response = await self.call(request)
        logging.info(response)

    async def send_clear_charging_profile(self, **kwargs):
        request = call.ClearChargingProfilePayload()
        response = await self.call(request)
        logging.info(response)

    async def send_start_transaction(self, id_tag, connector_id, **kwargs):
        request = call.RemoteStartTransactionPayload(id_tag=id_tag, connector_id=connector_id)
        response = await self.call(request)
        logging.info(response)

    async def send_stop_transaction(self, transaction_id, **kwargs):
        request = call.RemoteStopTransactionPayload(transaction_id=transaction_id)
        response = await self.call(request)
        logging.info(response)

    async def send_nanogrid_status(self, **kwargs):
        request = call.DataTransferPayload(vendor_id="se.chargestorm", message_id="NgStatus")
        response = await self.call(request)
        logging.info(response)

    async def send_nanogrid_client_status(self, **kwargs):
        request = call.DataTransferPayload(vendor_id="com.ctek", message_id="NgClientStatus")
        response = await self.call(request)
        logging.info(response)

    async def send_generic_datatransfer(self, vendorid="com.ctek", messageid=None, data=None, **kwargs):
        request = call.DataTransferPayload(vendor_id=vendorid, message_id=messageid, data=data)
        response = await self.call(request)
        logging.info(response.status)

    async def send_random_sized_datatransfer(self, vendorid="com.ctek", messageid=None, size=10000, **kwargs):
        data = ''.join(random.choices(string.ascii_letters + string.digits, k=size))
        if messageid is None:
            messageid = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        request = call.DataTransferPayload(vendor_id=vendorid, message_id=messageid, data=data)
        response = await self.call(request)
        logging.info(response.status)

    async def send_update_firmware(self, **kwargs):
        """ Run "python -m SimpleHTTPServer" in the folder where you have your firmware file.
        Find your IP address and use port 8000 as file location. Eg. "http://192.168.7.1:8000/upgrade.bin"
        """
        firmwareLocation = "http://192.168.7.1:8000/upgrade.bin"
        request = call.UpdateFirmwarePayload(location=firmwareLocation, retrieve_date=datetime.utcnow().isoformat())
        response = await self.call(request)

    async def send_change_configuration(self, key, value, **kwargs):
        request = call.ChangeConfigurationPayload(key=key, value=value)
        response = await self.call(request)

    async def send_get_configuration(self, key=None, **kwargs):
        if key is None:
            logging.info("None")
            request = call.GetConfigurationPayload()
        else:
            logging.info("Not None")
            request = call.GetConfigurationPayload([key])
        response = await self.call(request)

    async def send_trigger_message(self, message=None, connector_id=None, **kwargs):
        if message is None:
            logging.error("Missing message type")
            return
        if connector_id is None:
            request = call.TriggerMessagePayload(requested_message=message)
        else:
            request = call.TriggerMessagePayload(requested_message=message, connector_id=connector_id)
        response = await self.call(request)
        print('request: ', request)
        print('response: ' , response)

    async def send_clear_cache(self, **kwargs):
        request = call.ClearCachePayload()
        response = await self.call(request)
        logging.info(response)

    async def send_get_diagnostics(self, url=None, **kwargs):
        if url is None:
            url = "ftp://anonymous:none@ftp.oamportal.com"
        request = call.GetDiagnosticsPayload(location=url)
        response = await self.call(request)
        logging.info(response)


class CentralSystem:
    def __init__(self):
        self._chargers = {}

    def register_charger(self, cp: ChargePoint) -> asyncio.Queue:
        """ Register a new ChargePoint at the CSMS. The function returns a
        queue.  The CSMS will put a message on the queue if the CSMS wants to
        close the connection.
        """
        queue = asyncio.Queue(maxsize=1)

        # Store a reference to the task so we can cancel it later if needed.
        task = asyncio.create_task(self.start_charger(cp, queue))
        self._chargers[cp] = task

        return queue

    async def start_charger(self, cp, queue):
        """ Start listening for message of charger. """
        try:
            await cp.start()
        except Exception as e:
            print(f"Charger {cp.id} disconnected: {e}")
        finally:
            # Make sure to remove reference to charger after it disconnected.
            del self._chargers[cp]

            # This will unblock the `on_connect()` handler and the connection
            # will be destroyed.
            await queue.put(True)

    def connected_chargers(self):
        return self._chargers

    def disconnect_charger(self, id: str):
        for cp, task in self._chargers.items():
            if cp.id == id:
                task.cancel()
                return

        raise ValueError(f"Charger {id} not connected.")


async def on_connect(websocket, path, csms):
    """ For every new charge point that connects, create a ChargePoint instance
    and start listening for messages.

    """

    charge_point_id = path.strip('/')
    cp = ChargePoint(charge_point_id, websocket)

    logging.info('CP is connected')
    # If this handler returns the connection will be destroyed. Therefore we need some
    # synchronization mechanism that blocks until CSMS wants to close the connection.
    # An `asyncio.Queue` is used for that.
    queue = csms.register_charger(cp)
    await queue.get()


async def create_websocket_server(csms: CentralSystem):
    handler = partial(on_connect, csms=csms)
    return await websockets.serve(handler, "0.0.0.0", 8080, subprotocols=["ocpp1.6"])


async def command_terminal(csms: CentralSystem):
    logging.info("Please run 'nc localhost 8001' in a shell or use 'CommandGUI.py'.")
    await server_begin(csms)


async def handle_commands(receive_command, sock, csms):
    command = ""
    while command != "quit":
        
        data = await receive_command.read(1024)
        
        argument = data.decode().split()
        print("argument: ", argument)
        if data == "b''" or len(argument) == 0:
            break
        command = argument[0]
        if not csms.connected_chargers():
            sock.write("ErrorCS: No CS connected.\n".encode())
            continue
        elif len(csms.connected_chargers()) != 1:
            sock.write("ErrorCS: Too many CS's connected.\n".encode())
            continue
        
        cp, task = list(csms.connected_chargers().items())[0]
        logging.info("Sending command '{}' to {}".format(command, cp.id))
        
        if command == "quit":
            logging.info("Quit")
            sock.write("Quit".encode())
        elif command == "reboot":
            await cp.send_hardreset()
        elif command == "unlock":
            connector_id = 1
            if len(argument) > 1:
                connector_id = int(argument[1])
            await cp.send_unlock(connector_id)
        elif command == "profile1":
            await cp.send_set_charging_recurring_profile()
        elif command == "profile2":
            await cp.send_set_charging_relative_profile()
        elif command == "profile3":
            await cp.send_set_charging_spike_profile()
        elif command == "profileCustom":
            if len(argument) > 2:
                if argument[2] == "0" or argument[2] == "1" or argument[2] == "2":
                    connector_id = argument[2]
                    try:
                        f = open(argument[1], "r")
                        charging_profile = json.load(f)
                    except FileNotFoundError:
                        sock.write("Error: file \"{}\" not found!\n".format(argument[1]).encode())
                    except json.JSONDecodeError:
                        sock.write("Error: {} is not a JSON file!\n".format(argument[1]).encode())
                    else:
                        await cp.send_set_charging_custom_profile(charging_profile, int(connector_id))
                    finally:
                        f.close()
            else:
                sock.write("Error: Too few arguments\nUsage: {} <JSON file> <connector>\n".format(command).encode())
        elif command == "clear":
            await cp.send_clear_charging_profile()
        elif command == "start":
            if len(argument) > 1:
                if argument[1] == "1" or argument[1] == "2":
                    id_tag = "960E3F97"
                    if argument[2] != "":
                        id_tag = argument[2]
                    await cp.send_start_transaction(id_tag, (int(argument[1])))
            else:
                sock.write("Error: Too few arguments\nUsage: {} <connector> <id tag>\n".format(command).encode())
        elif command == "stop":
            if len(argument) > 1:
                await cp.send_stop_transaction(int(argument[1]))
            else:
                sock.write("Error: Too few arguments\nUsage: {} <transactionId>\n".format(command).encode())
        elif command == "NgStatus":
            await cp.send_nanogrid_status()
        elif command == "NgClientStatus":
            await cp.send_nanogrid_client_status()
        elif command == "DataTransfer" or command == "dt":
            if len(argument) == 2:
                await cp.send_generic_datatransfer(argument[1])
            elif len(argument) == 3:
                await cp.send_generic_datatransfer(argument[1], argument[2])
            elif len(argument) > 3:
                data = ' '.join(argument[3:])
                data = data.strip('"')
                await cp.send_generic_datatransfer(argument[1], argument[2], data)
            else:
                sock.write(
                    "Error: Wrong number of arguments!\nUsage: {} <vendorId> [<messeageId> [<data>]]\n".format(command).encode())
        elif command == "RandDataTransfer" or command == "rdt":
            if len(argument) == 1:
                await cp.send_random_sized_datatransfer()
            elif len(argument) == 2:
                try:
                    length = int(argument[1])
                    await cp.send_random_sized_datatransfer(size=length)
                except ValueError:
                    logging.error("No integer supplied")
        elif command == "Update":
            await cp.send_update_firmware()
        elif command == "ChangeConfiguration" or command == "CC":
            if len(argument) > 2:
                await cp.send_change_configuration(argument[1], argument[2])
            else:
                sock.write("Error: Too few arguments.\nUsage: {} <key> <value>\n".format(command).encode())
        elif command == "GetConfiguration" or command == "GC":
            logging.info("What? {}".format(argument))
            if len(argument) > 1:
                logging.info(argument)
                await cp.send_get_configuration(argument[1])
            else:
                logging.info("No arg")
                await cp.send_get_configuration()
            logging.info("Done")
        elif command == "GetCompositeSchedule" or command == "GCS" or command == "gcs":
            if len(argument) == 3:
                await cp.send_get_composite_schedule(int(argument[1]), int(argument[2]))
            else:
                logging.error("Usage: {} <connectorId> <duration>".format(argument[0]))
                sock.write("Error: Usage: {} <connectorId> <duration>\n".format(argument[0]).encode())
        elif command == "TriggerMessage" or command.lower() == "tm":
            if len(argument) < 2 or len(argument) > 3:
                logging.error("Usage: {} <requestedMessage> [connectorId]".format(argument[0]))
                sock.write("Error: Usage: {} <requestedMessage> [connectorId]".format(argument[0]).encode())
                continue
            req_message = argument[1]
            message = None
            if req_message == "BootNotification" or req_message.lower() == "bn":
                message = MessageTrigger.boot_notification
            elif req_message == "DiagnosticStatusNotification" or req_message.lower() == "dsn":
                message = MessageTrigger.diagnostics_status_notification
            elif req_message == "FirmwareStatusNotification" or req_message.lower() == "fsn":
                message = MessageTrigger.firmware_status_notification
            elif req_message == "Heartbeat" or req_message.lower() == "hb":
                message = MessageTrigger.heartbeat
            elif req_message == "MeterValues" or req_message.lower() == "mv":
                message = MessageTrigger.meter_values
            elif req_message == "StatusNotification" or req_message.lower() == "sn":
                message = MessageTrigger.status_notification
            else:
                logging.error("err: Usage: {} <requestedMessage> [connectorId]".format(argument[0]))
                sock.write("Error: Usage: {} <requestedMessage> [connectorId]".format(argument[0]).encode())
                continue
            connector_id = None
            if len(argument) == 3:
                connector_id = int(argument[2])

            if connector_id is None:
                await cp.send_trigger_message(message)
            else:
                await cp.send_trigger_message(message, connector_id)
            sock.write("{}".format(json.dumps(cp.status_pack)).encode())
        elif command == "ClearCache":
            await cp.send_clear_cache()
        elif command == "GetDiagnostics" or command == "gd":
            if len(argument) == 2:
                await cp.send_get_diagnostics(argument[1])
            else:
                await cp.send_get_diagnostics()
        elif command == "ReserveNow" or command == "rn":
            if len(argument) > 3:
                await cp.send_reserve_now(int(argument[1]), argument[2], int(argument[3]))
            else:
                sock.write(
                    "Error: Too few arguments.\nUsage: {} <connectorId> <tagId> <reservationId>\n".format(command).encode())
        elif command == "CancelReservation":
            if len(argument) > 1:
                await cp.send_cancel_reservation(int(argument[1]))
            else:
                sock.write("Error: Too few arguments.\nUsage: {} <reservationId>\n".format(command).encode())
        else:
            sock.write("Error: Unknown command: {}\n".format(command).encode())
            logging.error("Unknown command: {}\n".format(command))

    sock.close()


async def server_begin(csms: CentralSystem):
    server = await asyncio.start_server(lambda r, w: handle_commands(r, w, csms), 'localhost', 8001)
    address = server.sockets[0].getsockname()
    print(f'Serving on {address}')

    async with server:
        await server.serve_forever()


async def main():
    csms = CentralSystem()
    task_command = asyncio.create_task(command_terminal(csms))
    server = await create_websocket_server(csms)
    logging.info('server up and running: connect SUT to ws://192.168.7.1:8080')
    await asyncio.wait([server.wait_closed(), task_command])


if __name__ == '__main__':
    asyncio.run(main())

