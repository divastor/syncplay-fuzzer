from pythonfuzz.main import PythonFuzz
import json

import sys
sys.path.insert(1, 'syncplay')
from syncplay.server import SyncFactory, ConfigurationGetter

from consumable import *
from params import *

# --- GLOBAL INITIALIZATION
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
#  send first hello
hello = {}
hello["username"] = "stevie"
room = "test"
if room:
    hello["room"] = {"name": room}
hello["version"] = "1.2.255"  # Used so newer clients work on 1.2.X server
hello["realversion"] = "1.7.0"
protocol.handleHello(hello)

@PythonFuzz
def fuzz(buf):
    try:
        if len(buf) < 1:
            return
        message = None
        commandName = ""
        c = Consumable(buf)
        command = c.getByte() % 7

        if command == 0:
            message = helloMsg(c)
            commandName = "Hello"
            protocol.handleHello(message)
        elif command == 1:
            message = setMsg(c)
            commandName = "Set"
            protocol.handleSet(message)
        elif command == 2:
            message = {}
            commandName = "List"
            protocol.handleList(message)
        elif command == 3:
            message = stateMsg(c)
            commandName = "State"
            protocol.handleState(message)
        elif command == 4:
            commandName = "Error"
            pass
            # protocol.handleError(message)
        elif command == 5:
            message = chatMsg(c)
            commandName = "Chat"
            protocol.handleChat(message)
        elif command == 6:
            message = tlsMsg(c)
            commandName = "TLS"
            protocol.handleTLS(message)
        else:
            print("nope")
            return
        # print(message)
    except (json.decoder.JSONDecodeError, UnicodeDecodeError, ConsumableException):
        pass
    except Exception as e:
        print(buf)
        print("message = "+str({commandName:message}))
        raise e


if __name__ == '__main__':
    fuzz()
