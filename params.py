from consumable import *

# buf is Consumable type

def getUsername(buf):
    choice = buf.getByte()%5
    if choice == 0:
        return "user1"
    elif choice == 1:
        return "user2"
    elif choice == 2:
        return "user3"
    elif choice == 3:
        return "user4"
    elif choice == 4:
        return "user5"
def getRoom(buf):
    choice = buf.getByte()%5
    if choice == 0:
        return "room1"
    elif choice == 1:
        return "room2"
    elif choice == 2:
        return "room3"
    elif choice == 3:
        return "room4"
    elif choice == 4:
        return "room5"
def getVersion(buf):
    return str(buf.getInt())+'.'+str(buf.getInt())+'.'+str(buf.getInt())
        
def helloMsg(buf):
    msg = {}
    msg["username"]=getUsername(buf)
    msg["room"] = {"name":getRoom(buf)}
    msg["version"]=getVersion(buf)
    if buf.getBool():
        msg["password"]='pass1234'
    if buf.getBool():
        msg["realversion"]=getVersion(buf)
    if buf.getBool():
        msg["features"] = {}
    return msg

def setMsg(buf):
    msg = {}
    if buf.getBool():
        msg["room"] = {}
        if buf.getBool():
            msg["room"]["name"] = getRoom(buf)
    if buf.getBool():
        msg["file"] = {}
    if buf.getBool():
        msg["controllerAuth"] = {}
        if buf.getBool():
            msg["controllerAuth"]["password"] = buf.getString()
        if buf.getBool():
            msg["controllerAuth"]["room"] = {}
            if buf.getBool():
                msg["controllerAuth"]["room"]["name"] = getRoom(buf)
    if buf.getBool():
        msg["ready"] = {}
        if buf.getBool():
            msg["ready"]["manuallyInitiated"] = buf.getBool()
        # if buf.getBool(): # exception
        msg["ready"]["isReady"] = buf.getBool()
    if buf.getBool():
        msg["playlistChange"] = {}
        # if buf.getBool(): # exception
        msg["playlistChange"]["files"] = []
    if buf.getBool():
        msg["playlistIndex"] = {}
        # if buf.getBool(): # exception
        msg["playlistIndex"]["index"] = buf.getInt()
    """ 
    # exception - seems not implemented:
    if buf.getBool():
        msg["features"] = {}
    """
    return msg

def listMsg(buf):
    msg = {}
    return msg

def stateMsg(buf):
    msg = {}
    if buf.getBool():
        msg["ignoringOnTheFly"] = {}
        if buf.getBool():
            msg["server"] = buf.getBool()
        if buf.getBool():
            msg["client"] = buf.getBool()
    if buf.getBool():
        msg["playstate"] = {}
        if buf.getBool():
            msg["position"] = buf.getInt()
        if buf.getBool():
            msg["paused"] = buf.getBool()
        if buf.getBool():
            msg["doSeek"] = buf.getBool()
    if buf.getBool():
        msg["ping"] = {}
        if buf.getBool():
            msg["latencyCalculation"] = buf.getBool()
        if buf.getBool():
            msg["clientLatencyCalculation"] = buf.getBool()
    return msg

def chatMsg(buf):
    msg = buf.getString()
    return msg

def tlsMsg(buf):
    msg = {}
    msg["startTLS"] = ["send"]
    return msg