from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ClientFactory
from twisted.internet.error import ReactorNotRunning
import json
import sys
from threading import Thread
import readline

sys.path.insert(1, 'syncplay')
from syncplay.protocols import PingService

CLIENT_PROMPT="Client >> "
SERVER_PROMPT="Server << "

import signal
def sigint_handler(sig, frame):
    print("\n" + CLIENT_PROMPT, flush=True, end="")
signal.signal(signal.SIGINT, sigint_handler)

class SyncplayClient(LineReceiver):
    def __init__(self):
        self._pingService = PingService()
        self.thread = None
        self.getting_input = False

    def connectionMade(self):
        # self.sendHello()
        self.thread = Thread(target = self.requestLine)
        self.thread.start()

    def sendHello(self):
        message_dict = {
            'Hello': {
                'username': 'divastor',
                'room': {
                    'name': 'test'
                },
                'version': '1.7.0'
            }
        }
        self.sendMessage(message_dict)
    def sendMessage(self, msg):
        self.transport.write(json.dumps(msg).encode('utf-8') + b'\r\n')
    def checkForPing(self, message):
        if "State" in message:
            state = message["State"]
            if "ping" in state:
                if "latencyCalculation" in state["ping"]:
                    latencyCalculation = state["ping"]["latencyCalculation"]
                if "clientLatencyCalculation" in state["ping"]:
                    timestamp = state["ping"]["clientLatencyCalculation"]
                    senderRtt = state["ping"]["serverRtt"]
                    self._pingService.receiveMessage(timestamp, senderRtt)
                state["ping"] = {}
                if latencyCalculation:
                    state["ping"]["latencyCalculation"] = latencyCalculation
                state["ping"]["clientLatencyCalculation"] = self._pingService.newTimestamp()
                state["ping"]["clientRtt"] = self._pingService.getRtt()
                self.sendMessage({"State": state})
                return True
        return False
    def requestLine(self):
        while True:
            self.getting_input = True
            try:
                line = input(CLIENT_PROMPT)
            except EOFError:
                try:
                    reactor.stop()
                    signal.raise_signal( signal.SIGINT )
                except ReactorNotRunning:
                    pass
                return
            self.getting_input = False
            line = line.strip().replace("\'", "\"")
            if line == "":
                continue
            # print(line)
            try: 
                messages = json.loads(line)
                self.sendMessage(messages)
            except json.decoder.JSONDecodeError:
                print("Invalid formatting. Check https://syncplay.pl/about/protocol/.")
    def lineReceived(self, line):
        line = line.decode('utf-8').strip()
        message = json.loads(line)
        if not self.checkForPing(message):
            print("\n" + SERVER_PROMPT + str(message))
            if self.getting_input:
                print(CLIENT_PROMPT, flush=True, end="")

class SyncplayClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return SyncplayClient()

    def clientConnectionLost(self, connector, reason):
        print('\nLost connection.  Reason:\n', reason)
        # connector.connect()
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print('\nConnection failed. Reason:\n', reason)
        reactor.stop()

reactor.connectTCP("localhost", 8999, SyncplayClientFactory())
reactor.run()