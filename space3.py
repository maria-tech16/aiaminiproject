import pygame, random

# =============================
# 1. Initialize Pygame
# =============================
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 Space Shooter with AI Enemies")
clock = pygame.time.Clock()

# =============================
# 2. Load Images (AFTER display created)
# =============================
player_img = pygame.image.load("assets/player.png").convert_alpha()
bullet_img = pygame.image.load("assets/bullet.png").convert_alpha()
enemy_img = pygame.image.load("assets/enemy.png").convert_alpha()
shield_img = pygame.image.load("assets/shield.png").convert_alpha()
double_img = pygame.image.load("assets/double.png").convert_alpha()
bomb_img = pygame.image.load("assets/bomb.png").convert_alpha()

# =============================
# 3. Colors & Fonts
# =============================
BLACK, WHITE, RED, GREEN = (0,0,0), (255,255,255), (255,60,60), (0,255,0)
font = pygame.font.SysFont("Arial", 22, bold=True)

# =============================
# 4. Game Variables
# =============================
player_width, player_height = player_img.get_width(), player_img.get_height()
player_speed = 6
score = 0
lives = 3
bullets = []
bullet_speed = -7
enemies = []
enemy_speed = 2
enemy_spawn_time = 50
frame_count = 0
powerups = []
powerup_types = ["shield", "double", "bomb"]

# Powerup states
double_shoot = False
shield_active = False
shield_timer = 0

# Background stars
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(60)]

# =============================
# 5. Helper Functions
# =============================
def reset_game():
    global score, lives, bullets, enemies, frame_count
    global powerups, double_shoot, shield_active, shield_timer, enemy_spawn_time
    score, lives = 0, 3
    bullets, enemies, powerups = [], [], []
    frame_count = 0
    double_shoot = False
    shield_active = False
    shield_timer = 0
    enemy_spawn_time = 50

def draw_stars():
    for (x,y) in stars:
        pygame.draw.circle(screen, WHITE, (x,y), 1)

def draw_player(x, y):
    screen.blit(player_img, (x, y))
    if shield_active:
        # Center the shield aura around player
        screen.blit(shield_img, (x-10, y-10))

def draw_bullets(bullets):
    for bx, by in bullets:
        screen.blit(bullet_img, (bx, by))

def draw_enemies(enemies):
    for ex, ey in enemies:
        screen.blit(enemy_img, (ex, ey))

def draw_powerups(powerups):
    for px, py, ptype in powerups:
        if ptype == "shield":
            screen.blit(shield_img, (px, py))
        elif ptype == "double":
            screen.blit(double_img, (px, py))
        elif ptype == "bomb":
            screen.blit(bomb_img, (px, py))

def enemy_ai(enemies, bullets, player_x):
    new_enemies = []
    for ex, ey in enemies:
        move_x = 0
        # dodge bullets
        for bx, by in bullets:
            if abs(bx - ex) < 30 and by < ey:
                move_x = 5 if ex > WIDTH//2 else -5
        # chase player sometimes
        if random.random() < 0.02:
            if player_x > ex: move_x = 3
            elif player_x < ex: move_x = -3
        ex += move_x
        ey += enemy_speed
        ex = max(0, min(WIDTH - enemy_img.get_width(), ex))
        new_enemies.append((ex, ey))
    return new_enemies

# =============================
# 6. Game Loop
# =============================
running, game_over = True, False
player_x, player_y = WIDTH//2, HEIGHT-60
reset_game()

while running:
    clock.tick(30)
    screen.fill(BLACK)
    draw_stars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if double_shoot:
                    bullets.append((player_x+10, player_y-20))
                    bullets.append((player_x+player_width-10, player_y-20))
                else:
                    bullets.append((player_x + player_width//2, player_y-20))
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                game_over = False
                player_x, player_y = WIDTH//2, HEIGHT-60
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed

        # Update bullets
        bullets = [(bx, by+bullet_speed) for bx, by in bullets if by > 0]

        # Enemy spawn speed scaling
        if score < 10: enemy_spawn_time = 50
        elif score < 20: enemy_spawn_time = 40
        elif score < 40: enemy_spawn_time = 30
        elif score < 70: enemy_spawn_time = 20
        else: enemy_spawn_time = 15

        # Spawn enemies
        frame_count += 1
        if frame_count % enemy_spawn_time == 0:
            ex = random.randint(0, WIDTH-enemy_img.get_width())
            enemies.append((ex, 0))

        # Update enemies
        enemies = enemy_ai(enemies, bullets, player_x)

        # Update powerups
        powerups = [(px, py+2, ptype) for px, py, ptype in powerups if py < HEIGHT]

        # Bullet collisions
        hit_enemies, new_bullets = [], []
        for bx, by in bullets:
            hit = False
            for i, (ex, ey) in enumerate(enemies):
                if ex < bx < ex+enemy_img.get_width() and ey < by < ey+enemy_img.get_height():
                    hit_enemies.append(i)
                    hit = True
                    score += 1
                    # Chance to drop powerup
                    if random.random() < 0.2:
                        ptype = random.choice(powerup_types)
                        powerups.append((ex+20, ey, ptype))
                    break
            if not hit: new_bullets.append((bx, by))
        bullets = new_bullets
        enemies = [e for i, e in enumerate(enemies) if i not in hit_enemies]

        # Enemy reaching bottom
        survived = []
        for ex, ey in enemies:
            if ey >= HEIGHT-30:
                if not shield_active:
                    lives -= 1
                    double_shoot = False
                    if lives <= 0:
                        game_over = True
                else:
                    shield_active = False
            else:
                survived.append((ex, ey))
        enemies = survived

        # Powerup collection
        new_powerups = []
        for px, py, ptype in powerups:
            if player_x < px < player_x+player_width and player_y-30 < py < player_y+player_height:
                if ptype=="shield":
                    shield_active = True
                    shield_timer = pygame.time.get_ticks()
                elif ptype=="double":
                    double_shoot = True
                elif ptype=="bomb":
                    enemies = []
                continue
            new_powerups.append((px, py, ptype))
        powerups = new_powerups

        # Shield expires after 5 sec
        if shield_active and pygame.time.get_ticks() - shield_timer > 5000:
            shield_active = False

        # Draw everything
        draw_player(player_x, player_y)
        draw_bullets(bullets)
        draw_enemies(enemies)
        draw_powerups(powerups)
        score_text = font.render(f"Score: {score}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, GREEN)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH-100, 10))
    else:
        over_text = font.render("GAME OVER!", True, RED)
        retry_text = font.render("Press R to Restart or ESC to Quit", True, WHITE)
        screen.blit(over_text, (WIDTH//3, HEIGHT//2-20))
        screen.blit(retry_text, (WIDTH//5, HEIGHT//2+20))

    pygame.display.update()

pygame.quit()
