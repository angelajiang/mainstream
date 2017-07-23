import zmq

import zmq

context = zmq.Context()

# Socket to talk to server
print "Connecting to hello world server..."
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print "Sending request"
socket.send("Hello")

# Get the reply.
message = socket.recv()
print "Received reply ", message
