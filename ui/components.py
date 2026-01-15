import pygame
from ui import colors

class InputBox:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = colors.BORDER_COLOR
        self.text = ""
        self.font = font
        self.txt_surface = self.font.render(self.text, True, colors.TEXT_WHITE)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = colors.ACCENT_BLUE if self.active else colors.BORDER_COLOR
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                content = self.text
                self.text = ""
                self.txt_surface = self.font.render(self.text, True, colors.TEXT_WHITE)
                return content
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.txt_surface = self.font.render(self.text, True, colors.TEXT_WHITE)
            else:
                self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, colors.TEXT_WHITE)
        return None

    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, colors.BG_PANEL, self.rect)
        # Draw border
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        # Draw text
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw cursor
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer % 60 < 30: # Blink speed
                cursor_x = self.rect.x + 10 + self.txt_surface.get_width()
                pygame.draw.line(screen, colors.TEXT_WHITE, (cursor_x, self.rect.y + 8), (cursor_x, self.rect.y + self.rect.height - 8), 2)


class ChatLog:
    def __init__(self, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.messages = [] # List of (sender, message, color)

    def add_message(self, sender, text, color=colors.TEXT_WHITE):
        self.messages.append((sender, text, color))
        if len(self.messages) > 50: # Keep history manageable
             self.messages.pop(0)

    def draw(self, screen):
        # Draw translucent background
        s = pygame.Surface((self.rect.width, self.rect.height))
        s.set_alpha(180)
        s.fill((0,0,0))
        screen.blit(s, (self.rect.x, self.rect.y))
        
        # Render messages from bottom up
        y_offset = self.rect.bottom - 20
        for sender, text, color in reversed(self.messages):
            # Simple wrapping or just truncation for now could be improved later
            full_text = f"{sender}: {text}" if sender else text
            
            # Basic word wrap handled by rendering simply for now
            # If line too long, we might need a real wrap function, but let's keep it simple first
            
            text_surface = self.font.render(full_text, True, color)
            
            # Only draw if it fits in the box
            if y_offset - text_surface.get_height() < self.rect.top:
                break
                
            screen.blit(text_surface, (self.rect.x + 10, y_offset - text_surface.get_height()))
            y_offset -= (text_surface.get_height() + 5)

class SpeechBubble:
    @staticmethod
    def draw(screen, text, pos, font):
        text_surface = font.render(text, True, colors.SPEECH_BUBBLE_TEXT)
        rect = text_surface.get_rect(midbottom=(pos[0] + 40, pos[1] - 15))
        
        padding = 8
        bg_rect = rect.inflate(padding * 2, padding * 2)
        
        pygame.draw.rect(screen, colors.SPEECH_BUBBLE_BG, bg_rect, border_radius=10)
        pygame.draw.polygon(screen, colors.SPEECH_BUBBLE_BG, [
            (bg_rect.centerx - 5, bg_rect.bottom),
            (bg_rect.centerx + 5, bg_rect.bottom),
            (bg_rect.centerx, bg_rect.bottom + 8)
        ])
        
        screen.blit(text_surface, rect)
