import asyncio
from hashlib import md5
import math
import time
import webbrowser
from PIL import ImageGrab, Image
import pyautogui
from rich import inspect
import requests
import json
from os.path import exists

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

async def main():
    r = requests.Session()
    r.headers.update({'User-Agent': 'vulpera.com'})

    if exists('token.bin'):
        utoken = open('token.bin').read()
    if exists('uid.bin'):
        uid = open('uid.bin').read()

    api_token = 'token'

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
    try:
        while True:
                img = ImageGrab.grab(bbox=(0,0,40,10))
                img_health = img.getpixel((11,0))
                # Get the pixel of the health value
                # 0 is red, 1 is green, 2 is blue
                color_value = img_health[1]

                img_heal = img.getpixel((20, 0))
                heal_value = img_heal
                # Start running the toy if we detect damage
                if timeout < time.time():
                    if color_value > 0 and img_health == (0, 0, color_value):
                        print("Magic damage")
                        data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                            'token': api_token,
                            'uid': toy_data['uid'],
                            'command': 'Pattern',
                            'rule': 'V:1;F:vrp;S:100',
                            'strength': ','.join(str(e) for e in random.choice(patterns_magic)),
                            'timeSec': 1,
                            'apiVer': 1
                        })
                        timeout = time.time() + 1
                    if color_value > 0 and img_health == (0, color_value, 0):
                        print("Melee damage")
                        data = r.post('https://api.lovense.com/api/lan/v2/command', data={
                            'token': api_token,
                            'uid': toy_data['uid'],
                            'command': 'Pattern',
                            'rule': 'V:1;F:vrp;S:100',
                            'strength': ','.join(str(e) for e in random.choice(patterns_magic)),
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
                                'command': 'Pattern',
                                'rule': 'V:1;F:v;S:200',
                                'strength': ','.join(str(e) for e in random.choice(patterns_magic)),
                                'timeSec': 1,
                                'apiVer': 1
                            })
                        timeout = time.time() + 1
    except KeyboardInterrupt:
        pass


asyncio.run(main())