import socket
import tank_trouble_globals
import Game_Objects
from cryptography.fernet import Fernet, MultiFernet
import random


my_port = random.randint(2000,10000)
server_port = 8888
server_ip = "192.168.172.253"
my_ip = socket.gethostbyname(socket.gethostname())
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

def reset_socket():
    global my_port
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        try:
            s.bind((my_ip, my_port))
            break
        except:
            my_port = random.randint(2000, 10000)

while True:
    try:
        s.bind((my_ip, my_port))
        break
    except:
        my_port = random.randint(2000, 10000)
print("listening")

f = MultiFernet([Fernet(b'ET6ZW0oCmQKeRlcOASPCcKhvzyYUOrkZyDHf0ky7qL4='), Fernet(b'0XwCEUAoKYWkeTFAiL43gsFT3vZRUE4QUjvALet2ESs=')])


def send(txt, dest):
    #ENCRYPT THE MESSAGE
    msg = f.encrypt(txt)
    #SEND THE ENCRYPTED MESSAGE
    s.sendto(msg, dest)

sec = ""

# ---------------------update movement functions--------------------#
def move_update(dir):
    send(f"action:move,dir:{dir},name:{sec}".encode(), (server_ip, server_port))


def stop_update(dir):
    send(f"action:stop,dir:{dir},name:{sec}".encode(), (server_ip, server_port))


def update_angle(angle):
    send(f"action:angle,dir:{angle},name:{sec}".encode())


def shoot(type):
    send(f"action:shoot,name:{sec},type:{type}".encode(), (server_ip, server_port))


def send_msg(msg):
    send(f"action:msg,msg:{msg},name:{sec}".encode(), (server_ip, server_port))

def send_ability(ability):
    send(f"action:ability,type:{ability},name:{sec}".encode(), (server_ip, server_port))


# -----------connection functions---------#
def sign_up(name, password, ip):
    global server_ip
    server_ip = ip
    send(f"action:signup,name:{name},password:{password},ip:{my_ip}".encode(), (server_ip, server_port))


def login(username, password, ip):
    try:
        global server_ip
        server_ip = ip
        print("connecting to server")
        print(f"username: {username}, password: {password}, server ip: {server_ip}")
        send(f"action:login,name:{username},password:{password},ip:{my_ip}".encode(), (server_ip, server_port))
    except Exception as e:
        print(e)

def disconnect():
    send(f"action:disconnect,name:{sec}".encode(), (server_ip, server_port))


def convert_raw(msg):
    res = []
    msg = msg.split(";")
    for i in msg:
        obj = {}
        for j in i.split(","):
            if "*" in j[j.find(":") + 1:]:
                obj[j[:j.find(":")]] = j[j.find(":") + 1:].split("*")
            else:
                obj[j[0:j.find(":")]] = j[j.find(":") + 1:]
        res.append(obj)
    return res



def listen():
    replay = False
    while tank_trouble_globals.RUN:
    # update the client accordingly
        data, addr = s.recvfrom(4096)
        if not data:
            break
        data = f.decrypt(data)
        if addr != (server_ip, server_port):
            continue
        data = str(data)
        data = data[2:]
        data = data[:-1]
        if data == "":
            continue

        if replay:
            send(f"action:check_active,name:{tank_trouble_globals.MY_NAME}".encode(), (server_ip, server_port))

        dict = convert_raw(data)[0]
        if dict["action"] == "cr":
            tank = Game_Objects.Tank(float(dict["x"]), float(dict["y"]),
                                          dict["image"] , dict["name"])
            tank_trouble_globals.init_tank(dict["name"], tank)
            global sec
            sec = dict["sec"]
            tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].coins = int(dict["coins"])


        if dict["action"] == "correction":
            for i in dict.keys():
                if i != "action" and i in tank_trouble_globals.TANKS:
                    tank = tank_trouble_globals.TANKS[i]
                    tank.x = float(dict[i][0])
                    tank.y = float(dict[i][1])
                    tank.angle = float(dict[i][2])
                elif i != "action" and i != tank_trouble_globals.MY_NAME:
                    tank = Game_Objects.Tank(float(dict[i][0]), float(dict[i][1]),
                                                  "green tank",i)
                    tank_trouble_globals.init_tank(i,tank)

        elif dict["action"] == "bullets":
            for i in dict:
                if i != "action":
                    exists = False
                    for bullet in tank_trouble_globals.BULLETS:
                        if bullet.owner_name == dict[i][0] and bullet.bullet_id == dict[i][5]:
                            exists = True
                    if not(exists):
                        bullet = Game_Objects.Bullet(dict[i])
                        tank_trouble_globals.BULLETS.append(bullet)
            pass

        elif dict["action"] == "move":
            if dict["name"] in tank_trouble_globals.ACTIONS:
                if f"move {dict['dir']}" not in tank_trouble_globals.ACTIONS[dict["name"]]:
                    tank_trouble_globals.ACTIONS[dict["name"]].append(dict['dir'])

        elif dict["action"] == "stop":
            if dict["name"] in tank_trouble_globals.ACTIONS and dict['dir'] in tank_trouble_globals.ACTIONS[
                dict["name"]]:
                tank_trouble_globals.ACTIONS[dict["name"]].remove(dict['dir'])

        elif dict["action"] == "turn":
            if f"turn {dict['dir']}" not in tank_trouble_globals.ACTIONS[dict["name"]]:
                tank_trouble_globals.ACTIONS[dict["name"]].append(dict["dir"])

        elif dict["action"] == "stop turn":
            if dict["name"] in tank_trouble_globals.ACTIONS and f"turn {dict['dir']}" in tank_trouble_globals.ACTIONS[
                dict["name"]]:
                tank_trouble_globals.ACTIONS[dict["name"]].remove(dict["dir"])

        elif dict["action"] == "msg":
            msg = dict["name"] + ": " + dict["msg"]
            tank_trouble_globals.CHAT_MESSAGES.append(msg)
            if len(tank_trouble_globals.CHAT_MESSAGES) > 20:
                tank_trouble_globals.CHAT_MESSAGES.pop(0)

        elif dict["action"] == "coins":
            tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].coins = int(dict["value"])

        elif dict["action"] == "hit":
            if int(dict["value"]) <= 0:
                tank_trouble_globals.TANKS[dict["name"]].health = 100
            tank_trouble_globals.TANKS[dict["name"]].health = int(dict["value"])

        elif dict["action"] == "disconnect":
            if dict["name"] in tank_trouble_globals.TANKS:
                del tank_trouble_globals.TANKS[dict["name"]]

        elif dict["action"] == "check_active":
            try:
                if dict["info"] == "ok":
                    replay = False
            except:
                replay = True

        elif dict["action"] == "ability":
            if dict["type"] == "fuel":
                print(dict)
                tank_trouble_globals.TANKS[dict["name"]].movement *= 2
                if dict["name"] == tank_trouble_globals.MY_NAME:
                    Game_Objects.ITEMS_TO_DRAW = (Game_Objects.FUEL_ACTIVATION, (29,20))

        elif dict["action"] == "stop_fuel":
            print(dict)
            tank_trouble_globals.TANKS[dict["name"]].movement /= 2
            if dict["name"] == tank_trouble_globals.MY_NAME:
                Game_Objects.ITEMS_TO_DRAW = (Game_Objects.INVENTORY_WITH_ITEMS, (20, 20))

        #send_state_to_server(tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME], tank_trouble_globals.MY_NAME)