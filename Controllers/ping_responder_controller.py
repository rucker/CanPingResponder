from Tools.can_adapter import CanAdapter

class PingResponderController(object):

    def __init__(self, can_bus = "vcan0"):
        self.canAdapter = CanAdapter(can_bus)

    def start_up(self):
        self.canAdapter.start(self.receive_message_callback)

    def shut_down(self):
        self.canAdapter.stop()

    def receive_message_callback(self, msg):
        modified_data = msg.data[0:7]
        modified_data.append((msg.data[7] + 1) % 256)
        self.send_message(modified_data)

    def send_message(self, data):
        self.canAdapter.send(101, data)
