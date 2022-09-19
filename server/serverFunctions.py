from sql_utils import sql_utils
import movement , random , csv
sql = sql_utils()

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


def login(name, password):
    player_details = sql.get_player_by_name_and_password(name, password)
    if player_details is not None:
        return True
    else:
        return False

def get_random_point():
    x = random.randint(0,1062*32)
    y = random.randint(0,749*32)
    while grid[int(y/32)][int(x/32)] != "-1" or grid[int(y/32)+1][int(x/32)+1] != "-1" or ice_grid[int(y/32)][int(x/32)] != "-1" or ice_grid[int(y/32)+1][int(x/32)+1] != "-1":
        x = random.randint(0,1062*32)
        y = random.randint(0,749*32)
    return x,y

def signup(name, password):
    if sql.get_player_by_name(name) is not None:     #if the username is already taken
        return False
    else:
        x,y = get_random_point()
        player_details = {"name": name, "password": password, "coins": "0", "image": "blue tank", "x": x, "y": y, "angle": "90",\
                              "velocity": "2", "cool down": "2", "items": ""}
        sql.insert_player(player_details)
        return True


#move to the tick rate
def handleMovement(action,info): #info holds [x,y,angle]
    pos = [info[0],info[1],info[2]]

    if action == "left":
        pos[2] = (pos[2] + 4)%360
    if action == "right":
        pos[2] = (pos[2] - 4)%360
    if action == "forward":
        pos[0],pos[1] = movement.move_forward(5, info[0], info[1], info[2])
    if action == "back":
        pos[0],pos[1] = movement.move_back(5, info[0], info[1], info[2])
    return pos





