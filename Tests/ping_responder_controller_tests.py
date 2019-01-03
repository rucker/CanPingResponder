#!/usr/bin/python3

import os
import time
import unittest

from Tools.can_adapter import CanAdapter
from Controllers.ping_responder_controller import PingResponderController

class TestPingResponderControllerShould(unittest.TestCase):

    def setUp(self):
        self._can_interface = "vcan0"
        self._received_message_id = 0
        self._received_message_data = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self._tester_can_adapter = CanAdapter(self._can_interface)
        self._tester_can_adapter.start(self._receive_message_callback)
        self._system_under_test = PingResponderController(self._can_interface)
        self._system_under_test.start_up()

    def tearDown(self):
        self._system_under_test.shut_down()
        self._tester_can_adapter.stop()

    def test_detectPingAndSendResponse(self):
        self._send_test_message()
        self.assertEqual(self._received_message_id, 101)
        count = self._received_message_data[7]
        self.assertEqual(count, 124)

    def test_onlyRespondToMessageWithId100(self):
        self._send_test_message(99)
        self.assertEqual(self._received_message_id, 0)
        count = self._received_message_data[7]
        self.assertEqual(count, 0)

    def test_wrapByteValueToZeroAfterMaxValueExceeded(self):
        self._send_test_message(100, bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 255]))
        self.assertEqual(self._received_message_id, 101)
        count = self._received_message_data[7]
        self.assertEqual(count, 0)

    def _send_test_message(self, message_id = 100, message_data = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 123])):
        self._tester_can_adapter.send(message_id, message_data)
        time.sleep(0.1)

    def _receive_message_callback(self, msg):
        self._received_message_id = msg.arbitration_id
        self._received_message_data = msg.data

if __name__ == '__main__':
    unittest.main()
