import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Unique Hex Objects")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

GREEN = (60, 200, 90)
BLUE = (80, 130, 255)

CENTER_GREEN = (20, 180, 60)


class Triangle:
    def __init__(self, points, color):
        self.points = points
        self.color = color

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points)
        pygame.draw.polygon(surface, BLACK, self.points, 1)


class HexTile:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

        self.vertices = self.calculate_vertices()

        # Each hex gets its own random triangle layout
        self.triangle_colors = self.generate_random_colors()

        self.triangles = self.create_triangles()

    def calculate_vertices(self):
        vertices = []

        # Flat-top hexagon
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = math.radians(angle_deg)

            px = self.x + self.size * math.cos(angle_rad)
            py = self.y + self.size * math.sin(angle_rad)

            vertices.append((px, py))

        return vertices

    def generate_random_colors(self):
        """
        Generate a random mix of green and blue
        triangles for this specific hex.
        """

        colors = []

        # Random number of green triangles (0-6)
        green_count = random.randint(0, 6)

        # Create color pool
        for _ in range(green_count):
            colors.append(GREEN)

        for _ in range(6 - green_count):
            colors.append(BLUE)

        # Shuffle so positions are random
        random.shuffle(colors)

        return colors

    def create_triangles(self):
        triangles = []

        for i in range(6):

            center = (self.x, self.y)
            p2 = self.vertices[i]
            p3 = self.vertices[(i + 1) % 6]

            triangle = Triangle([center, p2, p3], self.triangle_colors[i])

            triangles.append(triangle)

        return triangles

    def draw(self, surface):

        # Draw all 6 triangles
        for triangle in self.triangles:
            triangle.draw(surface)

        # Draw outer hex border
        pygame.draw.polygon(surface, BLACK, self.vertices, 2)

        # Center circle ALWAYS green
        pygame.draw.circle(
            surface, CENTER_GREEN, (int(self.x), int(self.y)), int(self.size * 0.22)
        )

        pygame.draw.circle(
            surface, BLACK, (int(self.x), int(self.y)), int(self.size * 0.22), 2
        )


class HexGrid:
    def __init__(self, rows, cols, hex_size, start_x, start_y):

        self.rows = rows
        self.cols = cols
        self.hex_size = hex_size
        self.start_x = start_x
        self.start_y = start_y

        self.hexes = []

        self.create_grid()

    def create_grid(self):

        width = self.hex_size * 2

        # Flat-top spacing
        horizontal_spacing = width * 0.75
        vertical_spacing = math.sqrt(3) * self.hex_size

        for row in range(self.rows):
            for col in range(self.cols):

                x = self.start_x + col * horizontal_spacing

                y = self.start_y + row * vertical_spacing

                # Offset every other column
                if col % 2 == 1:
                    y += vertical_spacing / 2

                # Every hex is its own object
                hex_tile = HexTile(x, y, self.hex_size)

                self.hexes.append(hex_tile)

    def draw(self, surface):

        for hex_tile in self.hexes:
            hex_tile.draw(surface)


def main():

    clock = pygame.time.Clock()
    running = True

    # 4 rows vertical, 5 columns horizontal
    grid = HexGrid(rows=4, cols=5, hex_size=50, start_x=120, start_y=120)

    while running:

        screen.fill(WHITE)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        grid.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
