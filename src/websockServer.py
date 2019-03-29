#!/usr/bin/env python

# WS server that sends messages at random intervals

import asyncio
import websockets
import json

STATE = {'type':'newimage','stage':4,'standbyMsg':'/app/uploads/11h33m48s892_4_blob.jpeg'}

USERS = set()

def state_event():
    return json.dumps(STATE)#{'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def response(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            print('SETTING STAGE :', data['stage'])
            await notify_state()
    finally:
        await unregister(websocket)

start_server = websockets.serve(response, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()