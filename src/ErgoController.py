import sys
import asyncio
import websockets
import json
import requests
import os
from threading import Thread
from pyosc import Server
from pyosc import Client

MSG = 'Focus on the conference'
PROT = 0

WS_PATH = 'ws://ergoliveconference.herokuapp.com'
LOCAL_PATH = os.getcwd() + '/img/'
SERVER_PATH = 'https://ergoliveconference.herokuapp.com/uploads/'
PROTOCOL1 = {'type':'broadcast','stage':1}
PROTOCOL2 = {'type':'broadcast','stage':2}
PROTOCOL3 = {'type':'broadcast','stage':3}
PROTOCOL4 = {'type':'broadcast','stage':4}
PROTOCOL5 = {'type':'broadcast','stage':5}
PAUSE = {'type':'broadcast','stage':0, 'standbyMsg':'Focus on the conference'}
DELETE_DATA = {'type':'deleteAllServerData'}

class DownThread(Thread):
    def __init__(self, image_name, osc_client=None):
        Thread.__init__(self)
        self.image_name = image_name
        self.osc_client = osc_client
        
    def run(self):
        img_path = SERVER_PATH + self.image_name
        new_path = LOCAL_PATH + self.image_name 
        print(" > Downloading... " + self.image_name)
        print("URL", img_path)
        print("LOCAL", new_path)
        img_data=requests.get(img_path)
        with open(new_path, 'wb') as handler:
            handler.write(img_data.content)
            self.osc_client.send('/newimage',new_path)
        print("   ...done")

@asyncio.coroutine
def ImageReceiver(osc_client_host='127.0.0.1', osc_client_port=5551):
    osc_client = Client(osc_client_host, osc_client_port)
    print("ImageReceiver Ready")
    websocket = yield from websockets.connect(WS_PATH)
    try:
        osc_client.send('/connected',1)
        while True:
            message = yield from websocket.recv()
            data = json.loads(message)
            print("RECEIVED", data)#['type'])
            if(data['type'] == 'newimage'):
                img_name = str(data['standbyMsg']).split('uploads/', 1)[1]
                thd = DownThread(img_name, osc_client)
                thd.start()
    finally:
        yield from websocket.close()
        osc_client.send('/connected',0)
        
#asyncio.get_event_loop().run_until_complete(protocol(i))
#asyncio.get_event_loop().run_until_complete(pause(s))

@asyncio.coroutine
def send_protocol(prot):
    protocol = {'type':'broadcast','stage':prot}
    print("SEND_PROTOCOL", protocol)
    websocket = yield from websockets.connect(WS_PATH)
    try:
        yield from websocket.send(json.dumps(protocol))
    finally:
        yield from websocket.close()

@asyncio.coroutine
def send_pause(msg):
    pause = {'type':'broadcast','stage':0, 'standbyMsg':msg}
    print("SEND_PAUSE", pause)
    websocket = yield from websockets.connect(WS_PATH)
    try:
        yield from websocket.send(json.dumps(pause))
    finally:
        yield from websocket.close()

@asyncio.coroutine
def send_delete_data():
    print("SEND_DELETE_DATA", DELETE_DATA)
    websocket = yield from websockets.connect(WS_PATH)
    try:
        yield from websocket.send(json.dumps(DELETE_DATA))
    finally:
        yield from websocket.close()

class ErgoController:
    
    def __init__(self, osc_server_port=5550, osc_client_host='127.0.0.1', osc_client_port=5551):
        self.osc_server = Server('127.0.0.1', osc_server_port, self.callback)
        print("ErgoController Ready")
        asyncio.new_event_loop().run_until_complete(ImageReceiver(osc_client_host, osc_client_port))

    def callback(self, address, *args):
        #print("callback : "+str(address))
            
        argsStr = ""
        l = len(args)
        for x in range(0,l):
            argsStr += str(args[x])
            if(x < (l-1)):
                argsStr += " "
                
        if(address == '/exit'):
            print("--- EXIT ---")
            self.osc_server.stop()
            sys.exit()
        elif(address == '/deleteData'):
            print('DELETE_DATA')
            asyncio.new_event_loop().run_until_complete(send_delete_data())
        elif(address == '/socket'):
            WS_PATH = argsStr
            print('WS_PATH', WS_PATH)
        elif(address == '/local'):
            LOCAL_PATH = argsStr
            print('LOCAL_PATH', LOCAL_PATH)
        elif(address == '/server'):
            SERVER_PATH = argsStr
            print('SERVER_PATH', SERVER_PATH)
        elif(address == '/protocol'):
            print('PROTOCOL', args[0])
            asyncio.new_event_loop().run_until_complete(send_protocol(args[0]))
        elif(address == '/pause'):
            print('PAUSE', argsStr)
            asyncio.new_event_loop().run_until_complete(send_pause(argsStr))
        else:
            print("callback : "+str(address))
            for x in range(0,len(args)):
                print("     " + str(args[x]))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        ErgoController();
    elif len(sys.argv) == 4:
        ErgoController(int(sys.argv[1]))
    else:
        print('usage: %s <pyosc-server-port> <pyosc-client-host> <pyosc-client-port>')
