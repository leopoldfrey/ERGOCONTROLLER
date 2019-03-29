#!/usr/bin/env python

# WS client example

import asyncio
import websockets
import json
import requests

LOCAL_PATH = './img/'
SERVER_PATH = 'https://ergoliveconference.herokuapp.com/uploads/'
PROTOCOL1 = {'type':'broadcast','stage':1}

async def controller():
    async with websockets.connect('ws://localhost:5678') as websocket:
        #name = input("What's your name? ")

        await websocket.send(json.dumps(PROTOCOL1))
        print(f"> {PROTOCOL1}")

        async for message in websocket:
            data = json.loads(message)
            print(data['type'])
            if(data['type'] == 'newimage'):
                img_name = str(data['standbyMsg']).split('uploads/', 1)[1]
                img_path = SERVER_PATH + img_name
                print('Image path:', img_path)
                
                img_data=requests.get(img_path)
                with open(LOCAL_PATH + img_name, 'wb') as handler:
                    handler.write(img_data.content)



asyncio.get_event_loop().run_until_complete(controller())