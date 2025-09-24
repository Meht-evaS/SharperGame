import pygame
import random
import math
import os
from enum import Enum

# -----------------------------
# Inizializzazione Pygame
# -----------------------------
pygame.init()

# -----------------------------
# Costanti
# -----------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 808   # <--- aumenta di 40px per bottom sidebar

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
ORANGE = (255, 140, 0)

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

# -----------------------------
# Sprite Manager con cache/scaling
# -----------------------------
class SpriteManager:
    """Gestisce il caricamento e la creazione degli sprite; pre-scala dove serve."""
    def __init__(self):
        self.sprites = {}
        self.big_factor = 1.5  # scala “grande” usata da player/guard
        self.load_sprites()

    def load_sprites(self):
        # Procedurali
        self.create_cat_sprites()
        self.create_guard_sprite()
        self.create_background_tiles()
        self.create_goal_sprite()
        self.create_particle_effects()

    def _scale(self, surf, w, h):
        return pygame.transform.smoothscale(surf, (int(w), int(h)))

    def create_cat_sprites(self):
        colors = {
            'blue': BLUE, 'red': RED, 'green': GREEN, 'yellow': YELLOW,
            'purple': PURPLE, 'black': BLACK, 'white': WHITE
        }
        for color_name, color in colors.items():
            cat_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            # Corpo
            pygame.draw.ellipse(cat_surf, color, (4, 8, 24, 20))
            # Testa
            pygame.draw.circle(cat_surf, color, (16, 12), 8)
            # Orecchie
            pygame.draw.polygon(cat_surf, color, [(8, 8), (6, 2), (12, 6)])
            pygame.draw.polygon(cat_surf, color, [(20, 6), (24, 2), (22, 8)])
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
            # versione big
            big = self._scale(cat_surf, TILE_SIZE*self.big_factor, TILE_SIZE*self.big_factor)
            self.sprites[f'cat_{color_name}_big'] = big
    def get_cat_sprite(self, color, big=False):
        """Restituisce la surface del gatto richiesta con fallback intelligente."""
        key = f'cat_{color}_big' if big else f'cat_{color}'

        # Se esiste direttamente la chiave richiesta, restituiscila
        if key in self.sprites:
            return self.sprites[key]

        # Se chiedo la big ma esiste la versione normale, scala al volo e cache-ala
        if big and f'cat_{color}' in self.sprites:
            scaled = self._scale(self.sprites[f'cat_{color}'],
                                 int(TILE_SIZE * self.big_factor),
                                 int(TILE_SIZE * self.big_factor))
            # cache per future richieste
            self.sprites[f'cat_{color}_big'] = scaled
            return scaled

        # Fall back preferito: cat_blue_big -> cat_blue -> qualunque cat_*
        if big and 'cat_blue_big' in self.sprites:
            return self.sprites['cat_blue_big']
        if 'cat_blue' in self.sprites:
            return self.sprites['cat_blue']

        # Ultimo resort: trova la prima cat_* (big se richiesta)
        for k in self.sprites:
            if big and k.startswith('cat_') and k.endswith('_big'):
                return self.sprites[k]
            if not big and k.startswith('cat_') and not k.endswith('_big'):
                return self.sprites[k]

        # Se proprio nulla, crea una surface vuota minimale
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        return surf

    def create_guard_sprite(self):
        guard_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(guard_surf, DARK_GRAY, (6, 10, 20, 18))
        pygame.draw.rect(guard_surf, RED, (8, 12, 16, 14))
        pygame.draw.circle(guard_surf, WHITE, (16, 19), 6)
        pygame.draw.circle(guard_surf, RED, (16, 19), 4)
        pygame.draw.circle(guard_surf, BLACK, (16, 19), 2)
        pygame.draw.line(guard_surf, GRAY, (16, 10), (16, 4), 2)
        pygame.draw.circle(guard_surf, RED, (16, 3), 3)
        pygame.draw.circle(guard_surf, DARK_GRAY, (10, 28), 3)
        pygame.draw.circle(guard_surf, DARK_GRAY, (22, 28), 3)
        self.sprites['guard'] = guard_surf
        self.sprites['guard_big'] = self._scale(guard_surf, TILE_SIZE*self.big_factor, TILE_SIZE*self.big_factor)

    def create_background_tiles(self):
        floor_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        floor_tile.fill((40, 40, 50))
        for i in range(0, TILE_SIZE, 8):
            pygame.draw.line(floor_tile, (35, 35, 45), (i, 0), (i, TILE_SIZE), 1)
            pygame.draw.line(floor_tile, (35, 35, 45), (0, i), (TILE_SIZE, i), 1)
        self.sprites['floor'] = floor_tile

        wall_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        wall_tile.fill((100, 100, 120))
        for y in range(0, TILE_SIZE, 8):
            for x in range(0, TILE_SIZE, 16):
                offset = 8 if (y // 8) % 2 else 0
                pygame.draw.rect(wall_tile, (80, 80, 100), (x + offset - 8, y, 15, 7), 1)
        self.sprites['wall'] = wall_tile

        circuit_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
        circuit_tile.fill((20, 30, 40))
        pygame.draw.line(circuit_tile, (0, 100, 100), (0, 16), (32, 16), 2)
        pygame.draw.line(circuit_tile, (0, 100, 100), (16, 0), (16, 32), 2)
        pygame.draw.circle(circuit_tile, (0, 150, 150), (8, 8), 3)
        pygame.draw.circle(circuit_tile, (0, 150, 150), (24, 24), 3)
        self.sprites['circuit'] = circuit_tile

    def create_goal_sprite(self):
        goal_surf = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.rect(goal_surf, (60, 60, 70), (8, 4, 48, 36))
        pygame.draw.rect(goal_surf, (0, 200, 255), (12, 8, 40, 28))
        for i in range(5):
            y = 12 + i * 5
            pygame.draw.line(goal_surf, GREEN, (14, y), (14 + random.randint(10, 35), y), 1)
        pygame.draw.rect(goal_surf, (40, 40, 50), (24, 40, 16, 8))
        pygame.draw.rect(goal_surf, (40, 40, 50), (16, 48, 32, 4))
        self.sprites['goal'] = goal_surf

    def create_particle_effects(self):
        teleport_particle = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(teleport_particle, (100, 200, 255), (4, 4), 4)
        pygame.draw.circle(teleport_particle, WHITE, (4, 4), 2)
        self.sprites['teleport_particle'] = teleport_particle

        ghost_particle = pygame.Surface((16, 16), pygame.SRCALPHA)
        ghost_particle.set_alpha(100)
        pygame.draw.circle(ghost_particle, (150, 150, 255), (8, 8), 8)
        self.sprites['ghost_particle'] = ghost_particle

# -----------------------------
# Effetti/Entità
# -----------------------------
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
                    'x': x, 'y': y,
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
        self.radius = radius

    def update(self, walls):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        if self.x < 20 or self.x > GAME_WIDTH - 20:
            self.vx *= -1
        if self.y < 20 or self.y > GAME_HEIGHT - 20:
            self.vy *= -1
        pulse_rect = pygame.Rect(int(self.x - 4), int(self.y - 4), 8, 8)
        for w in walls:
            if pulse_rect.colliderect(w):
                self.life = 0
                break
        return self.life > 0

    def draw(self, screen, tiny_font):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 255, 255, 60), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (255, 255, 255, 180), (self.radius, self.radius), 3)
        text = tiny_font.render("0x90", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.radius, self.radius))
        s.blit(text, text_rect)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))

class Player:
    def __init__(self, x, y, sprite_manager, lives=3):
        self.x = x
        self.y = y
        self.speed = 4
        self.color = 'blimblau'   # colore “fuori palette” = camuffato
        self.original_color = 'blimblau'
        self.transformation = TransformationType.NONE
        self.transformation_timer = 0
        self.ghost_steps = []
        self.detected = False
        self.win = False
        self.sprite_manager = sprite_manager
        self.animation_frame = 0
        self.facing_right = True
        self.lives = lives
        self.dir = [1, 0]

        self.rem_eq_transformations = MAX_EQ_TRANSFORMATIONS
        self.rem_nop_transformations = MAX_NOP_TRANSFORMATIONS
        self.rem_combo_transformations = MAX_COMBO_TRANSFORMATIONS
        self.rem_ibp_transformations = MAX_IBP_TRANSFORMATIONS

    def update(self):
        if self.transformation_timer > 0:
            self.transformation_timer -= 1
            if self.transformation_timer == 0:
                self.reset_transformation()
        self.animation_frame = (self.animation_frame + 1) % 60

    def move(self, dx, dy, walls):
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False

        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        player_rect = pygame.Rect(new_x, new_y, TILE_SIZE-4, TILE_SIZE-4)
        collision = any(player_rect.colliderect(w) for w in walls)

        if not collision:
            if self.transformation == TransformationType.NOP_INSERTION:
                self.ghost_steps.append((self.x, self.y, self.animation_frame))
                if len(self.ghost_steps) > 5:
                    self.ghost_steps.pop(0)
            if dx != 0 or dy != 0:
                mag = math.hypot(dx, dy)
                self.dir = [dx / mag, dy / mag]
            self.x = new_x
            self.y = new_y

    def apply_transformation(self, trans_type, game_ref):
        self.transformation = trans_type
        self.transformation_timer = 180  # 3 secondi a 60 FPS

        colors = ['red', 'green', 'yellow', 'purple', 'black', 'white']

        if trans_type == TransformationType.SUBSTITUTION:
            if self.rem_eq_transformations <= 0:
                return None
            self.color = random.choice(colors)
            self.rem_eq_transformations -= 1

        elif trans_type == TransformationType.PERMUTATION:
            if self.rem_ibp_transformations <= 0:
                return None
            self.teleport_random(game_ref)
            self.rem_ibp_transformations -= 1
            return ParticleEffect(self.x, self.y, 'teleport')

        elif trans_type == TransformationType.NOP_INSERTION:
            if self.rem_nop_transformations <= 0:
                return None
            base_angle = math.atan2(self.dir[1], self.dir[0])
            for off in (-0.25, 0.0, 0.25):
                ang = base_angle + off
                cx = self.x + TILE_SIZE * 0.75
                cy = self.y + TILE_SIZE * 0.75
                game_ref.nop_pulses.append(NopPulse(cx, cy, ang))
            self.ghost_steps = []
            self.rem_nop_transformations -= 1
            return None

        elif trans_type == TransformationType.COMBO:
            if self.rem_combo_transformations <= 0:
                return None
            self.color = random.choice(colors)
            self.ghost_steps = []
            self.rem_combo_transformations -= 1
            return None

        elif trans_type == TransformationType.POSITION_INDEPENDENT:
            if self.rem_ibp_transformations <= 0:
                return None
            self.teleport_random(game_ref)
            self.color = random.choice(colors)
            self.ghost_steps = []
            self.rem_ibp_transformations -= 1
            return ParticleEffect(self.x, self.y, 'teleport')

    def teleport_random(self, game_ref):
        safe = False
        attempts = 0
        while not safe and attempts < 100:
            new_x = random.randint(20, GAME_WIDTH - 20 - TILE_SIZE)
            new_y = random.randint(20, GAME_HEIGHT - 20 - TILE_SIZE)
            player_rect = pygame.Rect(new_x, new_y, TILE_SIZE-4, TILE_SIZE-4)
            safe = True
            for wall in game_ref.walls:
                if player_rect.colliderect(wall):
                    safe = False
                    break
            if safe:
                for guard in game_ref.guards:
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
        # ghost steps
        if self.transformation == TransformationType.NOP_INSERTION:
            for i, (gx, gy, frame) in enumerate(self.ghost_steps):
                alpha = 50 + i * 20
                ghost_sprite = self.sprite_manager.get_cat_sprite(self.color, big=False).copy()
                ghost_sprite.set_alpha(alpha)
                screen.blit(ghost_sprite, (gx, gy))

        if self.detected:
            pygame.draw.circle(screen, RED,
                               (int(self.x + TILE_SIZE//2), int(self.y + TILE_SIZE//2)),
                               TILE_SIZE//2 + 5, 3)

        # usa sprite pre-scalato tramite helper
        sprite = self.sprite_manager.get_cat_sprite(self.color, big=True)
        sprite_to_draw = pygame.transform.flip(sprite, True, False) if not self.facing_right else sprite
        y_offset = math.sin(self.animation_frame * 0.2) * 2
        screen.blit(sprite_to_draw, (self.x, self.y + y_offset))


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
        self.animation_frame = (self.animation_frame + 1) % 60
        if self.seconds_to_travel <= 0:
            self.choicex = random.choice([-1, 0, 1])
            self.choicey = random.choice([-1, 0, 1])
            self.seconds_to_travel = 60

        if self.choicex != 0 or self.choicey != 0:
            if self.x + self.choicex * self.speed < 20 or self.x + self.choicex * self.speed > GAME_WIDTH - 20 - TILE_SIZE:
                self.choicex = 0
            if self.y + self.choicey * self.speed < 20 or self.y + self.choicey * self.speed > GAME_HEIGHT - 20 - TILE_SIZE:
                self.choicey = 0
            self.x += self.choicex * self.speed
            self.y += self.choicey * self.speed
            self.facing_direction = math.atan2(self.choicey, self.choicex)
        self.seconds_to_travel -= 1
        return self.detect_player(player)

    def detect_player(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.detection_radius:
            if self.detection_color is not None:
                if player.color != self.detection_color and player.color != 'blimblau':
                    return False
            angle_to_player = math.atan2(dy, dx)
            angle_diff = abs(angle_to_player - self.facing_direction)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            if angle_diff < math.radians(self.viewing_angle / 2):
                return True
        return False

    def _vision_points(self):
        points = [(self.x + TILE_SIZE//2, self.y + TILE_SIZE//2)]
        for angle_offset in range(-self.viewing_angle//2, self.viewing_angle//2 + 1, 5):
            angle = self.facing_direction + math.radians(angle_offset)
            end_x = self.x + TILE_SIZE//2 + math.cos(angle) * self.detection_radius
            end_y = self.y + TILE_SIZE//2 + math.sin(angle) * self.detection_radius
            points.append((end_x, end_y))
        return points

    def draw_vision(self, vision_surface):
        points = self._vision_points()
        if len(points) > 2:
            pygame.draw.polygon(vision_surface, (255, 50, 50, 40), points)

    def draw_sprite(self, screen):
        sprite = self.sprite_manager.sprites['guard_big']
        angle = -math.degrees(self.facing_direction) - 90
        rotated_sprite = pygame.transform.rotate(sprite, angle)
        rect = rotated_sprite.get_rect(center=(self.x + TILE_SIZE//2, self.y + TILE_SIZE//2))
        screen.blit(rotated_sprite, rect)
        scan_radius = 10 + math.sin(self.animation_frame * 0.1) * 5
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x + TILE_SIZE//2), int(self.y + TILE_SIZE//2)), int(scan_radius), 2)

class Goal:
    def __init__(self, x, y, sprite_manager):
        self.x = x
        self.y = y
        self.pulse = 0
        self.sprite_manager = sprite_manager

    def update(self):
        self.pulse = (self.pulse + 2) % 360

    def draw(self, screen):
        glow_size = 40 + math.sin(math.radians(self.pulse)) * 10
        s = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 100, 50), (glow_size, glow_size), glow_size)
        screen.blit(s, (self.x - glow_size + TILE_SIZE, self.y - glow_size + TILE_SIZE))
        screen.blit(self.sprite_manager.sprites['goal'], (self.x, self.y))

# -----------------------------
# Gioco
# -----------------------------
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Metamorphic Maze - Sharper Night")
        self.clock = pygame.time.Clock()

        # Font precaricati
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 20)

        self.running = True
        self.level = 1
        self.sprite_manager = SpriteManager()
        self.particle_effects = []
        self.nop_pulses = []
        self.player_name = "Sonic Feet"

        # Surface condivise per performance
        self.vision_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        self.bg_surface = None           # sfondo prerender
        self.walls_surface = None        # muri prerender

        # Cache classifica
        self.top10_cache = []
        self._load_scoreboard()

        # Background del menu (precaricato)
        self.menu_bg = None
        self._load_menu_background()

        self.menu()

    # ---------- Asset loading helpers ----------
    def _load_menu_background(self):
        path = "assets/CyberGarflieldpng.png"
        if os.path.exists(path):
            img = pygame.image.load(path)
            img = pygame.transform.smoothscale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            img.set_alpha(100)
            self.menu_bg = img

    def _load_scoreboard(self):
        self.top10_cache = []
        if os.path.exists("classifica.txt"):
            with open("classifica.txt", "r") as f:
                lines = f.readlines()
            lines = sorted(lines, key=lambda x: int(x.split(':')[-1].strip()) if ':' in x else 0, reverse=True)
            for i, line in enumerate(lines[:10]):
                try:
                    nome = line.split('-')[0].strip()
                    livello = line.split(':')[-1].strip()
                    self.top10_cache.append(f"{i+1}. {nome} - {livello}")
                except Exception:
                    continue

    def _append_score(self, name, level):
        with open("classifica.txt", "a") as f:
            f.write(f"{name} - Livello raggiunto: {level}\n")
        self._load_scoreboard()

    # ---------- Menu ----------
    def menu(self):
        waiting = True
        selected = 0
        menu_options = [
            {"text": "- Inizia partita", "action": "start_game"},
            {"text": "- Istruzioni", "action": "instructions"},
            {"text": "- Significato scientifico", "action": "scientifico"},
            {"text": "- Classifica", "action": "classifica"},
        ]

        while waiting:
            # Background
            self.screen.fill(BLACK)
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))

            # Testi intro
            title = self.font.render("Metamorphic Maze - Sharper Night", True, ORANGE)
            small_description1 = self.small_font.render("Sei Garfield, un virus informatico che deve infiltrarsi in un sistema sorvegliato da antivirus.", True, WHITE)
            small_description2 = self.small_font.render("Usa le trasformazioni metamorfiche per evitare di essere rilevato e raggiungere il server.", True, WHITE)

            top_margin = 30
            sd1_x = 50
            sd1_y = top_margin + title.get_height() + 8
            title_x = sd1_x + (small_description1.get_width() // 2) - (title.get_width() // 2)
            title_y = top_margin
            sd2_x = sd1_x + (small_description1.get_width() // 2) - (small_description2.get_width() // 2)
            sd2_y = sd1_y + small_description1.get_height() + 4

            min_x = min(title_x, sd1_x, sd2_x)
            max_x = max(title_x + title.get_width(),
                        sd1_x + small_description1.get_width(),
                        sd2_x + small_description2.get_width())
            box_width = max_x - min_x + 33
            box_left = min_x - 16
            min_y = min(title_y, sd1_y, sd2_y)
            max_y = max(title_y + title.get_height(),
                        sd1_y + small_description1.get_height(),
                        sd2_y + small_description2.get_height())
            box_height = max_y - min_y + 33
            texts_center_y = (min_y + max_y) // 2
            box_top = texts_center_y - (box_height // 2)
            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 0, 102))
            self.screen.blit(box_surface, (box_left, box_top))
            self.screen.blit(title, (title_x, title_y))
            self.screen.blit(small_description1, (sd1_x, sd1_y))
            self.screen.blit(small_description2, (sd2_x, sd2_y))

            # Box opzioni
            menu_width = max(self.small_font.size(opt["text"])[0] for opt in menu_options)
            menu_height = sum(self.small_font.size(opt["text"])[1] for opt in menu_options)
            padding_x, padding_y, spacing = 20, 12, 8
            box_width = menu_width + 2 * padding_x
            box_height = menu_height + (len(menu_options)-1)*spacing + 2 * padding_y
            box_x = SCREEN_WIDTH - box_width - 30
            box_y = SCREEN_HEIGHT - box_height - 30
            menu_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            menu_box.fill((0, 0, 0, 102))
            self.screen.blit(menu_box, (box_x, box_y))
            current_y = box_y + padding_y
            for idx, option in enumerate(menu_options):
                color = ORANGE if idx == selected else WHITE
                text = self.small_font.render(option["text"], True, color)
                self.screen.blit(text, (box_x + padding_x, current_y))
                current_y += text.get_height() + spacing

            pygame.display.flip()
            self.clock.tick(FPS)  # LIMITA FPS NEL MENU

            # Eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        action = menu_options[selected]["action"]
                        if action == "start_game":
                            # prompt nome giocatore
                            self.player_name = ""
                            asking_name = True
                            while asking_name:
                                self.screen.fill(BLACK)
                                if self.menu_bg:
                                    self.screen.blit(self.menu_bg, (0, 0))
                                prompt = self.small_font.render("Inserisci il tuo nome (max 15 caratteri): " + self.player_name, True, WHITE)
                                self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2))
                                pygame.display.flip()
                                self.clock.tick(FPS)  # LIMITA FPS
                                for ev in pygame.event.get():
                                    if ev.type == pygame.QUIT:
                                        asking_name = False
                                        waiting = False
                                        self.running = False
                                    elif ev.type == pygame.KEYDOWN:
                                        if ev.key == pygame.K_RETURN:
                                            if len(self.player_name) > 0:
                                                asking_name = False
                                        elif ev.key == pygame.K_BACKSPACE:
                                            self.player_name = self.player_name[:-1]
                                        else:
                                            if len(self.player_name) < 15 and ev.unicode.isprintable():
                                                self.player_name += ev.unicode
                            waiting = False
                            self.init_level()
                            return

                        elif action == "scientifico":
                            self._screen_scrolling_text(self._scientifico_text())
                        elif action == "classifica":
                            self._screen_classifica()
                        elif action == "instructions":
                            self._screen_instructions()

    def _screen_scrolling_text(self, string):
        lines_raw = string.split('\n')
        lines = []
        indent = 0
        for line in lines_raw:
            if line.strip().startswith(('1)', '2)', '3)', '4)', '5)')):
                indent = 0
                lines.append((line.strip(), indent))
                indent = 18.5
            elif line.strip() == '':
                indent = 0
                lines.append(('', 0))
            else:
                lines.append((line.strip(), indent))
        offset = 0
        waiting = True
        while waiting and self.running:
            self.screen.fill(BLACK)
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))
            y = SCREEN_HEIGHT//2 - len(lines)*10 + offset
            for line, ind in lines:
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (50 + ind, y))
                y += 20
            info = "Premi R, ESC o INVIO per tornare al menu"
            text_info = self.small_font.render(info, True, ORANGE)
            padding_x, padding_y = 28, 10
            box_width = text_info.get_width() + 2 * padding_x
            box_height = text_info.get_height() + 2 * padding_y
            box_x = SCREEN_WIDTH//2 - box_width//2
            box_y = SCREEN_HEIGHT - 60 - padding_y
            menu_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            menu_box.fill((0, 0, 0, 179))
            self.screen.blit(menu_box, (box_x, box_y))
            self.screen.blit(text_info, (SCREEN_WIDTH//2 - text_info.get_width()//2, box_y + padding_y))
            pygame.display.flip()
            self.clock.tick(FPS)  # LIMITA FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_ESCAPE, pygame.K_RETURN):
                        waiting = False
                    elif event.key == pygame.K_UP:
                        offset += 20
                    elif event.key == pygame.K_DOWN:
                        offset -= 20

    def _screen_classifica(self):
        # carica da file una sola volta all’apertura della schermata
        self._load_scoreboard()
        waiting = True
        show_first_n = 10
        while waiting and self.running:
            self.screen.fill(BLACK)
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))
            title = self.font.render("Classifica TOP 10", True, WHITE)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
            y = 100
            for line in self.top10_cache[:show_first_n]:
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
                y += 30
            info = "Premi R, ESC o INVIO per tornare al menu"
            text_info = self.small_font.render(info, True, ORANGE)
            padding_x, padding_y = 28, 10
            box_width = text_info.get_width() + 2 * padding_x
            box_height = text_info.get_height() + 2 * padding_y
            box_x = SCREEN_WIDTH//2 - box_width//2
            box_y = SCREEN_HEIGHT - 60 - padding_y
            menu_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            menu_box.fill((0, 0, 0, 179))
            self.screen.blit(menu_box, (box_x, box_y))
            self.screen.blit(text_info, (SCREEN_WIDTH//2 - text_info.get_width()//2, box_y + padding_y))
            pygame.display.flip()
            self.clock.tick(FPS)  # LIMITA FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_ESCAPE, pygame.K_RETURN):
                        waiting = False

    def _screen_instructions(self):
        waiting = True
        while waiting and self.running:
            self.screen.fill(BLACK)
            if self.menu_bg:
                self.screen.blit(self.menu_bg, (0, 0))
            lines = [
                "ISTRUZIONI:",
                "WASD/Frecce: Muovi il giocatore",
                "1: Camuffamento (Substitution)",
                "2: Teletrasporto (Permutation)",
                "3: NOP Raygun (NOP Insertion)",
                "4: Combo (Combo)",
                "R: Reset Livello"
            ]
            big_font = pygame.font.Font(None, self.small_font.get_height() + 20)
            text_title = big_font.render(lines[0], True, WHITE)
            title_x = SCREEN_WIDTH//2 - text_title.get_width()//2
            title_y = SCREEN_HEIGHT//2 - len(lines)*20
            self.screen.blit(text_title, (title_x, title_y))
            y = title_y + text_title.get_height() + 20
            for line in lines[1:]:
                text = self.small_font.render(line, True, WHITE)
                self.screen.blit(text, (180, y))
                y += 30

            info = "Premi R, ESC o INVIO per tornare al menu"
            text_info = self.small_font.render(info, True, ORANGE)
            padding_x, padding_y = 28, 10
            box_width = text_info.get_width() + 2 * padding_x
            box_height = text_info.get_height() + 2 * padding_y
            box_x = SCREEN_WIDTH//2 - box_width//2
            box_y = SCREEN_HEIGHT - 60 - padding_y
            menu_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            menu_box.fill((0, 0, 0, 179))
            self.screen.blit(menu_box, (box_x, box_y))
            self.screen.blit(text_info, (SCREEN_WIDTH//2 - text_info.get_width()//2, box_y + padding_y))
            pygame.display.flip()
            self.clock.tick(FPS)  # LIMITA FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_r, pygame.K_ESCAPE, pygame.K_RETURN):
                        waiting = False

    def _scientifico_text(self):
        return '''
Il metamorfismo è una tecnica utilizzata dagli autori di malware (software malevolo, comunemente detti virus informatici) per 
aggirare gli strumenti di sicurezza come antivirus o EDR.

Gli antivirus, infatti, rilevano un malware principalmente riconoscendo determinati tratti distintivi (signature detection), 
come specifiche istruzioni o sequenze di byte che compaiono solo in quel programma.
Se questi tratti distintivi vengono modificati senza alterare il funzionamento originale, 
si ottiene un malware che compie le stesse azioni, ma in modo diverso, e che quindi può eludere la rilevazione.

Per raggiungere questo obiettivo esistono diverse tecniche. 
Noi abbiamo realizzato un software che ne implementa 4 già conosciute e 1 da noi inventata. È anche possibile combinarle.

Ecco quali sono e cosa fanno, in breve:

1) Equal Instruction Substitution
   Sostituisce alcune istruzioni con altre che hanno lo stesso identico effetto.

2) NOP Insertion
   Inserisce istruzioni che non alterano in alcun modo il comportamento del programma.

3) Instruction Block Permutation
   Divide il programma in blocchi di istruzioni e ne cambia l’ordine. 
   Per mantenere il corretto flusso di esecuzione, vengono inseriti salti (JMP) alla fine dei blocchi,
   così che il programma funzioni come prima, ma con una struttura diversa.

4) Bogus Control Flow
   Aggiunge interi blocchi di codice inutili che non verranno mai eseguiti. 
   Ogni blocco è preceduto da una condizione che forziamo sempre a vera o falsa, in modo da impedirne l’esecuzione.
   Questo complica anche l’analisi statica del codice.

5) Position Independent Instruction (tecnica originale)
   Permette di rimescolare non solo i blocchi, ma ogni singola istruzione. 
   È una tecnica molto potente ma anche estremamente invasiva, perché richiede che ogni istruzione restituisca il controllo a
   un’unità centrale che gestisce il flusso del programma.
'''

    # ---------- Gioco ----------
    def init_level(self):
        # Player
        if self.level == 1:
            self.player = Player(100, 100, self.sprite_manager, lives=3)
        else:
            new_lives = self.player.lives + 1 if self.player.lives < 5 else self.player.lives
            self.player = Player(100, 100, self.sprite_manager, lives=new_lives)

        self.goal = Goal(GAME_WIDTH - 150, GAME_HEIGHT - 150, self.sprite_manager)
        self.guards = []
        self.walls = []

        # Bordi
        self.walls.append(pygame.Rect(0, 0, GAME_WIDTH, 20))
        self.walls.append(pygame.Rect(0, GAME_HEIGHT-20, GAME_WIDTH, 20))
        self.walls.append(pygame.Rect(0, 0, 20, GAME_HEIGHT))
        self.walls.append(pygame.Rect(GAME_WIDTH-20, 0, 20, GAME_HEIGHT))
        # Muri interni (come prima)
        self.walls += [
            pygame.Rect(200, 100, 20, 300),
            pygame.Rect(400, 200, 200, 20),
            pygame.Rect(600, 100, 20, 300),
            pygame.Rect(300, 500, 400, 20),
            pygame.Rect(150, 300, 300, 20),
            pygame.Rect(500, 400, 20, 200),
            pygame.Rect(700, 250, 20, 300),
            pygame.Rect(250, 150, 20, 200),
            pygame.Rect(350, 350, 200, 20),
            pygame.Rect(100, 450, 150, 20),
            pygame.Rect(450, 100, 20, 150),
            pygame.Rect(600, 500, 150, 20),
            pygame.Rect(800, 300, 20, 200),
            pygame.Rect(700, 150, 150, 20),
            pygame.Rect(900, 100, 20, 300),
            pygame.Rect(850, 400, 150, 20),
            pygame.Rect(300, GAME_HEIGHT - 180, 400, 20),
        ]

        # Guardie
        for i in range(min(self.level + 2, 15)):
            x = random.randint(200, GAME_WIDTH - 200)
            y = random.randint(200, GAME_HEIGHT - 200)
            path = self.generate_random_path(x, y)
            self.guards.append(Guard(
                x, y, path, self.sprite_manager,
                detection_color=random.choice(['blue','red','green','yellow','purple','black','white'])
            ))

        # Prerender sfondo e muri (performance)
        self._prerender_background()
        self._prerender_walls()

        # Pulisci effetti/pulses
        self.particle_effects = []
        self.nop_pulses = []

    def _prerender_background(self):
        self.bg_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        for y in range(0, GAME_HEIGHT, TILE_SIZE):
            for x in range(0, GAME_WIDTH, TILE_SIZE):
                if (x // TILE_SIZE + y // TILE_SIZE) % 3 == 0:
                    self.bg_surface.blit(self.sprite_manager.sprites['circuit'], (x, y))
                else:
                    self.bg_surface.blit(self.sprite_manager.sprites['floor'], (x, y))

    def _prerender_walls(self):
        self.walls_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        wall_tile = self.sprite_manager.sprites['wall']
        for wall in self.walls:
            for x in range(wall.x, wall.x + wall.width, TILE_SIZE):
                for y in range(wall.y, wall.y + wall.height, TILE_SIZE):
                    if x < GAME_WIDTH and y < GAME_HEIGHT:
                        self.walls_surface.blit(wall_tile, (x, y))

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
                if event.key == pygame.K_1:
                    effect = self.player.apply_transformation(TransformationType.SUBSTITUTION, self)
                    if effect: self.particle_effects.append(effect)
                elif event.key == pygame.K_2:
                    effect = self.player.apply_transformation(TransformationType.PERMUTATION, self)
                    if effect: self.particle_effects.append(effect)
                elif event.key == pygame.K_3:
                    effect = self.player.apply_transformation(TransformationType.NOP_INSERTION, self)
                    if effect: self.particle_effects.append(effect)
                elif event.key == pygame.K_4:
                    effect = self.player.apply_transformation(TransformationType.COMBO, self)
                    if effect: self.particle_effects.append(effect)
                elif event.key == pygame.K_5:
                    effect = self.player.apply_transformation(TransformationType.POSITION_INDEPENDENT, self)
                    if effect: self.particle_effects.append(effect)
                elif event.key == pygame.K_r:
                    self.init_level()  # Reset livello

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.player.move(dx, dy, self.walls)
        self.player.update()

        detected = False
        for guard in self.guards:
            if guard.update(self.player):
                detected = True
        self.player.detected = detected

        # Particelle (cap max per non esplodere)
        for effect in self.particle_effects[:]:
            if not effect.update():
                self.particle_effects.remove(effect)
        if len(self.particle_effects) > 100:
            self.particle_effects = self.particle_effects[-100:]

        self.goal.update()

        # NOP pulses + collisioni
        for pulse in self.nop_pulses[:]:
            alive = pulse.update(self.walls)
            hit_something = False
            for guard in self.guards:
                gx = guard.x + TILE_SIZE / 2
                gy = guard.y + TILE_SIZE / 2
                d = math.hypot(gx - pulse.x, gy - pulse.y)
                if d <= pulse.radius + TILE_SIZE * 0.5:
                    ux = (gx - pulse.x) / (d + 1e-6)
                    uy = (gy - pulse.y) / (d + 1e-6)
                    push_strength = 80
                    atten = max(0.35, 1.0 - d / (pulse.radius + TILE_SIZE * 0.5))
                    dx = ux * push_strength * atten
                    dy = uy * push_strength * atten
                    guard.x = max(20, min(GAME_WIDTH - 20 - TILE_SIZE, guard.x + dx))
                    guard.y = max(20, min(GAME_HEIGHT - 20 - TILE_SIZE, guard.y + dy))
                    guard.choicex = int(math.copysign(1, ux)) if abs(ux) > 0.2 else 0
                    guard.choicey = int(math.copysign(1, uy)) if abs(uy) > 0.2 else 0
                    guard.seconds_to_travel = 30
                    hit_something = True
            if not alive or hit_something:
                self.nop_pulses.remove(pulse)
        if len(self.nop_pulses) > 20:
            self.nop_pulses = self.nop_pulses[-20:]

        # Vittoria
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

    def draw_ui(self):
        # Sidebar destra (nera)
        sidebar_x = GAME_WIDTH
        sidebar_y = 0
        sidebar_width = SCREEN_WIDTH - GAME_WIDTH
        sidebar_height = GAME_HEIGHT
        sidebar_panel = pygame.Surface((sidebar_width, sidebar_height))
        sidebar_panel.fill(BLACK)
        self.screen.blit(sidebar_panel, (sidebar_x, sidebar_y))
        center_sidebar = sidebar_x + sidebar_width // 2

        level_text = self.font.render(f"Livello: {self.level}", True, WHITE)
        lives_text = self.font.render(f"Vite rimaste: {self.player.lives}", True, WHITE)
        self.screen.blit(level_text, (center_sidebar - level_text.get_width() // 2, 50))
        self.screen.blit(lives_text, (center_sidebar - lives_text.get_width() // 2, 50 + level_text.get_height() + 10))

        # Classifica (da cache)
        scoreboard = self.small_font.render("CLASSIFICA TOP 10", True, WHITE)
        classifica_height = (len(self.top10_cache) * 20) + scoreboard.get_height() + 10
        sidebar_center_y = sidebar_y + sidebar_height // 2
        scoreboard_y = sidebar_center_y - (classifica_height // 2) - 20
        scoreboard_x = center_sidebar - scoreboard.get_width() // 2
        self.screen.blit(scoreboard, (scoreboard_x, scoreboard_y))
        base_y = scoreboard_y + scoreboard.get_height() + 10
        for line in self.top10_cache:
            text = self.small_font.render(line, True, WHITE)
            tx = center_sidebar - text.get_width() // 2
            self.screen.blit(text, (tx, base_y))
            base_y += 20

        # Bottom bar (nera)
        bottom_sidebar_height = 40
        bottom_sidebar_y = GAME_HEIGHT
        bottom_sidebar_panel = pygame.Surface((SCREEN_WIDTH, bottom_sidebar_height))
        bottom_sidebar_panel.fill(BLACK)
        self.screen.blit(bottom_sidebar_panel, (0, bottom_sidebar_y))

        rem_transformations = self.font.render(
            f"Rimanenti - Camuffamenti: {self.player.rem_eq_transformations} | Teletrasporti: {self.player.rem_ibp_transformations} | NOP raygun: {self.player.rem_nop_transformations} | Combo: {self.player.rem_combo_transformations}",
            True, WHITE)
        rem_x = (GAME_WIDTH - rem_transformations.get_width()) // 2
        rem_y = bottom_sidebar_y + (bottom_sidebar_height - rem_transformations.get_height()) // 2
        self.screen.blit(rem_transformations, (rem_x, rem_y))

        # Istruzioni in basso a destra
        ui_panel = pygame.Surface((250, 200), pygame.SRCALPHA)
        ui_panel.fill((0, 0, 0, 180))
        self.screen.blit(ui_panel, (SCREEN_WIDTH - 200, GAME_HEIGHT - 205))
        instructions = ["WASD/Frecce: Muovi", "1: Camuffamento", "2: Teletrasporto", "3: NOP Raygun", "4: Combo", "R: Reset Livello"]
        y = GAME_HEIGHT - 180
        for instruction in instructions:
            text = self.small_font.render(instruction, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 200, y))
            y += 30

        # Info trasformazione attiva
        if self.player.transformation != TransformationType.NONE:
            trans_text = f"Trasformazione: {self.player.transformation.name}"
            timer_text = f"Tempo: {self.player.transformation_timer // 60}s"
            text1 = self.small_font.render(trans_text, True, WHITE)
            text2 = self.small_font.render(timer_text, True, WHITE)
            self.screen.blit(text1, (10, 50))
            self.screen.blit(text2, (10, 80))

        # Warning rilevato + gestione vite/game over
        if self.player.detected:
            warning = self.font.render("RILEVATO!", True, RED)
            x = GAME_WIDTH//2 - warning.get_width()//2
            pygame.draw.rect(self.screen, BLACK, (x-10, 45, warning.get_width()+20, 40))
            self.screen.blit(warning, (x, 50))
            self.player.lives -= 1
            self.player.x, self.player.y = 30, 30

            if self.player.lives <= 0:
                self.player.lives = 0
                lives_text = self.font.render(f"Vite rimaste: {self.player.lives}", True, WHITE)
                self.screen.blit(lives_text, (x, 90))
                pygame.display.flip()
                self._append_score(self.player_name, self.level)
                game_over = self.font.render("GAME OVER! Premi R per riprovare o chiudi per uscire.", True, RED)
                x_go = GAME_WIDTH//2 - game_over.get_width()//2
                pygame.draw.rect(self.screen, BLACK, (x_go-10, SCREEN_HEIGHT//2 - 30, game_over.get_width()+20, 40))
                self.screen.blit(game_over, (x_go, SCREEN_HEIGHT//2 - 20))
                pygame.display.flip()
                # loop attesa game-over limitato
                waiting = True
                while waiting and self.running:
                    self.clock.tick(FPS)  # LIMITA FPS
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            waiting = False
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                waiting = False
                                self.level = 1
                                self.init_level()

    def draw(self):
        # Sfondo prerender
        self.screen.blit(self.bg_surface, (0, 0))
        # Muri prerender
        self.screen.blit(self.walls_surface, (0, 0))

        # Coni di visione: pulisci surface e disegna tutti i coni, poi blit una volta
        self.vision_surface.fill((0, 0, 0, 0))
        for guard in self.guards:
            guard.draw_vision(self.vision_surface)
        # Blit unico dei coni di visione
        self.screen.blit(self.vision_surface, (0, 0))

        # Goal
        self.goal.draw(self.screen)

        # Guardie (sprite)
        for guard in self.guards:
            guard.draw_sprite(self.screen)

        # Player
        self.player.draw(self.screen)

        # NOP pulses
        for pulse in self.nop_pulses:
            pulse.draw(self.screen, self.tiny_font)

        # Effetti particellari
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
            self.clock.tick(FPS)  # limita il frame rate anche in-game
        pygame.quit()

# -----------------------------
# Utility per sprite esterni (opzionale)
# -----------------------------
def load_custom_sprites(sprite_manager):
    """
    Carica sprite personalizzati da /assets se presenti.
    Le dimensioni verranno adattate a TILE_SIZE e cache-izzate.
    """
    asset_path = "assets"
    if not os.path.exists(asset_path):
        os.makedirs(asset_path)
        print(f"Creata cartella '{asset_path}'. Inserisci i tuoi asset e riavvia.")
        return

    sprites_to_load = {
        'cat_blimblau': 'cat_blimblau.png',
        'cat_red': 'cat_red.png',
        'cat_green': 'cat_green.png',
        'cat_yellow': 'cat_yellow.png',
        'cat_purple': 'cat_purple.png',
        'cat_blue': 'cat_blue.png',
        'cat_black': 'cat_black.png',
        'cat_white': 'cat_white.png',
        'guard': 'guard.png',
        'wall': 'wall_tile.png',
        'floor': 'floor_tile.png',
        'goal': 'goal.png',
        'background': 'background.png'
    }

    def safe_load(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Errore caricamento {path}: {e}")
            return None

    for key, filename in sprites_to_load.items():
        path = os.path.join(asset_path, filename)
        if not os.path.exists(path):
            continue
        print(f"Caricando asset personalizzato: {path}")
        img = safe_load(path)
        if img is None:
            continue

        # Adatta dimensioni
        if key == 'goal':
            img = pygame.transform.smoothscale(img, (TILE_SIZE * 2, TILE_SIZE * 2))
        elif key == 'background':
            img = pygame.transform.smoothscale(img, (GAME_WIDTH, GAME_HEIGHT))
        else:
            img = pygame.transform.smoothscale(img, (TILE_SIZE, TILE_SIZE))

        sprite_manager.sprites[key] = img

        # Per i gatti: crea anche la versione big per il player
        # Per i gatti: crea anche la versione big per TUTTI i cat_*
        if key.startswith('cat_'):
            big = pygame.transform.smoothscale(img, (int(TILE_SIZE * sprite_manager.big_factor),
                                                     int(TILE_SIZE * sprite_manager.big_factor)))
            sprite_manager.sprites[f'{key}_big'] = big


    # Guard big
    if 'guard' in sprite_manager.sprites:
        sprite_manager.sprites['guard_big'] = pygame.transform.smoothscale(
            sprite_manager.sprites['guard'],
            (int(TILE_SIZE * sprite_manager.big_factor), int(TILE_SIZE * sprite_manager.big_factor))
        )

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    game = Game()
    load_custom_sprites(game.sprite_manager)
    print("\n=== METAMORPHIC MAZE ===")
    print("Un gioco educativo sulla sicurezza informatica")
    print("Basato su tecniche di offuscamento metamorfico\n")
    game.run()
