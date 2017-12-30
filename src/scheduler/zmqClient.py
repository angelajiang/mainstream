import os
import sys
from threading import Thread

import zmq

from zhelpers import socket_set_hwm, zpipe

CHUNK_SIZE = 2000000
#PIPELINE = 10
ref_schedule = \
        [{"net_id": 0,
          "app_id": -1,
          "parent_id": -1,
          "input_layer": "input",
          "output_layer": "conv1",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 8,
          "shared": True,
          "model_path": "app1_model.pb"
         },
         {"net_id": 1,
          "app_id": 1,
          "parent_id": 0,
          "input_layer": "conv1",
          "output_layer": "softmax",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 2,
          "shared": False,
          "model_path": "app1_model.pb"
          },
         {"net_id": 2,
          "app_id": -1,
          "parent_id": 0,
          "input_layer": "conv1",
          "output_layer": "pool",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 8,
          "shared": True,
          "model_path": "app2_model.pb"
          },
         {"net_id": 3,
          "app_id": 2,
          "parent_id": 2,
          "input_layer": "pool",
          "output_layer": "softmax",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 4,
          "shared": False,
          "model_path": "app2_model.pb"
          },
         {"net_id": 4,
          "app_id": 3,
          "parent_id": 2,
          "input_layer": "pool",
          "output_layer": "softmax",
          "channels": 3,
          "height": 299,
          "width": 299,
          "target_fps": 8,
          "shared": False,
          "model_path": "app3_model.pb"
          }
          ]
test_sched = [{'output_layer': 'mixed6/concat', 'parent_id': -1, 'target_fps': 5, 'app_id': -1, 'height': 299, 'channels': 1, 'width': 299, 'input_layer': 'input_1', 'shared': True, 'net_id': 0, 'model_path': 'onetest-197-frozen.pb'}, {'output_layer': 'dense_2/Softmax:0', 'parent_id': 0, 'target_fps': 5, 'app_id': '1', 'height': 299, 'channels': 1, 'width': 299, 'input_layer': 'mixed6/concat', 'shared': False, 'net_id': 1, 'model_path': 'onetest-197-frozen.pb'}, {'output_layer': 'dense_2/Softmax:0', 'parent_id': 0, 'target_fps': 5, 'app_id': '2', 'height': 299, 'channels': 1, 'width': 299, 'input_layer': 'mixed6/concat', 'shared': False, 'net_id': 2, 'model_path': 'onetest-197-frozen.pb'}]

new_test_sched = [{'output_layer': 'dense_2/Softmax:0', 'parent_id': -1, 'target_fps': 5, 'app_id': '1', 'height': 299, 'channels': 1, 'width': 299, 'input_layer': 'input_1', 'shared': False, 'net_id': 1, 'model_path': 'onetest-197-frozen.pb'}]
def client_thread(ctx, pipe, host, path):
    dealer = ctx.socket(zmq.DEALER)
    socket_set_hwm(dealer, 1)
    dealer.connect("tcp://{}:6378".format(host))

    #credit = PIPELINE   # Up to PIPELINE chunks in transit

    total = 0           # Total bytes sent
    chunks = 0          # Total chunks sent
    offset = 0          # Offset of next chunk request
    file = open(path, "r")
    filename = os.path.basename(path)
    while True:
        #while credit:

        # Read chunk of data from file
        file.seek(offset, os.SEEK_SET)
        data = file.read(CHUNK_SIZE)

        # send next chunk
        dealer.send_multipart([
            b"pull",
            b"%i" % offset,
            b"%i" % len(data),
            b"%s" % filename,
            data,
        ])

        offset += CHUNK_SIZE
        #credit -= 1

        try:
            chunksz_str = dealer.recv()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return   # shutting down, quit
            else:
                raise

        chunks += 1
        #credit += 1
        size = int(chunksz_str)
        if size == -1:
            print "Informed from the server that the file already exists: " + filename
            pipe.send(b"EXISTS")
            return 
        total += size
        #print total
        if size < CHUNK_SIZE:
            break   # Last chunk finished; exit

    print ("%i chunks sent, %i bytes" % (chunks, total))
    pipe.send(b"OK")

def send_schedule(ctx,host):
    socket = ctx.socket(zmq.REQ)
    socket.connect("tcp://{}:6377".format(host))
    socket.send_json(ref_schedule)
    fps_message = socket.recv()
    print fps_message

def send_schedule(ctx, schedule, host):
    socket = ctx.socket(zmq.REQ)
    socket.connect("tcp://{}:6377".format(host))
    socket.send_json(schedule)
    fps_message = socket.recv()
    print fps_message
    return fps_message

def main(host):

    # Start child threads
    ctx = zmq.Context()
    print "Uploading schedule"
    send_schedule(ctx,test_sched,host)
    '''
    a,b = zpipe(ctx)
    print "File transferring"
    path = "/home/iamabcoy/Desktop/capstone/mainstream/testdata"
    client = Thread(target=client_thread, args=(ctx, b, host, path))
    client.start()

    # loop until client tells us it's done
    try:
        print a.recv()
    except KeyboardInterrupt:
        pass
    del a,b
    '''
    print "going to terminate context at client"
    ctx.term()

if __name__ == '__main__':
    host = sys.argv[1]# could be localhost or some endpoints
    main(host)

