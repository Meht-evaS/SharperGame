import pygame
import random
import math
import os
from enum import Enum

# Inizializzazione Pygame
pygame.init()

# Costanti
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 808   # <--- aumenta di 40px per bottom sidebar

# WINDOW_WIDTH = 1400        # larghezza totale della finestra (gioco + sidebar)
# WINDOW_HEIGHT = 768
SIDEBAR_WIDTH = 244
GAME_WIDTH = SCREEN_WIDTH - SIDEBAR_WIDTH
GAME_HEIGHT = 768     # <--- SCREEN_HEIGHT - 40px di bottom sidebar

TILE_SIZE = 40
FPS = 60

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)


MAX_EQ_TRANSFORMATIONS = 2
MAX_NOP_TRANSFORMATIONS = 5
MAX_COMBO_TRANSFORMATIONS = 1
MAX_IBP_TRANSFORMATIONS = 2


class TransformationType(Enum):
    NONE = 0
    SUBSTITUTION = 1  # Cambia aspetto
    PERMUTATION = 2   # Teletrasporto
    NOP_INSERTION = 3 # NOP Raygun
    COMBO = 4         # Combinazione
    POSITION_INDEPENDENT = 5

class SpriteManager:
    """Gestisce il caricamento e la creazione degli sprite"""
    def __init__(self):
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self):
        """Carica sprite da file o crea sprite procedurali"""
        # Se hai file di immagini, caricali così:
        # if os.path.exists("assets/cat.png"):
        #     self.sprites['cat'] = pygame.image.load("assets/cat.png")
        #     self.sprites['cat'] = pygame.transform.scale(self.sprites['cat'], (TILE_SIZE, TILE_SIZE))
        
        # Altrimenti, crea sprite procedurali più dettagliati:
        self.create_cat_sprites()
        self.create_guard_sprite()
        self.create_background_tiles()
        self.create_goal_sprite()
        self.create_particle_effects()
    
    def create_cat_sprites(self):
        """Crea sprite del gatto in diversi colori"""
        colors = {
            'blue': BLUE,
            'red': RED,
            'green': GREEN,
            'yellow': YELLOW,
            'purple': PURPLE,
            'black': BLACK,
            'white': WHITE
        }
        
        for color_name, color in colors.items():
            # Crea superficie per il gatto
            cat_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            # Corpo del gatto
            pygame.draw.ellipse(cat_surf, color, (4, 8, 24, 20))
            
            # Testa
            pygame.draw.circle(cat_surf, color, (16, 12), 8)
            
            # Orecchie
            points_left = [(8, 8), (6, 2), (12, 6)]
            points_right = [(20, 6), (24, 2), (22, 8)]
            pygame.draw.polygon(cat_surf, color, points_left)
            pygame.draw.polygon(cat_surf, color, points_right)
            
            # Occhi
            pygame.draw.circle(cat_surf, WHITE, (12, 11), 3)
            pygame.draw.circle(cat_surf, WHITE, (20, 11), 3)
            pygame.draw.circle(cat_surf, BLACK, (13, 11), 2)
            pygame.draw.circle(cat_surf, BLACK, (19, 11), 2)
            
            # Naso
            pygame.draw.polygon(cat_surf, BLACK, [(16, 14), (14, 16), (18, 16)])
            
            # Coda
            pygame.draw.arc(cat_surf, color, (20, 12, 16, 16), 0, math.pi/2, 3)
            
            self.sprites[f'cat_{color_name}'] = cat_surf
    
    def create_guard_sprite(self):
        """Crea sprite della guardia/antivirus"""
        guard_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # Corpo della guardia (robot/scanner)
        pygame.draw.rect(guard_surf, DARK_GRAY, (6, 10, 20, 18))
        pygame.draw.rect(guard_surf, RED, (8, 12, 16, 14))
        
        # "Occhio" scanner
        pygame.draw.circle(guard_surf, WHITE, (16, 19), 6)
        pygame.draw.circle(guard_surf, RED, (16, 19), 4)
        pygame.draw.circle(guard_surf, BLACK, (16, 19), 2)
        
        # Antenna
        pygame.draw.line(guard_surf, GRAY, (16, 10), (16, 4), 2)
        pygame.draw.circle(guard_surf, RED, (16, 3), 3)
        
        # Gambe/ruote
        pygame.draw.circle(guard_surf, DARK_GRAY, (10, 28), 3)
        pygame.draw.circle(guard_surf, DARK_GRAY, (22, 28), 3)
        
        self.sprites['guard'] = guard_surf
    
    def create_background_tiles(self):
        """Crea tile per lo sfondo"""
        # Tile pavimento base
        floor_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        floor_tile.fill((40, 40, 50))
        # Aggiungi pattern
        for i in range(0, TILE_SIZE, 8):
            pygame.draw.line(floor_tile, (35, 35, 45), (i, 0), (i, TILE_SIZE), 1)
            pygame.draw.line(floor_tile, (35, 35, 45), (0, i), (TILE_SIZE, i), 1)
        self.sprites['floor'] = floor_tile
        
        # Tile muro
        wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_tile.fill((100, 100, 120))
        # Pattern mattoni
        for y in range(0, TILE_SIZE, 8):
            for x in range(0, TILE_SIZE, 16):
                offset = 8 if (y // 8) % 2 else 0
                pygame.draw.rect(wall_tile, (80, 80, 100), 
                               (x + offset - 8, y, 15, 7), 1)
        self.sprites['wall'] = wall_tile
        
        # Tile decorativo (circuit board per tema tech)
        circuit_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        circuit_tile.fill((20, 30, 40))
        # Linee circuito
        pygame.draw.line(circuit_tile, (0, 100, 100), (0, 16), (32, 16), 2)
        pygame.draw.line(circuit_tile, (0, 100, 100), (16, 0), (16, 32), 2)
        pygame.draw.circle(circuit_tile, (0, 150, 150), (8, 8), 3)
        pygame.draw.circle(circuit_tile, (0, 150, 150), (24, 24), 3)
        self.sprites['circuit'] = circuit_tile
    
    def create_goal_sprite(self):
        """Crea sprite dell'obiettivo (server/computer)"""
        goal_surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)
        
        # Monitor
        pygame.draw.rect(goal_surf, (60, 60, 70), (8, 4, 48, 36))
        pygame.draw.rect(goal_surf, (0, 200, 255), (12, 8, 40, 28))
        
        # Schermo con "codice"
        for i in range(5):
            y = 12 + i * 5
            pygame.draw.line(goal_surf, GREEN, (14, y), (14 + random.randint(10, 35), y), 1)
        
        # Base
        pygame.draw.rect(goal_surf, (40, 40, 50), (24, 40, 16, 8))
        pygame.draw.rect(goal_surf, (40, 40, 50), (16, 48, 32, 4))
        
        self.sprites['goal'] = goal_surf
    
    def create_particle_effects(self):
        """Crea sprite per effetti particellari"""
        # Particella teletrasporto
        teleport_particle = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(teleport_particle, (100, 200, 255), (4, 4), 4)
        pygame.draw.circle(teleport_particle, WHITE, (4, 4), 2)
        self.sprites['teleport_particle'] = teleport_particle
        
        # Particella ghost
        ghost_particle = pygame.Surface((16, 16), pygame.SRCALPHA)
        ghost_particle.set_alpha(100)
        pygame.draw.circle(ghost_particle, (150, 150, 255), (8, 8), 8)
        self.sprites['ghost_particle'] = ghost_particle

class ParticleEffect:
    """Sistema di particelle per effetti visivi"""
    def __init__(self, x, y, effect_type):
        self.particles = []
        self.x = x
        self.y = y
        
        if effect_type == 'teleport':
            for _ in range(20):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 5)
                self.particles.append({
                    'x': x,
                    'y': y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'life': 30,
                    'color': (100, 200, random.randint(200, 255))
                })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = particle['life'] * 8
            size = particle['life'] // 6
            if size > 0:
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*particle['color'], min(alpha, 255)), 
                                 (size, size), size)
                screen.blit(s, (particle['x'] - size, particle['y'] - size))


class NopPulse:
    """Impulso NOP: piccolo proiettile che respinge le guardie"""
    def __init__(self, x, y, angle, speed=9, life=40, radius=22):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = life
        self.radius = radius  # raggio di effetto/colpo

    def update(self, walls):
        # movimento semplice; rimbalzo leggero sui bordi
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

        # limiti schermo
        if self.x < 20 or self.x > GAME_WIDTH - 20:
            self.vx *= -1
        if self.y < 20 or self.y > GAME_HEIGHT - 20:
            self.vy *= -1

        # opzionale: fermati se colpisci un muro
        pulse_rect = pygame.Rect(int(self.x - 4), int(self.y - 4), 8, 8)
        for w in walls:
            if pulse_rect.colliderect(w):
                self.life = 0
                break

        return self.life > 0

    def draw(self, screen):
        # piccolo glow ciano per richiamare il “NOP”
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 255, 60), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (255, 255, 255, 180), (self.radius, self.radius), 3)
        # write 0x90 inside the circle
        font = pygame.font.Font(None, 20)
        text = font.render("0x90", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.radius, self.radius))
        s.blit(text, text_rect)
        

        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        

class Player:
    def __init__(self, x, y, sprite_manager, lives=3):
        self.x = x
        self.y = y
        self.speed = 4
        self.color = 'blimblau'
        self.original_color = 'blimblau'
        self.transformation = TransformationType.NONE
        self.transformation_timer = 0
        self.ghost_steps = []
        self.detected = False
        self.win = False
        self.sprite_manager = sprite_manager
        self.animation_frame = 0
        self.facing_right = True
        self.lives = lives  # Aggiunta delle vite

        self.dir = [1, 0]

        self.rem_eq_transformations = MAX_EQ_TRANSFORMATIONS
        self.rem_nop_transformations = MAX_NOP_TRANSFORMATIONS
        self.rem_combo_transformations = MAX_COMBO_TRANSFORMATIONS
        self.rem_ibp_transformations = MAX_IBP_TRANSFORMATIONS
        
    def update(self):
        # Gestione timer trasformazioni
        if self.transformation_timer > 0:
            self.transformation_timer -= 1
            if self.transformation_timer == 0:
                self.reset_transformation()
        
        # Animazione
        self.animation_frame = (self.animation_frame + 1) % 60
    
    def move(self, dx, dy, walls):
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
            
        # Movimento con collision detection
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # Controllo collisioni con muri
        player_rect = pygame.Rect(new_x, new_y, TILE_SIZE-4, TILE_SIZE-4)
        collision = False
        for wall in walls:
            if player_rect.colliderect(wall):
                collision = True
                break
        
        if not collision:
            # Salva posizione precedente per effetto ghost
            if self.transformation == TransformationType.NOP_INSERTION:
                self.ghost_steps.append((self.x, self.y, self.animation_frame))
                if len(self.ghost_steps) > 5:
                    self.ghost_steps.pop(0)
            
            if dx != 0 or dy != 0:
                mag = math.hypot(dx, dy)
                self.dir = [dx / mag, dy / mag]
            self.x = new_x
            self.y = new_y
    
    def apply_transformation(self, trans_type):
        self.transformation = trans_type
        self.transformation_timer = 180  # 3 secondi a 60 FPS

        colors = ['red', 'green', 'yellow', 'purple', 'black', 'white']

        if trans_type == TransformationType.SUBSTITUTION:
            # Cambia colore/aspetto
            if self.rem_eq_transformations <= 0:
                return None
            self.color = random.choice(colors)
            self.rem_eq_transformations -= 1
        elif trans_type == TransformationType.PERMUTATION:
            # Teletrasporto in posizione casuale sicura
            if self.rem_ibp_transformations <= 0:
                return None
            self.teleport_random()
            self.rem_ibp_transformations -= 1
            return ParticleEffect(self.x, self.y, 'teleport')
        elif trans_type == TransformationType.NOP_INSERTION:
            if self.rem_nop_transformations <= 0:
                return None
            base_angle = math.atan2(self.dir[1], self.dir[0])
            for off in (-0.25, 0.0, 0.25):  # ~±14°
                ang = base_angle + off
                # centro dal petto del gatto
                cx = self.x + TILE_SIZE * 0.75
                cy = self.y + TILE_SIZE * 0.75
                game.nop_pulses.append(NopPulse(cx, cy, ang))

            # tracce fantasma come prima (estetica NOP)
            self.ghost_steps = []

            self.rem_nop_transformations -= 1
            return None
            # Spara NOP che allontanano le guardie
        elif trans_type == TransformationType.COMBO:
            # Applica combo di effetti
            if self.rem_combo_transformations <= 0:
                return None
            self.color = random.choice(colors)
            self.ghost_steps = []
            self.rem_combo_transformations -= 1
            return None
        elif trans_type == TransformationType.POSITION_INDEPENDENT:
            if self.rem_ibp_transformations <= 0:
                return None
            self.teleport_random()
            self.color = random.choice(colors)
            self.ghost_steps = []
            self.rem_ibp_transformations -= 1
            return ParticleEffect(self.x, self.y, 'teleport')
    
    def teleport_random(self):
        # Teletrasporto in una posizione casuale sicura, no guardie vicine e no muri
        safe = False
        attempts = 0
        while not safe and attempts < 100:
            new_x = random.randint(20, GAME_WIDTH - 20 - TILE_SIZE)
            new_y = random.randint(20, GAME_HEIGHT - 20 - TILE_SIZE)
            player_rect = pygame.Rect(new_x, new_y, TILE_SIZE-4, TILE_SIZE-4)
            safe = True
            
            # Controllo collisioni con muri
            for wall in game.walls:
                if player_rect.colliderect(wall):
                    safe = False
                    break
            
            # Controllo vicinanza guardie
            if safe:
                for guard in game.guards:
                    guard_rect = pygame.Rect(guard.x, guard.y, TILE_SIZE, TILE_SIZE)
                    if player_rect.colliderect(guard_rect.inflate(100, 100)):
                        safe = False
                        break
            
            attempts += 1
        if safe:
            self.x = new_x
            self.y = new_y

        

    
    def reset_transformation(self):
        self.transformation = TransformationType.NONE
        self.color = self.original_color
        self.ghost_steps = []
    
    def draw(self, screen):
        # Disegna passi fantasma se attivi
        if self.transformation == TransformationType.NOP_INSERTION:
            for i, (gx, gy, frame) in enumerate(self.ghost_steps):
                alpha = 50 + i * 20
                ghost_sprite = self.sprite_manager.sprites[f'cat_{self.color}'].copy()
                ghost_sprite.set_alpha(alpha)
                screen.blit(ghost_sprite, (gx, gy))
        
        # Disegna il giocatore
        if self.detected:
            pygame.draw.circle(screen, RED, 
                             (int(self.x + TILE_SIZE//2), int(self.y + TILE_SIZE//2)), 
                             TILE_SIZE//2 + 5, 3)
        
        # Usa sprite del gatto
        sprite = self.sprite_manager.sprites[f'cat_{self.color}']
        # make it 2 times bigger
        sprite = pygame.transform.scale(sprite, (TILE_SIZE*1.5, TILE_SIZE*1.5))
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Effetto bobbing durante il movimento
        y_offset = math.sin(self.animation_frame * 0.2) * 2
        screen.blit(sprite, (self.x, self.y + y_offset))

class Guard:
    def __init__(self, x, y, patrol_path, sprite_manager, detection_color=None):
        self.x = x
        self.y = y
        self.patrol_path = patrol_path
        self.current_target = 0
        self.speed = 2
        self.detection_radius = 80
        self.detection_color = detection_color
        self.viewing_angle = 90
        self.facing_direction = 0
        self.sprite_manager = sprite_manager
        self.animation_frame = 0

        self.seconds_to_travel = 0
        self.choicex = 0
        self.choicey = 0
        
    def update(self, player):
        # Animazione
        self.animation_frame = (self.animation_frame + 1) % 60
        
        # Movimento lungo il percorso di pattuglia
        # if len(self.patrol_path) > 0:
            # target = self.patrol_path[self.current_target]

            # target = random.randint

            # dx = target[0] - self.x
            # dy = target[1] - self.y
            # dist = math.sqrt(dx**2 + dy**2)
            
            # if dist > 5:
            #     self.x += (dx / dist) * self.speed
            #     self.y += (dy / dist) * self.speed
            #     self.facing_direction = math.atan2(dy, dx)
            # else:
            #     self.current_target = (self.current_target + 1) % len(self.patrol_path)

        # generate a random patrol movement

        if self.seconds_to_travel <= 0:
            self.choicex = random.choice([-1, 0, 1])
            self.choicey = random.choice([-1, 0, 1])
            self.seconds_to_travel = 60
        
        if self.choicex != 0 or self.choicey != 0:
            
            # prima check collisioni con muri
            if self.x + self.choicex * self.speed < 20 or self.x + self.choicex * self.speed > GAME_WIDTH - 20 - TILE_SIZE:
                self.choicex = 0
            if self.y + self.choicey * self.speed < 20 or self.y + self.choicey * self.speed > GAME_HEIGHT - 20 - TILE_SIZE:
                self.choicey = 0

            self.x += self.choicex * self.speed
            self.y += self.choicey * self.speed
            self.facing_direction = math.atan2(self.choicey, self.choicex)
        self.seconds_to_travel -= 1

        # Controllo rilevamento giocatore
        return self.detect_player(player)
    
    def detect_player(self, player):
        # Calcola distanza dal giocatore
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.detection_radius:
            # Se la guardia cerca un colore specifico
            if self.detection_color is not None:
                if player.color != self.detection_color and player.color != 'blimblau':
                    return False
            
            
            
            # Controllo angolo di visione
            angle_to_player = math.atan2(dy, dx)
            angle_diff = abs(angle_to_player - self.facing_direction)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            if angle_diff < math.radians(self.viewing_angle / 2):
                
                return True
        
        return False
    
    def draw(self, screen):
        # Disegna cono di visione
        points = [(self.x + TILE_SIZE//2, self.y + TILE_SIZE//2)]
        for angle_offset in range(-self.viewing_angle//2, self.viewing_angle//2 + 1, 5):
            angle = self.facing_direction + math.radians(angle_offset)
            end_x = self.x + TILE_SIZE//2 + math.cos(angle) * self.detection_radius
            end_y = self.y + TILE_SIZE//2 + math.sin(angle) * self.detection_radius
            points.append((end_x, end_y))
        
        if len(points) > 2:
            s = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            color = (255, 50, 50, 40)# if not self.detection_color else (*self.detection_color, 40)
            pygame.draw.polygon(s, color, points)
            screen.blit(s, (0, 0))
        
        # Disegna sprite guardia, make it 1.5 times bigger
        sprite = self.sprite_manager.sprites['guard']
        sprite = pygame.transform.scale(sprite, (int(TILE_SIZE*1.5), int(TILE_SIZE*1.5)))
        # Ruota sprite in base alla direzione
        angle = -math.degrees(self.facing_direction) - 90
        rotated_sprite = pygame.transform.rotate(sprite, angle)
        rect = rotated_sprite.get_rect(center=(self.x + TILE_SIZE//2, self.y + TILE_SIZE//2))
        screen.blit(rotated_sprite, rect)
        
        # Indicatore scanner animato
        scan_radius = 10 + math.sin(self.animation_frame * 0.1) * 5
        pygame.draw.circle(screen, (255, 0, 0, 100), 
                          (int(self.x + TILE_SIZE//2), int(self.y + TILE_SIZE//2)), 
                          int(scan_radius), 2)

class Goal:
    def __init__(self, x, y, sprite_manager):
        self.x = x
        self.y = y
        self.pulse = 0
        self.sprite_manager = sprite_manager
        
    def update(self):
        self.pulse = (self.pulse + 2) % 360
        
    def draw(self, screen):
        # Effetto glow
        glow_size = 40 + math.sin(math.radians(self.pulse)) * 10
        s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 100, 50), 
                         (glow_size, glow_size), glow_size)
        screen.blit(s, (self.x - glow_size + TILE_SIZE, self.y - glow_size + TILE_SIZE))
        
        # Disegna sprite goal
        screen.blit(self.sprite_manager.sprites['goal'], (self.x, self.y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Metamorphic Maze - Sharper Night")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True
        self.level = 1
        self.sprite_manager = SpriteManager()
        self.particle_effects = []

        self.nop_pulses = []


        self.player_name = "Sonic Feet"  # Nome di default del giocatore

        self.menu()
        # self.init_level()
    
    def menu(self):
        waiting = True
        while waiting:
            # put a background image
            bg_img = pygame.image.load("assets/CyberGarflieldpng.png")
            # lower the contrast of the image
            bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            bg_img.set_alpha(100)

            self.screen.blit(bg_img, (0, 0))

            

            title = self.font.render("Metamorphic Maze - Sharper Night", True, WHITE)
            instruction = self.small_font.render("- Premi SPAZIO per iniziare", True, WHITE)
            regolamento = self.small_font.render("- Premi O per le istruzioni", True, WHITE)
            background_scientifico = self.small_font.render("- Premi B per leggere il signficiato scientifico di questo gioco", True, WHITE)
            classifica = self.small_font.render("- Premi C per la classifica", True, WHITE)

            small_description1 = self.small_font.render("Sei Garfield, un virus informatico che deve infiltrarsi in un sistema sorvegliato da antivirus.", True, WHITE)
            small_description2 = self.small_font.render("Usa le trasformazioni metamorfiche per evitare di essere rilevato e raggiungere il server.", True, WHITE)
            
            

            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 150))
            self.screen.blit(instruction, (80, SCREEN_HEIGHT//2 + 10))
            self.screen.blit(regolamento, (80, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(background_scientifico, (80, SCREEN_HEIGHT//2 + 70))
            self.screen.blit(classifica, (80, SCREEN_HEIGHT//2 + 100))
            # vai a capo
            self.screen.blit(small_description1, (SCREEN_WIDTH//2 - small_description1.get_width()//2, SCREEN_HEIGHT//2 - 70))
            self.screen.blit(small_description2, (SCREEN_WIDTH//2 - small_description2.get_width()//2, SCREEN_HEIGHT//2 - 50))

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                        # first ask for player name
                        self.player_name = ""
                        asking_name = True
                        while asking_name:
                            self.screen.fill(BLACK)
                            self.screen.blit(bg_img, (0, 0))
                            prompt = self.small_font.render("Inserisci il tuo nome (max 15 caratteri): " + self.player_name, True, WHITE)
                            self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))
                            pygame.display.flip()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    asking_name = False
                                    waiting = False
                                    self.running = False
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_RETURN:
                                        if len(self.player_name) > 0:
                                            asking_name = False
                                    elif event.key == pygame.K_BACKSPACE:
                                        self.player_name = self.player_name[:-1]
                                    else:
                                        if len(self.player_name) < 15 and event.unicode.isprintable():
                                            self.player_name += event.unicode

                        self.init_level()
                    if event.key == pygame.K_b or event.key == pygame.KSCAN_B:
                        string = '''
Il metamorfismo è una tecnica utilizzata dagli autori di malware (software malevolo, comunemente detti virus informatici) per 
aggirare gli strumenti di sicurezza come antivirus o EDR.

Gli antivirus, infatti, rilevano un malware principalmente riconoscendo determinati tratti distintivi (signature detection), 
come specifiche istruzioni o sequenze di byte che compaiono solo in quel programma.
Se questi tratti distintivi vengono modificati senza alterare il funzionamento originale, 
si ottiene un malware che compie le stesse azioni, ma in modo diverso, e che quindi può eludere la rilevazione.

Per raggiungere questo obiettivo esistono diverse tecniche. 
Noi abbiamo realizzato un software che ne implementa 4 già conosciute e 1 da noi inventata.E' anche possibile combinarle.

Ecco quali sono e cosa fanno, in breve:

1)Equal Instruction Substitution
Sostituisce alcune istruzioni con altre che hanno lo stesso identico effetto.

2)NOP Insertion
Inserisce istruzioni che non alterano in alcun modo il comportamento del programma.

3)Instruction Block Permutation
Divide il programma in blocchi di istruzioni e ne cambia l’ordine. Per mantenere il corretto flusso di esecuzione, 
vengono inseriti salti (JMP) alla fine dei blocchi, così che il programma funzioni come prima, ma con una struttura diversa.

4)Bogus Control Flow
Aggiunge interi blocchi di codice inutili che non verranno mai eseguiti. 
Ogni blocco è preceduto da una condizione che forziamo sempre a vera o falsa, in modo da impedirne l’esecuzione.
 Questo complica anche l’analisi statica del codice.

5)Position Independent Instruction (tecnica originale)
Permette di rimescolare non solo i blocchi, ma ogni singola istruzione. 
È una tecnica molto potente ma anche estremamente invasiva, perché richiede che ogni istruzione restituisca il controllo a
un’unità centrale che gestisce il flusso del programma.
'''
                    # make it scrollable
                        waiting_scientifico = True
                        lines = string.split('\n')
                        offset = 0
                        while waiting_scientifico:
                            self.screen.fill(BLACK)
                            # bg_img = pygame.image.load("assets/CyberGarflieldpng.png")
                            self.screen.blit(bg_img, (0, 0))
                            y = SCREEN_HEIGHT//2 - len(lines)*10 + offset
                            for line in lines:
                                text = self.small_font.render(line, True, WHITE)
                                self.screen.blit(text, (50, y))
                                y += 20
                            pygame.display.flip()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting_scientifico = False
                                    waiting = False
                                    self.running = False
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_r:
                                        waiting_scientifico = False
                                    if event.key == pygame.K_ESCAPE:
                                        waiting_scientifico = False
                                        waiting = False
                                        self.running = False
                                    if event.key == pygame.K_UP:
                                        offset += 20
                                    if event.key == pygame.K_DOWN:
                                        offset -= 20
                                    if event.key == pygame.K_b or event.key == pygame.KSCAN_B:
                                        offset = 0
                                        waiting_scientifico = False
                        continue
                    if event.key == pygame.K_c or event.key == pygame.KSCAN_C:
                        show_first_n = 10
                        #  leggi classifica da file classifica.txt
                        waiting_classifica = True
                        if not os.path.exists("classifica.txt"):
                            with open("classifica.txt", "w") as f:
                                f.write("Nessun punteggio ancora.\n")
                        with open("classifica.txt", "r") as f:
                            lines = f.readlines()
                        while waiting_classifica:
                            self.screen.fill(BLACK)
                            # bg_img = pygame.image.load("assets/CyberGarflieldpng.png")
                            self.screen.blit(bg_img, (0, 0))
                            title = self.font.render("Classifica TOP 10", True, WHITE)
                            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
                            y = 100
                            # sort lines by level reached (assuming format "name: level")
                            lines = sorted(lines, key=lambda x: int(x.split(':')[-1].strip()), reverse=True)
                            for x,line in enumerate(lines):
                                if x >= show_first_n:
                                    break
                                text = self.small_font.render(line.strip(), True, WHITE)
                                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
                                y += 30
                            instruction = self.small_font.render("Premi R per tornare al menu", True, WHITE)
                            self.screen.blit(instruction, (SCREEN_WIDTH//2 - instruction.get_width()//2, SCREEN_HEIGHT - 50))
                            pygame.display.flip()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting_classifica = False
                                    waiting = False
                                    self.running = False
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_r:
                                        waiting_classifica = False
                                    if event.key == pygame.K_ESCAPE:
                                        waiting_classifica = False
                                        waiting = False
                                        self.running = False
                        continue
                    if event.key == pygame.K_o or event.key == pygame.KSCAN_O:
                    # mostra le istruzioni
                        waiting_instr = True
                        while waiting_instr:
                            self.screen.fill(BLACK)
                            # bg_img = pygame.image.load("assets/CyberGarflieldpng.png")
                            self.screen.blit(bg_img, (0, 0))
                            lines = [
                                "Istruzioni:",
                                "WASD/Frecce: Muovi",
                                "1: Camuffamento (Substitution, camuffa il colore, attento pero', ogni guardia rileva un colore specifico)",
                                "2: Teletrasporto (Permutation, teletrasporta in una zona casuale sicura)",
                                "3: NOP Raygun (NOP Insertion, fa girare le guardie)",
                                "4: Combo (Combo)",
                                "R: Reset Livello",
                                "Premi R per tornare al menu"

                                "Premi ESC per Tornare al menu"
                            ]
                            y = SCREEN_HEIGHT//2 - len(lines)*20
                            for line in lines:
                                text = self.small_font.render(line, True, WHITE)
                                self.screen.blit(text, (180, y))
                                y += 30
                            pygame.display.flip()
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    waiting_instr = False
                                    waiting = False
                                    self.running = False
                                elif event.type == pygame.KEYDOWN:
                                    if event.key == pygame.K_r:
                                        waiting_instr = False
                                    if event.key == pygame.K_ESCAPE:
                                        waiting_instr = False
                                        waiting = False
                                        self.running = False

    def init_level(self):
        # Inizializza livello
        if self.level == 1:
            self.player = Player(100, 100, self.sprite_manager, lives=3)
        else:
            new_lives = self.player.lives + 1 if self.player.lives < 5 else self.player.lives
            self.player = Player(100, 100, self.sprite_manager, lives=new_lives)
        self.goal = Goal(GAME_WIDTH - 150, GAME_HEIGHT - 150, self.sprite_manager)
        self.guards = []
        self.walls = []
        
        # Crea muri del labirinto
        # Bordi
        self.walls.append(pygame.Rect(0, 0, GAME_WIDTH, 20))
        self.walls.append(pygame.Rect(0, GAME_HEIGHT-20, GAME_WIDTH, 20))
        self.walls.append(pygame.Rect(0, 0, 20, GAME_HEIGHT))
        self.walls.append(pygame.Rect(GAME_WIDTH-20, 0, 20, GAME_HEIGHT))
        
        # Muri interni
        self.walls.append(pygame.Rect(200, 100, 20, 300))
        self.walls.append(pygame.Rect(400, 200, 200, 20))
        self.walls.append(pygame.Rect(600, 100, 20, 300))
        self.walls.append(pygame.Rect(300, 500, 400, 20))

        # Aggiungi altre strutture di muri per rendere il labirinto più complesso
        self.walls.append(pygame.Rect(150, 300, 300, 20))
        self.walls.append(pygame.Rect(500, 400, 20, 200))
        self.walls.append(pygame.Rect(700, 250, 20, 300))
        self.walls.append(pygame.Rect(250, 150, 20, 200))
        self.walls.append(pygame.Rect(350, 350, 200, 20))
        self.walls.append(pygame.Rect(100, 450, 150, 20))
        self.walls.append(pygame.Rect(450, 100, 20, 150))
        self.walls.append(pygame.Rect(600, 500, 150, 20))


        self.walls.append(pygame.Rect(800, 300, 20, 200))
        self.walls.append(pygame.Rect(700, 150, 150, 20))
        self.walls.append(pygame.Rect(900, 100, 20, 300))
        self.walls.append(pygame.Rect(850, 400, 150, 20))

        # make 2 walls. one on y = GAME_HEIGHT - 180 horizontal and to x = 300
        self.walls.append(pygame.Rect(300, GAME_HEIGHT - 180, 400, 20))


        # Aggiungi guardie basate sul livello
 
            # Livelli successivi
        for i in range(min(self.level + 2, 15)):
            x = random.randint(200, GAME_WIDTH - 200)
            y = random.randint(200, GAME_HEIGHT - 200)
            path = self.generate_random_path(x, y)
            self.guards.append(Guard(x, y, path, self.sprite_manager, detection_color=random.choice(['blue', 'red', 'green', 'yellow', 'purple', 'black', 'white'])))
    
    def generate_random_path(self, start_x, start_y):
        path = [(start_x, start_y)]
        for _ in range(3):
            x = random.randint(100, GAME_WIDTH - 100)
            y = random.randint(100, GAME_HEIGHT - 100)
            path.append((x, y))
        return path
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Attivazione trasformazioni
                if event.key == pygame.K_1:
                    effect = self.player.apply_transformation(TransformationType.SUBSTITUTION)
                    if effect:
                        self.particle_effects.append(effect)
                elif event.key == pygame.K_2:
                    effect = self.player.apply_transformation(TransformationType.PERMUTATION)
                    if effect:
                        self.particle_effects.append(effect)
                elif event.key == pygame.K_3:
                    effect = self.player.apply_transformation(TransformationType.NOP_INSERTION)
                    if effect:
                        self.particle_effects.append(effect)
                elif event.key == pygame.K_4:
                    effect = self.player.apply_transformation(TransformationType.COMBO)
                    if effect:
                        self.particle_effects.append(effect)
                elif event.key == pygame.K_5:
                    effect = self.player.apply_transformation(TransformationType.POSITION_INDEPENDENT)
                    if effect:
                        self.particle_effects.append(effect)
                elif event.key == pygame.K_r:
                    self.init_level()  # Reset livello
    
    def update(self):
        # Input movimento
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        self.player.move(dx, dy, self.walls)
        self.player.update()
        
        # Update guardie e controllo rilevamento
        detected = False
        for guard in self.guards:
            if guard.update(self.player):
                detected = True
        
        self.player.detected = detected
        
        # Update particelle
        for effect in self.particle_effects[:]:
            if not effect.update():
                self.particle_effects.remove(effect)
        
        # Update goal
        self.goal.update()
    
        # Aggiorna impulsi NOP e collisioni con guardie
        for pulse in self.nop_pulses[:]:
            alive = pulse.update(self.walls)
            # collisione con guardie: se entro raggio, respingi e consuma l'impulso
            hit_something = False
            for guard in self.guards:
                gx = guard.x + TILE_SIZE / 2
                gy = guard.y + TILE_SIZE / 2
                d = math.hypot(gx - pulse.x, gy - pulse.y)
                if d <= pulse.radius + TILE_SIZE * 0.5:
                    # spinta: più vicino => più forte
                    ux = (gx - pulse.x) / (d + 1e-6)
                    uy = (gy - pulse.y) / (d + 1e-6)
                    push_strength = 80  # pixel di “teletrascinamento”
                    # attenua in base alla distanza (entro raggio)
                    atten = max(0.35, 1.0 - d / (pulse.radius + TILE_SIZE * 0.5))
                    dx = ux * push_strength * atten
                    dy = uy * push_strength * atten

                    # applica spostamento, clamp ai bordi
                    guard.x = max(20, min(GAME_WIDTH - 20 - TILE_SIZE, guard.x + dx))
                    guard.y = max(20, min(GAME_HEIGHT - 20 - TILE_SIZE, guard.y + dy))

                    # “disorienta” per un attimo: nuova direzione opposta al player
                    guard.choicex = int(math.copysign(1, ux)) if abs(ux) > 0.2 else 0
                    guard.choicey = int(math.copysign(1, uy)) if abs(uy) > 0.2 else 0
                    guard.seconds_to_travel = 30  # mezzo secondo a 60 FPS
                    hit_something = True

            if not alive or hit_something:
                self.nop_pulses.remove(pulse)

        
        # Controllo vittoria
        player_rect = pygame.Rect(self.player.x, self.player.y, TILE_SIZE, TILE_SIZE)
        goal_rect = pygame.Rect(self.goal.x, self.goal.y, TILE_SIZE * 2, TILE_SIZE * 2)
        if player_rect.colliderect(goal_rect):
            self.player.win = True
            self.level += 1
            self.player.rem_combo_transformations = MAX_COMBO_TRANSFORMATIONS
            self.player.rem_eq_transformations = MAX_EQ_TRANSFORMATIONS
            self.player.rem_nop_transformations = MAX_NOP_TRANSFORMATIONS
            self.player.rem_ibp_transformations = MAX_IBP_TRANSFORMATIONS

            self.init_level()



    
    def draw_background(self):
        """Disegna lo sfondo con tiles"""
        for y in range(0, GAME_HEIGHT, TILE_SIZE):
            for x in range(0, GAME_WIDTH, TILE_SIZE):
                # Alterna tra floor e circuit tiles per creare pattern
                if (x // TILE_SIZE + y // TILE_SIZE) % 3 == 0:
                    self.screen.blit(self.sprite_manager.sprites['circuit'], (x, y))
                else:
                    self.screen.blit(self.sprite_manager.sprites['floor'], (x, y))
    
    def draw_ui(self):
        # --- SIDEBAR NERA OPACA (area non di gioco) ---
        sidebar_x = GAME_WIDTH
        sidebar_y = 0
        sidebar_width = SCREEN_WIDTH - GAME_WIDTH
        sidebar_height = GAME_HEIGHT  # <-- solo altezza area di gioco, NON tutta la finestra!
        sidebar_panel = pygame.Surface((sidebar_width, sidebar_height))
        sidebar_panel.fill(BLACK)
        self.screen.blit(sidebar_panel, (sidebar_x, sidebar_y))

        center_sidebar = sidebar_x + sidebar_width // 2

        # --- "Livello" e "Vite rimaste" centrati nella sidebar in alto ---
        level_text = self.font.render(f"Livello: {self.level}", True, WHITE)
        lives_text = self.font.render(f"Vite rimaste: {self.player.lives}", True, WHITE)
        level_x = center_sidebar - level_text.get_width() // 2
        level_y = 50
        lives_x = center_sidebar - lives_text.get_width() // 2
        lives_y = level_y + level_text.get_height() + 10
        self.screen.blit(level_text, (level_x, level_y))
        self.screen.blit(lives_text, (lives_x, lives_y))

        # --- Classifica centrata verticalmente nella sidebar ---
        scoreboard_text = "CLASSIFICA TOP 10"
        scoreboard = self.small_font.render(scoreboard_text, True, WHITE)
        # Calcola altezza della classifica
        top_10_string = []
        if os.path.exists("classifica.txt"):
            with open("classifica.txt", "r") as f:
                lines = f.readlines()
                lines = sorted(lines, key=lambda x: int(x.split(':')[-1].strip()) if ':' in x else 0, reverse=True)
                for i, line in enumerate(lines[:10]):
                    stringa_utile = ""
                    linea = line.split('-')
                    stringa_utile = linea[0].strip() + " - " + linea[1].split(':')[-1].strip()
                    top_10_string.append(f"{i+1}. {stringa_utile}")

        classifica_height = (len(top_10_string) * 20) + scoreboard.get_height() + 10
        # Centro verticale della sidebar SOLO nell'area di gioco
        sidebar_center_y = sidebar_y + sidebar_height // 2
        scoreboard_y = sidebar_center_y - (classifica_height // 2) - 20
        scoreboard_x = center_sidebar - scoreboard.get_width() // 2

        self.screen.blit(scoreboard, (scoreboard_x, scoreboard_y))
        base_y = scoreboard_y + scoreboard.get_height() + 10

        for i in top_10_string:
            text = self.small_font.render(i, True, WHITE)
            tx = center_sidebar - text.get_width() // 2
            self.screen.blit(text, (tx, base_y))
            base_y += 20

        # --- BOTTOM SIDEBAR NERA (sotto l'area di gioco, NON in overlay) ---
        bottom_sidebar_height = 40
        bottom_sidebar_y = GAME_HEIGHT  # Subito dopo l'area di gioco
        bottom_sidebar_panel = pygame.Surface((SCREEN_WIDTH, bottom_sidebar_height))
        bottom_sidebar_panel.fill(BLACK)
        self.screen.blit(bottom_sidebar_panel, (0, bottom_sidebar_y))

        # Centrato SOLO rispetto all'area di gioco (non l'intera finestra)
        rem_transformations = self.font.render(
            f"Rimanenti - Camuffamenti: {self.player.rem_eq_transformations} | Teletrasporti: {self.player.rem_ibp_transformations} | NOP raygun: {self.player.rem_nop_transformations} | Combo: {self.player.rem_combo_transformations}",
            True, WHITE)
        rem_x = (GAME_WIDTH - rem_transformations.get_width()) // 2
        rem_y = bottom_sidebar_y + (bottom_sidebar_height - rem_transformations.get_height()) // 2
        self.screen.blit(rem_transformations, (rem_x, rem_y))

        ui_panel = pygame.Surface((250, 200), pygame.SRCALPHA)
        ui_panel.fill((0, 0, 0, 180))
        self.screen.blit(ui_panel, (SCREEN_WIDTH - 200, GAME_HEIGHT - 205))

        instructions = [
            "WASD/Frecce: Muovi",
            "1: Camuffamento",
            "2: Teletrasporto",
            "3: NOP Raygun",
            "4: Combo",
            "R: Reset Livello"
        ]
        y = GAME_HEIGHT - 180
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, y))
            y += 30

        # --- Info trasformazione attiva ---
        if self.player.transformation != TransformationType.NONE:
            trans_text = f"Trasformazione: {self.player.transformation.name}"
            timer_text = f"Tempo: {self.player.transformation_timer // 60}s"
            text1 = self.small_font.render(trans_text, True, WHITE)
            text2 = self.small_font.render(timer_text, True, WHITE)
            self.screen.blit(text1, (10, 50))
            self.screen.blit(text2, (10, 80))

        # --- Trasformazioni rimanenti in basso a sinistra ---
        # self.screen.blit(rem_transformations, (10, SCREEN_HEIGHT - 30))

        # --- Attenzione rilevato ---
        if self.player.detected:
            warning = self.font.render("RILEVATO!", True, RED)
            x = GAME_WIDTH//2 - warning.get_width()//2
            pygame.draw.rect(self.screen, BLACK, (x-10, 45, warning.get_width()+20, 40))
            self.screen.blit(warning, (x, 50))
            # togli una vita
            self.player.lives -= 1
            #allontana il giocatore
            self.player.x = 30
            self.player.y = 30
            if self.player.lives <= 0:
                self.player.lives = 0  # Ci assicuriamo che sia visualizzato 0 prima del game over
                # Aggiorna subito la UI per mostrare vite a 0
                lives_text = self.font.render(f"Vite rimaste: {self.player.lives}", True, WHITE)
                self.screen.blit(lives_text, (lives_x, lives_y))
                pygame.display.flip()
                game_over = self.font.render("GAME OVER! Premi R per riprovare o chiudi per uscire.", True, RED)
                x = GAME_WIDTH//2 - game_over.get_width()//2
                pygame.draw.rect(self.screen, BLACK, (x-10, SCREEN_HEIGHT//2 - 30, game_over.get_width()+20, 40))
                self.screen.blit(game_over, (x, SCREEN_HEIGHT//2 - 20))
                # Write results to classifica.txt
                with open("classifica.txt", "a") as f:
                    f.write(f"{self.player_name} - Livello raggiunto: {self.level}\n")
                # wait for a key to close the game
                pygame.display.flip()
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                waiting = False
                                # self.player.lives = 3
                                self.level = 1
                                self.init_level()

                # self.running = False
    
    def draw(self):
        # Disegna sfondo
        self.draw_background()

        #disegna le vite in alto a destra
        lives_text = self.font.render(f"Vite: {self.player.lives}", True, WHITE)
        self.screen.blit(lives_text, (GAME_WIDTH - lives_text.get_width() - 10, 10))
        
        # Disegna muri con tile sprite
        for wall in self.walls:
            for x in range(wall.x, wall.x + wall.width, TILE_SIZE):
                for y in range(wall.y, wall.y + wall.height, TILE_SIZE):
                    if x < GAME_WIDTH and y < GAME_HEIGHT:
                        self.screen.blit(self.sprite_manager.sprites['wall'], (x, y))
        
        # Disegna elementi di gioco
        self.goal.draw(self.screen)
        for guard in self.guards:
            guard.draw(self.screen)
        self.player.draw(self.screen)

        for pulse in self.nop_pulses:
            pulse.draw(self.screen)

        
        # Disegna effetti particellari
        for effect in self.particle_effects:
            effect.draw(self.screen)
        
        # UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

# Funzione helper per caricare immagini esterne
def load_custom_sprites(sprite_manager):
    """
    Carica sprite personalizzati da file esterni.
    Crea una cartella 'assets' nella stessa directory dello script
    e metti dentro le tue immagini.
    """
    import os
    
    asset_path = "assets"
    if not os.path.exists(asset_path):
        os.makedirs(asset_path)
        print(f"Creata cartella '{asset_path}' - aggiungi qui le tue immagini!")
        print("Nomi file suggeriti:")
        print("  - cat_blimblau.png, cat_red.png, etc. (32x32 px)")
        print("  - guard.png (32x32 px)")
        print("  - background.png (1024x768 px)")
        print("  - wall_tile.png (32x32 px)")
        print("  - floor_tile.png (32x32 px)")
        print("  - goal.png (64x64 px)")
        return
    
    # Dizionario dei file da caricare
    sprites_to_load = {
        'cat_blimblau': 'cat_blimblau.png',
        'cat_red': 'cat_red.png',
        'cat_green': 'cat_green.png',
        'cat_yellow': 'cat_yellow.png',
        'cat_purple': 'cat_purple.png',
        'guard': 'guard.png',
        'wall': 'wall_tile.png',
        'floor': 'floor_tile.png',
        'goal': 'goal.png',
        'background': 'background.png'
    }
    
    for sprite_name, filename in sprites_to_load.items():
        filepath = os.path.join(asset_path, filename)
        if os.path.exists(filepath):
            try:
                img = pygame.image.load(filepath)

                # make the cat_blimblau and guard bigger
                # img = img.convert_alpha()
                # img = pygame.transform.scale(img, (img.get_width()*4, img.get_height()*4))

                
                # Ridimensiona se necessario
                if sprite_name == 'goal':
                    img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
                elif sprite_name == 'background':
                    img = pygame.transform.scale(img, (GAME_WIDTH, GAME_HEIGHT))
                elif sprite_name != 'background':
                    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                
                sprite_manager.sprites[sprite_name] = img
                print(f"✓ Caricato: {filename}")
            except Exception as e:
                print(f"✗ Errore nel caricare {filename}: {e}")
        else:
            print(f"- File non trovato: {filepath} (usando sprite procedurale)")

# Main
if __name__ == "__main__":
    # menu di benvenuto, sempre in Pygame
   


    game = Game()
    
    # Prova a caricare sprite personalizzati
    load_custom_sprites(game.sprite_manager)
    
    print("\n=== METAMORPHIC MAZE ===")
    print("Un gioco educativo sulla sicurezza informatica")
    print("Basato su tecniche di offuscamento metamorfico\n")
    
    game.run()
