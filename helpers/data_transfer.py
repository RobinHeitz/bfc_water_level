import urequests, ujson
from helpers.read_config import read_config

"""
This file is just to demonstrate the login procedure with the pico.
"""


BACKEND_URL_LOGIN = "https://smarthome-frontend.onrender.com/api-token-auth/"
BACKEND_URL_DATA = "https://smarthome-frontend.onrender.com/bfc/water-lvl/"

HEADERS = {'content-type': 'application/json'}


def login(login_url, auth_conf):
    print("login")
    res = urequests.post(login_url, json=auth_conf)
    if res.status_code == 200:
        print("status = 200")
        token = res.json()['token']
        res.close()
        return token
    elif res.status_code == 400:
        res.close()
        return None
    
    

def post_data(water_lvl):
    data = {"water_level":0.123}
    with urequests.post(BACKEND_URL_DATA, json=data) as res:
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 400:
            ... #login routine
        return
    

def get_login_header(token):
    print("get_login_header")
    return {'Authorization': f'Token {token}'}


def main():
    conf = read_config("../auth.json")
    token = login(BACKEND_URL_LOGIN, conf)
    header = get_login_header(token)



    # res = urequests.post(BACKEND_URL_LOGIN, json=conf)
    # json = res.json()
    # print(res.status_code)

    # json = {'token': '5d26a536f58ea0d7f74982eae9e9ad43949b3cce'}
    # print(json)
    # token = json["token"]
    # print(token)
    # token_str = res.text

    # my_obj = ujson.load(token_str)
    # print(my_obj)


    # res.close()



if __name__ == "__main__":
    main()