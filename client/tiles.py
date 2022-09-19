import pygame
from csv import reader


class Camera:
    def __init__(self, win, screen_width, screen_height, tile_size):
        self.win = win
        self.half_screen_width = screen_width // 2
        self.half_screen_height = screen_height // 2
        self.tile_size = tile_size

    def get_pos_to_draw(self, tile_pos, tank_pos):
        start_screen_x = tank_pos[0] - self.half_screen_width
        start_screen_y = tank_pos[1] - self.half_screen_height

        pos_to_draw = (tile_pos[0] - start_screen_x, tile_pos[1] - start_screen_y)
        return pos_to_draw

    def draw_groups(self, groups_list, tank_pos):
        """ Draw the entire frame with the tank in the middle """
        for group in groups_list:
            for tile in group:
                pos = self.get_pos_to_draw(tile.get_pos(), tank_pos)
                tile.draw_tile(self.win, pos)


class StaticTilesScreen(Camera):
    def __init__(self, win, tile_size, screen_width, screen_height):
        # Initialize the inheritance
        super().__init__(win, screen_width, screen_height, tile_size)
        # General setup
        self.win = win
        self.tile_size = tile_size
        # Layers setup
        self.csv_files = {
            "terrain - walls": "tiles assets/csv map files/map_terrain - walls.csv",
            "terrain - ice": "tiles assets/csv map files/map_terrain - ice.csv",
            "terrain desert - all tiles": "tiles assets/csv map files/map_terrain desert - all tiles.csv",
            "terrain grass - all tiles": "tiles assets/csv map files/map_terrain grass - all tiles.csv",
            "obstacles - walls": "tiles assets/csv map files/map_obstacles - walls.csv",
            "obstacles - ice": "tiles assets/csv map files/map_obstacles - ice.csv"
        }
        self.tiles_images = {
            "all tiles": pygame.image.load("tiles assets/all tiles 2.png"),
            "ice": pygame.image.load("tiles assets/ice.png"),
            "walls": pygame.image.load("tiles assets/walls.png")
        }
        self.cut_graphics_images = {
            "all tiles": self.import_cut_graphics(self.tiles_images["all tiles"], self.tile_size),
            "ice": self.import_cut_graphics(self.tiles_images["ice"], self.tile_size),
            "walls": self.import_cut_graphics(self.tiles_images["walls"], self.tile_size)
        }
        # Terrain layer
        self.terrain_1_data = self.import_csv_file(self.csv_files["terrain grass - all tiles"])
        self.terrain_2_data = self.import_csv_file(self.csv_files["terrain desert - all tiles"])
        self.terrain_3_data = self.import_csv_file(self.csv_files["terrain - ice"])
        self.terrain_4_data = self.import_csv_file(self.csv_files["terrain - walls"])
        # walls layer
        self.walls_1_data = self.import_csv_file(self.csv_files["obstacles - walls"])
        self.walls_2_data = self.import_csv_file(self.csv_files["obstacles - ice"])
        # lists
        self.csv_files_list = [self.terrain_1_data, self.terrain_2_data, self.terrain_3_data, self.terrain_4_data, self.walls_1_data, self.walls_2_data]
        self.tiles_name_list = ["all tiles", "all tiles", "ice", "walls", "walls", "ice"]
        self.groups = []
        self.wall_groups = []

    def get_walls_groups(self):
        return self.wall_groups

    def create_tile_group(self, csv_data, tile_set_name, tank_pos, is_walls_groups):
        """ Create the tile groups to a specific frame """
        start_draw_pos = (tank_pos[0] - self.half_screen_width - 32, tank_pos[1] - self.half_screen_height - 32)
        end_draw_pos = (start_draw_pos[0] + self.half_screen_width*2 + 32, start_draw_pos[1] + self.half_screen_height*2 + 32)
        sprite_group = pygame.sprite.Group()
        tile_cut_graphics_list = self.cut_graphics_images[tile_set_name]

        for row_index, row in enumerate(csv_data):
            y = row_index * self.tile_size
            if y > end_draw_pos[1]:
                break
            if y < start_draw_pos[1]:
                continue
            for col_index, val in enumerate(row):
                x = col_index * self.tile_size
                if x > end_draw_pos[0]:
                    break
                if x < start_draw_pos[0]:
                    continue
                if val != "-1":
                    tile_surface = tile_cut_graphics_list[int(val)]
                    sprite = Tile(self.tile_size, x, y, tile_surface)
                    sprite_group.add(sprite)

        self.groups.append(sprite_group)
        if is_walls_groups:
            self.wall_groups.append(sprite_group)

    def delete_all_groups(self):
        self.groups.clear()
        self.wall_groups.clear()

    def run(self, tank_pos):
        for index, csv_file in enumerate(self.csv_files_list):
            is_walls_group = False
            if index >= 4:
                is_walls_group = True
            self.create_tile_group(csv_file, self.tiles_name_list[index], tank_pos, is_walls_group)

        self.draw_groups(self.groups, tank_pos)

    @staticmethod
    def import_csv_file(path):
        data = []
        with open(path) as the_map:
            level_data = reader(the_map, delimiter=",")
            for row in level_data:
                data.append(list(row))

        return data  # return a 2d list with the file data

    @staticmethod
    def import_cut_graphics(tiles_image, tile_size):
        tile_num_x = int(tiles_image.get_width() / tile_size)
        tile_num_y = int(tiles_image.get_height() / tile_size)

        cut_tiles_list = []
        for row in range(tile_num_y):
            for col in range(tile_num_x):
                x = col * tile_size
                y = row * tile_size
                the_cut_surf = pygame.Surface((tile_size, tile_size))
                the_cut_surf.blit(tiles_image, (0, 0), pygame.rect.Rect(x, y, tile_size, tile_size))  # This represents a smaller portion of the source Surface to draw.
                cut_tiles_list.append(the_cut_surf)

        return cut_tiles_list


class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y, tile_image):
        super().__init__()
        self.x = x
        self.y = y
        self.rect = pygame.rect.Rect((x, y), (size, size))
        self.image = tile_image

    def get_rect(self):
        return self.rect

    def get_pos(self):
        return self.x, self.y

    def draw_tile(self, win, pos):
        win.blit(self.image, pos)

