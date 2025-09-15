import pygame
import random
import sys
import time
import os   # to check if image exists

# Initialize pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("assets/sound/background-music.ogg")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop indefinitely
is_muted = False

# Screen setup
WIDTH, HEIGHT = 650, 650
ROWS, COLS = 5, 5
RADIUS = 40
GAP = 40
BACKGROUND_COLOR = (76, 187, 23)  # Light green

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Whack-a-Mole")

# Font setup
font = pygame.font.SysFont("comicsans", 30)

mole_image = None
image_path = "assets/img/zombie.png"
if os.path.exists(image_path):
    mole_image = pygame.image.load(image_path)
    mole_image = pygame.transform.scale(mole_image, (RADIUS * 2 - 10, RADIUS * 2 - 10))
    
# Load sound effect
sound_effect = None
sound_path = "assets/sound/whack-mole.flac"
if os.path.exists(sound_path):
    try:
        sound_effect = pygame.mixer.Sound(sound_path)
    except Exception as e:
        print("Error loading sound:", e)


class Circle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.filled = False  # False = empty hole, True = mole
        self.timer = 0

    def draw(self, screen):
        # Draw hole (black border + brown fill)
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), RADIUS + 5)
        pygame.draw.circle(screen, (139, 69, 19), (self.x, self.y), RADIUS)

        # If mole is active
        if self.filled:
            if mole_image:  # CHANGE: Draw image if available
                rect = mole_image.get_rect(center=(self.x, self.y))
                screen.blit(mole_image, rect.topleft)
            else:  # Fallback red dot
                pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), RADIUS - 10)

    def is_clicked(self, pos):
        dx = self.x - pos[0]
        dy = self.y - pos[1]
        distance = (dx**2 + dy**2) ** 0.5
        return distance <= RADIUS - 10 if self.filled else False
        # Only detect clicks on the mole


# Create grid of holes
circles = []
for row in range(ROWS):
    for col in range(COLS):
        x = GAP + col * (2 * RADIUS + GAP) + RADIUS 
        y = GAP + row * (2 * RADIUS + GAP) + RADIUS + 20
        circles.append(Circle(x, y))


def reset_mole():
    for circle in circles:
        circle.filled = False
        circle.timer = 0
    new_circle = random.choice(circles)
    new_circle.filled = True

def toggle_mute():
    if is_muted:
        pygame.mixer.music.set_volume(0.5)
    else:
        pygame.mixer.music.set_volume(0)
    is_muted = not is_muted

# Game variables
score = 0
hit=0
clicked = 0
reset_mole()
game_time = 60
start_ticks = pygame.time.get_ticks()
background = pygame.image.load("assets/img/grass.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


# Game loop
clock = pygame.time.Clock()
running = True
while running:
    screen.blit(background, (0, 0))

    # Timer
    seconds = game_time - (pygame.time.get_ticks() - start_ticks) // 1000
    if seconds <= 0:
        running = False  # End game

    # Draw circles
    for circle in circles:
        circle.draw(screen)

    # Draw score and timer
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    timer_text = font.render(f"Time: {seconds}", True, (0, 0, 0))
    accuracy = hit * 100 / clicked if clicked > 0 else 0
    Accuracy_text = font.render(f"Accuracy: {accuracy:.2f}%", True, (0, 0, 0))
    
    screen.blit(score_text, (10, 10) )
    screen.blit(timer_text, (WIDTH - 150, 10))
    screen.blit(Accuracy_text, (WIDTH//2 - Accuracy_text.get_width()//2, 10))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            clicked +=1
            pos = pygame.mouse.get_pos()
            for circle in circles:
                if circle.is_clicked(pos):  # Only mole counts
                    hit+=1
                    score += 1
                    if sound_effect:
                        sound_effect.play()
                    reset_mole()
                    break
            else:
                score -= 1  # Clicked wrong place (not mole)
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_q:
                running = False
            if event.key == pygame.K_m:
                toggle_mute()
    for circle in circles:
        if circle.filled:
            circle.timer += 1
            if circle.timer > 60:
                circle.filled = False
                circle.timer = 0
                reset_mole()
    pygame.display.update()
    clock.tick(30)

# Game over screen
screen.fill(BACKGROUND_COLOR)
end_text = (
    f"Game Over!\n"
    f"Score: {score}\n"
    f"Clicks: {clicked}\n"
    f"Hits: {hit}\n"
    f"Accuracy: {accuracy:.2f}%"
)
lines = end_text.split('\n')
rendered_lines = [font.render(line, True, (0, 0, 0)) for line in lines]

# Blit each line to the screen at appropriate positions
y_offset = 100  # Starting y position
for line_surface in rendered_lines:
    screen.blit(line_surface, (100, y_offset))
    y_offset += line_surface.get_height() + 10
pygame.display.update()
time.sleep(5)
pygame.quit()
