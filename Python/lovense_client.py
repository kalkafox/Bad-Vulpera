import asyncio
from hashlib import md5
import sys
from requests.exceptions import ConnectionError
import math
import time
import webbrowser
from PIL import ImageGrab, Image
import pyautogui
from rich import inspect
import requests
import json
from os.path import exists
from os import remove

import random

#toy_data_json = json.loads(toy_data.content)

async def run_toy(request, api_token, toy_data, color_value):
    request.post('https://api.lovense.com/api/lan/v2/command', data={
        'token': api_token,
        'uid': toy_data['uid'],
        'command': 'Function',
        'action': f'Vibrate:{(color_value / 255) * 20}',
        'timeSec': 5,
        'apiVer': 1
    })


patterns_magic = [
    [20, 10, 20, 10, 5, 10, 5, 10, 5, 10],
    [10, 20, 15, 18, 19, 20, 19, 15, 10],
    [5, 10, 10, 10, 5, 10, 10, 10, 20, 10]
]

patterns_melee = [
    [5, 5, 5],
    [5, 10, 5],
    [10, 5, 10]
]

patterns_heal = [
    [1,2,3,2,1,2,3,2,1,2,3,2],
    [3,4,3,5,3,4,3,5,3,4,3,5],
    [2,5,2,3,1,2,5,2,3,1,3,1]
]

patterns_environmental = [
    [20,15,20,15,20,15,20,15],
    [15,20,19],
    [20,1,20,1,20,1,20,10,20,1]
]

async def main():
    r = requests.Session()
    r.headers.update({'User-Agent': 'vulpera.com'})

    if exists('token.bin'):
        utoken = open('token.bin').read()
    if exists('uid.bin'):
        uid = open('uid.bin').read()

    if exists('api_token'):
        token = open('api_token').read()
    else:
        print("You need an API token.")
        sys.exit()
    
    api_token = token
    while True:
        if not exists('token.bin') and not exists('uid.bin'):
            uid = random.randint(1000000, 9999999)
            utoken = md5(str(uid).encode() + str(random.randint(100000, 200000)).encode()).hexdigest()


            post = r.post('https://api.lovense.com/api/lan/getQrCode', data={
                'token': api_token,
                'uid': uid,
                'uname': 'kalka',
                'utoken': utoken
            })

            data = json.loads(post.content)

            webbrowser.open(data['message'])
            print(data['message'])

            print("\nYour browser should have opened a tab with a QR code. This is the necessary info we need to connect to the toy.")

            print("Feel free to scan it. The toy will be added, and this script will listen for it. Good luck!\n")

            with open('token.bin', 'w') as f:
                f.write(utoken)
            with open('uid.bin', 'w') as f:
                f.write(str(uid))

        toy_data = None

        try:
            timeout = time.time() + 1
            print("Querying for toy...")
            while True:
                if timeout < time.time():
                    toy_data = json.loads(r.get('http://vulpera.com:8080/get_toy_data', headers={'utoken': utoken}).text)
                    timeout = time.time() + 1
                    try:
                        toy_data['uid']
                        break
                    except KeyError:
                        continue
        except KeyboardInterrupt:
            return

        print("Activating the Lovenses...")
        dmg_value = 0
        current_heal_value = 0

        heal_active = False
        dmg_active = False
        timeout = time.time()
        retries = 0
        redo = False
        try:
            while True:
                    if retries >= 3:
                        print(f"Retried {retries} times. Assuming Lovense to be disconnected.")
                        print("We will need to grab a new session.\n")
                        remove('token.bin')
                        remove('uid.bin')
                        redo = True
                        break
                    img = ImageGrab.grab(bbox=(0,0,40,10))
                    img_dmg = img.getpixel((11,0))
                    # Get the pixel of the health value
                    # 0 is red, 1 is green, 2 is blue
                    color_value = img_dmg[1]

                    img_heal = img.getpixel((20, 0))
                    heal_value = img_heal
                    # Start running the toy if we detect damage
                    if timeout < time.time():
                        data = None
                        try:
                            if color_value > 0 and img_dmg == (0, 0, color_value):
                                print("Magic damage")
                                data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                                    'token': api_token,
                                    'uid': toy_data['uid'],
                                    'command': 'Pattern',
                                    'rule': 'V:1;F:v;S:100',
                                    'strength': ';'.join(str(e) for e in random.choice(patterns_melee)),
                                    'timeSec': 1,
                                    'apiVer': 1
                                })
                                timeout = time.time() + 1
                            if color_value > 0 and img_dmg == (0, color_value, 0):
                                print("Melee damage")
                                data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                                    'token': api_token,
                                    'uid': toy_data['uid'],
                                    'command': 'Pattern',
                                    'rule': 'V:1;F:v;S:100',
                                    'strength': ';'.join(str(e) for e in random.choice(patterns_magic)),
                                    'timeSec': 1,
                                    'apiVer': 1
                                })
                                timeout = time.time() + 1
                            if img_dmg[0] > 0 and img_dmg == (img_dmg[0], 0, 0):
                                print("Environmental damage")
                                data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                                    'token': api_token,
                                    'uid': toy_data['uid'],
                                    'command': 'Pattern',
                                    'rule': 'V:1;F:v;S:100',
                                    'strength': ';'.join(str(e) for e in random.choice(patterns_environmental)),
                                    'timeSec': 1,
                                    'apiVer': 1
                                })
                                timeout = time.time() + 1
                            if heal_value[1] > 0 and heal_value[2] > 0 and heal_value[0] == 0:
                                if current_heal_value != heal_value:
                                    print("Heal")
                                    data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                                        'token': api_token,
                                        'uid': toy_data['uid'],
                                        'command': "Pattern",
                                        'rule': "V:1;F:v;S:100",
                                        'strength': ";".join(str(e) for e in random.choice(patterns_heal)),
                                        'timeSec': 1,
                                        'apiVer': 1
                                    })
                                    # data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                                    #     'token': api_token,
                                    #     'uid': toy_data['uid'],
                                    #     'command': 'Function',
                                    #     'action': f'Vibrate:{int((heal_value[1] / 255) * 20)}',
                                    #     #'strength': ','.join(str(e) for e in random.choice(patterns_magic)),
                                    #     'timeSec': 1,
                                    #     'toy': "f0decd6bb7f0",
                                    #     'apiVer': 1
                                    # })
                                    print((heal_value[1] / 255) * 20)
                                    print(toy_data)
                                    print(data.content)
                            if data is not None:
                                if json.loads(data.content)['code'] == 507:
                                    print("Lovense App is offline. Retrying...")
                                    retries += 1
                                timeout = time.time() + 1
                        except ConnectionError:
                            print("Connection error! Retrying...")
                            continue
        except KeyboardInterrupt:
            pass
        if redo:
            continue


asyncio.run(main())