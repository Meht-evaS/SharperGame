import pygame
import random
import math
import os
from enum import Enum

# Inizializzazione Pygame
pygame.init()

# Costanti
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 32
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

class TransformationType(Enum):
    NONE = 0
    SUBSTITUTION = 1  # Cambia aspetto
    PERMUTATION = 2   # Teletrasporto
    NOP_INSERTION = 3 # Passi fantasma
    COMBO = 4         # Combinazione

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
            'purple': PURPLE
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

class Player:
    def __init__(self, x, y, sprite_manager):
        self.x = x
        self.y = y
        self.speed = 4
        self.color = 'blue'
        self.original_color = 'blue'
        self.transformation = TransformationType.NONE
        self.transformation_timer = 0
        self.ghost_steps = []
        self.detected = False
        self.win = False
        self.sprite_manager = sprite_manager
        self.animation_frame = 0
        self.facing_right = True
        
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
            
            self.x = new_x
            self.y = new_y
    
    def apply_transformation(self, trans_type):
        self.transformation = trans_type
        self.transformation_timer = 180  # 3 secondi a 60 FPS
        
        if trans_type == TransformationType.SUBSTITUTION:
            # Cambia colore/aspetto
            colors = ['red', 'green', 'yellow', 'purple']
            self.color = random.choice(colors)
        elif trans_type == TransformationType.PERMUTATION:
            # Teletrasporto in posizione casuale sicura
            self.teleport_random()
            return ParticleEffect(self.x, self.y, 'teleport')
        elif trans_type == TransformationType.NOP_INSERTION:
            # Inizia a lasciare "passi fantasma"
            self.ghost_steps = []
        elif trans_type == TransformationType.COMBO:
            # Applica combo di effetti
            self.color = random.choice(['red', 'green', 'yellow', 'purple'])
            self.ghost_steps = []
        return None
    
    def teleport_random(self):
        self.x = random.randint(100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 100)
    
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
        
    def update(self, player):
        # Animazione
        self.animation_frame = (self.animation_frame + 1) % 60
        
        # Movimento lungo il percorso di pattuglia
        if len(self.patrol_path) > 0:
            target = self.patrol_path[self.current_target]
            dx = target[0] - self.x
            dy = target[1] - self.y
            dist = math.sqrt(dx**2 + dy**2)
            
            if dist > 5:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.facing_direction = math.atan2(dy, dx)
            else:
                self.current_target = (self.current_target + 1) % len(self.patrol_path)
        
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
                if player.color != self.detection_color:
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
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            color = (255, 50, 50, 40)# if not self.detection_color else (*self.detection_color, 40)
            pygame.draw.polygon(s, color, points)
            screen.blit(s, (0, 0))
        
        # Disegna sprite guardia
        sprite = self.sprite_manager.sprites['guard']
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
        self.init_level()
        
    def init_level(self):
        # Inizializza livello
        self.player = Player(100, 100, self.sprite_manager)
        self.goal = Goal(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150, self.sprite_manager)
        self.guards = []
        self.walls = []
        
        # Crea muri del labirinto
        # Bordi
        self.walls.append(pygame.Rect(0, 0, SCREEN_WIDTH, 20))
        self.walls.append(pygame.Rect(0, SCREEN_HEIGHT-20, SCREEN_WIDTH, 20))
        self.walls.append(pygame.Rect(0, 0, 20, SCREEN_HEIGHT))
        self.walls.append(pygame.Rect(SCREEN_WIDTH-20, 0, 20, SCREEN_HEIGHT))
        
        # Muri interni
        self.walls.append(pygame.Rect(200, 100, 20, 300))
        self.walls.append(pygame.Rect(400, 200, 200, 20))
        self.walls.append(pygame.Rect(600, 100, 20, 300))
        self.walls.append(pygame.Rect(300, 500, 400, 20))
        
        # Aggiungi guardie basate sul livello
        if self.level == 1:
            # Livello 1: Guardia semplice
            self.guards.append(Guard(400, 300, 
                                   [(400, 300), (400, 500), (600, 500), (600, 300)],
                                   self.sprite_manager))
        elif self.level == 2:
            # Livello 2: Guardie con rilevamento colore
            self.guards.append(Guard(300, 300, 
                                   [(300, 300), (500, 300)], 
                                   self.sprite_manager,
                                   detection_color='blue'))
            self.guards.append(Guard(500, 400, 
                                   [(500, 400), (300, 400)], 
                                   self.sprite_manager,
                                   detection_color='red'))
        else:
            # Livelli successivi
            for i in range(min(self.level, 5)):
                x = random.randint(200, SCREEN_WIDTH - 200)
                y = random.randint(200, SCREEN_HEIGHT - 200)
                path = self.generate_random_path(x, y)
                self.guards.append(Guard(x, y, path, self.sprite_manager, detection_color=None))
    
    def generate_random_path(self, start_x, start_y):
        path = [(start_x, start_y)]
        for _ in range(3):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
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
        
        # Controllo vittoria
        player_rect = pygame.Rect(self.player.x, self.player.y, TILE_SIZE, TILE_SIZE)
        goal_rect = pygame.Rect(self.goal.x, self.goal.y, TILE_SIZE * 2, TILE_SIZE * 2)
        if player_rect.colliderect(goal_rect):
            self.player.win = True
            self.level += 1
            self.init_level()
    
    def draw_background(self):
        """Disegna lo sfondo con tiles"""
        for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
            for x in range(0, SCREEN_WIDTH, TILE_SIZE):
                # Alterna tra floor e circuit tiles per creare pattern
                if (x // TILE_SIZE + y // TILE_SIZE) % 3 == 0:
                    self.screen.blit(self.sprite_manager.sprites['circuit'], (x, y))
                else:
                    self.screen.blit(self.sprite_manager.sprites['floor'], (x, y))
    
    def draw_ui(self):
        # Background pannello UI
        ui_panel = pygame.Surface((250, 200), pygame.SRCALPHA)
        ui_panel.fill((0, 0, 0, 180))
        self.screen.blit(ui_panel, (5, SCREEN_HEIGHT - 205))
        
        # Informazioni trasformazione attiva
        if self.player.transformation != TransformationType.NONE:
            trans_text = f"Trasformazione: {self.player.transformation.name}"
            timer_text = f"Tempo: {self.player.transformation_timer // 60}s"
            text1 = self.small_font.render(trans_text, True, WHITE)
            text2 = self.small_font.render(timer_text, True, WHITE)
            self.screen.blit(text1, (10, 50))
            self.screen.blit(text2, (10, 80))
        
        # Istruzioni
        instructions = [
            "WASD/Frecce: Muovi",
            "1: Camuffamento",
            "2: Teletrasporto",
            "3: Passi Fantasma",
            "4: Combo",
            "R: Reset Livello"
        ]
        
        y = SCREEN_HEIGHT - 180
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (10, y))
            y += 30
        
        # Livello e stato
        level_text = self.font.render(f"Livello: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 10))
        
        if self.player.detected:
            warning = self.font.render("RILEVATO!", True, RED)
            x = SCREEN_WIDTH//2 - warning.get_width()//2
            pygame.draw.rect(self.screen, BLACK, (x-10, 45, warning.get_width()+20, 40))
            self.screen.blit(warning, (x, 50))
    
    def draw(self):
        # Disegna sfondo
        self.draw_background()
        
        # Disegna muri con tile sprite
        for wall in self.walls:
            for x in range(wall.x, wall.x + wall.width, TILE_SIZE):
                for y in range(wall.y, wall.y + wall.height, TILE_SIZE):
                    if x < SCREEN_WIDTH and y < SCREEN_HEIGHT:
                        self.screen.blit(self.sprite_manager.sprites['wall'], (x, y))
        
        # Disegna elementi di gioco
        self.goal.draw(self.screen)
        for guard in self.guards:
            guard.draw(self.screen)
        self.player.draw(self.screen)
        
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
        print("  - cat_blue.png, cat_red.png, etc. (32x32 px)")
        print("  - guard.png (32x32 px)")
        print("  - background.png (1024x768 px)")
        print("  - wall_tile.png (32x32 px)")
        print("  - floor_tile.png (32x32 px)")
        print("  - goal.png (64x64 px)")
        return
    
    # Dizionario dei file da caricare
    sprites_to_load = {
        'cat_blue': 'cat_blue.png',
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
                
                # Ridimensiona se necessario
                if sprite_name == 'goal':
                    img = pygame.transform.scale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
                elif sprite_name == 'background':
                    img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
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
    game = Game()
    
    # Prova a caricare sprite personalizzati
    load_custom_sprites(game.sprite_manager)
    
    print("\n=== METAMORPHIC MAZE ===")
    print("Un gioco educativo sulla sicurezza informatica")
    print("Basato su tecniche di offuscamento metamorfico\n")
    
    game.run()