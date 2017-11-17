import os
from threading import Thread

import zmq

import sys
from zhelpers import socket_set_hwm, zpipe


# The rest of the code is exactly the same as in model 2, except
# that we set the HWM on the server's ROUTER socket to PIPELINE
# to act as a sanity check.

def server_thread(ctx,filedir):
    

    router = ctx.socket(zmq.ROUTER)
    router.bind("tcp://*:6000")
    
    scheduleReq = ctx.socket(zmq.REP)
    scheduleReq.bind("tcp://*:5555")
    # Initialize poll set
    poller = zmq.Poller()
    poller.register(router, zmq.POLLIN)
    poller.register(scheduleReq, zmq.POLLIN)
    while True:
        try:
            socks = dict(poller.poll())
        except KeyboardInterrupt:
            break

        if router in socks:
            try:
                msg = router.recv_multipart()
            except zmq.ZMQError as e:
                if e.errno == zmq.ETERM:
                    print "Context terminated"
                    return   # shutting down, quit
                else:
                    raise

            identity, command, offset_str, chunksz_str, filename, data = msg

            assert command == b"pull"

            offset = int(offset_str)
            chunksz = int(chunksz_str)
            size = len(data)
            print "received " + str(size) +" bytes for "+filename 
            path = os.path.join(filedir,filename)
            if offset == 0:#assume a valid file transfer always starts from offset zero, which should be always true
                if os.path.isfile(path):
                    #if it exists then tell client to abort the file transfer
                    router.send_multipart([identity, b"%i" % -1])
                    continue
            file = open(path, "ab")
            file.write(data)
            file.close()
            # Send resulting chunk to client
            router.send_multipart([identity, b"%i" % size])

        if scheduleReq in socks:
            message = scheduleReq.recv()
            print message
            scheduleReq.send(b"World")
        # First frame in each message is the sender identity

       

def main(filedir):

    # Start child threads
    ctx = zmq.Context()

    #server = Thread(target=server_thread, args=(ctx,))
    #server.start()
    

    # loop until client tells us it's done
    try:
        server_thread(ctx,filedir)
    except KeyboardInterrupt:
        pass

    print "going to terminate context at server"
    ctx.term()

if __name__ == '__main__':
    path = sys.argv[1]
    main(path)


