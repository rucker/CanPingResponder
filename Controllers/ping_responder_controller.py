from Tools.can_adapter import CanAdapter

class PingResponderController(object):

    def __init__(self, can_bus = "vcan0"):
        self.canAdapter = CanAdapter(can_bus)

    def start_up(self):
        self.canAdapter.start(self.receive_message_callback)

    def shut_down(self):
        self.canAdapter.stop()

    def receive_message_callback(self, msg):
        raise RuntimeError('receive_message_callback() not implemented')

    def send_message(self, data):
        raise RuntimeError('send_message() not implemented')
