import sqlite3

"""The wrapper of our the sql database"""
# crsr.execute("""CREATE TABLE players(
#                  name text,
#                  password integer,
#                  coins integer,
#                  tank_image text,
#                  x real,
#                  y real,
#                  rotation integer,
#                  velocity integer,
#                  cool_down integer,
#                  items text
#                  )""")

class sql_utils:

    def __init__(self):
        self.conn = sqlite3.connect("single_server.db")
        self.crsr = self.conn.cursor()
        print("Connected to the database")


    def insert_player(self, player_details):
        # inserts a player to the database
        with self.conn:
            self.crsr.execute(
                """INSERT INTO players VALUES (:name, :password, :coins, :tank_image, :x, :y, :rotation, :velocity, :cool_down, :items)""",
                {'name': player_details["name"], 'password': player_details["password"],
                 'coins': player_details["coins"], 'tank_image': player_details["image"],
                 'x': player_details["x"], 'y': player_details["y"], 'rotation': player_details["angle"],
                 'velocity': player_details["velocity"], 'cool_down': player_details["cool down"],
                 'items': player_details["items"]})

    def get_player_by_name(self, name):
        # returns a player column according to his name
        self.crsr.execute("""SELECT * FROM players WHERE name = :name""", {'name': name})
        if self.crsr.fetchone() != None:
            player_details_tuple = self.crsr.fetchone()
            if player_details_tuple !=None:
                player_details = {"action":"cr",
                                "name": player_details_tuple[0], "password": player_details_tuple[1],
                                "coins": player_details_tuple[2], \
                                "image": player_details_tuple[3], "x": player_details_tuple[4], "y": player_details_tuple[5], \
                                "angle": player_details_tuple[6], "velocity": player_details_tuple[7],
                                "cool down": player_details_tuple[8], \
                                "items": player_details_tuple[9]}
                return player_details
        return
    
    def get_all_players_pos(self):
        position = []
        self.crsr.execute("""SELECT * FROM players""")
        players = self.crsr.fetchone()
        for i in players:
            #print(i)
            #position.append(i[4],i[5])
            pass


    def get_player_by_name_and_password(self, name, password):
        # returns a player column according to his name
        self.crsr.execute("""SELECT * FROM players WHERE name = :name AND password = :player_password""",\
                          {'name': name, 'player_password': password})
        player_details_tuple = self.crsr.fetchone()
        if player_details_tuple is None:
            return None
        player_details = {"name": player_details_tuple[0], "password": player_details_tuple[1],
                          "coins": player_details_tuple[2], \
                          "image": player_details_tuple[3], "x": player_details_tuple[4], "y": player_details_tuple[5], \
                          "angle": player_details_tuple[6], "velocity": player_details_tuple[7],
                          "cool down": player_details_tuple[8], \
                          "items": player_details_tuple[9]}
        return player_details

    def update_player_position(self, name, x, y):
        # updates a player's position
        self.crsr.execute("""UPDATE players SET x = :x, y = :y WHERE name = :name""", \
                     {'x': x, 'y': y, 'name': name})

    def update_player_rotation(self, name, rotation):
        # updates a player's rotation
        self.crsr.execute(
            """UPDATE players SET rotation = :rotation WHERE name = :name AND password = :password""", \
            {'rotation': rotation, 'name': name})

    def update_player_coins(self, name, coins):
        # updates a player's coins
        self.crsr.execute("""UPDATE players SET coins = :coins WHERE name = :name""", \
                     {'coins': coins, 'name': name})

    def update_player_image(self, player_details, image):
        # updates a player's image (image is a string that contains a code name for the actual image
        self.crsr.execute("""UPDATE players SET image = :image WHERE name = :name AND password = :password""", \
                     {'image': image, 'name': player_details["name"], 'password': player_details["password"]})

    def update_player_items(self, player_details, items):
        # updates a player's items (items is a string that contains a code name for the actual items)
        self.crsr.execute("""UPDATE players SET items = :items WHERE name = :name AND password = :password""", \
                     {'items': items, 'name': player_details["name"], 'password': player_details["password"]})

    def update_player_password(self, player_details, password):
        # updates a player's password
        self.crsr.execute(
            """UPDATE players SET password = :password WHERE name :name AND password = :password""", \
            {'password': password, 'name': player_details["name"], 'password': player_details["password"]})

    def get_pos_by_name_and_password(self, name, password):
        """get a touple of (x,y) of the location of the player by the player's name and password"""
        self.crsr.execute("""SELECT x FROM players WHERE name = :name AND password = :password""",\
                          {'name': name, 'password': password})
        x = int(self.crsr.fetchone())
        self.self.crsr.execute("""SELECT x FROM players WHERE name = :name AND password = :password""",\
                          {'name': name, 'password': password})
        y = int(self.crsr.fetchone())

        return x,y