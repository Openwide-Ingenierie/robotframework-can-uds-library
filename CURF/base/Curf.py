#!/usr/bin/env python3

#  Copyright 2019 SMILE SA
#  Author: Jean LE QUELLEC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# Can Specific python libs
import can
import cantools
import isotp

# Common python libs
import time
import datetime as dt
import binascii
import os

# Libs created for this project
from averagetime import AverageTime


class Curf:
    def __init__(self):
        """ The class to handle CURF
        You have to instanciate CAN BUS with set_can() method
        """
        self.is_set = False
        self.is_isotp = False
        self.statusOfDTCbits = {"0": "testFailed",
                                "1": "testFailedThisMonitoringCycle",
                                "2": "pendingDTC",
                                "3": "confirmedDTC",
                                "4": "testNotCompletedSinceLastClear",
                                "5": "testFailedSinceLastClear",
                                "6": "testNotCompletedThisMonitoringCycle",
                                "7": "warningIndicatorRequested"}

    def waiting(self, wait_time=1.0):
        """ Wait the given time
        Keyword argument:
        wait_time -- the time to wait in second (default 1.0)
        """
        time.sleep(float(wait_time))

    def remove_char_from(self, nb_of_bits, payload):
        """ Remove the first n char from a payload and return result
        Keyword arguments:
        nb_of_bits -- number of char to remove
        payload -- payload to remove char
        """
        return payload[int(nb_of_bits):]

    def length_must_be(self, nb_of_bytes, payload):
        """ Evaluate the lenght of a payload
        Keyword arguments:
        nb_of_bytes -- Wanted size in bytes
        payload -- Payload to check
        """
        if ((len(payload)//2) == int(nb_of_bytes)):
            pass
        else:
            raise AssertionError("Bad Length! Wanted Length for Payload: " +
                                 payload+" Is: "+nb_of_bytes +
                                 " But Was: "+str((len(payload)//2)))

    def curf_error_handler(self, error):
        raise AssertionError('Curf error happened : %s - %s' %
                             (error.__class__.__name__, str(error)))

    def set_can(self, interface, channel, bitrate, db=None, test_name=None):
        """ Set the CAN BUS
        Keyword arguments:
        interface -- can interface (socketcan, vector, ...)
        channel -- can channel (can0, vcan0, ...)
        bitrate -- can bitrate (125000, 500000, ...)
        db -- can database (arxml,dbc,kcd,sym,cdd)
        test_name -- Name of test case

        See https://cantools.readthedocs.io/en/latest/#about
        See https://python-can.readthedocs.io/en/master/interfaces.html
        """
        dt_now = dt.datetime.now()
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.db_file = db
        self.bus = can.interface.Bus(
            bustype=self.interface, channel=self.channel, bitrate=self.bitrate)
        self.logbus = can.ThreadSafeBus(
            interface=self.interface, channel=self.channel)
        if db is not None and db != 'None':
            self.db = cantools.database.load_file(db)
            self.db_default_node = self.db.nodes[0].name
        path = os.getcwd()
        path = path + "/outputs/" + ("%d%02d%02d/" % (dt_now.year,
                                                                    dt_now.month,
                                                                    dt_now.day))
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        output_candump_filename = path + ("%s_%d%02d%02d_%02d%02d%02d" % (test_name,
                                                                    dt_now.year,
                                                                    dt_now.month,
                                                                    dt_now.day,
                                                                    dt_now.hour,
                                                                    dt_now.minute,
                                                                    dt_now.second))
        self.logger = can.Logger(output_candump_filename)
        self.notifier = can.Notifier(self.logbus, [self.logger])
        self.is_set = True

    def end_can(self):
        """ Stop the CAN BUS
        """
        self.notifier.remove_listener(self.logger)
        self.logger.stop()

    def get_message_name_by_signal(self, signal_name):
        """ Search message_name in Database by signal
        Keyword argument:
        signal_name -- The signal name for whom to search for the message
        """
        is_in_db = False
        for message in self.db.messages:
            for signal in message.signals:
                if signal_name == signal.name:
                    msg_name = message.name
                    is_in_db = True
                    return msg_name
        if not(is_in_db):
            return None

    def get_next_raw_can(self):
        """ Return the next received Can Frame
        """
        return self.bus.recv(3)

    def get_can_config(self):
        """ Return the CAN configuration
        """
        return self.bus.channel_info

    def get_can_state(self):
        """ Return the CAN bus state
        """
        return self.bus.state

    def set_isotp(self, source, destination,
                  addr_mode='Normal_29bits', test_name=None):
        """ Set ISO-TP protocol
        Keyword Argument:
        source -- Sender address
        destination -- Receiver address
        addr_mode -- Adressing mode (default Normal_29bits)
        """
        if addr_mode == 'Normal_29bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Normal_29bits,
                rxid=int(destination, 16),
                txid=int(source, 16))
        elif addr_mode == 'Normal_11bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Normal_11bits,
                rxid=int(destination, 16),
                txid=int(source, 16))
        elif addr_mode == 'Mixed_11bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Mixed_11bits,
                rxid=int(destination, 16),
                txid=int(source, 16), address_extension=0x99)
        elif addr_mode == 'Mixed_29bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Mixed_29bits,
                source_address=int(source, 16),
                target_address=int(destination, 16), address_extension=0x99)
        elif addr_mode == 'NormalFixed_29bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.NormalFixed_29bits,
                target_address=int(destination, 16),
                source_address=int(source, 16))
        elif addr_mode == 'Extended_11bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Extended_11bits,
                rxid=int(destination, 16),
                txid=int(source, 16),
                source_address=0x55,
                target_address=0xAA)
        elif addr_mode == 'Extended_29bits':
            self.isotp_addr = isotp.Address(
                isotp.AddressingMode.Extended_29bits,
                rxid=int(destination, 16),
                txid=int(source, 16),
                source_address=0x55,
                target_address=0xAA)
        else:
            raise AssertionError(
                """Uncompatible addressing\nSee
                https://can-isotp.readthedocs.io/en/latest/isotp/
                examples.html#different-type-of-addresses""")

        self.isotp_stack = isotp.CanStack(
            bus=self.bus, address=self.isotp_addr,
            error_handler=self.curf_error_handler)
        self.is_isotp = True

    def send_frame(self, frame_id, frame_data):
        """ Send a CAN frame
        Keyword arguments:
        frame_id -- ID to send
        frame_data -- Data to send
        """
        frame_data = [frame_data[i:i+2] for i in range(0, len(frame_data), 2)]
        frame_data = [int(x, 16) for x in frame_data]
        frame = can.Message(arbitration_id=int(frame_id, 16), data=frame_data)
        self.bus.send(frame)

    def send_signal(self, signal_name, value):
        """ Send a CAN signal from Database
        Keyword arguments:
        signal_name -- Name of the signal to send
        value -- Value of the signal to send
        """
        signal_dict = {signal_name: float(value)}
        message_to_send = self.get_message_name_by_signal(signal_name)
        message_to_send = self.db.get_message_by_name(message_to_send)
        if message_to_send is not None:
            for signal in message_to_send.signals:
                if signal.name != signal_name and signal is not None:
                    signal_dict[signal.name] = 0.0

            message_to_send = self.db.get_message_by_name(message_to_send.name)
            data = message_to_send.encode(signal_dict)
            message = can.Message(
                arbitration_id=message_to_send.frame_id, data=data)
            print(message)
            self.bus.send(message)
        else:
            raise AssertionError('Signal : %s is not in Database' %
                                 (signal_name))

    # def send_signals(self,signal_dict):

    def check_msg(self, msg_name, time_out,
                  check_not_received, node_name=None):
        """Check the reception of given message
        with the given time out value
        Keyword arguments:
        msg_name -- message expected to be received
        time_out -- timeout value in second for the reception
        check_not_received -- the parameters to decide
                              either check reception or
                              check no-reception
                              check_not_received = True if
                              we want to check the no-reception
        node_name -- Node ID (optional)
        """
        if node_name is None or node_name == 'None':
            node_name = self.db_default_node
        tester = cantools.tester.Tester(
            dut_name=node_name, database=self.db, can_bus=self.bus)
        res = tester.expect(msg_name, signals=None, timeout=int(time_out))
        print(res)
        if res is not None:
            if check_not_received == 'False':
                pass
            elif check_not_received == 'True':
                raise AssertionError('Message : %s was received in:%d Seconds'
                                     % (msg_name, int(time_out)))
        else:
            if check_not_received == 'False':
                raise AssertionError('No Message : %s received in:%d Seconds'
                                     % (msg_name, int(time_out)))
            elif check_not_received == 'True':
                pass

    def check_frame(self, expect_id, expect_data, timeout, node_name=None):
        """Check the reception of give frame
        with the given time out value
        Keyword arguments:
        expect_id -- frame expected ID to be received
        expect_data -- frame expected data to be received
        timeout -- timeout value in second for the reception
        node_name -- Node ID (optional)
        """
        expect_id = expect_id.upper()
        expect_id = "0X"+expect_id
        if expect_data != 'ANY':
            expect_data = int(expect_data, 16)
        end_time = time.time()+float(timeout)
        if node_name is None or node_name == 'None':
            node_name = self.db_default_node
        while 1:
            received_frame = self.bus.recv(float(timeout))
            print(received_frame)
            received_id = str(hex(received_frame.arbitration_id)).upper()
            received_data = int(binascii.hexlify(received_frame.data), 16)
            if received_frame is not None and received_id == expect_id:
                if expect_data == "ANY":
                    break
                elif received_data == expect_data:
                    break
                elif expect_data == "NoReception":
                    raise AssertionError('Frame : %s was received with ID: %s'
                                         % (received_frame, received_id))
                else:
                    raise AssertionError("""Frame : %s received with good ID: %s
                                         \nBut with Data: %s instead of: %s"""
                                         % (received_frame, received_id,
                                            received_data, expect_data))

            elif received_frame is None and expect_data == "NoReception":
                break
            elif received_frame is None and expect_data != "NoReception":
                raise AssertionError('No Frame was received')
            elif received_frame is not None and received_id != expect_id and time.time() > end_time:
                raise AssertionError("""Frame : %s received with bad ID: %s\n
                                     With Data: %s instead of ID: %s""" %
                                     (received_frame, received_id,
                                      received_data, expect_id))
            else:
                continue
        pass

    def check_signal(self, signal_name, expect_value,
                     time_out, node_name=None):
        """Check the reception of give signal
        with the given time out value
        Keyword arguments:
        signal_name -- signal expected name to be received
        expect_value -- signal expected value to be received
        time_out -- timeout value in second for the reception
        node_name -- Node ID (optional)
        """
        if node_name is None or node_name == 'None':
            node_name = self.db_default_node
        tester = cantools.tester.Tester(
            dut_name=node_name, database=self.db, can_bus=self.bus)
        message_to_send = self.get_message_name_by_signal(signal_name)
        if message_to_send is not None:
            res = tester.expect(
                message_to_send, signals=None, timeout=int(time_out))
            if res is not None:
                for key, value in res.items():
                    if key == signal_name:
                        if value == expect_value:
                            pass
                        elif expect_value == 'NoReception':
                            raise AssertionError('Signal : %s was received' %
                                                 (key))
                        else:
                            raise AssertionError(""""Signal : %s was received but
                                                 value is: %s instead of: %s"""
                                                 % (key, value, expect_value))
            elif res is None and expect_value == 'NoReception':
                pass
            else:
                raise AssertionError("""Signal : %s was not received
                                     in timeout: %f""" %
                                     (signal_name, float(time_out)))
        else:
            raise AssertionError('Signal : %s was not in database' %
                                 (signal_name))

    def check_period(self, id_frame, expect_period, times):
        """Check the periodicity of given frame ID
        Keyword arguments:
        expect_id -- frame expected ID to be received
        expect_period -- expected period in second
        times -- number of measured frame
        """
        timeOut = float(expect_period)*int(times)+1
        end_time = time.time()+float(timeOut)
        self.avrTime = AverageTime()
        self.avrTime.clean_list()
        count = 0
        while time.time() < end_time:
            while (count < int(times)):
                if(time.time() >= end_time):
                    break
                received_frame = self.bus.recv(float(expect_period)+1)
                received_id = str(hex(received_frame.arbitration_id)).upper()
                expect_id = id_frame.upper()
                if received_id == expect_id:
                    self.avrTime.put_tick()
                    count += 1
        up_bound = float(expect_period)*1.1
        down_bound = float(expect_period)*0.9
        if(count > 0):
            period = self.avrTime.get_average()
        else:
            raise RuntimeError("No Message with ID:%s Received" % (id_frame))
        if not (period < up_bound and period > down_bound):
            raise RuntimeError("""The period is wrong, expected period is %f
                               but the real period is %f"""
                               % (float(expect_period), float(period)))
        pass

    def send_periodic_message(self, message_to_send, period, data=None):
        """Send a message with the given periodicity
        Keyword arguments:
        message_to_send -- name of the message
                          (relative to databse) to send
        period -- periodicity in second
        data -- data to send
        """
        if data is None or data == 'None':
            data = '0'
        is_in_db = False
        for message in self.db.messages:
            if message.name == message_to_send:
                messagets = message
                is_in_db = True
        if is_in_db:
            msg = can.Message(
                arbitration_id=messagets.frame_id, data=bytearray([int(data)]))
            print(msg)
            self.bus.send_periodic(msg, float(period))
        else:
            raise AssertionError('Message : %s is not in Database' %
                                 (message_to_send))

    def send_periodic_signal(self, signal_name, signal_value, period):
        """Send a signal with the given periodicity
        Keyword arguments:
        signal_name -- name of the signal
                       (relative to databse) to send
        signal_value -- signal value to send
        period -- periodicity in second
        """
        is_in_db = False
        signal_dict = {signal_name: float(signal_value)}
        for message in self.db.messages:
            for signal in message.signals:
                if signal_name == signal.name:
                    message_to_send = message
                    is_in_db = True
        if is_in_db:
            for signal in message_to_send.signals:
                if signal.name != signal_name and signal is not None:
                    signal_dict[signal.name] = 0.0
            message_to_send = self.db.get_message_by_name(message_to_send.name)
            data = message_to_send.encode(signal_dict)
            msg = can.Message(
                arbitration_id=message_to_send.frame_id, data=data)
            print(msg)
            self.bus.send_periodic(msg, float(period))
        else:
            raise AssertionError('Signal : %s is not in Database' %
                                 (signal_name))

    def stop_periodic_message(self):
        """Stop the sending of all periodic messages, signals and frames"""
        self.bus.stop_all_periodic_tasks()

    def stop_bus(self):
        """Stop the CAN BUS"""
        self.bus.shutdown()

    def flush_bus(self):
        """Flush the TX buffer"""
        self.bus.flush_tx_buffer()

    def send_diagnostic_request(self, data_to_send, address_type='Physical'):
        """Send a diagnostic (ISO-TP) request
        set_isotp() must be already instanciate
        Keyword arguments:
        data_to_send -- The payload to send
        address_type -- Addressing type (default Physical)
        """
        data = bytes.fromhex(data_to_send)
        print(data)
        print(address_type)
        if address_type == 'Functional':
            self.isotp_stack.send(
                data, isotp.TargetAddressType.Functional)
        else:
            self.isotp_stack.send(
                data)
        while self.isotp_stack.transmitting():
            self.isotp_stack.process()
            time.sleep(self.isotp_stack.sleep_time())

    def check_diag_request(self, expect_reponse_data,
                           timeout_value, exact_or_contain):
        """Check the reception of diagnostic (ISO-TP) response
        set_isotp() must be already instanciate
        Keyword arguments:
        expect_reponse_data -- The wanted payload to check
        timeout_value -- timeout value in second for the reception
        exact_or_contain -- keyword to check pieces of response
        """
        res = "NoReception"
        end_time = time.time() + float(timeout_value)
        while (time.time() < end_time):
            recv_data = None
            self.isotp_stack.process()
            if self.isotp_stack.available():
                recv_data = self.isotp_stack.recv()
            if(recv_data is None):
                continue
            recv_data = recv_data.hex()
            print(recv_data)
            if(recv_data[0:2] == "7f"):
                if(recv_data[4:6] == "78"):
                    print("7F XX 78")
                    end_time = time.time() + float(timeout_value)
                    continue
                else:
                    pass
            recv_data = recv_data.upper()
            if (recv_data is not None):
                if(expect_reponse_data == "ANY"):
                    res = "Good Reponse Received"
                    break
                if (expect_reponse_data != "NoReception"):
                    if (exact_or_contain == "EXACT"):
                        if recv_data == expect_reponse_data:
                            res = "Good Reponse Received"
                            break
                        else:
                            res = "Bad Reponse Received"
                            break
                    elif (exact_or_contain == "CONTAIN"):
                        if(recv_data.find(expect_reponse_data) >= 0):
                            res = "Good Reponse Received"
                            break
                        else:
                            res = "Bad Reponse Received"
                            break
                    elif (exact_or_contain == "START"):
                        if(recv_data.find(expect_reponse_data) == 0):
                            res = "Good Reponse Received"
                            break
                        else:
                            res = "Bad Reponse Received"
                            break
                    elif (exact_or_contain == "NOTSTART"):
                        if(recv_data.find(expect_reponse_data) == 0):
                            res = "Bad Reponse Received"
                            break
                        else:
                            res = "Good Reponse Received"
                            break
                    else:
                        raise AssertionError("BAD ARGUMENTS")
                else:
                    res = "Bad Reponse Received"
                    break
            else:
                if expect_reponse_data == "NoReception":
                    res = "Good Reponse Received"
                    break
                else:
                    res = "Bad Reponse Received"
                    break
        if(res == "Good Reponse Received"):
            pass
            # Verify the result
        if res == "Bad Reponse Received":
            raise AssertionError(("The diagnostic reponse "
                                  "expect to  be %s but was %s.")
                                 % (expect_reponse_data,
                                    str(recv_data)))
        if res == "NoReception" and expect_reponse_data != "NoReception":
            raise AssertionError("Error CAN TimeOut Reached")

    def get_next_isotp_frame(self, timeout='3'):
        """Return the next diagnostic (ISO-TP) frame
        set_isotp() must be already instanciate
        Keyword arguments:
        timeout -- timeout value in second for the reception
        """
        end_time = time.time() + float(timeout)
        while (time.time() < end_time):
            recv_data = None
            self.isotp_stack.process()
            if self.isotp_stack.available():
                recv_data = self.isotp_stack.recv()
            if(recv_data is None):
                continue
            try:
                recv_data = recv_data.hex()
            except:
                recv_data = recv_data
            print(recv_data)
            if(recv_data[0:2] == "7f"):
                if(recv_data[4:6] == "78"):
                    print("7F XX 78")
                    end_time = time.time() + float(timeout)
                    continue
                else:
                    pass
            else:
                pass
            if recv_data is not None:
                return recv_data
            if recv_data is None and time.time() >= end_time:
                raise AssertionError("No ISO-TP Frame received in Timeout")

    def check_snapshot(self, DtcSnapshot, DtcMaskRecord, DidValue):
        """Check the DTCmaskRecord and his value for a given snapshot
        Keyword arguments:
        DtcSnapshot -- The snapshot to check
        DtcMaskRecord -- Wanted DtcMaskRecord
        DidValue -- Wanted DID value
        """
        DtcSnapshot = DtcSnapshot.upper()
        if(DtcSnapshot.find(DtcMaskRecord + DidValue) > 0):
            pass
        else:
            raise AssertionError(DtcMaskRecord + DidValue +
                                 " Not Found in " + DtcSnapshot)

    def check_statusofdtc(self, bit_name, bit_value, snapshot):
        """Check the status of DTC by bit and his value for a given snapshot
        Keyword arguments:
        bit_name -- Name of the statusOfDTC bit (example: testFailed)
        bit_value -- Wanted bit value
        snapshot -- The snapshot to check
        """
        wanted_bit = 2
        if snapshot[0:2] != "59":
            raise AssertionError("SnapShot: " + snapshot +
                                 " does not contain DTC\n")
        snapshot = '{:032b}'.format(int(snapshot, 16))
        statusOfDTC = snapshot[39:47]
        print(statusOfDTC)
        for key, value in self.statusOfDTCbits.items():
            if(bit_name == value):
                wanted_bit = statusOfDTC[7-int(key)]
                print(wanted_bit)
                print(key)
                print(value)
        if(int(wanted_bit) < 2):
            if(wanted_bit == bit_value):
                pass
            else:
                raise AssertionError(
                    "Wanted "+bit_name+" Value is: "+bit_value +
                    " But was: " + wanted_bit)
        else:
            raise AssertionError("Bit Name Must Be One of Those:\n" +
                                 ' \n'.join(str(self.statusOfDTCbits[x])
                                            for x in
                                            sorted(self.statusOfDTCbits)) +
                                 "\nBut Was:\n"+bit_name)

    def get_seedkey(self, Seed, Constant_1, Constant_2):
        """Return a Key generated by a given key and 2 constants
        This is a "dumb" example only adding constant to seed.
        You must implement your own security handshake.
        Keyword arguments:
        Seed -- The seed to generate key from
        Constant_1 -- The first constant
        Constant_2 -- The second constant
        """
        Constant_1 = int(Constant_1, 16)
        Constant_2 = int(Constant_2, 16)
        Seed = int(Seed, 16)
        result_key = Seed + Constant_1 + Constant_2
        result_key = (result_key).to_bytes(4, byteorder='big')
        return result_key.hex()
