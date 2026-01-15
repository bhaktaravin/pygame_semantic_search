import os
import pygame
from PIL import Image
from ai.semantic_search import find_best_response
from ui import colors
from ui.components import InputBox, ChatLog, SpeechBubble

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Medieval RPG - NPC Chat")

# Fonts
FONT = pygame.font.Font(None, 28)
CHAT_FONT = pygame.font.Font(None, 24)

# --- Get absolute paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- Helper to load images with Pillow & Transparency Fix ---
def load_image(path, size=None, colorkey=None):
    """Load image with Pillow, resize, and convert to Pygame surface."""
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size)
        surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
        
        # Automatic transparency based on top-left pixel if not specified
        if colorkey is None:
            colorkey = surface.get_at((0, 0))
            
        surface.set_colorkey(colorkey)
        return surface
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pygame.Surface(size if size else (50, 50))


# --- Load Assets ---
npc_assets = {
    "blacksmith": load_image(os.path.join(ASSETS_DIR, "blacksmith.jpeg"), (80, 80)),
    "inkeeper": load_image(os.path.join(ASSETS_DIR, "inkeeper.jpeg"), (80, 80)),
}

town_map = None
try:
    # Use load_image but no colorkey for background
    img = Image.open(os.path.join(ASSETS_DIR, "town_map.jpeg")).convert("RGB") # Map shouldn't have transparency
    if img:
         img = img.resize((WIDTH, HEIGHT))
         town_map = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
except Exception as e:
    print(f"No town_map.jpeg found or error: {e}")


# NPC positions
npc_positions = {"blacksmith": (100, 150), "inkeeper": (400, 200)}

# --- UI Instances ---
chat_log = ChatLog(50, HEIGHT - 250, 700, 190, CHAT_FONT)
input_box = InputBox(50, HEIGHT - 50, 700, 32, FONT)

# Game State
running = True
npc_name = "blacksmith" # Selected NPC
chat_log.add_message("System", f"You are approaching the {npc_name}.", colors.CHAT_SYSTEM)

# --- Main loop ---
clock = pygame.time.Clock()

while running:
    screen.fill(colors.BG_DARK)

    # 1. Draw Map
    if town_map:
        screen.blit(town_map, (0, 0))

    # 2. Draw NPCs
    for npc, pos in npc_positions.items():
        screen.blit(npc_assets[npc], pos)
        
        # Highlight selected NPC
        if npc == npc_name:
            # Draw a subtle selection marker (e.g., triangle above)
            pygame.draw.polygon(screen, colors.ACCENT_BLUE, [
                (pos[0] + 40, pos[1] - 10),
                (pos[0] + 35, pos[1] - 20),
                (pos[0] + 45, pos[1] - 20)
            ])

        # Draw Speech Bubble if they spoke recently
        # We need to find the last message from this NPC
        last_msg = None
        for sender, text, _ in reversed(chat_log.messages):
            if sender == npc:
                last_msg = text
                break
        
        if last_msg:
             # Basic check to see if we should show bubble (e.g. only if last message was recent?)
             # For now, just show lag message
             SpeechBubble.draw(screen, last_msg, pos, CHAT_FONT)


    # 3. Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pass events to UI
        user_input = input_box.handle_event(event)
        if user_input:
            chat_log.add_message("You", user_input, colors.CHAT_YOU)
            response = find_best_response(user_input, npc_name)
            chat_log.add_message(npc_name, response, colors.CHAT_NPC)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check for NPC selection
            for npc, pos in npc_positions.items():
                rect = npc_assets[npc].get_rect(topleft=pos)
                if rect.collidepoint(event.pos):
                    npc_name = npc
                    chat_log.add_message("System", f"Talking to {npc_name}.", colors.CHAT_SYSTEM)
                    break 

    # 4. Draw UI
    chat_log.draw(screen)
    input_box.draw(screen)

    pygame.display.flip()
    clock.tick(60) # Limit FPS

pygame.quit()
