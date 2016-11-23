import json
import socket
import uuid

READ_SIZE = 4096
ENCODING = "utf-8"

# Connect to lightsd, here using an Unix socket. The rest of the example is
# valid for TCP sockets too. Replace /run/lightsd/socket by the output of:
# echo $(lightsd --rundir)/socket
lightsd_socket = socket.socket(socket.AF_UNIX)
lightsd_socket.connect("/run/lightsd/socket")
lightsd_socket.settimeout(2)  # seconds

# Prepare the request:
request = json.dumps({
    "method": "get_light_state",
    "params": ["*"],
    "jsonrpc": "2.0",
    "id": str(uuid.uuid4()),
}).encode(ENCODING, "surrogateescape")

# Send it:
lightsd_socket.sendall(request)

# Prepare an empty buffer to accumulate the received data:
response = bytearray()
while True:
    # Read a chunk of data, and accumulate it in the response buffer:
    response += lightsd_socket.recv(READ_SIZE)
    try:
        # Try to load the received the data, we ignore encoding errors
        # since we only wanna know if the received data is complete.
        json.loads(response.decode(ENCODING, "ignore"))
        break  # Decoding was successful, we have received everything.
    except Exception:
        continue  # Decoding failed, data must be missing.

response = response.decode(ENCODING, "surrogateescape")
print(json.loads(response))
