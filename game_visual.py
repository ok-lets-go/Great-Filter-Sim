"""
Nomenclature: 
Grid/HexGrid (used interchangably) = the overall play area
Tile/HexTile (used interchangably) = a hex tile that contains 6 separate areas
Plot = a single area on a Tile, each tile contains 6
"""

import pygame, math, random, os
from string import ascii_lowercase as acl
from archive.game import Die
# Initialize Pygame
pygame.init()



# Constants
fullscreen = True
FPS = 60
WHITE = (255, 255, 255)
if fullscreen: 
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((1000,600))
WIDTH, HEIGHT = pygame.display.get_window_size()
pygame.display.set_caption("Great Filter")

RED = ('#FF0000')
PURPLE = ('#800080')
ORANGE = ("#A56B00")
YELLOW = ("#FFEE00")
BLACK = ('#000000')
GREEN = pygame.Color("#A1FB03")
BLUE = pygame.Color("#01E3FD")
BROWN = pygame.Color("#C19A6B")

HEX_SIZE = WIDTH/22

pygame.font.init()

generic_scalable_font = pygame.font.SysFont(name='arial', size=int(HEIGHT/45))

info_font = pygame.font.SysFont("verdana", 15)
hex_font = pygame.font.SysFont("verdana", 10)
fancy_font = pygame.font.SysFont(name='vivaldi', size=125)
basic_font_small = pygame.font.SysFont(name='arial', size=12)
basic_font_xl = pygame.font.SysFont(name='arial', size=72, bold=True)

# Create the game window


# Clock to control frame rate
clock = pygame.time.Clock()


#Miscellaneous Methods
def shuffle(input_list: list):
    "Randomly shuffle values in a list"
    for n in range(1000):
        a = random.randint(0, len(input_list)-1)
        input_list.append(input_list.pop(a))
    return input_list


def roll_dice(die_value):
    "Return random value for given dice roll"
    return random.randint(1, die_value)


def generate_text(text, fg, bg, rect_center, border=None, border_width=5, font=generic_scalable_font):
    "Returns text and rect object to use in pygame blit"
    return_text = font.render(text, True, fg, bg)
    return_rect = return_text.get_rect()
    return_rect.center = rect_center
    if border:
        border_rect = return_rect.inflate(border_width, border_width)
        return (return_text, return_rect, (border, border_rect))
    return return_text, return_rect

#Game Tokens
class City:
    def __init__(self, color):
        self.sprite = None
        edge = int(HEIGHT/57.6)
        self.dimensions = (edge, edge)
        self.placed = False
        self.color = color

    def place(self, pos):
        x, y = pos
        w, h = self.dimensions
        pygame.draw.circle(screen, self.color, radius=HEX_SIZE/5.1, center=pos)
        self.placed = True


#Properties of each individual triangle of each hex tile
class Plot:
    def __init__(self, index, composition, value, rotation):
        self.rotation = rotation

        #index is used to determine where the plot is in physical space, regardless of rotation
        #index 0 is always the bottom left plot on a given hex
        self.index = index

        #letter value and buildable status need to take into consideration the rotation of the tile
        self.letter = acl[(index + rotation) % 6]
        self.buildable = composition[(index + rotation) % 6] == 'l'

        self.occupied = False
        self.connections = []
        self.center = None

        #tile identity is a tuple of the tile number, and its position on the hex
        self.identity = (value, self.index)
        self.adjacencies = None



#Properties and functions of individual hex tiles
class HexTile:
    def __init__(self, composition, value):
        self.x, self.y = 0, 0
        self.coordinate = None
        #composition dictates how many land and water tiles appear
        composition_list = ['llllll', 'lllllw',  'llllww', 'lllwww', 'llwwww', 'llwwww', 'llwwww', 'llwwww']
        #used to set the color of the plot fill when drawing shapes
        self.colors = {'l':GREEN, 'w':BLUE}
        self.composition = composition_list[composition]
        self.city = None
        #sets random rotation of tile, in 60 degree increments
        self.rotation = random.randint(0, 5)
        self.value = value
        self.occupied = False
        self.adjacencies = None
        #create identity for each individual plot in the hex
        self.plots = [
            Plot(index, self.composition, self.value, self.rotation)
            for index in range(6)
        ]

    def set_location(self, x, y):
        "Assigns position of tile on screen"
        self.x = x
        self.y = y

    def set_coordinates(self, col, row):
        "Assigns position of tile in the grid"
        self.coordinate = (col, row)

    def place(self, x, y): 
        "Draws hexagon on the screen"
        self.tile = pygame.draw.polygon(screen, BLUE, [(self.x + HEX_SIZE * math.cos(math.radians(angle)), self.y + HEX_SIZE * math.sin(math.radians(angle))) for angle in range(0, 360, 60)], 10)
        
        for angle in range(0, 360, 60):
            index = (angle//60 + self.rotation) % 6
            #draw hex triangle fill, references composition string to get plot color
            pygame.draw.polygon(screen, self.colors[self.composition[index]],
                                [(self.x, self.y),
                                 (self.x + (HEX_SIZE - 4) * math.cos(math.radians(angle)), self.y + (HEX_SIZE - 4) * math.sin(math.radians(angle))),
                                 (self.x + (HEX_SIZE - 4) * math.cos(math.radians(angle+60)), self.y + (HEX_SIZE - 4) * math.sin(math.radians(angle+60)))]
            )
            #draw hex triangle line
            pygame.draw.polygon(screen, BLACK, 
                                [(self.x, self.y), 
                                 (self.x + (HEX_SIZE) * math.cos(math.radians(angle)), self.y + (HEX_SIZE) * math.sin(math.radians(angle))), 
                                 (self.x + (HEX_SIZE) * math.cos(math.radians(angle+60)), self.y + (HEX_SIZE) * math.sin(math.radians(angle+60)))
                                ], width=3
            )
            self.plots[index].center = (self.x + (HEX_SIZE/2) * math.cos(math.radians(angle+30+60*self.rotation)), self.y + (HEX_SIZE/2) * math.sin(math.radians(angle+30+60*self.rotation)))
        
        for angle, plot in zip(range(0, 360, 60), self.plots):
            tile_letter = hex_font.render(plot.letter, True, BLACK)
            screen.blit(tile_letter, ((self.x + (HEX_SIZE-HEX_SIZE/3) * math.cos(math.radians(angle+30))-tile_letter.width/2, self.y + (HEX_SIZE-HEX_SIZE/3) * math.sin(math.radians(angle+30))-tile_letter.height/2)))
        pygame.draw.circle(screen, BLACK, (x, y), HEX_SIZE/5+HEX_SIZE/20)
        pygame.draw.circle(screen, GREEN, (x, y), HEX_SIZE/5)
        if self.city: 
            self.city.place((x, y))
        hex_num = hex_font.render(str(self.value), True, BLACK)

        ## also shows rotation value of given hex for debug
        # hex_num = hex_font.render(str(tile.value)+" "+str(tile.rotation), True, WHITE)

        screen.blit(hex_num, (x - hex_num.width/2, y- hex_num.height/2))
    def adjacency_debug(self): 
        "used to ensure individual plots know when an adjacent tile exists"
        for angle in range(0, 360, 60):
            index = angle//60
            adjaceny_value = hex_font.render(str(int(self.adjacencies[index])), True, BLACK)
            screen.blit(adjaceny_value, ((self.x + (HEX_SIZE-HEX_SIZE/4) * math.cos(math.radians(angle+30))-adjaceny_value.get_width()/2, self.y + (HEX_SIZE-HEX_SIZE/4) * math.sin(math.radians(angle+30))-adjaceny_value.get_height()/2)))


class HexGrid:
    def __init__(self):
        #grid and tile list filled in with tile objects during the draw method
        #grid variable contains the tiles how they appear on the screen, so their relative locations can be easily determined
        self.grid = [[None for _ in range(5)] for _ in range(4)]
        #tile_list contains the same tile objects, but in a single list in numerical order, so they can be iterated through more easily
        self.tile_list = [None for _ in range(20)]
        self.printed = False
        self.tile_highlight = None
        self.printed = False

    def draw_hex_grid(self, rows, cols, hex_size, tiles):
        "Get set of points where tiles will be drawn, then 'place' the tile objects on these points"
        grid_width = (cols - 1) * (1.5 * hex_size) + hex_size
        grid_height = (rows - 1) * (hex_size * math.sqrt(3)) + hex_size * math.sqrt(3)
        offset_x = (WIDTH - grid_width) / 2 + 50
        offset_y = (HEIGHT - grid_height) / 3
        index = 0
        for row in range(rows):
            for col in range(cols):
                tile: HexTile = tiles[index]
                x = col * hex_size * 1.5 + offset_x
                y = row * hex_size * math.sqrt(3) + (hex_size * math.sqrt(3) / 2 * (col % 2)) + offset_y
                tile.set_location(x, y)
                tile.set_coordinates(col, row)
                tile.place(x, y)

                self.grid[row][col] = tile
                self.tile_list[tile.value-1] = tile
                index += 1

        for row in range(rows):
            for col in range(cols):
                self.detect_adjacencies(row, col)
                tile:HexTile
                tile = self.grid[row][col]
                # tile.adjacency_debug()


    def detect_adjacencies(self, row, col):
        "Tell each plot which plot identities are next to it"

        def get_plot_from_adjacent_tile(identity):
            "table for how to shift row and column based on plot index"
            tile_shift = (
                (int(col % 2 == 1), 1),
                (1, 0),
                (1*int(col % 2 == 1), -1),
                (-1*int(col % 2 == 0), -1),
                (-1, 0),
                (-1*int(col % 2 == 0), 1)
            )

            index = identity[1]
            row_shift, col_shift = tile_shift[index]
            adj_tile: HexTile
            adj_tile = self.grid[(row+row_shift)][(col+col_shift)]
            adj_identity = (adj_tile.value, (index+3)%6)
            return adj_identity

        tile: HexTile
        tile = self.grid[row][col]

        #truth table to determine if an adjacent tile exists for a given plot. 
        adjacency_table = [
            (col != 4) and (row != 3 or col%2 == 0), 
            (row != 3), 
            (col != 0) and (row != 3 or col%2 == 0), 
            (col != 0) and (row != 0 or col%2 == 1), 
            (row != 0), 
            (col != 4) and (row != 0 or col%2 == 1)
        ]

        tile.adjacencies = adjacency_table
        plot: Plot
        for plot_adjacent, plot in zip(adjacency_table, tile.plots):
            value, index = plot.identity
            adjacent_plots = [
                (value, (index+1)%6),
                (value, (index-1)%6)
            ]
            if plot_adjacent:
                adjacent_plots.append(get_plot_from_adjacent_tile(plot.identity))
            
            plot.adjacencies = adjacent_plots



    
class InfoBar:
    def __init__(self, players: list):
        self.players = players
        self.round_btn = pygame.Rect(WIDTH*2/5, 4.5*HEIGHT/6,2*WIDTH/10, 0.3*HEIGHT/6)
        self.round_num = 1
        
        #standard scale down for assets
        width_scale = 0.035 * HEIGHT/ (WIDTH+HEIGHT)
        height_scale = 0.035 * WIDTH/ (WIDTH+HEIGHT)

        #load resource icons from assets
        self.resource_icons = (
            ('water', pygame.transform.scale(
            pygame.image.load('assets/droplet.png'), (WIDTH* width_scale, HEIGHT* height_scale))),
            ('food', pygame.transform.scale(
            pygame.image.load('assets/food.png'), (WIDTH* width_scale, HEIGHT* height_scale))),
            ('wood', pygame.transform.scale(
            pygame.image.load('assets/log.png'), (WIDTH* width_scale, HEIGHT* height_scale))),
            ('brick', pygame.transform.scale(
            pygame.image.load('assets/stone.png'), (WIDTH* width_scale, HEIGHT* height_scale))) 
        )

        #load die images from assets
        self.die_icons = {
            4: pygame.transform.scale(
            pygame.image.load('assets/dice/d4.png'), (WIDTH * width_scale, HEIGHT* height_scale)),
            6:pygame.transform.scale(
            pygame.image.load('assets/dice/d6.png'), (WIDTH * width_scale, HEIGHT* height_scale)),
            8:pygame.transform.scale(
            pygame.image.load('assets/dice/d8.png'), (WIDTH * width_scale, HEIGHT* height_scale)),
            12:pygame.transform.scale(
            pygame.image.load('assets/dice/d12.png'), (WIDTH * width_scale, HEIGHT* height_scale)),
            20:pygame.transform.scale(
            pygame.image.load('assets/dice/d20.png'), (WIDTH * width_scale, HEIGHT* height_scale)),
        }



    def draw_sections(self): 
        "Ratios for item sizes were trial and errored to get the info bar to appear nicely"
        offset = (WIDTH/150, HEIGHT/300)
        main_box = [(WIDTH/20, HEIGHT/10), (4*WIDTH/20, 8*HEIGHT/10)]

        round_num_box = [(WIDTH/2-WIDTH/20, 5.1*HEIGHT/6-HEIGHT/25), (WIDTH/10, 0.2*HEIGHT/6)]

        pygame.draw.rect(screen, WHITE, main_box)
        pygame.draw.rect(screen, BLACK, main_box, width=4)

        for n in range(4): 
            pygame.draw.rect(screen, BLACK, [(main_box[0][0], main_box[0][1]+n*HEIGHT/5), (main_box[1][0], main_box[1][1]/4)], width=1)
            player: Player = self.players[n]
            screen.blit(player.name, (WIDTH/20 + offset[0], HEIGHT/10 +n*HEIGHT/5 + offset[1]))
            pygame.draw.circle(screen, color = player.color,radius = WIDTH/300, center=(WIDTH/20 + 5.5 * offset[0], HEIGHT/10 +n*HEIGHT/5 + 3*offset[1]))
            #place icons on infobar
            for index, icon in enumerate(self.resource_icons):
                screen.blit(icon[1], (WIDTH/20+ 2 * offset[0] + index * 7 * offset[0], HEIGHT/10 + (n)*HEIGHT/5  + 8*(index//4+1) * offset[1]))

                value_text, value_rect = generate_text(": " +str( player.resources[icon[0]]), BLACK, WHITE, (WIDTH/20 + 1.3*offset[0] + index * 7 * offset[0] + WIDTH/45, HEIGHT/10+(n)*HEIGHT/5 + 8 * offset[1] + HEIGHT/100))
                screen.blit(value_text, value_rect)
            die: Die
            for index, die in enumerate(player.dice): 
                screen.blit(self.die_icons[die.value], (WIDTH/20+ 2 * offset[0] + index * 5 * offset[0], HEIGHT/10 +(n)*HEIGHT/5  + HEIGHT/5- 10 * offset[1]))

        #next round button
        pygame.draw.rect(screen, GREEN, self.round_btn)
        pygame.draw.rect(screen, BLACK, self.round_btn, 5)
        text, text_rect = generate_text("Play Round",  BLACK, GREEN, self.round_btn.center)
        screen.blit(text, text_rect)
        round_value, round_value_rect = generate_text(f"Round {self.round_num}", BLACK, BROWN, pygame.Rect(round_num_box).center)
        screen.blit(round_value, round_value_rect)



#Technical Elements
class GameEngine: 
    "Central command of the game"
    def __init__(self, game, tiles, grid: HexGrid):
        self.players = [Player(1, RED, self), Player(2, PURPLE, self), Player(3, ORANGE, self), Player(4, YELLOW, self)]
        self.assign_players()
        start_pos_set = False
        self.game = game
        self.grid = grid
        self.info_bar = InfoBar(self.players)
        self.start_locations = []

        #quit button
        self.quit_button = pygame.Rect(9/10*WIDTH, HEIGHT/30, WIDTH/12, HEIGHT/20)
        self.quit_text, self.quit_rect = generate_text("Quit Sim", BLACK, GREEN, self.quit_button.center)

        
        self.draw_screen(tiles)
        self.set_start()

    def draw_screen(self, tiles):
        "Places everything on the screen"
        screen.fill(BROWN)  # Clear the screen with white
        self.grid.draw_hex_grid(4, 5, HEX_SIZE, tiles)
        self.place_tokens()
        self.info_bar.draw_sections()
        pygame.draw.rect(screen, GREEN, self.quit_button)
        pygame.draw.rect(screen, BLACK, self.quit_button, 5)
        screen.blit(self.quit_text, self.quit_rect)

    def place_tokens(self):
        "Place tiles on plots which are labeled occupied"
        tile: HexTile
        for tile in self.grid.tile_list:
            plot: Plot
            for plot in tile.plots:
                if plot.occupied:
                    plot.city.place(plot.center)
                    

    def assign_players(self):
        "Set player names"
        for n, player in enumerate(self.players):
            player.set_name(f"Player {n+1}")

    def set_start(self): 
        "Assign starting location for each player by rolling a d20, referenced in the choose_start Player method"
        for player in self.players: 
            start_value = roll_dice(20)
            player.start_pos = start_value
            player.choose_start(self.grid)

    def play_round(self):
        "Dictates what occurs when round is played"

        for player in self.players:
            player.roll_action()
            if player.position-1 == (self.info_bar.round_num-1)%4:
                player.purchase_action()
                player.card_action()

        self.info_bar.round_num += 1

class Player:
    def __init__(self, position, color, engine:GameEngine):
        self.name = None
        self.position = position
        self.color=color
        self.start_pos = None
        self.engine = engine
        self.cities = [City(self.color) for _ in range(5)]
        self.shop = Shop()        
        self.dice = [Die()]

        #assign resource values at start
        self.resources = {
            'water': (5-position)//2,
            'food': (5-position)//3,
            'wood': (5-position)//4,
            'brick': (5-position)//5
        }

    def set_name(self, name):
        "Sets the name of the player as appears on the infobar"
        self.name = info_font.render(name, True, BLACK)

    def choose_start(self, grid: HexGrid): 
        "Player can choose any land plot on the hextile they are assigned"
        spawn_tile: HexTile = grid.tile_list[self.start_pos-1]
        #two players can not start on the same hex, if they do then the second one to place their tile has to reroll
        if not spawn_tile.occupied:
            spawn_tile.occupied = True
            placed, index = True, 0
            #this iterates through the cities in the player inventory and places one that isnt placed yet. 
            #somewhat unneccessary since it is the first placement, but I am I am afraid of removing it in case anything else important is tied to it. It can possibly be implemented as a separate method
            index = 0
            while placed:
                try:
                    city = self.cities[index]
                    placed = city.placed
                    if not placed: 
                        spawn_tile.city = city
                        return
                    index += 1
                except IndexError:
                    return
        self.start_pos = roll_dice(20)
        self.choose_start(grid)
    
    def roll_action(self):
        die: Die
        for die in self.dice:
            roll_value = die.roll()
            #increase 
            self.resources[die.die_resources[roll_value]] += 1
    
    def purchase_action(self):
        #this is the spot I am at where I am stuck, want to automate buying roads, which connect between adjacent land plots,
        #and new settlements on plots with roads connected to them
        #to do it properly would require pathfinding algorithms, and creating a graph structure to connect all the plots together. 
        print(f"Player {self.position} purchased ___")

    def card_action(self):
        ...


class Shop:
    def __init__(self):
        self.prices = {
            'road': (0, 0, 1, 0, 0, 0, 0, 0),
            'town': (0, 0, 1, 1, 0, 0, 0, 0),
            'aquifer': (2, 0, 3, 4, 0, 0, 0, 0),
            'farm': (1, 2, 4, 4, 0, 0, 0, 0),
            'upgrade6': (0, 2, 2, 0, 0, 0, 0, 0),
            'upgrade8': (2, 1, 1, 2, 0, 0, 0, 0),
            'upgrade10': (2, 1, 3, 4, 0, 0, 0, 0), 
            'upgrade12': (2, 2, 2, 2, 1, 1, 0, 0), 
            'upgrade20': (4, 4, 4, 4, 2, 2, 1, 1), 
        }


class Game:
    def __init__(self):
        self.fullscreen = True
        self.screen = screen
        self.main()


    # Game loop
    def main(self):
        tile_dragging = False
        #initial conditions
        
        #creates list of unplaced tiles
        tiles = shuffle([HexTile(n%8, n+1) for n in range(20)])

        #creates grid where tiles will be placed
        grid = HexGrid()
        #starts the game engine
        engine = GameEngine(self, tiles, grid)
        
        #test to ensure plot adjacency works correctly
        def tile_adjacency_debug(row, col):
            my_tile: HexTile
            my_tile = grid.grid[row][col]
            for plot in my_tile.plots:
                print(plot.adjacencies)

        # tile_debug(2, 3)

        running = True
        while running:
            clock.tick(FPS)  # Limit the frame rate

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not self.fullscreen: 
                            self.screen = pygame.display.set_mode(
                                (0, 0), pygame.FULLSCREEN
                            )
                            self.fullscreen = True
                        else:
                            self.screen = pygame.display.set_mode(
                                (1280, 720)
                            )
                            self.fullscreen = False


                if event.type == pygame.MOUSEBUTTONUP:
                    if engine.info_bar.round_btn.collidepoint(event.pos):
                        engine.play_round()
                    
                    if engine.quit_button.collidepoint(event.pos): 
                        running = False
                
                #Code for drag and dropping tiles, moot due to auto-assigment, may be revisited in the future. 


                # elif event.type == pygame.MOUSEBUTTONDOWN:
                #     if event.button == 1:            
                #         if tile.tile.collidepoint(event.pos):
                #             tile_dragging = True
                #             mouse_x, mouse_y = event.pos
                #             offset_x = tile.x - mouse_x
                #             offset_y = tile.y - mouse_y
                #             print('click')

                # elif event.type == pygame.MOUSEBUTTONUP:
                #     if event.button == 1:            
                #         tile_dragging = False

                # elif event.type == pygame.MOUSEMOTION:
                #     if tile_dragging:
                #         mouse_x, mouse_y = event.pos
                #         tile.x = mouse_x + offset_x
                #         tile.y = mouse_y + offset_y


            # Game logic goes here

            # Drawing
            engine.draw_screen(tiles)
            
            # Update display
            pygame.display.flip()

        # Quit Pygame
        pygame.quit()

if __name__ == "__main__":
    game = Game()
