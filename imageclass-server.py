#!/usr/bin/env python3.7

import selectors
import socket
import types
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

sel = selectors.DefaultSelector()    
learned_model = load_model('model-tini-loosy.h5') # TF initialization

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sentstr = data.outb.decode("UTF-8")
            print("Analyzing", sentstr, "and reply to", data.addr)
            predict_string = predict(sentstr, learned_model)
            data.outb = predict_string.encode('utf_8')  # Should be ready to write
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

def predict(inputfile, model):
    image_path = inputfile
    class_names = ['distort', 'normal']
    img_height = 36
    img_width = 64
    try:
        img = image.load_img(
        image_path, target_size=(img_height, img_width)
        )
        img_array = image.img_to_array(img)
        img_array = img_array / 255
        img_array = np.array([img_array])
        predictions = model.predict(img_array)
        result_string = class_names[np.argmax(predictions[0])]
    except FileNotFoundError:
        result_string="File not accessible"
    finally:
        print(
            'Result:', result_string
        )
        return result_string
    
def main():
    HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
    lsock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((HOST,PORT))
    lsock.listen()
    print("listening on", (HOST, PORT))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__== "__main__":
    main()

