import os

import pygame
from PIL import Image

from ai.semantic_search import find_best_response

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Medieval RPG - NPC Chat")

# Fonts & colors
FONT = pygame.font.Font(None, 28)  # Input font
CHAT_FONT = pygame.font.Font(None, 24)  # Chat log font
COLOR_INACTIVE = pygame.Color("lightskyblue3")
COLOR_ACTIVE = pygame.Color("dodgerblue2")
COLOR_BG = (30, 30, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_BUBBLE = (50, 50, 50)

# --- Get absolute paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Path to this script
ASSETS_DIR = os.path.join(BASE_DIR, "assets")  # Assets folder


# --- Helper to load images with Pillow ---
def load_image(path, size=None):
    """Load image with Pillow and convert to Pygame surface."""
    img = Image.open(path).convert("RGBA")
    if size:
        img = img.resize(size)
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


# --- Load NPC assets ---
npc_assets = {
    "blacksmith": load_image(os.path.join(ASSETS_DIR, "blacksmith.jpeg"), (80, 80)),
    "inkeeper": load_image(
        os.path.join(ASSETS_DIR, "inkeeper.jpeg"), (80, 80)
    ),  # note single 'n' to match file
}

# --- Load background map (Castlegate) ---
try:
    town_map = load_image(os.path.join(ASSETS_DIR, "town_map.jpeg"), (WIDTH, HEIGHT))
except Exception:
    town_map = None
    print("No castlegate.jpeg found, using plain background.")

# NPC positions on map
npc_positions = {"blacksmith": (100, 150), "inkeeper": (400, 200)}

# Input & chat state
user_text = ""
input_active = False
chat_log = []

# Current NPC
npc_name = "blacksmith"

# Input box
INPUT_BOX = pygame.Rect(50, HEIGHT - 50, 700, 32)

# --- Main loop ---
running = True
while running:
    screen.fill(COLOR_BG)

    # Draw map if available
    if town_map:
        screen.blit(town_map, (0, 0))

    # Draw NPCs and dialogue bubbles
    for npc, pos in npc_positions.items():
        screen.blit(npc_assets[npc], pos)

        # Draw last line of NPC chat above NPC
        last_lines = [line for line in chat_log if line.startswith(f"{npc}:")]
        if last_lines:
            text = last_lines[-1].split(f"{npc}:")[1].strip()
            bubble_surface = CHAT_FONT.render(text, True, COLOR_TEXT)
            bubble_rect = bubble_surface.get_rect(midbottom=(pos[0] + 40, pos[1] - 10))
            pygame.draw.rect(screen, COLOR_BUBBLE, bubble_rect.inflate(10, 10))
            screen.blit(bubble_surface, bubble_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Activate input box
            input_active = INPUT_BOX.collidepoint(event.pos)

            # Check if NPC clicked
            for npc, pos in npc_positions.items():
                npc_rect = npc_assets[npc].get_rect(topleft=pos)
                if npc_rect.collidepoint(event.pos):
                    npc_name = npc
                    chat_log.append(f"System: You are now talking to {npc_name}.")

        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    if user_text.strip():
                        response = find_best_response(user_text, npc_name)
                        chat_log.append(f"You: {user_text}")
                        chat_log.append(f"{npc_name}: {response}")
                        user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

    # Draw chat log (bottom-left)
    y_offset = HEIGHT - 250
    for line in chat_log[-10:]:
        txt_surface = CHAT_FONT.render(line, True, COLOR_TEXT)
        screen.blit(txt_surface, (50, y_offset))
        y_offset += 24

    # Draw input box
    color = COLOR_ACTIVE if input_active else COLOR_INACTIVE
    pygame.draw.rect(screen, color, INPUT_BOX, 2)
    txt_surface = FONT.render(user_text, True, COLOR_TEXT)
    screen.blit(txt_surface, (INPUT_BOX.x + 5, INPUT_BOX.y + 5))

    pygame.display.flip()

pygame.quit()
