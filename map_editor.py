import pygame
import sys

# Constants
WIDTH, HEIGHT = 1000, 600
TILE_SIZE = 40
MAP_WIDTH, MAP_HEIGHT = 20, 15
FPS = 60

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)  # Color for starting position
GREY = (200, 200, 200)
LIGHT_GREY = (220, 220, 220)
DARK_GREY = (50, 50, 50)

# Map data
map_data = [['.' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
start_point = None  # To store the starting point

def draw_grid():
    for x in range(0, WIDTH - 200, TILE_SIZE):  # Reserve space for panel
        for y in range(0, HEIGHT, TILE_SIZE):
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, GREY, rect, 1)  # Draw grid lines

def draw_map():
    for j in range(MAP_HEIGHT):
        for i in range(MAP_WIDTH):
            if map_data[j][i] == '#':
                pygame.draw.rect(screen, BLACK, (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif map_data[j][i] == 'S':
                pygame.draw.rect(screen, GREEN, (i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                pygame.draw.line(screen, WHITE, (i * TILE_SIZE, j * TILE_SIZE), ((i + 1) * TILE_SIZE, (j + 1) * TILE_SIZE), 2)
                pygame.draw.line(screen, WHITE, ((i + 1) * TILE_SIZE, j * TILE_SIZE), (i * TILE_SIZE, (j + 1) * TILE_SIZE), 2)

def save_map(filename='map.txt'):
    with open(filename, 'w') as file:
        for row in map_data:
            file.write(''.join(row) + '\n')
    print("Map saved to", filename)

def load_map(filename='map.txt'):
    global map_data, start_point
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            map_data = [list(line.strip()) for line in lines]
        # Find the starting point
        start_point = None
        for j, row in enumerate(map_data):
            for i, cell in enumerate(row):
                if cell == 'S':
                    start_point = (i, j)
                    break
            if start_point:
                break
    except FileNotFoundError:
        print("File not found. Please save a map first.")
    except Exception as e:
        print(f"An error occurred while loading the map: {e}")

def draw_buttons():
    # Draw save button
    save_rect = pygame.Rect(WIDTH - 190, 50, 180, 40)
    pygame.draw.rect(screen, LIGHT_GREY if save_hover else DARK_GREY, save_rect)
    text = font.render('Save Map', True, WHITE)
    screen.blit(text, (WIDTH - 180, 60))

    # Draw load button
    load_rect = pygame.Rect(WIDTH - 190, 100, 180, 40)
    pygame.draw.rect(screen, LIGHT_GREY if load_hover else DARK_GREY, load_rect)
    text = font.render('Load Map', True, WHITE)
    screen.blit(text, (WIDTH - 180, 110))

save_hover = False
load_hover = False

def check_button_hover():
    global save_hover, load_hover
    mouse_x, mouse_y = pygame.mouse.get_pos()
    save_hover = WIDTH - 190 <= mouse_x <= WIDTH - 10 and 50 <= mouse_y <= 90
    load_hover = WIDTH - 190 <= mouse_x <= WIDTH - 10 and 100 <= mouse_y <= 140

def handle_mouse_click():
    global map_data, start_point
    x, y = pygame.mouse.get_pos()
    if x < WIDTH - 200:  # Click is within the map area
        i, j = x // TILE_SIZE, y // TILE_SIZE
        if map_data[j][i] == 'S':
            map_data[j][i] = '.'  # Remove start point if clicked
            start_point = None
        else:
            map_data[j][i] = '#' if map_data[j][i] == '.' else '.'
    elif save_hover:
        save_map()
    elif load_hover:
        load_map()

def handle_key_press():
    global map_data, start_point
    keys = pygame.key.get_pressed()
    if keys[pygame.K_s]:  # If 'S' key is pressed
        x, y = pygame.mouse.get_pos()
        if x < WIDTH - 200:  # Click is within the map area
            i, j = x // TILE_SIZE, y // TILE_SIZE
            if start_point:
                map_data[start_point[1]][start_point[0]] = '.'  # Remove old start point
            map_data[j][i] = 'S'
            start_point = (i, j)

def main():
    running = True
    while running:
        screen.fill(WHITE)
        draw_grid()
        draw_map()
        draw_buttons()
        check_button_hover()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click()
            elif event.type == pygame.KEYDOWN:
                handle_key_press()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
