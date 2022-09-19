
TANKS = {}  #a dictionary containing the player name as the key and his tank object as the value
ACTIONS = {}
BULLETS = []
CHAT_MESSAGES = []

MY_NAME = ""
RUN = True

def init_tank(name,my_tank):
    global TANKS
    TANKS[name] = my_tank
    ACTIONS[name] = []

def init_actions():
    global ACTIONS

def init_other_clients():
    global MY_NAME