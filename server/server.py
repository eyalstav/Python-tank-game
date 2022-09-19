from argparse import Action
from math import sin,cos,radians,atan,sqrt,pi
import socket, threading
import pygame
import serverFunctions
from sql_utils import sql_utils
import rsa
import csv, random
import time
import random, string
from cryptography.fernet import Fernet, MultiFernet
import keyboard

bufferSize = 1024*4
msg_close = "End Connection"

sql = sql_utils()



# ▄█▀▀▀▄█  ▀██▀  ▀██▀ ▀██▀ █▀▀██▀▀█ 
# ██▄▄  ▀   ██    ██   ██     ██    
#  ▀▀███▄   ██▀▀▀▀██   ██     ██    
#▄     ▀██  ██    ██   ██     ██    
#█▀▄▄▄▄█▀  ▄██▄  ▄██▄ ▄██▄   ▄██▄   

def dict_to_string(data):
    msg = ""
    for i in data:
        msg = msg + f"{i}:{data[i]},"
    return msg[:-1]
def convert_raw(msg):
    res = []
    msg = msg.split(";")
    for i in msg:
        obj = {}
        for j in i.split(","):
            obj[j[0:j.find(":")]] = j[j.find(":") + 1:]
        res.append(obj)
    return res

f = MultiFernet([Fernet(b'ET6ZW0oCmQKeRlcOASPCcKhvzyYUOrkZyDHf0ky7qL4='), Fernet(b'0XwCEUAoKYWkeTFAiL43gsFT3vZRUE4QUjvALet2ESs=')])
def send(txt, dest):
    #ENCRYPT THE MESSAGE
    msg = f.encrypt(txt)
    #SEND THE ENCRYPTED MESSAGE
    s.sendto(msg, dest)

def get_sec():
    ran = ''.join(random.choices(string.ascii_letters, k = 12))
    return ran

def get_random_point():
    x = random.randint(0,1062*32)
    y = random.randint(0,749*32)
    while grid[int(y/32)][int(x/32)] != "-1" or grid[int(y/32)+1][int(x/32)+1] != "-1" or ice_grid[int(y/32)][int(x/32)] != "-1" or ice_grid[int(y/32)+1][int(x/32)+1] != "-1":
        x = random.randint(0,1062*32)
        y = random.randint(0,749*32)
    return x,y


#███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
#██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
#█████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
#██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
#██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
#╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

def make_actions():
    for player in active_players: #player holds a tuple (ip,name,[x,y,angle],[actions])
        player = active_players[player]
        for action in player[3]:
            x,y,angle = serverFunctions.handleMovement(action, player[2])
            if player[6][0]:
                if time.perf_counter() - player[6][1] > 5:
                    player[6][0] = False
                    for other_player in active_players:
                        other_player = active_players[other_player]
                        send(f"action:stop_fuel,name:{player[1]}".encode(), other_player[0])
                x,y,angle = serverFunctions.handleMovement(action, [x,y,angle])
            #check in the wall grid if we can move
            if grid[int(y / 32)][int(x / 32)] == "-1" and  ice_grid[int(y / 32)][int(x / 32)] == "-1" and \
                    grid[int(y / 32)+1][int(x / 32)+1] == "-1" and ice_grid[int(y / 32)+1][int(x / 32)+1] == "-1":
                player[2][0] = x
                player[2][1] = y

            player[2][2] = angle

    for bullet in bullets: #bullet will hold: (owner, type, x,y,angle)
        bullet[2] = bullet[2] - 8*sin(radians(bullet[4]))
        bullet[3] = bullet[3] - 8*cos(radians(bullet[4]))              #checking if we hit the wall
        if not(grid[int(bullet[3] / 32)][int(bullet[2] / 32)] == "-1" and grid[int(bullet[3] / 32 + 34/32)][
            int(bullet[2] / 32 + 30/32)] == "-1" and ice_grid[int(bullet[3] / 32)][int(bullet[2] / 32)] == "-1" and \
                ice_grid[int(bullet[3] / 32 + 34/32)][int(bullet[2] / 32 + 30/34)] == "-1"):
            bullets.remove(bullet)

        for player in active_players: #player holds a tuple (ip,name,[x,y,angle],[actions])
            player = active_players[player]
            if player[1] == bullet[0]: #if the bullet is from the same player, dont check for collision
                continue
            #checking if we hit the player, player width is 32, bullet width is 8
            if bullet[2] > player[2][0] and bullet[2] < player[2][0] + 30 and bullet[3] > player[2][1] and bullet[3] < player[2][1] + 34:
                damage = 34
                if bullet[1] == "shotgun":
                    damage = 20
                if bullet[1] == "sniper":
                    damage = 60
                #print(f"bullet hit {player[1]} by {bullet[0]} with bullet: {bullet[5]}")
                player[4] -= damage
                if player[4] <= 0:
                    send(f"action:hit,value:100,name:{player[1]}".encode(), player[0])
                    player[2][0], player[2][1] = get_random_point()
                    player[4] = 100
                    # add bullet [0] 10 , i[5]
                    for i in active_players:
                        i = active_players[i]
                        if i[1] == bullet[0]:
                            i[5] += 10
                            send(f"action:coins,value:{i[5]}".encode(), i[0])
                for other_player in active_players:
                    other_player = active_players[other_player]
                    send(f"action:hit,value:{player[4]},name:{player[1]}".encode(), other_player[0])
                try:
                    bullets.remove(bullet)
                except:
                    pass
            break

def update_players():
    positions = {}
    for i in active_players:
        i = active_players[i]
        here = f"{i[2][0]}*{i[2][1]}*{i[2][2]}"
        positions[i[1]] = here

    #for bot in bots:
    #    here = f"{bot.x}*{bot.y}*{bot.angle}"
    #    positions[bot.name] =here
                                                    
    if positions:
        pos = str(positions)
        pos = pos[1:]
        pos = pos[:-1]
        msg = "action:correction,"+pos.replace("'","").replace(" ","")
    try:
        for i in active_players:
            i = active_players[i]
            send(msg.encode(),i[0])
    except:
        pass

def bullet_update():
    live_bullets = {}
    c=0
    for i in bullets: #bullet will hold: (owner, type, x,y,angle)
        if i[6] <= 3:       #limits the amount of times a bullet can be sent (to reduce traffic)
            i[6] += 1
            here = f"{i[0]}*{i[1]}*{i[2]}*{i[3]}*{i[4]}*{i[5]}"
            live_bullets[c] = here
            c += 1
        if len(live_bullets) > 20:
            pos = str(live_bullets)
            pos = pos[1:]
            pos = pos[:-1]
            msg = "action:bullets,"+pos.replace("'","").replace(" ","")
            try:
                for i in active_players:
                    i = active_players[i]
                    send(msg.encode(),i[0])
            except:
                pass
            live_bullets = {}
        if live_bullets:
            pos = str(live_bullets)
            pos = pos[1:]
            pos = pos[:-1]
            msg = "action:bullets," + pos.replace("'", "").replace(" ", "")
        try:
            for i in active_players:
                i = active_players[i]
                send(msg.encode(), i[0])
        except:
            pass



def check_who_is_active():
    #check if 3 seconds have passed, if the player is still on the list, remove him
    
    global checking_players_active
    global active_players
    global send_time
    for i in checking_players_active:
        for j in active_players:
            if i == j[1]:
                send(f"action:check_active".encode(), j[0])
    if time.time() - send_time > 3:
        for j in checking_players_active:
            for i in active_players:
                i = active_players[i]
                if i[1] == j:
                    active_players.remove(i)
        checking_players_active = []
        #put the new list in the global list, and wait for the response
        send_time = time.time()
        for i in active_players:
            i = active_players[i]
            checking_players_active.append(i[1])

    


def update():
    clock = pygame.time.Clock()
    tick_rate = 30
    counter = 0
    while run:
        if len(active_players) > 0:
            make_actions()
            
            if counter % 5 == 0:
                bullet_update()
            if counter > tick_rate:
                #check_who_is_active()
                counter = 0
                
                if active_players == []:
                    print("no active players")
            update_players()
                    
            counter+=1

        clock.tick(tick_rate)
    return

# ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ 
#█  ▄    █       █       █
#█ █▄█   █   ▄   █▄     ▄█
#█       █  █ █  █ █   █  
#█  ▄   ██  █▄█  █ █   █  
#█ █▄█   █       █ █   █  
#█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█ █▄▄▄█  
class Bot:
    def __init__(self, name, type):
        self.x,self.y = get_random_point()
        self.angle = 0
        self.velocity = 3
        self.type = type
        self.bullet_id = 0

        self.hp = 100

        self.name = name
        self.players = []

        self.new = None

        self.last_shot = 0
        if self.type == "sniper":
            self.shot_delay = 1500
        if self.type == "shotgun":
            self.shot_delay = 2000
        if self.type == "regular":
            self.shot_delay = 750

    def update_players(self):
        for i in active_players:
            i = active_players[i]
            if i[2][0] - 1000 < self.x < i[2][0]+1000 and i[2][1] -1000 < self.y < i[2][1]+1000:
                self.players.append(i)
        
        # for i in self.players:
        #     if not i[2][0] - 1000 < self.x < i[2][0]+1000 and not i[2][1] -1000 < self.y < i[2][1]+1000:
        #         self.players.remove(i)
    
    def move(self):
        if len(self.players) > 0:
            try:
                new_angle = atan((self.x - self.players[0][2][0]+5)/(self.y - self.players[0][2][1]-20))*180/pi
            except:
                new_angle = 0
            if self.y > self.players[0][2][1]:
                new_angle = new_angle + 180
            #flip the angle
            new_angle -= 180
            if new_angle < 0:
                new_angle = new_angle + 360
            self.new = new_angle

            if 0 < new_angle - self.angle  < 180:
                self.x,self.y,self.angle = serverFunctions.handleMovement("left",[self.x,self.y,self.angle])
                for i in active_players:
                    i = active_players[i]
                    #send(f"action:move,dir:left,name:{self.name}".encode(),i[0])
                    send(f"action:correction,{self.name}:{self.x}*{self.y}*{self.angle}".encode(),i[0])
            else:
                self.x,self.y,self.angle = serverFunctions.handleMovement("right",[self.x,self.y,self.angle])
                for i in active_players:
                    i = active_players[i]
                    #send(f"action:move,dir:right,name:{self.name}".encode(),i[0])
                    send(f"action:correction,{self.name}:{self.x}*{self.y}*{self.angle}".encode(),i[0])       



            if abs(sqrt((self.players[0][2][0] - self.x)**2+(self.players[0][2][1] - self.y)**2)) > 70:
                nx,ny,self.angle = serverFunctions.handleMovement("forward",[self.x,self.y,self.angle])
                #check for collision
                if grid[int(ny / 32)][int(nx / 32)] == "-1" and ice_grid[int(ny / 32)][int(nx / 32)] == "-1" and \
                        grid[int(ny / 32 + 34 / 32)][int(nx / 32 + 30 / 32)] == "-1" and ice_grid[int(ny / 32 + 34 / 32)][
                    int(nx / 32 + 30 / 32)] == "-1":
                    self.x, self.y = nx, ny
                for i in active_players:
                    i = active_players[i]
                    #send(f"action:move,dir:forward,name:{self.name}".encode(),i[0])
                    send(f"action:correction,{self.name}:{self.x}*{self.y}*{self.angle}".encode(),i[0])
                    
            if new_angle -10 < self.angle < new_angle + 10:
                for i in active_players:
                    i = active_players[i]
                    #make sure the bot isnt shooting too often
                    if pygame.time.get_ticks() - self.last_shot > self.shot_delay:
                        if self.type == "shotgun":
                            for j in range(-2,2):
                                self.bullet_id = (self.bullet_id+1) % 700
                                bullets.append([self.name,self.type,self.x,self.y,self.angle+j*2,self.bullet_id, 0])
                        else:
                            self.bullet_id = (self.bullet_id+1) % 700
                            bullets.append([self.name,self.type,self.x,self.y,self.angle,self.bullet_id, 0])
                        self.last_shot = pygame.time.get_ticks()
            
            #take damage and die if hp is 0
            for bullet in bullets:
                if bullet[2] > self.x and bullet[2] < self.x + 30 and bullet[3] > self.y and bullet[3] < self.y + 34 and bullet[0] != self.name:
                    if bullet[1] == "regular":
                        self.hp -= 30
                    if bullet[1] == "shotgun":
                        self.hp -= 20
                    if bullet[1] == "sniper":
                        self.hp -= 60
                    bullets.remove(bullet)
                    print(f"{self.name} took damage")
                    if self.hp <= 0:
                        self.x,self.y = get_random_point()
                        self.hp = 100
                        print(f"{self.name} died")
                        #give the killer 5 coins
                        for i in active_players:
                            i = active_players[i]
                            if i[1] == bullet[0]:
                                i[5] += 5
                                send(f"action:coins,value:{i[5]}".encode(), i[0])
                    for player in active_players:
                        player = active_players[player]
                        send(f"action:hit,value:{self.hp},name:{self.name}".encode(),player[0])
            


                    
                
def bot_loop():
    c = pygame.time.Clock()
    print("Bot started")
    for i in range(100):
        if i % 3 == 0:
            bots.append(Bot(f"Bot{i}", "sniper"))
        elif i % 2 == 0:
            bots.append(Bot(f"Bot{i}", "shotgun"))
        else:
            bots.append(Bot(f"Bot{i}", "regular"))

    while run:
        for bot in bots:
            bot.update_players()
            bot.move()
        c.tick(15)
    return

# ▄████▄  ▒█████   ▓█████▄ ▓█████
#▒██▀ ▀█ ▒██▒  ██▒ ▒██▀ ██▌▓█   ▀
#▒▓█    ▄▒██░  ██▒ ░██   █▌▒███  
#▒▓▓▄ ▄██▒██   ██░▒░▓█▄   ▌▒▓█  ▄
#▒ ▓███▀ ░ ████▓▒░░░▒████▓ ░▒████
#░ ░▒ ▒  ░ ▒░▒░▒░ ░ ▒▒▓  ▒ ░░ ▒░ 
#  ░  ▒    ░ ▒ ▒░   ░ ▒  ▒  ░ ░  
#░       ░ ░ ░ ▒    ░ ░  ░    ░  
#░ ░         ░ ░      ░       ░  


ip = socket.gethostbyname(socket.gethostname())
port = 8888

s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s.bind((ip,port))

print(f"[!][!]  Server is up, running on {ip}, port- {port}  [!][!]")
print("***  Press q to close the server ***")

bots = []
#holds (ip,name,[x,y,angle],[actions], hp, coins, fuel(t/f, time)):
active_players = {}
bullets = [] #bullet will hold: (owner, type, x,y,angle)

checking_players_active = []
send_time = time.time()
global run
run = True

csv_file = open("walls.csv","r")
file = csv.reader(csv_file)
grid = []
for i in file:
    grid.append(i)

ice_file = open("ice.csv","r")
file = csv.reader(ice_file)
ice_grid = []
for i in file:
    ice_grid.append(i)



update_thread = threading.Thread(target=update)
update_thread.start()
bot_thread = threading.Thread(target=bot_loop)
bot_thread.start()


while run:
    if keyboard.read_key() == "q":
        print("The server is shut down")
        run = False
        break
    data, ips = s.recvfrom(bufferSize)
    ip = (ips[0], ips[1])
    data = f.decrypt(data)
    data = str(data.decode())
    if data == "":
        continue
    data = convert_raw(data)
    data = data[0]

    #SQL injections

    action_to_send = False      #indicates if the action should be broadcasted (if it's a real action)
    try:
        try:
            if data["password"]:
                if not data["name"].isalpha() and not data["name"].isalnum() or len(data["name"]) > 10:
                        send(("action:fucked_name").encode(),ip)
                        continue
                if not data["password"].isalpha() and not data["password"].isalnum() or len(data["password"]) > 10:
                        send(("action:fucked_pass").encode(),ip)
                        continue
        except:
            pass

        if data["action"] == "disconnect":
            print(active_players)
            print(f"{data['name']} disconnected")
            i = active_players[data["name"]]
            sql.update_player_position(i[1],i[2][0],i[2][1])
            sql.update_player_coins(i[1],i[5])
            del active_players[data["name"]]


        #login / register
        elif data["action"] == "login":
            print(f"{data['name']} trys to log in")
            if not serverFunctions.login(data["name"],data["password"]):
                send("action:false info".encode(),ip)
            else:
                active = False
                for i in active_players:
                    if active_players[i][1] == data["name"]:
                        active = True
                startData = sql.get_player_by_name(data["name"])
                print(startData)
                if not active:
                    sec = get_sec()
                    x = int(startData["x"])
                    y = int(startData["y"])
                    angle = int(startData["angle"])
                    send(f"{dict_to_string(startData)},sec:{sec},value:{startData['coins']}".encode(), ip)
                    active_players[sec] = [ip,data["name"],[x,y,angle],[],100,startData["coins"],(False,0),0,0]   #the second last item is the counter of the bullets and the last item is time from last shot
                    print(data["ip"] + f"=====> {ip} logged in to "+ data["name"])
            continue

        if data["action"] == "signup":
            if not serverFunctions.signup(data["name"],data["password"]):
                send("action:already taken".encode(),(data["ip"], ips[1]))
            else:
                sec = get_sec()
                x, y = get_random_point()
                player_details = {"name": data["name"], "password": data["password"], "coins": 0, "image": "blue tank", "x": x, "y": y, "angle": 0, "velocity": 2, "cool down": 2, "items": ""}
                sql.insert_player(player_details)
                startData = sql.get_player_by_name(data["name"])
                print(ip[0] + f"=====> signed up "+ data["name"])
            continue

        #handling actions
        if "name" in list(data) and data["name"] in list(active_players):   #if the player is active
            action_to_send = True
            if data["action"] == "move":
                action_to_send = True
                i = active_players[data["name"]]
                if data["dir"] not in i[3]:
                    i[3].append(data["dir"])

            elif data["action"] == "stop":
                action_to_send = True
                i = active_players[data["name"]]
                if data["dir"] in i[3]:
                    i[3].remove(data["dir"])

            elif data["action"] == "shoot":
                action_to_send = True
                i = active_players[data["name"]]
                if data["type"] == "shotgun":
                    if time.perf_counter() - i[8] > 2.5:
                        i[8] = time.perf_counter()
                        for j in range(-2,2):
                            i[7] = (i[7]+1) % 700
                            bullets.append([active_players[data["name"]][1], data["type"], i[2][0] + 30/2-8, i[2][1] + 34, i[2][2]+j*2,i[7], 0]) #the last parameter is the amount of times the bullet was sent
                        #print(active_players[data["name"]][1])
                else:
                    if (data["type"] == "sniper" and time.perf_counter() - i[8] > 1.5) or \
                            (data["type"] == "regular" and time.perf_counter() - i[8] > 0.5):
                        i[8] = time.perf_counter()
                        i[7] = (i[7]+1) % 700
                        bullets.append([active_players[data["name"]][1], data["type"], i[2][0] + 30/2-8,i[2][1] + 34,i[2][2],i[7], 0])
                    #print(active_players[data["name"]][1])


            elif data["action"] == "check_active":
                action_to_send = True
                send("action:check_active,info:ok".encode(),ip)
                if data["name"] in active_players:
                    checking_players_active.remove(data["name"])

            elif data["action"] == "ability":
                action_to_send = True
                i = active_players[data["name"]]
                if data["type"] == "fuel":
                    if not i[6][0] and i[5] >= 2:
                        i[6] = [True, time.perf_counter()]
                        i[5] -= 2
                    send(f"action:coins,value:{i[5]}".encode(),ip)
                if data["type"] == "tp" and i[5] >= 3:
                    i[2][0], i[2][1] = get_random_point()
                    i[5] -= 3
                    send(f"action:coins,value:{i[5]}".encode(),ip)
                if data["type"] == "hp" and i[5] >= 3:
                    i[4] = min(i[4]+50,100)
                    i[5] -= 3
                    for other_player in active_players:
                        other_player = active_players[other_player]
                        send(f"action:hit,value:{i[4]},name:{i[1]}".encode(),other_player[0])
                    send(f"action:coins,value:{i[5]}".encode(),ip)
            elif data["action"] != "msg":
                action_to_send = False
            #broadcasting all the actions

            try:
                data["name"] = active_players[data["name"]][1]
            except:
                pass
            for i in active_players:
                i = active_players[i]
                if action_to_send and i[1]:
                    send(dict_to_string(data).encode(),i[0])
    except:
        print("illegal action")

bot_thread.join()
update_thread.join()
