# File Transfer model #3
#
# In which the client requests each chunk individually, thus
# eliminating server queue overflows, but at a cost in speed.

import os
from threading import Thread

import zmq

from zhelpers import socket_set_hwm, zpipe

CHUNK_SIZE = 2500
#PIPELINE = 10

def client_thread(ctx, pipe):
    dealer = ctx.socket(zmq.DEALER)
    socket_set_hwm(dealer, 1)
    dealer.connect("tcp://localhost:6000")

    #credit = PIPELINE   # Up to PIPELINE chunks in transit

    total = 0           # Total bytes sent
    chunks = 0          # Total chunks sent
    offset = 0          # Offset of next chunk request
    path = "/home/iamabcoy/Desktop/capstone/mainstream/testdata"
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
            b"%i" % CHUNK_SIZE,
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
        total += size
        #print total
        if size < CHUNK_SIZE:
            break   # Last chunk finished; exit

    print ("%i chunks sent, %i bytes" % (chunks, total))
    pipe.send(b"OK")

# The rest of the code is exactly the same as in model 2, except
# that we set the HWM on the server's ROUTER socket to PIPELINE
# to act as a sanity check.

def server_thread(ctx):
    

    router = ctx.socket(zmq.ROUTER)

    router.bind("tcp://*:6000")
    
    while True:
        # First frame in each message is the sender identity
        # Second frame is "fetch" command
        try:
            msg = router.recv_multipart()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                return   # shutting down, quit
            else:
                raise

        identity, command, offset_str, chunksz_str, filename, data = msg

        assert command == b"pull"

        offset = int(offset_str)
        chunksz = int(chunksz_str)
        size = len(data)
        print "received " + str(size) +" bytes for "+filename 
        file = open(filename, "ab")
        file.write(data)

        # Send resulting chunk to client
        router.send_multipart([identity, b"%i" % size])

# The main task is just the same as in the first model.

def main():

    # Start child threads
    ctx = zmq.Context()
    a,b = zpipe(ctx)

    client = Thread(target=client_thread, args=(ctx, b))
    server = Thread(target=server_thread, args=(ctx,))
    client.start()
    server.start()

    # loop until client tells us it's done
    try:
        print a.recv()
    except KeyboardInterrupt:
        pass
    del a,b
    print "going to terminate context"
    ctx.term()

if __name__ == '__main__':
    main()
