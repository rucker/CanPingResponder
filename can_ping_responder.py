import signal

from Controllers.ping_responder_controller import PingResponderController

running = 1

def signal_handler(signal, frame):
    global running
    running = 0
    print ("\n")

signal.signal(signal.SIGINT, signal_handler)

pr_controller = PingResponderController("can0")
pr_controller.start_up()

print ("Nothing fancy. Just type Ctrl-C to quit...")

while True:
    if running == 0:
        break

pr_controller.shut_down()
