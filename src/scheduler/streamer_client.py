import zmq
import sys

shared = int(sys.argv[1])

context = zmq.Context()

# Socket to talk to server
print "Connecting to Streamer server..."
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

print "Sending request"

if shared:
    print "Sharing."
    json_obj = {"nnes": [{"name": "baseNN",
                          "model_path": "/home/ahjiang/models/flowers-40-0.0001-310-frozen.pb",
                          "input_layer": "input_1",
                          "output_layer": "mixed7/concat",
                          "channels": 3,
                          "width": 299,
                          "height": 299,
                          "input_processor": ""},
                         {"name": "task1",
                          "model_path": "/home/ahjiang/models/trains-40-0.0001-310-frozen.pb",
                          "input_layer": "mixed7/concat",
                          "output_layer": "dense_2/Softmax:0",
                          "channels": 1,
                          "width": 1,
                          "height": 1,
                          "input_processor": "baseNN"},
                         {"name": "task2",
                          "model_path": "/home/ahjiang/models/flowers-40-0.0001-310-frozen.pb",
                          "input_layer": "mixed7/concat",
                          "output_layer": "dense_2/Softmax:0",
                          "channels": 1,
                          "width": 1,
                          "height": 1,
                          "input_processor": "baseNN"}
                         ]}
else:
    print "Not sharing."
    json_obj = {"nnes": [{"name": "task1",
                          "model_path": "/home/ahjiang/models/flowers-40-0.0001-310-frozen.pb",
                          "input_layer": "input_1",
                          "output_layer": "dense_2/Softmax:0",
                          "channels": 3,
                          "width": 299,
                          "height": 299,
                          "input_processor": ""},
                         {"name": "task2",
                          "model_path": "/home/ahjiang/models/trains-40-0.0001-310-frozen.pb",
                          "input_layer": "input_1",
                          "output_layer": "dense_2/Softmax:0",
                          "channels": 1,
                          "width": 1,
                          "height": 1,
                          "input_processor": ""}
                         ]}

socket.send_json(json_obj)

# Get the reply.
message = socket.recv()
print "Received reply ", message
