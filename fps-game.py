import pygame
import math
import sys
import ollama
import threading

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WALL_HEIGHT = 60
WALL_WIDTH = 60
FOV = math.pi / 3  # Field of view
HALF_FOV = FOV / 2
NUM_RAYS = 300
MAX_DEPTH = 1200  # Adjusted for larger maps
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = DIST * WALL_HEIGHT
SCALE = WIDTH // NUM_RAYS

# Ollama API Configuration
OLLAMA_MODEL = "llama3.1"  # Replace with your model if different

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Map Loading
def load_map(filename):
    global player_x, player_y
    map_data = []
    with open(filename, 'r') as file:
        for j, line in enumerate(file):
            row = line.strip()
            map_data.append(list(row))
            if 'S' in row:
                player_y = j * WALL_HEIGHT + WALL_HEIGHT // 2
                player_x = row.index('S') * WALL_WIDTH + WALL_WIDTH // 2
                # Remove the start position marker from the map
                map_data[j][row.index('S')] = '.'
    return map_data

map = load_map('map.txt')  # Map file should be in the same directory as this script

# Player attributes
player_x, player_y = 150, 150  # Initial position might need adjustment based on the map
player_angle = 0
player_speed = 5
show_help = False  # Flag to toggle help display
message = ""  # Variable to store Ollama message
message_timer = 0  # Timer to control message display duration
MESSAGE_DURATION = 3000  # Duration to display message in milliseconds
message_lock = threading.Lock()  # Lock to ensure only one thread handles the message
fullscreen = True  # Flag to track fullscreen mode

def cast_ray(angle):
    """ Cast a ray and return the distance to the obstacle """
    x, y = player_x, player_y
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    for depth in range(MAX_DEPTH):
        x += cos_a
        y += sin_a
        i, j = int(x // WALL_WIDTH), int(y // WALL_HEIGHT)
        if 0 <= j < len(map) and 0 <= i < len(map[0]):
            if map[j][i] == '#':
                return depth
        else:
            return depth
    return MAX_DEPTH

def move_player(dx, dy):
    """ Move player if the new position is not colliding with a wall """
    global player_x, player_y
    new_x = player_x + dx
    new_y = player_y + dy
    i, j = int(new_x // WALL_WIDTH), int(new_y // WALL_HEIGHT)
    if 0 <= j < len(map) and 0 <= i < len(map[0]) and map[j][i] != '#':
        player_x, player_y = new_x, new_y

def draw_background():
    """ Draw the floor and ceiling """
    screen.fill((135, 206, 235), (0, 0, WIDTH, HEIGHT // 2))
    screen.fill((60, 60, 60), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))

def draw_walls():
    """ Render the walls based on the ray casting """
    start_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        angle = start_angle + ray * FOV / NUM_RAYS
        depth = cast_ray(angle)
        depth *= math.cos(player_angle - angle)  # Correct fish-eye effect
        wall_height = int(PROJ_COEFF / (depth + 0.0001))  # Avoid division by zero
        color = 255 - int(depth / MAX_DEPTH * 255)
        pygame.draw.rect(screen, (color, color, color), (ray * SCALE, HEIGHT // 2 - wall_height // 2, SCALE, wall_height))

def draw_help():
    """ Draw help information """
    font = pygame.font.Font(None, 36)
    help_text = [
        "W, A, S, D: Move",
        "Mouse: Look Around",
        "F1: Toggle Help",
        "F2: Get Message",
        "F: Toggle Fullscreen"
    ]
    for i, line in enumerate(help_text):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (10, 10 + i * 40))

def draw_message():
    """ Draw game message at the bottom of the screen """
    global message, message_timer
    if message and pygame.time.get_ticks() < message_timer:
        font = pygame.font.Font(None, 36)
        text_surface = font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 30))  # Center text horizontally

        # Draw a background for the message
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 60, WIDTH, 60))  # Black background
        screen.blit(text_surface, text_rect)  # Draw text on screen
    elif pygame.time.get_ticks() >= message_timer:
        message = ""  # Clear the message when the timer expires

def get_ollama_message():
    """ Fetch a message from the Ollama API in a separate thread """
    global message, message_timer
    try:
        with message_lock:  # Ensure only one thread fetches a message at a time
            stream = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': 'in a few words imply that there is a secret in this stage. its like a type of maze game. dont print anything else'}],
                stream=True,
            )
            message = ""
            for chunk in stream:
                message += chunk['message']['content']
            message_timer = pygame.time.get_ticks() + MESSAGE_DURATION
    except Exception as e:
        message = f"Error: {str(e)}"
        message_timer = pygame.time.get_ticks() + MESSAGE_DURATION

def main():
    global player_x, player_y, player_angle, show_help, message, message_timer, fullscreen
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                x, y = event.rel
                player_angle += x * 0.005  # Adjust mouse sensitivity here
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    show_help = not show_help
                elif event.key == pygame.K_F2:
                    if not message:
                        threading.Thread(target=get_ollama_message).start()
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.display.flip()  # Update the display mode

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_w]:
            move_player(math.cos(player_angle) * player_speed, math.sin(player_angle) * player_speed)
        if keys[pygame.K_s]:
            move_player(-math.cos(player_angle) * player_speed, -math.sin(player_angle) * player_speed)
        if keys[pygame.K_d]:
            move_player(math.cos(player_angle + math.pi / 2) * player_speed, math.sin(player_angle + math.pi / 2) * player_speed)
        if keys[pygame.K_a]:
            move_player(-math.cos(player_angle + math.pi / 2) * player_speed, -math.sin(player_angle + math.pi / 2) * player_speed)

        draw_background()
        draw_walls()
        if show_help:
            draw_help()
        draw_message()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
