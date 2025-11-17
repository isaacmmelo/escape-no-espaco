# ----------- IMPORTS ----------- #
import pgzrun
import math
import random
from pygame.rect import Rect # PYGame Exception

# ----------- CONFIG ----------- #
# Screen
WIDTH = 800
HEIGHT = 600
TITLE = "Esquiva Espacial"

# ----------- VARIABLES ----------- #
# Global
game_state = "MENU" # States: "MENU", "PLAYING", "GAME_OVER"
score = 0
enemy_spawn_interval = 60
base_enemy_speed = 2
current_enemy_speed = base_enemy_speed

# Game Control
player = None
enemies = []
enemy_spawn_timer = 0
level_up_timer = 0
level_up_interval = 60 * 10 

# Menu click
start_button_rect = None
music_button_rect = None
quit_button_rect = None
restart_button_rect = None
menu_button_rect = None

# Sprites
PLAYER_SPRITES = ["player_ship"] # Player Ship img
ENEMY_SPRITES = ["enemy_ship1", "enemy_ship2", "enemy_ship3"] # Enemies ships img

# ----------- CLASS ----------- #

#Animation Sprite Class
class AnimatedSprite:
    
    def __init__(self, images, x, y, speed=0): # Default speed = 0
        self.images = images # List of images for animation
        self.current_image_index = 0
        self.animation_frames_delay = 10  # Frames to wait before switching image
        self.animation_timer = 0 

        self.actor = Actor(self.images[0]) # Create Actor with the first image
        self.actor.pos = (x, y)
        self.speed = speed

    def update_animation(self):
        self.animation_timer += 1  # Increment the animation timer
        
        if self.animation_timer >= self.animation_frames_delay:
            self.animation_timer = 0  # Reset the animation timer
            
            self.current_image_index = (self.current_image_index + 1) % len(self.images) # Move to the next image index and use operator % to loop back
            self.actor.image = self.images[self.current_image_index] # Update the actor's image

    def draw(self):
        self.actor.draw()  # Draw the actor on the screen

# Player Class
class Player(AnimatedSprite):
    def __init__(self, x, y, images, speed):
        super().__init__(images, x, y, speed) # Call parent constructor
        self.actor.midbottom = (x, y) # Set initial position

    def update(self):
        self.update_animation() 

        # Movement controls
        if keyboard.left: 
            self.actor.x -= self.speed # Move left decreasing x
        if keyboard.right:
            self.actor.x += self.speed # Move right increasing x
        if keyboard.up:
            self.actor.y -= self.speed # Move up decreasing y
        if keyboard.down:
            self.actor.y += self.speed # Move down increasing y

        self.actor.clamp_ip(Rect(0, 0, WIDTH, HEIGHT)) # Keep player within screen bounds

# Enemy Class
class Enemy(AnimatedSprite):
    def __init__(self, x, y, images, speed):
        super().__init__(images, x, y, speed) # Call parent constructor
        self.actor.top = y # Set initial position in top upper part of screen

    def update(self):
        self.update_animation() # Update enemy animation
        self.actor.y += self.speed # Move enemy down increasing y

    def is_offscreen(self):
        return self.actor.top > HEIGHT # Check if enemy is offscreen

# ----------- SCREENS ----------- #

# Draw Menu
def draw_menu():
    global start_button_rect, music_button_rect, quit_button_rect # Menu button rects
    screen.fill((0, 0, 0)) # Fill screen with black
    screen.draw.text(TITLE, center=(WIDTH // 2, HEIGHT // 4), color="white", fontsize=60) # Draw title text
    
    # Define button dimensions
    BTN_WIDTH = 300
    BTN_HEIGHT = 50

    # 1. Start Game Button
    start_center = (WIDTH // 2, HEIGHT // 2)
    start_button_rect = Rect(0, 0, BTN_WIDTH, BTN_HEIGHT) 
    start_button_rect.center = start_center # Center the Rect
    screen.draw.text("INICIAR JOGO", center=start_center, color="white", fontsize=35) # Draw the text centered in the Rect

    # 2. Music & Sounds Button
    music_center = (WIDTH // 2, HEIGHT // 2 + 70) # 70 pixels below the previous
    music_button_rect = Rect(0, 0, BTN_WIDTH, BTN_HEIGHT)
    music_button_rect.center = music_center 
    music_status = "ON" if music.is_playing("game_music") else "OFF" # Check music status
    screen.draw.text(f"MÚSICA & SONS: {music_status}", center=music_center, color="white", fontsize=30) # Draw the text centered in the Rect

    # 3. Quit Button
    quit_center = (WIDTH // 2, HEIGHT // 2 + 140) # 70 pixels below the previous
    quit_button_rect = Rect(0, 0, BTN_WIDTH, BTN_HEIGHT)
    quit_button_rect.center = quit_center
    screen.draw.text("SAIR", center=quit_center, color="white", fontsize=35) # Draw the text centered in the Rect

# Draw Game Over Screen
def draw_game_over():
    global restart_button_rect, menu_button_rect # Game Over button rects
    screen.fill((0, 0, 0)) # Fill screen with black
    
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 4), color="red", fontsize=70) # Game Over Text
    screen.draw.text(f"Pontuação Final: {score}", center=(WIDTH // 2, HEIGHT // 2 - 50), color="white", fontsize=40) # Draw final score text

    # Define button dimensions
    BTN_WIDTH = 300
    BTN_HEIGHT = 50
    
    # 1. Restart Game Button
    restart_center = (WIDTH // 2, HEIGHT // 2 + 50) # 50 pixels below the score
    restart_button_rect = Rect(0, 0, BTN_WIDTH, BTN_HEIGHT) # Create Rect
    restart_button_rect.center = restart_center
    screen.draw.text("REINICIAR JOGO", center=restart_center, color="blue", fontsize=35) # Draw the text centered in the Rect


    # 2. Back to Menu Button
    menu_center = (WIDTH // 2, HEIGHT // 2 + 120) # 70 pixels below the previous
    menu_button_rect = Rect(0, 0, BTN_WIDTH, BTN_HEIGHT)
    menu_button_rect.center = menu_center # Center the Rect
    screen.draw.text("VOLTAR AO MENU", center=menu_center, color="white", fontsize=35) # Draw the text centered in the Rect
    
    # Quit Instruction
    screen.draw.text("Pressione 'Q' para Sair", center=(WIDTH // 2, HEIGHT - 50), color="white", fontsize=25) # Draw quit instruction text

# ----------- GAME CONTROLLER ----------- #

# Music Control
def toggle_music():
    music_name = "game_music"
    
    if music.is_playing(music_name): 
        music.stop() # Stop music if playing
    else:
        music.play(music_name) # Play background music
        music.set_volume(0.2) # Set lower volume for background music

# Game Initialization
def init_game():
    # Initialize or reset game variables
    global player, enemies, score, enemy_spawn_timer, current_enemy_speed, level_up_timer, enemy_spawn_interval
    
    score = 0
    enemy_spawn_timer = 0
    current_enemy_speed = base_enemy_speed
    level_up_timer = 0
    enemy_spawn_interval = 60
    
    player = Player(WIDTH // 2, HEIGHT - 50, PLAYER_SPRITES, 5) # Create player instance 
    enemies = [] # Reset enemies list

    #Start Music
    music.play("game_music") # Start background music
    music.set_volume(0.2) # Set lower volume for background music


# Looping Draw Function
def draw():

    #Menu
    if game_state == "MENU":
        draw_menu()

    #Playing
    elif game_state == "PLAYING":
        screen.fill((0, 0, 0)) # Fill screen with black

        #Player Draw
        player.draw()

        #Enemies Draw
        for enemy in enemies:
            enemy.draw()

        #Score Draw
        screen.draw.text(f"Pontuação: {score}", topleft=(10, 10), color="white", fontsize=30) # Draw score text

    elif game_state == "GAME_OVER": 
        draw_game_over() # Draw Game Over screen

# Update Function - 60 times per second
def update():
    global game_state, enemy_spawn_timer, score, current_enemy_speed, level_up_timer, enemy_spawn_interval # Access global variables

    if game_state == "PLAYING":

        #Player Update
        player.update()

        #Enemies Update & Spawn
        enemy_spawn_timer += 1

        # Spawn new enemy if timer exceeds interval
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0
            x = random.randint(50, WIDTH - 50) # Random x position within screen bounds
            enemy_image = random.choice(ENEMY_SPRITES) # Randomly select enemy image
            new_enemy = Enemy(x, -50, [enemy_image], current_enemy_speed) # Create new enemy instance
            enemies.append(new_enemy) # Add new enemy to list

        # Update existing enemies
        for enemy in list(enemies):
            enemy.update()
            if enemy.is_offscreen(): # Remove enemy if offscreen
                enemies.remove(enemy)
                score += 1 # Increase score for each enemy dodged
        
        # Collision Detection
        for enemy in enemies:
            if player.actor.colliderect(enemy.actor): # Check collision between player and enemy
                sounds.explosion.play() # Play explosion sound
                game_state = "GAME_OVER" # Change state to Game Over
                break

        # Level Up System
        level_up_timer += 1 # Increment level up timer
        if level_up_timer >= level_up_interval: # Check if it's time to level up
            level_up_timer = 0 # Reset level up timer
            current_enemy_speed += 0.5  # Increase enemy speed
            if enemy_spawn_interval > 20: # Decrease spawn interval to a minimum limit
                enemy_spawn_interval -= 5  
            sounds.level_up.play() # Play level up sound

# Mouse Click Handler
def on_mouse_down(pos):
    global game_state # Access global game state variable
    
    if game_state == "MENU":
        # 1. Check Start Game Button        
        if start_button_rect and start_button_rect.collidepoint(pos):
            game_state = "PLAYING" # Change state to Playing
            init_game() # Initialize game

        # 2. Check Music & Sounds Button
        elif music_button_rect and music_button_rect.collidepoint(pos):
            toggle_music() # Toggle music on/off
        
        # 3. Check Quit Button
        elif quit_button_rect and quit_button_rect.collidepoint(pos):
            exit() # Exit the game

    #  Game Over Screen
    elif game_state == "GAME_OVER":
        
        # 1. Check Restart Button
        if restart_button_rect and restart_button_rect.collidepoint(pos):
            game_state = "PLAYING" # Change state to Playing
            init_game() # Initialize game

        # 2. Check Menu Button
        elif menu_button_rect and menu_button_rect.collidepoint(pos):
            game_state = "MENU" # Change state to Menu

# Keyboard Handler
def on_key_down(key):
    global game_state # Access global game state variable
    
    # Toggle Music with M key
    if key == keys.M:
        toggle_music()

    # Game Over Screen
    if game_state == "GAME_OVER":
        # Restart Game with R key
        if key == keys.R:
            game_state = "PLAYING" # Change state to Playing
            init_game() # Initialize game
        
        # Quit Game with Q key
        elif key == keys.Q:
            exit() # Exit the game

# ----------- START ----------- #
init_game() # Game launch function
game_state = "MENU" # Start in Menu
pgzrun.go() # PGZero start function