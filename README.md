# syncplay-fuzzer

This is an attempt at a fuzzer for the syncplay server.

You should first install the [`pythonfuzz`](https://gitlab.com/gitlab-org/security-products/analyzers/fuzzers/pythonfuzz) package with `pip3`:

```bash
pip3 install --extra-index-url https://gitlab.com/api/v4/projects/19904939/packages/pypi/simple pythonfuzz
```

The [syncplay_\<hash\>.patch](patches/syncplay_e2605577f5169dad14a238e6ab53b409af32f4d3.patch) should be applied at the checkout of syncplay that the hash denotes.

```bash
git submodule init
git submodule update
cd syncplay
git apply ../patches/syncplay_<hash>.patch
```

To run the fuzzer:

```bash
python3 fuzz_server.py
```

## Exceptions

The fuzzer will quickly find some errors with a `room` variable being `NoneType`. You can apply the [syncplay_fix_room_is_none.patch](patches/syncplay_fix_room_is_none.patch) to the syncplay codebase, to fix that bug.

There are also some other exceptions that can be triggered if the `# exception` lines get commented out in [params.py](fuzz_server.py)

One last thing: the fuzzer starts by sending a `"Hello"` message to the server, but this is completely optional. In fact, any client can send any message once the connection is established, but various messages cause crashes otherwise. As a #todo this will change in the future.

## Testing messages to the server

> Important Note: Remember to reset the `syncplay` repository before spawning a Syncplay server. The changes made with the [syncplay_\<hash\>.patch](patches/syncplay_e2605577f5169dad14a238e6ab53b409af32f4d3.patch) make it impossible to establish a connection to the server. A better way to test your messages is to use a different instance of the `syncplay` repository at this specific checkout to keep everything clean.

I have constructed a client that can send multiple messages to `localhost:8999`. You can spawn a server instance and use the client to send messages as such:

```bash
# in one terminal window
~/git/syncplay$ python3 syncplayServer.py

Welcome to Syncplay server, ver. 1.7.0
PLEASE NOTE: To allow room operator passwords generated by this server instance to still work when the server is restarted, please add the following command line argument when running the Syncplay server in the future: --salt WHJUCNVSVI
```

```bash
# in another terminal window
~/git/syncplay-fuzzer$ python3 client.py

Started to connect.
Connected.
Client >> 
```

At which point the connection has been established, and the server expects a `"Hello"` message to register this user. To automatically send `"Hello"` messages for connections established, comment out the line `self.sendHello()` in [client.py](client.py), line 23. In that case you will see something like this:

```bash
~/git/syncplay-fuzzer$ python3 client.py

Started to connect.
Connected.
Client >> 
Server << {'Set': {'ready': {'username': 'divastor', 'isReady': None, 'manuallyInitiated': False}}}
Client >> 
Server << {'Set': {'playlistChange': {'user': None, 'files': []}}}
Client >> 
Server << {'Set': {'playlistIndex': {'user': None, 'index': None}}}
Client >> 
Server << {'Hello': {'username': 'divastor', 'room': {'name': 'test'}, 'version': '1.7.0', 'realversion': '1.7.0', 'motd': '', 'features': {'isolateRooms': False, 'readiness': True, 'managedRooms': True, 'chat': True, 'maxChatMessageLength': 150, 'maxUsernameLength': 150, 'maxRoomNameLength': 35, 'maxFilenameLength': 250}}}
Client >> 
```

Press `Ctrl+D` to exit.

Visit https://syncplay.pl/about/protocol/ for more info on the kinds of messages that can be sent.