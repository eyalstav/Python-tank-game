# Tank Trouble game
import time
import openWindow
import pygame
import tank_client
from UI_screen import UI_SCREEN
from tiles import StaticTilesScreen
import threading
import Game_Objects
import tank_trouble_globals
from tank_trouble_globals import *
from tank_trouble_globals import MY_NAME

MY_TANK = None

# The window screen configurations
global WALL_GROUPS
WALL_GROUPS = None
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 128)

WIN = None
Font = pygame.font.Font(None, 35)
ICON = pygame.image.load("assets/Tank-icon.png")
WIDTH_AND_HEIGHT = (850, 600)
SCREEN_WIDTH, SCREEN_HEIGHT = WIDTH_AND_HEIGHT

pygame.display.set_caption("Tank Trouble Game")
pygame.display.set_icon(ICON)

# chat vars:
Text_For_Chat = ""  # the text that will be presented in the chat
Chat_Opened = False
Chat_Font = pygame.font.Font(None, 20)
UNSELECTED_CHAT = pygame.image.load("assets/Unselected chat.png")
UNSELECTED_CHAT = pygame.transform.scale(UNSELECTED_CHAT, (216, 35))
SELECTED_CHAT = pygame.image.load("assets/selected chat.png")
SELECTED_CHAT = pygame.transform.scale(SELECTED_CHAT, (216, 380))
CHAT_TO_DRAW = (UNSELECTED_CHAT, (20, SCREEN_HEIGHT - 40))    #the image and location on the map of the selected or unselected chat

# Load images! (Create Surface objects)
COINS = pygame.image.load("assets/coins.png")
COINS = pygame.transform.scale(COINS, (40, 40))
BULLET = pygame.image.load("assets/BULLET.png")
BULLET = pygame.transform.scale(BULLET, (int(BULLET.get_width() * 0.8), int(BULLET.get_height() * 0.8)))
SNIPER_BULLET = pygame.image.load("assets/sniper bullet.png")
SNIPER_BULLET = pygame.transform.scale(SNIPER_BULLET,
                                       (int(SNIPER_BULLET.get_width() * 0.7), int(SNIPER_BULLET.get_height() * 0.7)))
SHOTGUN_BULLET = pygame.image.load("assets/shotgun bullet.png")
SHOTGUN_BULLET = pygame.transform.scale(SHOTGUN_BULLET, (
    int(SHOTGUN_BULLET.get_width() * 0.25), int(SHOTGUN_BULLET.get_height() * 0.25)))
BLUE_TANK = pygame.image.load("assets/tank_blue.png")
BLUE_TANK = pygame.transform.flip(BLUE_TANK, False, True)  # Flip the image vertically
GREEN_TANK = pygame.image.load("assets/tank_green.png")
# load the background
BACKGROUND = pygame.image.load("assets/Background.png")
BACKGROUND = pygame.transform.scale(BACKGROUND, WIDTH_AND_HEIGHT)

# item images ------------------------>
FUEL_ACTIVATION = pygame.image.load("assets/fuel_activation.png")
FUEL_ACTIVATION = pygame.transform.scale(FUEL_ACTIVATION, (54, 50))
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

TANK_IMAGES = {"green tank": GREEN_TANK,
               "blue tank": BLUE_TANK}  # a dictionary containing the tank image name as the key and the image itself as the value


global PORTALS


global Actions_Ticks
Actions_Ticks = {}

def find_key(dict, item):
    for key in dict:
        if dict[key] == item:
            return key
    return None


def redraw_window(tank,tanks, tiles, health_bar_font):
    # Print the background to the screen
    WIN.fill((0, 0, 0))
    tiles.run(tank.get_pos())
    # WIN.blit(BACKGROUND, (0, 0))
    # Print the tank to the screen and its
    for portal in Game_Objects.PORTALS:
        start_screen_pos = (tank.x - SCREEN_WIDTH / 2, tank.y - SCREEN_HEIGHT / 2)
        pos = (portal.x - start_screen_pos[0], portal.y - start_screen_pos[1])
        WIN.blit(BLUE_PORTAL, pos)
        if portal.connected_portal:
            start_screen_pos = (tank.x - SCREEN_WIDTH / 2, tank.y - SCREEN_HEIGHT / 2)
            pos = (portal.connected_portal.x - start_screen_pos[0], portal.connected_portal.y - start_screen_pos[1])
            WIN.blit(YELLOW_PORTAL, pos)
    # Print the tank to the screen and its

    #print(tanks)
    for i in list(tanks.values()):
        i.draw_my_tank()
    for i in tank_trouble_globals.BULLETS:
        i.draw([tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].x,tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].y])
    # draws the coins amount and the coin icon on the screen
    coins_amount = Font.render(str(tank.coins), True, green, blue)
    textRect = coins_amount.get_rect()
    textRect.topright = (SCREEN_WIDTH - 40, 20)
    WIN.blit(coins_amount, textRect)
    WIN.blit(COINS, (SCREEN_WIDTH - 40, 13))

    # draw the item UI on the screen
    WIN.blit(Game_Objects.ITEMS_TO_DRAW[0], Game_Objects.ITEMS_TO_DRAW[1])

    # draws the chat
    WIN.blit(CHAT_TO_DRAW[0], CHAT_TO_DRAW[1])

    if Chat_Opened:
        chat_message = Chat_Font.render(Text_For_Chat, True, pygame.Color("gold"))
        message_rect = chat_message.get_rect()
        if chat_message.get_width() < UNSELECTED_CHAT.get_width() - 10:
            WIN.blit(chat_message, (46, SCREEN_HEIGHT - 27))
        else:
            WIN.blit(chat_message, (46, SCREEN_HEIGHT - 27), (message_rect.left, message_rect.top,\
                                                              SELECTED_CHAT.get_width() - 10, message_rect.height))
        for i in range(len(tank_trouble_globals.CHAT_MESSAGES)):
            chat_message = Chat_Font.render(tank_trouble_globals.CHAT_MESSAGES[len(tank_trouble_globals.CHAT_MESSAGES)-i-1], True, pygame.Color("gold"))
            if SCREEN_HEIGHT - 27 - 20*(i+1) > CHAT_TO_DRAW[1][1]:
                WIN.blit(chat_message, (46, SCREEN_HEIGHT - 27 - 20*(i+1)))
    for name in list(tank_trouble_globals.TANKS):
        if name != tank_trouble_globals.MY_NAME:
            tank = tank_trouble_globals.TANKS[name]
            tank.draw_enemy_health_bar(WIN)
            name_label = pygame.font.Font(None, 26)
            name_label = name_label.render(name, True, pygame.Color("gray2"))
            name_y = int(
                (tank.y - 184 - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].y) + SCREEN_WIDTH / 2)
            name_x = int(
                (tank.x - 36 - tank_trouble_globals.TANKS[tank_trouble_globals.MY_NAME].x) + SCREEN_WIDTH / 2)
            WIN.blit(name_label, (name_x, name_y))
    MY_TANK.draw_health_bar(WIN, health_bar_font)
    pygame.display.update()


WAIT_BEFORE_ERASE = 0

def chat_functions(event):
    global Chat_Opened
    global CHAT_TO_DRAW
    global Text_For_Chat
    global WAIT_BEFORE_ERASE
    if Chat_Opened:
        CHAT_TO_DRAW = (SELECTED_CHAT, (5, SCREEN_HEIGHT - SELECTED_CHAT.get_height()))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and Text_For_Chat != "":
                tank_client.send_msg(Text_For_Chat)
                Text_For_Chat = ""
                if len(tank_trouble_globals.CHAT_MESSAGES) > 20:
                    tank_trouble_globals.CHAT_MESSAGES.pop(0)
            else:
                if Chat_Font.render(Text_For_Chat, True, pygame.Color("gold")).get_width() < SELECTED_CHAT.get_width() - 37:    # Check if there is a space in the typing line
                    Text_For_Chat += event.unicode  # adds the text to the message
    else:
        CHAT_TO_DRAW = (UNSELECTED_CHAT, (2, SCREEN_HEIGHT - UNSELECTED_CHAT.get_height()))

    if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSLASH:
        Chat_Opened = not Chat_Opened
        Text_For_Chat = Text_For_Chat[:-1]

    if Chat_Opened and event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE and time.perf_counter() - WAIT_BEFORE_ERASE > 0.09:
        WAIT_BEFORE_ERASE = time.perf_counter()
        Text_For_Chat = Text_For_Chat[:-2]

def main():

    name = openWindow.loginWindow()
    if name != "":
        global WIN
        WIN = pygame.display.set_mode(WIDTH_AND_HEIGHT)
        tank_trouble_globals.MY_NAME = name
        listen_for_server = threading.Thread(target=tank_client.listen)
        listen_for_server.start()
        while name not in TANKS:
            print("waiting for connection")
            time.sleep(2)
        global Chat_Opened
        global CHAT_TO_DRAW
        health_bar_font = pygame.font.SysFont("ariel", 25)  # Create a Font object for the tank's health bar
        Game_Objects.WIN = WIN
        clock = pygame.time.Clock()
        FPS = 30
        global MY_TANK
        MY_TANK = TANKS[tank_trouble_globals.MY_NAME]
        UI_screen = UI_SCREEN(WIN)
        tiles_screen = StaticTilesScreen(WIN, 32, SCREEN_WIDTH, SCREEN_HEIGHT)
        global Text_For_Chat
        tank_trouble_globals.RUN = True
        wait_before_erase = 0  #the time spacing between each erase
        while tank_trouble_globals.RUN:  # Game loop!!!
            redraw_window(MY_TANK,tank_trouble_globals.TANKS, tiles_screen, health_bar_font)
            for event in pygame.event.get():
                chat_functions(event)
                if event.type == pygame.QUIT:
                    tank_trouble_globals.RUN = False
                    tank_client.disconnect()
                    tank_client.s.close()
                    break

                if not Chat_Opened:
                    if event.type == pygame.KEYDOWN:
                        MY_TANK.tank_movement(UI_screen, event.key)
                    elif event.type == pygame.KEYUP:
                        MY_TANK.stop_movement(event.key)
                if event.type == pygame.KEYDOWN:
                    # --------- item activation (1, 2, 3, 4 keys)
                    if event.key == pygame.K_1:
                        MY_TANK.activate_item(0)

                    if event.key == pygame.K_2:
                        MY_TANK.activate_item(1)

                    if event.key == pygame.K_3:
                        MY_TANK.activate_item(3)

            if Chat_Opened and pygame.key.get_pressed()[pygame.K_BACKSPACE] and time.perf_counter() - wait_before_erase > 0.1:
                wait_before_erase = time.perf_counter()
                Text_For_Chat = Text_For_Chat[:-1]

            global WALL_GROUPS
            WALL_GROUPS = tiles_screen.get_walls_groups()
            Game_Objects.WALL_GROUPS = WALL_GROUPS

            for i in tank_trouble_globals.TANKS.values():
                i.apply_actions()

            for i in tank_trouble_globals.BULLETS:
                i.bullet_movement()
                i.check_for_collide_with_a_wall()


            MY_TANK.cool_down_the_tank()
            tiles_screen.delete_all_groups()
            # print(f"x: {tank.x}, y: {tank.y}, degree: {tank.angle}")
            for portal in Game_Objects.PORTALS:  # applies all portals
                if portal.connected_portal:
                    portal.apply_portal(MY_TANK)
                    portal.connected_portal.apply_portal(MY_TANK)

            clock.tick(FPS)
        listen_for_server.join()
        pygame.quit()
    return

if __name__ == '__main__':
    main()
