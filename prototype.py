from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin, cos, radians
import math
import random

# === Global Variables ===
camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 800  
GRID_WIDTH = 120
rand_var = 423

player_pos = [0, 780, -30]  # x, y, z
player_angle = 180

player_life = 5
missed_bullets = 0
game_over = False
score = 0
fall = False

cheat_mode = False
cheat_rotation_speed = 2  # degrees per frame
cheat_fire_cooldown = 10  # frames between shots
cheat_fire_timer = 0

BOUNDARY_WIDTH = GRID_WIDTH  
BOUNDARY_HIGHT = GRID_LENGTH  

# Enemy variables
enemy_positions = []  # Initialize empty list
new_enemy_positions = []
new_enemy_spawn_timer = 0
NEW_ENEMY_SPAWN_INTERVAL = 300  # frames between spawns

# Giant enemy variables
giant_enemies = []
GIANT_ENEMY_SPAWN_INTERVAL = 1500  # frames between giant enemy spawns
giant_enemy_spawn_timer = 0

# Pickup variables
pickups = []  # Each pickup: {'pos': [x,y,z], 'type': 'health'/'ammo'/'score', 'speed': float}
PICKUP_SPAWN_INTERVAL = 700  # frames between spawns
pickup_spawn_timer = 0

camera_angle_horizontal = 0.0
camera_height = 500
follow_player = False

pulse_time = 0.0

bullets = []  # Each bullet = {'pos': [x, y, z], 'angle': deg}
bullet_speed = 5

# Sphere markers variables
SPHERE_RADIUS = GRID_WIDTH * 1.2  # Much larger than grid width
sphere_markers = [
    {'pos': [0, -GRID_LENGTH +65 - SPHERE_RADIUS, SPHERE_RADIUS//2], 'color': [.8, 1, 0], 'blink_time': 0},  # Entrance sphere
    {'pos': [0, GRID_LENGTH -130+ SPHERE_RADIUS, SPHERE_RADIUS//2], 'color': [1, .8, 0], 'blink_time': 0}    # Exit sphere
]
BLINK_DURATION = 30  # frames

escaped_enemies = 0
MAX_ESCAPED_ENEMIES = 20
game_over_reason = ""  # Can be "life", "bullets", or "escaped"

game_started = False
last_score = 0
last_reason = ""
pickup_messages = []  #  messages to  show when pickups are collected
PICKUP_MESSAGE_DURATION = 120 # frames  (about 2 seconds at 60fps)
# Initialize enemies
def init_enemies():
    global enemy_positions
    enemy_positions = [spawn_enemy() for _ in range(5)]

# === Input Handlers ===
def keyboardListener(key, x, y):
    global fovY, player_pos, player_angle, game_over, game_started, game_over_reason
    if not game_started and key == b' ':
        game_started = True
        glutPostRedisplay()
        return
    
    move_step = 10
    rotate_step = 25

    if key == b'r' and game_over:
        reset_game()
        glutPostRedisplay()
        return

    if game_over:
        return
    
    if key == b'z':
        fovY = max(10, fovY - 5)
    elif key == b'x':
        fovY = min(170, fovY + 5)
    elif key == b'w':
        new_x = player_pos[0] + move_step * sin(radians(player_angle))
        new_y = player_pos[1] + move_step * cos(radians(player_angle))
        if abs(new_x) > BOUNDARY_WIDTH or abs(new_y) > BOUNDARY_HIGHT:
            print("Player fell off the bridge")
            game_over = True
            fall = True
            game_over_reason = "fall"
        player_pos[0] = new_x
        player_pos[1] = new_y
    elif key == b's':
        new_x = player_pos[0] - move_step * sin(radians(player_angle))
        new_y = player_pos[1] - move_step * cos(radians(player_angle))
        if abs(new_x) > BOUNDARY_WIDTH or abs(new_y) > BOUNDARY_HIGHT:
            print("Player fell off the bridge")
            game_over = True
            fall = True  
            game_over_reason = "fall"  
        player_pos[0] = new_x
        player_pos[1] = new_y
    elif key == b'a':
        player_angle -= rotate_step
    elif key == b'd':
        player_angle += rotate_step
    elif key == b'c':
        global cheat_mode
        cheat_mode = not cheat_mode
        print("Cheat mode:", "ON" if cheat_mode else "OFF")    

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_angle_horizontal, camera_height
    if key == GLUT_KEY_LEFT:
        camera_angle_horizontal -= 0.05
    elif key == GLUT_KEY_RIGHT:
        camera_angle_horizontal += 0.05
    elif key == GLUT_KEY_UP:
        camera_height += 10
    elif key == GLUT_KEY_DOWN:
        camera_height -= 10
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global follow_player

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
        bullets.append({'pos': [bx, by, bz], 'angle': player_angle})

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_player = not follow_player

    glutPostRedisplay()

# === Game Functions ===
def spawn_enemy(min_distance=150, is_new_type=False):
    # Trigger entrance sphere blink
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [1, 1, 1]  #  white for spawn
    
    while True:
        x = random.randint(-GRID_WIDTH / 2 , GRID_WIDTH /2)
        y = -GRID_LENGTH + 50  # Always spawn at entrance
        z = 10

        px, py, _ = player_pos
        distance = math.sqrt((x - px)**2 + (y - py)**2)

        if distance >= min_distance:
            if is_new_type:
                return {'pos': [x, y, z], 'health': 5, 'direction': random.choice([-1, 1])}
            else:
                return (x, y, z)

def spawn_giant_enemy():
    #  Trigger entrance  sphere blink
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [1, 0.5, 0]  #  Orange for giant spawn
    
    x = random.randint(-GRID_WIDTH / 2, GRID_WIDTH / 2)
    y = -GRID_LENGTH + 50  #  Spawn at entrance
    z = 10
    
    return {
        'pos': [x, y, z],
        'health': 15,
        'max_health': 15,
        'speed': 0.5  # Slower than regular enemies
    }

def spawn_pickup():
    x = random.randint(-GRID_WIDTH/2, GRID_WIDTH/2)
    y = -GRID_LENGTH
    z = 30
    
    pickup_type = random.choice(['health', 'ammo', 'score'])
    speed = random.uniform(0.8, 1.5)
    
    return {'pos': [x, y, z], 'type': pickup_type, 'speed': speed}

def reset_game():
    global player_pos, bullets, player_life, missed_bullets
    global game_over, score, pickup_spawn_timer, new_enemy_positions, pickups
    global escaped_enemies, game_over_reason, giant_enemies, giant_enemy_spawn_timer
    global last_score, last_reason, game_started, pickup_messages
    
    last_score = score
    last_reason = game_over_reason
    
    player_pos = [0, 780, -30]
    bullets = []
    init_enemies()
    new_enemy_positions = []
    pickups = []
    pickup_messages = []
    player_life = 5
    missed_bullets = 0
    game_over = False
    score = 0
    pickup_spawn_timer = 0
    escaped_enemies = 0
    game_over_reason = ""
    giant_enemies = []
    giant_enemy_spawn_timer = 0
    game_started = True  # Auto-start after reset
    glutPostRedisplay()
    
# === Drawing Functions ===
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_sphere_markers():
    for i, marker in enumerate(sphere_markers):
        if marker['blink_time'] > 0:
            marker['blink_time'] -= 1
            if marker['blink_time'] <= 0:
                marker['color'] = [1, 1, 0]  # Reset to yellow
        
        glPushMatrix()
        glTranslatef(*marker['pos'])
        glColor3f(*marker['color'])
        
        if i == 1:  # This is the exit marker (index 1)
            # Draw a cube instead of sphere for the exit
            glScalef(1.2, 0.1, 1.2)
            glutSolidCube(SPHERE_RADIUS * 1.5)  # Slightly larger than the sphere would be
        else:
            
            glutSolidSphere(SPHERE_RADIUS, 50, 50)
        
        glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(*player_pos)

    if game_over:
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 40, 0)
    else:
        glRotatef(-player_angle, 0, 0, 1)

    # Body
    glPushMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.6, 0.3, 1.0)
    glutSolidCube(40)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 95)
    glutSolidCube(20)
    glPopMatrix()

    # Arms
    glPushMatrix()
    glColor3f(0.9, 0.7, 0.6)
    glTranslatef(13, 10, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.2, 1.2, 5)
    glutSolidCube(5)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.9, 0.7, 0.6)
    glTranslatef(-13, 10, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.2, 1.2, 5)
    glutSolidCube(5)
    glPopMatrix()

    # Gun
    glPushMatrix()
    glColor3f(0.75, 0.75, 0.75)
    glTranslatef(0, 25, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.5, 1.5, 8)
    glutSolidCube(5)
    glPopMatrix()

    # Legs
    for dx in [-5, 5]:
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(dx, 0, 20)
        gluCylinder(gluNewQuadric(), 2.5, 5, 25, 20, 20)
        glPopMatrix()

    glPopMatrix()

def draw_floor_with_boundaries():
    grid_row = 40
    grid_col = 6
    tile_size = 40
    half_size_col = grid_col * tile_size / 2.0
    half_size_row = grid_row * tile_size / 2.0
    color_r = 1
    color_g = 1
    color_b = 1
    
    for i in range(grid_col):
        for j in range(grid_row):
            color_r -= .0001
            color_g -= .00322
            color_b -= .022
            glColor3f(color_r, color_g, color_b)
            x = i * tile_size - half_size_col
            y = j * tile_size - half_size_row
            
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
            glEnd()

def draw_enemy(position):
    x, y, z = position
    z = 50  
    scale = 1.0 + 0.2 * math.sin(pulse_time)

    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    glColor3f(.5, .5, 1.0)
    gluSphere(gluNewQuadric(), 30, 35, 20)  

    glColor3f(0, 0, 0.501)
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 15, 20, 20)  
    glPopMatrix()

def draw_new_enemy(enemy):
    x, y, z = enemy['pos']
    health = enemy['health']
    pulse = 0.1 * math.sin(pulse_time * 2) if health < 5 else 0
    
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    size_scale = 1.0 + (5 - health) * 0.1 + pulse
    glScalef(size_scale, size_scale, size_scale)
    
    health_color = health / 5.0
    glColor3f(1.0, health_color, health_color)
    gluSphere(gluNewQuadric(), 40, 30, 30) 
   
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(15, 15, 30)
    gluSphere(gluNewQuadric(), 8, 10, 10) 
    glTranslatef(-30, 0, 0)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_giant_enemy(enemy):
    x, y, z = enemy['pos']
    health_ratio = max(0.1, enemy['health'] / enemy['max_health'])  # Keep at least 10% size when alive
    
    glPushMatrix()
    glTranslatef(x, y, z + 80)  # Higher position
    
    # Main body - scales with health
    body_scale = 0.5 + 0.5 * health_ratio  # Scales between 50%-100% of original size
    glPushMatrix()
    glScalef(body_scale, body_scale, body_scale)
    glColor3f(0.7, 0.2, 0.2)  # Dark red
    glutSolidSphere(60, 40, 40)
    glPopMatrix()
    
    # Eyes - don't scale with health
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(20 * body_scale, 20 * body_scale, 40 * body_scale)
    glutSolidSphere(10, 20, 20)
    glTranslatef(-40 * body_scale, 0, 0)
    glutSolidSphere(10, 20, 20)
    glPopMatrix()
    
    # Health bar - scales in width with health
    glPushMatrix()
    glTranslatef(0, 0, 90 * body_scale)  # Position scales with body
    glColor3f(0.2/body_scale, 0.2, 0.2)  # Dark gray background
    glScalef(1.0* body_scale, 0.1 * body_scale, 0.1 * body_scale)  # Scale thickness with body
    glutSolidCube(120)  # Full width background
    
    # Health bar foreground - scales with health
    glPushMatrix()
    glTranslatef(-60 * (1 - health_ratio), 0, 0)  # Center the shrinking bar
    glColor3f(1 - health_ratio, health_ratio, 0)  # Red to green
    glScalef(health_ratio, 1.0, 1.0)  # Scale width with health
    glutSolidCube(120)  # Scaled width
    glPopMatrix()
    
    glPopMatrix()
    
    glPopMatrix()

def draw_pickup(pickup):
    x, y, z = pickup['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    
    if pickup['type'] == 'health':
        glColor3f(0.0, 1.0, 0.0)  # Green
    elif pickup['type'] == 'ammo':
        glColor3f(0.0, 0.0, 1.0)  # Blue
    else:  # score
        glColor3f(1.0, 0.4, 0.7)  # Pink
    
    glRotatef(pulse_time * 50, 0, 1, 1)
    glutSolidCube(25)
    glPopMatrix()

def draw_bullet(bullet):
    x, y, z = bullet['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.3, 0.3, 0.3)
    glColor3f(0.4, 0.2, 0.3)
    glutSolidCube(20)
    glPopMatrix()

# === Movement Functions ===
def move_enemy_towards_player():
    global enemy_positions
    speed = 1
    updated_positions = []
    
    for ex, ey, ez in enemy_positions:
        px, py, _ = player_pos
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)

        if distance > 1e-2:
            dx /= distance
            dy /= distance
            ex += dx * speed
            ey += dy * speed

        # Check if enemy reached exit sphere
        if ey > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]  # Red for exit
            ex, ey, ez = spawn_enemy()
            
        updated_positions.append((ex, ey, ez))
    enemy_positions[:] = updated_positions

def move_new_enemies():
    global new_enemy_positions, score, escaped_enemies, game_over, game_over_reason
    
    speed = 1.5
    
    for enemy in new_enemy_positions[:]:
        if enemy['pos'][1] < 0:
            enemy['pos'][1] += speed * 0.8
        else:
            enemy['pos'][1] += speed * 0.8
            
        if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
            new_enemy_positions.remove(enemy)
            score += 100
        elif enemy['pos'][1] > GRID_LENGTH - 50:  # Reached exit
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]  # Red for exit
            new_enemy_positions.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES:
                game_over = True
                game_over_reason = "escaped"

def move_giant_enemies():
    global giant_enemies, score, escaped_enemies, game_over, game_over_reason
    
    for enemy in giant_enemies[:]:
        # Move straight toward exit (positive Y direction)
        enemy['pos'][1] += enemy['speed']
        
        # Check if reached exit
        if enemy['pos'][1] > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]  # Red for exit
            giant_enemies.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES:
                game_over = True
                game_over_reason = "escaped"

def move_pickups():
    global pickups
    for pickup in pickups[:]:
        if pickup['pos'][1] < 0:
            pickup['pos'][1] += pickup['speed']
        else:
            pickup['pos'][1] += pickup['speed']
            
        if abs(pickup['pos'][1]) > BOUNDARY_HIGHT:
            pickups.remove(pickup)

# === Game Logic Functions ===
def check_collisions():
    global bullets, enemy_positions, player_life, game_over, score
    global new_enemy_positions, missed_bullets, pickups, giant_enemies, game_over_reason

    bullet_radius = 10
    enemy_radius = 20
    player_radius = 30
    new_bullets = []
    
    px, py, pz = player_pos
    
    # Bullet collisions
    for bullet in bullets[:]:
        bx, by, bz = bullet['pos']
        bullet_hit = False
        
        # Regular enemies
        for i in range(len(enemy_positions)):
            ex, ey, ez = enemy_positions[i]
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - ez)**2)
            if dist < bullet_radius + enemy_radius + 20:
                bullet_hit = True
                enemy_positions[i] = spawn_enemy()
                score += 1
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue
                
        # New enemies
        for enemy in new_enemy_positions[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - (ez))**2)
            
            if dist < 50:
                bullet_hit = True
                enemy['health'] -= 1
                score += 1
                
                angle = math.atan2(by - ey, bx - ex)
                knockback = 100
                enemy['pos'][0] -= knockback * math.cos(angle)
                enemy['pos'][1] -= knockback * math.sin(angle)
                
                if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or 
                    abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
                    new_enemy_positions.remove(enemy)
                    score += 10
                elif enemy['health'] <= 0:
                    new_enemy_positions.remove(enemy)
                    score += 10
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue
            
        # Giant enemies
        for enemy in giant_enemies[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - (ez))**2)
            
            if dist < 70:  # Larger hit radius for giant enemy
                bullet_hit = True
                enemy['health'] -= 3
                score += 1  # 1 point per hit
                
                if enemy['health'] <= 0:
                    giant_enemies.remove(enemy)
                    score += 15  # Bonus 15 points for killing
                
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue

    # Enemy-player collisions
    # Regular enemies
    for i in range(len(enemy_positions)):
        ex, ey, ez = enemy_positions[i]
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - ez)**2)
        if dist < player_radius + enemy_radius:
            player_life -= 1
            enemy_positions[i] = spawn_enemy()
            if player_life <= 0:
                game_over = True
                game_over_reason = "life"
    
    # New enemies
    for enemy in new_enemy_positions[:]:
        ex, ey, ez = enemy['pos']
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - (ez))**2)
        
        if dist < player_radius + 40:
            
            player_life -= 2
            
            
            enemy['health'] -= 1
            
            # Apply knockback to enemy
            angle = math.atan2(py - ey, px - ex)
            knockback = 100
            enemy['pos'][0] -= knockback * math.cos(angle)
            enemy['pos'][1] -= knockback * math.sin(angle)
            
            # Remove enemy if out of bounds or dead
            if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or 
                abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
                new_enemy_positions.remove(enemy)
            elif enemy['health'] <= 0:
                new_enemy_positions.remove(enemy)
            
            if player_life <= 0:
                game_over = True
                game_over_reason = "life"
    # Giant enemy-player collisions
    for enemy in giant_enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - (ez))**2)
        
        if dist < player_radius + 60:  # Larger collision radius
            player_life -= 3  # More damage from giant enemy
            if player_life <= 0:
                game_over = True
                game_over_reason = "life"

    # Pickup collisions
    player_collision_height = pz + 50
    
    for pickup in pickups[:]:
        pickup_x, pickup_y, pickup_z = pickup['pos']
        
        dx = px - pickup_x
        dy = py - pickup_y
        dz = player_collision_height - pickup_z
        
        distance_sq = dx*dx + dy*dy + dz*dz
        collision_distance_sq = (player_radius + 15)**2
        
        if distance_sq < collision_distance_sq:
            if pickup['type'] == 'health':
                player_life = min(10, player_life + 5)
                pickup_messages.append({'text': "Health +5!", 'time': PICKUP_MESSAGE_DURATION})
            elif pickup['type'] == 'ammo':
                missed_bullets = max(0, missed_bullets - 5)
                pickup_messages.append({'text': "Ammo +5!", 'time': PICKUP_MESSAGE_DURATION})
            else:  # score
                score += 30
                pickup_messages.append({'text': "Score +30!", 'time': PICKUP_MESSAGE_DURATION})
            
            pickups.remove(pickup)

def rotate_gun_cheat_mode():
    global player_angle
    player_angle = (player_angle + cheat_rotation_speed) % 360

def will_bullet_hit(px, py, dir_x, dir_y, ex, ey, hit_radius=15):
    vx = ex - px
    vy = ey - py
    dot = vx * dir_x + vy * dir_y

    if dot < 0:
        return False

    closest_x = px + dot * dir_x
    closest_y = py + dot * dir_y
    dist_sq = (closest_x - ex) ** 2 + (closest_y - ey) ** 2

    return dist_sq <= hit_radius ** 2

def auto_aim_and_fire():
    px, py, pz = player_pos
    angle_rad = radians(player_angle)
    dir_x = math.sin(angle_rad)
    dir_y = math.cos(angle_rad)

    for ex, ey, ez in enemy_positions:
        if will_bullet_hit(px, py, dir_x, dir_y, ex, ey):
            fire_cheat_bullet()
            return True
    return False

def fire_cheat_bullet():
    bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
    bullets.append({'pos': [bx, by, bz], 'angle': player_angle})

def update_bullets():
    global bullets, missed_bullets
    new_bullets = []
    for bullet in bullets:
        angle_rad = math.radians(bullet['angle'])
        bullet['pos'][0] += bullet_speed * math.sin(angle_rad)
        bullet['pos'][1] += bullet_speed * math.cos(angle_rad)

        if abs(bullet['pos'][0]) < GRID_WIDTH and abs(bullet['pos'][1]) < GRID_LENGTH:
            new_bullets.append(bullet)
        else:
            missed_bullets += 1
    bullets = new_bullets

# === Camera Setup ===
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    look()

def look():
    if follow_player:
        px, py, pz = player_pos
        angle_rad = radians(player_angle)
        eye_x = px + 15* sin(angle_rad)
        eye_y = py + 15 * cos(angle_rad)
        eye_z = pz + 85
        center_x = px + 100 * sin(angle_rad)
        center_y = py + 100 * cos(angle_rad)
        center_z = pz + 75
    else:
        radius = 800
        eye_x = radius * sin(camera_angle_horizontal)
        eye_y = radius * cos(camera_angle_horizontal)
        eye_z = camera_height
        center_x = 0
        center_y = 0
        center_z = 0

    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

# === Main Game Loop ===
def idle():
    global pulse_time, game_over, cheat_fire_timer
    global new_enemy_spawn_timer, pickup_spawn_timer, score, giant_enemy_spawn_timer ,game_over_reason

    if game_over:
        return

    pulse_time += 0.05
    
    # Enemy movement and spawning
    move_enemy_towards_player()
    
    if not game_over:
        # Regular enemy spawning
        new_enemy_spawn_timer += 1
        if new_enemy_spawn_timer >= NEW_ENEMY_SPAWN_INTERVAL:
            new_enemy_positions.append(spawn_enemy(is_new_type=True))
            new_enemy_spawn_timer = 0
        
        # Giant enemy spawning
        giant_enemy_spawn_timer += 1
        if giant_enemy_spawn_timer >= GIANT_ENEMY_SPAWN_INTERVAL:
            giant_enemies.append(spawn_giant_enemy())
            giant_enemy_spawn_timer = 0
        
        move_new_enemies()
        move_giant_enemies()

        # Pickup spawning and movement
        pickup_spawn_timer += 1
        if pickup_spawn_timer >= PICKUP_SPAWN_INTERVAL:
            pickups.append(spawn_pickup())
            pickup_spawn_timer = 0
        move_pickups()

    if cheat_mode:
        rotate_gun_cheat_mode()
        cheat_fire_timer += 1
        if cheat_fire_timer >= cheat_fire_cooldown:
            if auto_aim_and_fire():
                cheat_fire_timer = 0

    update_bullets()
    check_collisions()

    if player_life <= 0:
        game_over = True
        game_over_reason = "life"
    elif missed_bullets >= 10:
        game_over = True
        game_over_reason = "bullets"
    glutPostRedisplay()

def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Set up orthogonal projection for 2D rendering
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    
    
    # Title - using larger font
    glColor3f(1, 1, 1)
    
    glRasterPos2f(300, 650)
    for char in "CUBE COMMANDO: ALONE WARRIOR":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    # Story lines
    story_lines = [
        "In a world dominated by evil circles,",
        "you are the last square warrior standing from the Squre word.",
        "",
        "Defend your bridge from the invading circles !",
        "",
        
        "Press SPACE to begin your defense!"
    ]
    
    y_pos = 550
    for line in story_lines:
        glRasterPos2f(350, y_pos)
        for char in line:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        y_pos -= 30
        
        
    # Dark background
    glColor3f(0.1, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    
    glEnd()
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def draw_pickup_notifications():
    if not pickup_messages:
        return
        
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Position in top-right corner
    x_pos = 700
    y_pos = 700
    
    for i, message in enumerate(pickup_messages[:]):
        # Fade out effect based on remaining time
        alpha = min(1.0, message['time'] / (PICKUP_MESSAGE_DURATION/2))
        glColor4f(1, 1, 1, alpha)
        
        draw_text(x_pos, y_pos - i*30, message['text'], GLUT_BITMAP_HELVETICA_12)
        
        # Update timer and remove expired messages
        message['time'] -= 1
        if message['time'] <= 0:
            pickup_messages.remove(message)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def showScreen():
    global game_started, game_over, game_over_reason
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if not game_started:
        draw_start_screen()
        return

    
    glViewport(0, 0, 1000, 800)
    setupCamera()
    
    draw_text(10, 770, f"Score: {score}  Life: {player_life}  Missed: {missed_bullets}  Escaped: {escaped_enemies}/{MAX_ESCAPED_ENEMIES}")
    
    draw_floor_with_boundaries()
    draw_player()
    draw_sphere_markers()

    for enemy in enemy_positions:
        draw_enemy(enemy)
        
    for enemy in new_enemy_positions:
        draw_new_enemy(enemy)
          
    for enemy in giant_enemies:
        draw_giant_enemy(enemy)
        
    for pickup in pickups:
        draw_pickup(pickup)
        
    for bullet in bullets:
        draw_bullet(bullet)

    # Draw pickup notifications
    draw_pickup_notifications()

    # Game over messages
    if game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        m= "asdfgasdf"
        # Message text
        if game_over_reason == "escaped":
            glColor3f(1, 0.2, 0.2)
            draw_text(250, 600, "The Square world is destroyed by the circles!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "The Square world is destroyed by the circles!"
        elif game_over_reason == "life":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You were defeated!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "Game Over! You were defeated!"
        elif game_over_reason == "bullets":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You ran out of ammo!", GLUT_BITMAP_TIMES_ROMAN_24)
            m= "Game Over! You ran out of ammo!"
        elif game_over_reason == "fall":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You have fall of the Bridge!", GLUT_BITMAP_TIMES_ROMAN_24)
            m= "Game Over! You have fall of the Bridge!"
        
        # Show last score and reason
        glColor3f(1, 1, 1)
        draw_text(350, 450, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 420, f"Reason: {m}", GLUT_BITMAP_HELVETICA_18)
        print(m)
        
        draw_text(400, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        # Dark semi-transparent background
        glColor4f(0.1, 0.2, 0, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(200, 250)
        glVertex2f(800, 250)
        glVertex2f(800, 550)
        glVertex2f(200, 550)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        
        
        

    glutSwapBuffers()

# === Initialization ===
def init():
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    init_enemies()

# === Entry Point ===
if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Cube Comando- Alone Warrior")
    init()
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()