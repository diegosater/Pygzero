# -*- coding: utf-8 -*-
import pgzrun
import random

WIDTH = 600
HEIGHT = 500
ANIMATION_SPEED = 0.15
FLOOR = 0
LADDER = 1
NUM_ENEMIES = 5
TIME_LIMIT = 30.0

# ANIMATIONS

idle = [
    "player_idle_1",
    "player_idle_2",
    "player_idle_3"
]

walk_left = [
    "player_walk_left_1",
    "player_walk_left_2"
]

walk_right = [
    "player_walk_right_1",
    "player_walk_right_2"
]

climb = [
    "player_climb_1",
    "player_climb_2",
    "player_climb_3"
]
dead = ["player_dead"]

idle_enemies = ["bomb_walk1",
                "bomb_walk2",
                "bomb_walk3"
]
death_enemies = ["death_frame1",
                 "death_frame2"
]
explosion_enemies = [
    "explosion_1",
    "explosion_2",
    "explosion_3",
    "explosion_4"
]

# ======================
# GAME STATES
# ======================
MENU = "menu"
GAME = "game"

game_state = MENU
sound_enabled = True

# needed for reset() and animations        
def set_player_animation(anim):
    global current_animation, frame_index, animation_timer

    if current_animation != anim:
        current_animation = anim
        frame_index = 0
        animation_timer = 0
        player.image = anim[0]
        
# BUTTON CLASS

class Button:
    def __init__(self, text, center):
        self.text = text
        self.center = center
        self.width = 260
        self.height = 50
        self.rect = Rect(
            center[0] - self.width // 2,
            center[1] - self.height // 2,
            self.width,
            self.height
        )

    def draw(self):
        screen.draw.filled_rect(self.rect, (50, 50, 50))
        screen.draw.rect(self.rect, "white")
        screen.draw.text(
            self.text,
            center=self.center,
            fontsize=36,
            color="white"
        )

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# ENEMY CLASS
enemies = []
class Enemy:
    def __init__(self, idle_enemies, death_enemies, explosion_frames):       
        
        self.idle_frames = idle_enemies  
        self.death_frames = death_enemies
        self.explosion_frames = explosion_frames
          
        self.actor = Actor(self.idle_frames[0])
        self.state ="idle"
        self.alive = True
        self.floor = None
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.2 
        self.explosion_sound_played = False
        
        # -------- MOVEMENT --------
        self.speed = random.uniform(30, 60)   # slowly
        self.direction = random.choice([-1, 1])
        self.change_dir_timer = random.uniform(1.5, 3.5)
        
    def spawn(self, floors):
        self.floor = random.choice(floors)

        margin = 20
        min_x = self.floor.left + margin
        max_x = self.floor.right - margin

        self.actor.x = random.uniform(min_x, max_x)
        self.actor.y = self.floor.top - self.actor.height / 2
        
    def update(self, dt, time_left):
      # -------- ANIMATION --------
      self.animation_timer += dt
      if self.animation_timer >= self.animation_speed:
        self.animation_timer = 0
        self.frame_index += 1

        if self.state == "idle":
            if self.frame_index >= len(self.idle_frames):
                self.frame_index = 0
            self.actor.image = self.idle_frames[self.frame_index]

        elif self.state == "exploding":
            if self.frame_index >= len(self.explosion_frames):
                self.frame_index = 0
            self.actor.image = self.explosion_frames[self.frame_index]

        elif self.state == "dying":
            if self.frame_index >= len(self.death_frames):
                self.alive = False
                return
            self.actor.image = self.death_frames[self.frame_index]
      # -------- MOVEMENT (ONLY IF IDLE) --------
      if self.state != "idle":
        return

      self.change_dir_timer -= dt
      if self.change_dir_timer <= 0:
        self.direction = random.choice([-1, 1])
        self.change_dir_timer = random.uniform(1.5, 3.5)

      self.actor.x += self.direction * self.speed * dt
      left_limit = self.floor.left + 10
      right_limit = self.floor.right - 10

      if self.actor.left <= left_limit:
        self.actor.left = left_limit
        self.direction = 1
      elif self.actor.right >= right_limit:
        self.actor.right = right_limit
        self.direction = -1
     
      # GLOBAL TIMER CHECK
      
      if time_left <= 3 and self.state == "idle":
        self.state = "exploding"
        self.frame_index = 0
        self.animation_timer = 0
        if not self.explosion_sound_played:
          sounds.explosion.set_volume(0.5)
          sounds.explosion.play()
          self.explosion_sound_played = True
          
      #---- ALL ENEMIES VANISH
      if time_left == 0:
        enemies.clear()

    def draw(self):
        self.actor.draw()
def spawn_enemy():
  enemy = Enemy(idle_enemies,death_enemies, explosion_enemies)
  enemy.spawn(floors)
  enemies.append(enemy)

def spawn_wave():
    global enemies
    enemies.clear()
    for _ in range(enemies_per_wave):
        spawn_enemy()
        
def reset_game():
    global time_left, timer_active
    global player_alive, player_state, player_place
    global enemies

    time_left = TIME_LIMIT
    timer_active = True   
    # player state
    player_place = FLOOR
    player_alive = True
    set_player_animation(idle)
    # ENEMIES
    enemies.clear()
    for _ in range(NUM_ENEMIES):
        spawn_enemy()
    # MUSIC
    if sound_enabled:
        music.play("music_track")

# MENU BUTTONS

start_button = Button("Start", (WIDTH // 2, 200))
sound_button = Button("Music/Sounds:ON", (WIDTH // 2, 270))
exit_button  = Button("Exit", (WIDTH // 2, 340))

# DRAW MENU

def draw_menu():
    screen.draw.text(
        "SAVE the BUILDING",
        center=(WIDTH // 2, 100),
        fontsize=64,
        color="yellow"
    )
    start_button.draw()
    sound_button.draw()
    exit_button.draw()
    
    
# MOUSE CLICK
def on_mouse_down(pos):
    global game_state, sound_enabled

    if game_state == MENU:
        if start_button.is_clicked(pos):
            start_game()

        elif sound_button.is_clicked(pos):
            toggle_sound()

        elif exit_button.is_clicked(pos):
            exit()
# ACTIONS
def start_game():
    global game_state
    game_state = GAME

    reset_game()  # SUA função existente de reset
    if sound_enabled:
        music.play("music_track")

def toggle_sound():
    global sound_enabled

    sound_enabled = not sound_enabled

    if sound_enabled:
        sound_button.text = "Music and sound: ON"
        music.play("music_track")
    else:
        sound_button.text = "Music and sound: OFF"
        music.stop()

# SCENARIO

background = Actor("background2")

ground_floor = Actor("ground_floor", (275, 415))
first_floor  = Actor("first_floor",  (275, 295))
second_floor = Actor("second_floor", (275, 175))

floors = [ground_floor, first_floor, second_floor]
floor_index = 0
current_floor = floors[floor_index]

ladder1 = Actor("ladder1", (125, 320))
ladder2 = Actor("ladder2", (445, 200))

ladders = [ladder1, ladder2]

# PLAYER SETTINGS
FOOT_OFFSET = 8
player = Actor("player_idle_1")
player.x = 415
player.y = ground_floor.top - player.height / 2 + FOOT_OFFSET
#states to start the game
player_alive = True
player_state = "idle"   # idle | dying
player_place = FLOOR
current_animation = idle
frame_index = 0
animation_timer = 0

# WAVES / PROGRESSION

INITIAL_ENEMIES = 5
ENEMY_INCREMENT = 2
INITIAL_TIME = 30.0
TIME_DECREMENT = 5.0
MIN_TIME = 5.0   
current_wave = 1
enemies_per_wave = INITIAL_ENEMIES
time_limit = INITIAL_TIME
time_left = time_limit
# ======================
# DRAW
# ======================
def draw():   
    screen.clear()
    
    if game_state == MENU:
      draw_menu()
    elif game_state == GAME:
      background.draw()
      screen.blit('wall',(50,50))
      for f in floors:
        f.draw()
      for l in ladders:
        l.draw()
      player.draw()
      for enemy in enemies:
        enemy.draw()
      screen.draw.text(
         f"Time: {int(time_left)}",
         (100, 10),
         fontsize=36,
         color="red"
      )
      screen.draw.text(
        f"Stage: {current_wave}",
        (400, 10),
        fontsize=32,
        color="yellow"
      )
      if not player_alive:
        screen.draw.text(
           "GAME OVER",
           center=(WIDTH//2, HEIGHT-80),
           fontsize=48,
           color="white"
        )
def kill_player():
      global player_alive, current_animation, frame_index, animation_timer
      if not player_alive:
        return
      player_alive = False
      player_state = "dying"
      set_player_animation(dead)
      frame_index = 0
      animation_timer = 0
# UPDATES (player, enemies, time, general update)
def update_player(dt):
    global frame_index, animation_timer
    global current_animation
    global player_place, player_alive
    global floor_index, current_floor  
    # MOVING LIMITS
    player.x = max(80, min(450, player.x))
    SPEED = 200
    moving = False
    if not player_alive:
      return   
    # HORIZONTAL MOVEMENT
    if player_alive:
      if keyboard.right:
        player.x += SPEED * dt
        set_player_animation(walk_right)
        moving = True
      elif keyboard.left:
        player.x -= SPEED * dt
        set_player_animation(walk_left)
        moving = True
    # DETECT LADDER
    on_ladder = False
    for ladder in ladders:
      if ladder.colliderect(player):
        on_ladder = True
        break
    # STICKS ON THE FLOOR

    if player_place == FLOOR:
        player.y = current_floor.top - player.height / 2 + FOOT_OFFSET

        if on_ladder and (keyboard.up or keyboard.down):
           player_place = LADDER
    # ON LADDER
    elif player_place == LADDER:
       if keyboard.up:
          player.y -= SPEED * dt
          set_player_animation(climb)
          moving = True

       elif keyboard.down:
          player.y += SPEED * dt
          set_player_animation(climb)
          moving = True
  
       # saiu da escada → gruda no piso mais próximo
       if not on_ladder:
          distances = [abs(player.bottom - f.top) for f in floors]
          floor_index = distances.index(min(distances))
          current_floor = floors[floor_index]
          player.y = current_floor.top - player.height / 2 + FOOT_OFFSET
          player_place = FLOOR

       if not moving and player_alive and current_animation != idle:
          set_player_animation(idle)
         
def update_enemies(dt):
    global current_wave, enemies_per_wave
    global time_left, time_limit, timer_active

    if player_alive and len(enemies) == 0:
        current_wave += 1
        enemies_per_wave += ENEMY_INCREMENT
        time_limit = max(MIN_TIME, time_limit - TIME_DECREMENT)
        time_left = time_limit
        timer_active = True
        spawn_wave()

    for enemy in enemies:
        enemy.update(dt, time_left)
        if enemy.state == "idle" and enemy.actor.colliderect(player):
            enemy.state = "dying"
            enemy.frame_index = 0
            enemy.animation_timer = 0

    enemies[:] = [e for e in enemies if e.alive]

def update_time(dt):
  global time_left, timer_active, player_alive, player_state  
  
  # Timing control related to player  
  if timer_active and player_alive:
    time_left -= dt
    if time_left <= 0:
      time_left = 0
      timer_active = False
      kill_player()

def update(dt):
  if game_state != GAME:
    return

  update_player(dt)
  update_enemies(dt)
  update_time(dt)

  # ANIMATION
  if len(current_animation) > 1:
    global animation_timer, frame_index
    animation_timer += dt
    if animation_timer >= ANIMATION_SPEED:
      animation_timer = 0
      frame_index = (frame_index + 1) % len(current_animation)
      player.image = current_animation[frame_index]
      
      
pgzrun.go()
