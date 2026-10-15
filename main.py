import pygame
import math
import random
import array
import sys

# Pygame initialize
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

WIDTH, HEIGHT = 480, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UnknownXPanel - The God of Panel")
clock = pygame.time.Clock()

# Colors
BG_DARK = (10, 12, 18)
CYAN_MAIN = (0, 240, 255)
GOLD_TAG = (255, 195, 0)
WHITE = (255, 255, 255)
GRAY_LINE = (35, 45, 65)

SKY_BLUE = (30, 40, 80)
GROUND_GREEN = (20, 60, 30)
ROAD_DARK = (40, 40, 45)
ROAD_LIGHT = (55, 55, 60)
PLAYER_COLOR = (0, 220, 255)
BLOCK_COLOR = (255, 50, 80)
SHIELD_COLOR = (255, 215, 0)

# Sound Tone Synthesizer
def create_tone(freq, duration_ms):
    sample_rate = 22050
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        val = int(32767 * 0.2 * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    return pygame.mixer.Sound(buf)

notes = [220, 261, 293, 329, 392, 329, 293, 261]
tones = [create_tone(n, 180) for n in notes]
music_idx = 0
music_timer = 0

# Fonts
font_title = pygame.font.SysFont("sans-serif", 36, bold=True)
font_sub = pygame.font.SysFont("sans-serif", 18, bold=True)
font_hud = pygame.font.SysFont("sans-serif", 24, bold=True)

# Game Variables
current_state = "SPLASH"  # SPLASH ya GAME
splash_timer = 0.0

player_x = 0.0
player_target_x = 0.0
speed = 8.0
distance = 0.0
score = 0
game_over = False

shield_timer_ms = 0
last_shield_distance = 0

obstacles = []
for z in range(300, 1500, 250):
    lane = random.choice([-0.65, 0.0, 0.65])
    obstacles.append([float(z), lane])

# Main Loop
running = True
while running:
    dt = clock.tick(30)
    music_timer += dt

    # Background rhythm audio
    if music_timer > 220:
        music_timer = 0
        tones[music_idx].play()
        music_idx = (music_idx + 1) % len(tones)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
            if current_state == "SPLASH":
                current_state = "GAME"
            elif game_over:
                # Reset
                player_x = 0.0
                player_target_x = 0.0
                distance = 0.0
                score = 0
                shield_timer_ms = 0
                last_shield_distance = 0
                obstacles = [[float(z), random.choice([-0.65, 0.0, 0.65])] for z in range(300, 1500, 250)]
                game_over = False
            else:
                pos_x = pygame.mouse.get_pos()[0]
                if pos_x < WIDTH / 3:
                    player_target_x = -0.65
                elif pos_x > 2 * WIDTH / 3:
                    player_target_x = 0.65
                else:
                    player_target_x = 0.0

    # 1. SPLASH SCREEN (UnknownXPanel - The God of Panel)
    if current_state == "SPLASH":
        splash_timer += 0.05
        screen.fill(BG_DARK)

        # Pulse Glow Effect
        pulse = (math.sin(splash_timer) + 1.0) / 2.0
        glow_val = int(pulse * 255)

        # Panel Card Box
        card = pygame.Rect(30, 180, WIDTH - 60, 320)
        pygame.draw.rect(screen, (16, 22, 34), card, border_radius=16)
        pygame.draw.rect(screen, GRAY_LINE, card, 2, border_radius=16)

        # Title: UNKNOWNXPANEL
        t_surf = font_title.render("UNKNOWNXPANEL", True, (0, glow_val, 255))
        screen.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 230))

        # Subtitle: THE GOD OF PANEL
        s_surf = font_sub.render("THE GOD OF PANEL", True, CYAN_MAIN)
        screen.blit(s_surf, (WIDTH // 2 - s_surf.get_width() // 2, 290))

        # Tap prompt
        start_surf = font_sub.render(">> TAP SCREEN TO PLAY <<", True, GOLD_TAG)
        screen.blit(start_surf, (WIDTH // 2 - start_surf.get_width() // 2, 400))

        # Auto transition after 3.5 seconds
        if splash_timer > 3.5:
            current_state = "GAME"

    # 2. 3D RUNNER GAME STATE
    elif current_state == "GAME":
        if not game_over:
            player_x += (player_target_x - player_x) * 0.25
            distance += speed
            score = int(distance // 10)

            # Shield Logic: Every 100 meters, activate 10 seconds (10000 ms)
            current_100m_mark = score // 100
            if current_100m_mark > last_shield_distance:
                last_shield_distance = current_100m_mark
                shield_timer_ms = 10000

            if shield_timer_ms > 0:
                shield_timer_ms = max(0, shield_timer_ms - dt)

            for obs in obstacles:
                obs[0] -= speed
                if obs[0] < 60 and abs(player_x - obs[1]) < 0.45:
                    if shield_timer_ms <= 0:
                        game_over = True
                    else:
                        obs[0] = 1300
                        obs[1] = random.choice([-0.65, 0.0, 0.65])
                if obs[0] < 10:
                    obs[0] = 1200 + random.randint(0, 200)
                    obs[1] = random.choice([-0.65, 0.0, 0.65])

        # Drawing Sky & Road Depth
        screen.fill(GROUND_GREEN)
        pygame.draw.rect(screen, SKY_BLUE, (0, 0, WIDTH, HEIGHT // 2))

        horizon_y = HEIGHT // 2
        road_bottom_w = WIDTH * 0.85

        for i in range(12, 0, -1):
            z1 = i * 60 - (distance % 60)
            z2 = (i - 1) * 60 - (distance % 60)
            if z2 <= 0:
                continue
            y1 = horizon_y + int((HEIGHT - horizon_y) * (150 / (z1 + 150)))
            y2 = horizon_y + int((HEIGHT - horizon_y) * (150 / (z2 + 150)))
            w1 = int(road_bottom_w * (150 / (z1 + 150)))
            w2 = int(road_bottom_w * (150 / (z2 + 150)))

            color = ROAD_LIGHT if (int((z1 + distance) // 60) % 2 == 0) else ROAD_DARK
            pts = [(WIDTH // 2 - w1 // 2, y1), (WIDTH // 2 + w1 // 2, y1),
                   (WIDTH // 2 + w2 // 2, y2), (WIDTH // 2 - w2 // 2, y2)]
            pygame.draw.polygon(screen, color, pts)

        # Draw 3D Blocks
        for obs in sorted(obstacles, key=lambda x: -x[0]):
            z = obs[0]
            if z <= 20:
                continue
            scale = 180 / (z + 180)
            oy = horizon_y + int((HEIGHT - horizon_y) * scale)
            cx = WIDTH // 2 + int(obs[1] * (road_bottom_w // 2) * scale)
            ow = int(70 * scale)
            oh = int(60 * scale)
            if ow > 2 and oh > 2:
                pygame.draw.rect(screen, BLOCK_COLOR, (cx - ow // 2, oy - oh, ow, oh))

        # Draw Player
        p_scale = 180 / (40 + 180)
        py = horizon_y + int((HEIGHT - horizon_y) * p_scale)
        px = WIDTH // 2 + int(player_x * (road_bottom_w // 2) * p_scale)
        pw = int(75 * p_scale)
        ph = int(65 * p_scale)

        if shield_timer_ms > 0:
            pygame.draw.circle(screen, SHIELD_COLOR, (px, py - ph // 2), int(pw * 0.9), 4)

        pygame.draw.rect(screen, PLAYER_COLOR, (px - pw // 2, py - ph, pw, ph), border_radius=6)

        # Top Game HUD
        dist_txt = font_hud.render(f"Distance: {score}m", True, WHITE)
        screen.blit(dist_txt, (20, 20))

        if shield_timer_ms > 0:
            sec_left = math.ceil(shield_timer_ms / 1000)
            shield_txt = font_hud.render(f"SHIELD: {sec_left}s", True, SHIELD_COLOR)
            screen.blit(shield_txt, (20, 50))

        if game_over:
            gover_surf = font_hud.render("CRASHED! Tap to Restart", True, (255, 80, 80))
            screen.blit(gover_surf, (WIDTH // 2 - gover_surf.get_width() // 2, HEIGHT // 3))

    pygame.display.flip()

pygame.quit()
sys.exit()
              
