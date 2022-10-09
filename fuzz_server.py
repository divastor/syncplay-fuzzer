import time
from pythonfuzz.main import PythonFuzz
import json

import sys
from threading import *

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP6ServerEndpoint
from twisted.internet.error import CannotListenError

from syncplay.server import SyncFactory, ConfigurationGetter

class ServerStatus: pass

def isListening6(f):
    ServerStatus.listening6 = True

def isListening4(f):
    ServerStatus.listening4 = True

def failed6(f):
    ServerStatus.listening6 = False
    print(f.value)
    print("IPv6 listening failed.")

def failed4(f):
    ServerStatus.listening4 = False
    if f.type is CannotListenError and ServerStatus.listening6:
        pass
    else:
        print(f.value)
        print("IPv4 listening failed.")

argsGetter = ConfigurationGetter()
args = argsGetter.getConfiguration()
factory = SyncFactory(
            args.port,
            args.password,
            args.motd_file,
            args.isolate_rooms,
            args.salt,
            args.disable_ready,
            args.disable_chat,
            args.max_chat_message_length,
            args.max_username_length,
            args.stats_db_file,
            args.tls
        )
protocol = factory.buildProtocol(1)

def sendHello():
    # while(True):
        # try:
    hello = {}
    hello["username"] = "stevie"
    # password = 'SYNCPLAY_PASSWORD'
    # if password:
    #     hello["password"] = password
    room = "emp"
    if room:
        hello["room"] = {"name": room}
    hello["version"] = "1.2.255"  # Used so newer clients work on 1.2.X server
    hello["realversion"] = "1.7.0"
    # hello["features"] = None
    protocol.handleHello(hello)
            # break
        # except AttributeError:
        #     continue



def tcplisten():
    endpoint6 = TCP6ServerEndpoint(reactor, int(args.port))
    endpoint6.listen(factory).addCallbacks(isListening6, failed6)
    endpoint4 = TCP4ServerEndpoint(reactor, int(args.port))
    endpoint4.listen(factory).addCallbacks(isListening4, failed4)
    if ServerStatus.listening6 or ServerStatus.listening4:
        print("started")
        tcp_thread = Thread(target=sendHello)
        tcp_thread.start()
        reactor.run()
    else:
        print("Unable to listen using either IPv4 and IPv6 protocols. Quitting the server now.")
        sys.exit()
sendHello()

@PythonFuzz
def fuzz(buf):
    try:
        if len(buf) < 2:
            return
        command = buf[0] % 7
        message = json.loads(buf[1:].decode())
        if type(message) is not dict:
            return
        
        if command == 0: # "Hello":
            protocol.handleHello(message)
        elif command == 1: # "Set":
            protocol.handleSet(message)
        elif command == 2: # "List":
            protocol.handleList(message)
        elif command == 3: # "State":
            protocol.handleState(message)
        elif command == 4: # "Error":
            pass
            # protocol.handleError(message)
        elif command == 5: # "Chat":
            protocol.handleChat(message)
        elif command == 6: # "TLS":
            if "startTLS" not in message:
                return
            if not message["startTLS"]:
                return
            protocol.handleTLS(message)
        else:
            print("nope")
            return
        # print(message)
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        pass
    except Exception as e:
        print(buf)
        print("message = "+str(message))
        raise e


if __name__ == '__main__':
    fuzz()
