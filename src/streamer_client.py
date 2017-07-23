import zmq

import zmq

context = zmq.Context()

# Socket to talk to server
print "Connecting to Streamer server..."
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print "Sending request"

json_obj = [{"name": "baseNN"}]
socket.send_json(json_obj)

# Get the reply.
message = socket.recv()
print "Received reply ", message
