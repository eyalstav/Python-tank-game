# Create the UI screen
import pygame
pygame.init()

# The window screen configurations
WIDTH_AND_HEIGHT = (850, 600)
SCREEN_WIDTH, SCREEN_HEIGHT = WIDTH_AND_HEIGHT

BACKGROUND_IMAGE = pygame.image.load("assets/UI Background.png")


class UI_SCREEN:
    def __init__(self, win):
        self.win = win
        self.background_image = pygame.transform.scale(BACKGROUND_IMAGE, WIDTH_AND_HEIGHT)

        self.back_button = Button(win, 230, 50, (int(SCREEN_WIDTH/2-110), int(SCREEN_HEIGHT-30)), "#FF8000", "Press Q to return to the game", "#FFFFFF")

        self.shotgun_text = "Click here\nto select the shotgun!\ndamage: 30%\nIt shoots three bullets at a time.\ngood weapon for short distances."
        self.shotgun_button = Button(win, 270, 130, (10, 135), "#475F77", self.shotgun_text, "#FFFFFF")
        self.regular_text = "Click here\nto select the regular weapon!\ndamage: 20%\ngood weapon for\nmedium distances."
        self.regular_weapon_button = Button(win, 270, 130, (290, 135), "#475F77", self.regular_text, "#FFFFFF")
        self.sniper_text = "Click here\nto select the sniper!\ndamage: 60%\ngood weapon for long distances.\nIt needs a lot of time to cool down."
        self.sniper_button = Button(win, 270, 130, (570, 135), "#475F77", self.sniper_text, "#FFFFFF")
        self.button_list = [self.shotgun_button, self.regular_weapon_button, self.sniper_button]
        self.weapon_that_was_selected = None

    def draw(self):
        self.win.blit(self.background_image, (0, 0))
        self.back_button.draw()
        for button in self.button_list:
            button.draw()
        pygame.display.update()

    def run_UI_screen(self):
        clock = pygame.time.Clock()
        FPS = 60
        run = True
        RED_COLOR = "#FF3333"
        BUTTON_COLOR = "#475F77"

        while run:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                run = False

            for i, the_button in enumerate(self.button_list):
                if the_button.check_for_click():
                    if i == 0:
                        the_button.set_button_color(RED_COLOR)
                        self.button_list[1].set_button_color(BUTTON_COLOR)
                        self.button_list[2].set_button_color(BUTTON_COLOR)
                        self.weapon_that_was_selected = "shotgun"
                    elif i == 1:
                        the_button.set_button_color(RED_COLOR)
                        self.button_list[0].set_button_color(BUTTON_COLOR)
                        self.button_list[2].set_button_color(BUTTON_COLOR)
                        self.weapon_that_was_selected = "regular"
                    else:
                        the_button.set_button_color(RED_COLOR)
                        self.button_list[0].set_button_color(BUTTON_COLOR)
                        self.button_list[1].set_button_color(BUTTON_COLOR)
                        self.weapon_that_was_selected = "sniper"
            self.draw()

        return self.weapon_that_was_selected


class Button:
    def __init__(self, screen, width, height, pos, button_color, text, text_color):
        # Rectangle
        self.is_the_button_pressed = False
        self.win = screen
        self.rect_pos = pos
        self.rect = pygame.Rect(pos, (width, height))
        self.button_color = button_color

        # Text
        self.text = text
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)

    def set_button_color(self, new_color):
        self.button_color = new_color

    def draw(self):
        pygame.draw.rect(self.win, self.button_color, self.rect, border_radius=12)

        split_text = self.text.split("\n")
        pos = [self.rect_pos[0] + 4, self.rect_pos[1] + 4]
        for line in split_text:
            text_surf = self.font.render(line, True, self.text_color)
            self.win.blit(text_surf, pos)
            pos[1] += text_surf.get_height() + 6

    def check_for_click(self):
        """ return true if the button is clicked"""
        mouse_pos = pygame.mouse.get_pos()  # Return a tuple that shows the current mouse location
        is_left_click_is_pressed = pygame.mouse.get_pressed()[0]
        if self.rect.collidepoint(mouse_pos) and is_left_click_is_pressed:
            self.is_the_button_pressed = True
        elif not is_left_click_is_pressed and self.is_the_button_pressed:  # Check if the button was release
            self.is_the_button_pressed = False
            return True
        return False


# UI_screen = UI_SCREEN(WIN)
# weapon = UI_screen.run_UI_screen()
