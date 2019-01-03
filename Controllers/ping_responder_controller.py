from Tools.can_adapter import CanAdapter

class PingResponderController(object):

    def __init__(self, can_bus = "vcan0"):
        self.canAdapter = CanAdapter(can_bus)

    def start_up(self):
        self.canAdapter.start(self.receive_message_callback)

    def shut_down(self):
        self.canAdapter.stop()

    def receive_message_callback(self, msg):
        self.send_message(msg.data)

    def send_message(self, data):
        self.canAdapter.send(101, data)
