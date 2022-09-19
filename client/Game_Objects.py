import pygame
import time
import tank_client
from math import sin, cos, radians
import tank_trouble_globals

global WIN
WIN = None
global WALL_GROUPS
WALL_GROUPS = None


ITEMS_COOLDOWN = {"fuel": 10,
                  "portal": 10, "second portal": 30, "shrinking": 20, "healing": 0}  # a dictionary that contains the item as the key and the cooldown in seconds as the value
PORTALS = []  # a list of all portal locations and the objects that went through the portal


ICON = pygame.image.load("assets/Tank-icon.png")
WIDTH_AND_HEIGHT = (850, 600)
SCREEN_WIDTH, SCREEN_HEIGHT = WIDTH_AND_HEIGHT
# Load images! (Create Surface objects)
BULLET = pygame.image.load("assets/BULLET.png")
BULLET = pygame.transform.scale(BULLET, (int(BULLET.get_width() * 0.8), int(BULLET.get_height() * 0.8)))
SNIPER_BULLET = pygame.image.load("assets/sniper bullet.png")
SNIPER_BULLET = pygame.transform.scale(SNIPER_BULLET,(int(SNIPER_BULLET.get_width() * 0.7), int(SNIPER_BULLET.get_height() * 0.7)))
SHOTGUN_BULLET = pygame.image.load("assets/shotgun bullet.png")
SHOTGUN_BULLET = pygame.transform.scale(SHOTGUN_BULLET, (
int(SHOTGUN_BULLET.get_width() * 0.25), int(SHOTGUN_BULLET.get_height() * 0.25)))
BLUE_TANK = pygame.image.load("assets/tank_blue.png")
BLUE_TANK = pygame.transform.flip(BLUE_TANK, False, True)  # Flip the image vertically
GREEN_TANK = pygame.image.load("assets/tank_green.png")
GREEN_TANK = pygame.transform.flip(GREEN_TANK, False, True)
# load the background
BACKGROUND = pygame.image.load("assets/Background.png")
BACKGROUND = pygame.transform.scale(BACKGROUND, WIDTH_AND_HEIGHT)
#item images ------------------------>
FUEL_ACTIVATION = pygame.image.load("assets/fuel_activation.png")
FUEL_ACTIVATION = pygame.transform.scale(FUEL_ACTIVATION, (54, 50))
DECOY = pygame.image.load("assets/decoy.png")
DECOY = pygame.transform.scale(DECOY, (35, 50))
BLUE_PORTAL = pygame.image.load("assets/blue portal.png")
BLUE_PORTAL = pygame.transform.scale(BLUE_PORTAL, (45, 52))
YELLOW_PORTAL = pygame.image.load("assets/yellow portal.png")
YELLOW_PORTAL = pygame.transform.scale(YELLOW_PORTAL, (45, 52))
PORTAL_ACTIVATION = pygame.image.load("assets/portal activation.png")
PORTAL_ACTIVATION = pygame.transform.scale(PORTAL_ACTIVATION, (54, 50))
SHRINKING_ACTIVATION = pygame.image.load("assets/shrinking activation.png")
SHRINKING_ACTIVATION = pygame.transform.scale(SHRINKING_ACTIVATION, (54, 50))
INVENTORY_WITH_ITEMS = pygame.image.load("assets/inventory_with_items.png")
INVENTORY_WITH_ITEMS = pygame.transform.scale(INVENTORY_WITH_ITEMS, (99, 202))

ITEMS_TO_DRAW = (INVENTORY_WITH_ITEMS, (20, 20))    #contains the items to draw and the location to draw in
TANK_IMAGES = {"green tank": GREEN_TANK, "blue tank": BLUE_TANK}    #a dictionary containing the tank image name as the key and the image itself as the value


def find_key(dict, item):
    for key in dict:
        if dict[key] == item:
            return key
    return None


class Portal:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.portal_mask = pygame.mask.from_surface(self.image)
        self.objects_that_moved_through = []
        self.connected_portal = None


    def set_connected_portal(self, portal):
        self.connected_portal = portal
        self.connected_portal.connected_portal = self

    def apply_location_according_to_portal(self, entity):
        offset = (int(entity.x - self.x), int(entity.y - self.y))
        is_collided = self.portal_mask.overlap(entity.mask, offset)
        previous_x = entity.x
        previous_y = entity.y
        if entity not in self.objects_that_moved_through and is_collided:
            entity.x = self.connected_portal.x
            entity.y = self.connected_portal.y
            if isinstance(entity, Tank):
                if entity.is_collided_with_other_tanks() or entity.is_collide_with_a_wall():
                    #if the the entity will be stuck at the other side of the portal
                    entity.x = previous_x
                    entity.y = previous_y
            self.connected_portal.objects_that_moved_through.append(entity)
        elif entity in self.objects_that_moved_through and not is_collided:
            self.objects_that_moved_through.remove(entity)

    def apply_portal(self, tank):
        self.apply_location_according_to_portal(tank)
        for bullet in tank.bullets:
            self.apply_location_according_to_portal(bullet)


class Bullet(pygame.sprite.Sprite):
    BULLETS_IMAGES = {
        "sniper": SNIPER_BULLET,
        "regular": BULLET,
        "shotgun": SHOTGUN_BULLET
    }
    DAMAGE_DICTIONARY = {
        # The damage in percents
        "sniper": 60,
        "regular": 20,
        "shotgun": 30
    }

    def __init__(self, info):
        super().__init__()
        self.owner_name = info[0]
        self.x = tank_trouble_globals.TANKS[self.owner_name].x + tank_trouble_globals.TANKS[self.owner_name].img.get_width() / 2 - 8
        self.y = tank_trouble_globals.TANKS[self.owner_name].y + tank_trouble_globals.TANKS[self.owner_name].img.get_height() / 2 - 8
        self.angle = float(info[4])
        self.bullet_type = info[1]
        self.bullet_id = info[5]
        if self.angle < 0:  # The angle of the bullet can be only positive angle
            self.angle = 360 - abs(self.angle)
            
        self.img = self.BULLETS_IMAGES.get(self.bullet_type)
        self.mask = pygame.mask.from_surface(self.img)
        self.rect = pygame.rect.Rect((self.x, self.y), (self.img.get_width(), self.img.get_height()))
        
        self.movement = 8
        self.damage = self.DAMAGE_DICTIONARY.get(self.bullet_type)
        tank_trouble_globals.BULLETS.append(self)

    def check_for_collide_with_a_wall(self):
        """ Check if a bullet collide with a wall. Return None if there isn't any collision or the walls that collided """
        self.rect = pygame.rect.Rect((self.x, self.y), (self.img.get_width(), self.img.get_height()))
        collided_walls_list = []
        for wall_group in WALL_GROUPS:
            for wall_sprite in wall_group:
                if pygame.sprite.collide_rect(self, wall_sprite):
                    #print(self.owner_name)
                    if self in tank_trouble_globals.BULLETS:
                        tank_trouble_globals.BULLETS.remove(self)

    def draw(self, tank_pos):
        start_screen_pos = (tank_pos[0] - SCREEN_WIDTH / 2, tank_pos[1] - SCREEN_HEIGHT / 2)
        pos = (self.x - start_screen_pos[0], self.y - start_screen_pos[1])
        try:
            start_screen_pos = (tank_pos[0] - SCREEN_WIDTH / 2, tank_pos[1] - SCREEN_HEIGHT / 2)
            pos = (self.x - start_screen_pos[0], self.y - start_screen_pos[1])
            if self.bullet_type == "sniper":  # Draw sniper bullet
                rotated_image = pygame.transform.rotate(self.img, self.angle)  # Rotate the image
                new_rect = rotated_image.get_rect(center=self.img.get_rect(
                    topleft=pos).center)  # Help to avoid from distortion of the image (rotate an image around its center)
                WIN.blit(rotated_image, new_rect)  # rotate without change x, y
            else:
                WIN.blit(self.img, pos)
        except:
            pass

    def bullet_movement(self):
        self.x -= self.movement * sin(radians(self.angle))
        self.y -= self.movement * cos(radians(self.angle))

class Tank(pygame.sprite.Sprite):
    MAX_COOL_DOWN = {
        "sniper": 150,
        "regular": 50,
        "shotgun": 100
    }

    def __init__(self, x, y, image_name,name):
        super().__init__()
        self.name = name
        self.x = x
        self.y = y
        self.img = TANK_IMAGES[image_name]
        self.image_name = image_name
        self.rect = pygame.rect.Rect((self.x, self.y), (self.img.get_width(), self.img.get_height()))
        self.mask = pygame.mask.from_surface(self.img)
        self.movement = 5
        self.angle = 0
        self.cool_down = 0
        self.bullets_type = "regular"
        self.items = ["fuel", "portal", "shrinking", "healing"]
        self.activated_items = {}  # dictionary that contains the item that's activated and the time when it was activated
        self.health = 100
        self.max_health = 100
        self.coins = 30
        self.actions = []





    def apply_items(self):  # checks that the items have not expired
        for item in list(self.activated_items):
            if time.perf_counter() - self.activated_items[item] >= ITEMS_COOLDOWN[item]:
                self.deactivate_item(item)

    def deactivate_item(self, item):
        global ITEMS_TO_DRAW
        ITEMS_TO_DRAW = (INVENTORY_WITH_ITEMS, (20, 20))
        del self.activated_items[item]
        if item == "fuel":
            self.movement = self.movement/2
        elif item == "second portal" or item == "first portal":
            PORTALS.pop(0)
            self.items[1] = "portal"
        elif item == "shrinking":
            self.img = pygame.transform.scale(TANK_IMAGES[self.image_name], (30, 34))
            self.mask = pygame.mask.from_surface(self.img)
            if self.is_collide_with_a_wall() or self.is_collided_with_other_tanks():
                self.img = pygame.transform.scale(TANK_IMAGES[self.image_name], (22, 25))
                self.mask = pygame.mask.from_surface(self.img)
                self.activated_items["shrinking"] = ITEMS_COOLDOWN[item] * (-1) - 1



    def activate_item(self, item_index):  # activates the item
        global ITEMS_TO_DRAW
        if ITEMS_TO_DRAW[0] == INVENTORY_WITH_ITEMS:
            item = self.items[item_index]
            self.activated_items[item] = time.perf_counter()
            print(self.activated_items)
            #self.items[item_index] = "no item"
            if item == "fuel" and self.coins >= 2:
                tank_client.send_ability("fuel")
                print("fuel activated")

            if item == "healing" and self.coins >= 1 and self.health < 100:
                tank_client.send_ability("hp")
                self.coins -= 1
                del self.activated_items[item]

            global TIME_FROM_FIRST_PORTAL
            if item == "portal" and self.coins >= 2:
                tank_client.send_ability("tp")



    def get_pos(self):
        return round(self.x), round(self.y)

    def draw_my_tank(self):
        rotated_image = pygame.transform.rotate(self.img, self.angle)  # Rotate the image
        if self.name == tank_trouble_globals.MY_NAME:
            new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(SCREEN_WIDTH / 2,
                                                                            SCREEN_HEIGHT / 2)).center)  # Help to avoid from distortion of the image (rotate an image around its center)
        else:
            rx = int((self.x - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].x ) + SCREEN_WIDTH / 2)
            ry = int((self.y - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].y) + SCREEN_HEIGHT / 2)
            if abs(rx) > 1000 or abs(ry) > 1000:
                return
            new_rect = rotated_image.get_rect(center=self.img.get_rect(center=(rx,ry)).center)
        WIN.blit(rotated_image, new_rect)  # rotate without change x, y

    def apply_actions(self):
        for action in tank_trouble_globals.ACTIONS[self.name]:
            if action == "forward":
                self.move_forward()
                if self.is_collide_with_a_wall():
                    self.move_back()
            elif action == "back":
                self.move_back()
                if self.is_collide_with_a_wall():
                    self.move_forward()
            elif action == "left":
                self.change_angel(4)
            elif action == "right":
                self.change_angel(-4)
            elif action == "shoot":
                self.create_new_bullet()

    def tank_movement(self, UI_screen, key):
        """ Move the tank on the screen, check if it collided with the maze image and shoot the bullets"""
        keys = pygame.key.get_pressed()  # Return a dictionary with the status of every key (True or False)
        if key == pygame.K_UP and "move forward" not in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:  # Move up
            #self.actions.append("move forward")
            tank_client.move_update("forward")

        elif key == pygame.K_DOWN and "move back" not in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:  # Move down
            #self.actions.append("move back")
            tank_client.move_update("back")

        elif key == pygame.K_RIGHT and "turn right" not in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:  # Move right
            #self.actions.append("turn right")
            tank_client.move_update("right")

        elif key == pygame.K_LEFT and "turn left" not in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:  # Move left
            #self.actions.append("turn left")
            tank_client.move_update("left")

        if key == pygame.K_SPACE and self.cool_down == 0:  # Shoot new bullet
            tank_client.shoot(self.bullets_type)

        if key == pygame.K_TAB:  # Change the tank's weapon (!open the UI screen!)
            self.bullets_type = UI_screen.run_UI_screen()


    def stop_movement(self, key):       #if key is up
        if key == pygame.K_UP and "forward" in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:
            #self.actions.remove("move forward")
            tank_client.stop_update("forward")

        elif key == pygame.K_DOWN and "back" in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:
            #self.actions.remove("move back")
            tank_client.stop_update("back")

        elif key == pygame.K_RIGHT and "right" in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:
            #self.actions.remove("turn right")
            tank_client.stop_update("right")

        elif key == pygame.K_LEFT and "left" in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:
            #self.actions.remove("turn left")
            tank_client.stop_update("left")

        elif key == pygame.K_SPACE and "shoot" in tank_trouble_globals.ACTIONS[tank_trouble_globals.MY_NAME]:
            #self.actions.remove("shoot")
            tank_client.shoot_update(self.bullets_type)

    def change_angel(self, degrees):
        self.angle += degrees
        if self.angle == 360 or self.angle == -360:
            self.angle = 0

    def move_forward(self):
        if self.angle < 0:
            positive_angle = 360 - abs(self.angle)
        else:
            positive_angle = self.angle

        self.x -= self.movement * sin(radians(positive_angle))
        self.y -= self.movement * cos(radians(positive_angle))

    def move_back(self):
        if self.angle < 0:
            positive_angle = 360 - abs(self.angle)
        else:
            positive_angle = self.angle

        self.x += self.movement * sin(radians(positive_angle))
        self.y += self.movement * cos(radians(positive_angle))

    #-------------collision check functions------------------>

    def is_collide_with_a_wall(self):
        """ Check if a bullet collide with a wall. Return None if there isn't any collision or the walls that collided """
        self.rect = pygame.rect.Rect((self.x, self.y), (self.img.get_width(), self.img.get_height()))
        collided_walls_list = []
        for wall_group in WALL_GROUPS:
            for wall_sprite in wall_group:
                if pygame.sprite.collide_rect(self, wall_sprite):
                    collided_walls_list.append(wall_sprite)

        if len(collided_walls_list) == 0:
            return None
        else:
            return collided_walls_list


    def draw_health_bar(self, window, font):
        green_health_bar_size = self.health / self.max_health
        health_text_label = font.render(f"health: {int(green_health_bar_size * 100)}%", True, (255, 255, 255))
        y_location = SCREEN_HEIGHT - 20
        x_location = SCREEN_WIDTH / 2 - 180
        # Red health bar
        pygame.draw.rect(window, (255, 0, 0), pygame.Rect(x_location, y_location, 400, 18))
        # Green health bar
        pygame.draw.rect(window, (0, 255, 0), pygame.Rect(x_location, y_location, 400 * green_health_bar_size, 18))
        # text label
        window.blit(health_text_label, (x_location + 200 - health_text_label.get_width() / 2, y_location))

    def draw_enemy_health_bar(self, window):
        font = pygame.font.SysFont("ariel", 20)
        green_health_bar_size = self.health / self.max_health
        health_text_label = font.render(f"health: {int(green_health_bar_size * 100)}%", True, (255, 255, 255))
        y_location = int((self.y - 160 - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].y) + SCREEN_WIDTH / 2)
        x_location = int((self.x - 37 - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].x) + SCREEN_WIDTH / 2)
        # Red health bar
        pygame.draw.rect(window, (255, 0, 0), pygame.Rect(x_location, y_location, 74, 12))
        # Green health bar
        pygame.draw.rect(window, (0, 255, 0), pygame.Rect(x_location, y_location, 74 * green_health_bar_size, 12))
        # text label
        window.blit(health_text_label, (x_location, y_location))

    #----------------------------------------------------<




    def cool_down_the_tank(self):
        if self.cool_down > 0:
            self.cool_down -= 1

