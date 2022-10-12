from unittest import runner
from pythonfuzz.main import PythonFuzz
import json

import sys
sys.path.insert(1, 'syncplay')
from syncplay.server import SyncFactory, ConfigurationGetter

from consumable import *
from params import *
# import tracemalloc
# import signal

# def sigint_handler(sig, frame):
#     snapshot = tracemalloc.take_snapshot()
#     top_stats = snapshot.statistics('lineno')

#     print("[ Top 10 ]")
#     for stat in top_stats[:10]:
#         print(stat)
#     raise KeyboardInterrupt()
# signal.signal(signal.SIGINT, sigint_handler)

# LOGGING = True
LOGGING = False

# --- GLOBAL INITIALIZATION
argsGetter = ConfigurationGetter()
args = argsGetter.getConfiguration()
class RunEnumerator:
    def __init__(self):
        self.runNum = 0
    def increment(self):
        self.runNum += 1
    def iterations(self):
        return self.runNum
run = RunEnumerator()

def dlog(s):
    if LOGGING == True:
        print(s)

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

@PythonFuzz
def fuzz(buf):
    if len(buf) < 1:
        return

    messages = []
    try:
        c = Consumable(buf)
        msg = helloMsg(c)

        # mock an established connection
        protocol = factory.buildProtocol(None) # addr=None (not used anywhere)

        # send one hello message
        commandName = "Hello"
        protocol.handleHello(msg)
        messages.append({commandName:msg})
        while c.remainingBytes():
            msg = None
            commandName = ""
            command = c.getByte() % 6

            if command == 0:
                msg = setMsg(c)
                commandName = "Set"
                protocol.handleSet(msg)
            elif command == 1:
                msg = {}
                commandName = "List"
                protocol.handleList(msg)
            elif command == 2:
                msg = stateMsg(c)
                commandName = "State"
                protocol.handleState(msg)
            elif command == 3:
                commandName = "Error"
                pass
                # protocol.handleError(msg)
            elif command == 4:
                msg = chatMsg(c)
                commandName = "Chat"
                protocol.handleChat(msg)
            elif command == 5:
                msg = tlsMsg(c)
                commandName = "TLS"
                protocol.handleTLS(msg)
            else:
                print("nope")
                return
            messages.append({commandName:msg})
            # print(msg)
        protocol.connectionLost(None)
        # run.increment()
        # dlog("--- " +str(run.iterations())+ " ---")
        # dlog(json.dumps(messages, indent=2, sort_keys=True))
    except (json.decoder.JSONDecodeError, UnicodeDecodeError, ConsumableException):
        pass
    except Exception as e:
        messages.append({commandName:msg})
        if len(messages):
            print(buf)
            print("Messages sent (json):\n"+json.dumps(messages, indent=2, sort_keys=True))
            print("Stack of messages:")
            i = 0
            for m in messages:
                print("#"+str(i)+":\t"+str(m))
                i+=1
            print("]")
        raise e


if __name__ == '__main__':
    # tracemalloc.start()
    fuzz()
