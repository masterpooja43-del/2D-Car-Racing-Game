import pygame
import random
import math
import os
import sys
import wave
import struct
import array

# ============================================================
# 2D CAR RACING GAME - VERSION 4.1
# Python + Pygame
# ============================================================

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

# ============================================================
# WINDOW
# ============================================================

WIDTH = 700
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Car Racing - Version 4.1")

clock = pygame.time.Clock()
FPS = 60

# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

ROAD = (48, 48, 52)
ROAD_LIGHT = (65, 65, 70)

GRASS = (38, 145, 48)
GRASS_DARK = (25, 110, 35)

RED = (220, 40, 45)
DARK_RED = (145, 20, 25)

BLUE = (40, 120, 235)
DARK_BLUE = (20, 65, 145)

YELLOW = (255, 215, 30)
ORANGE = (255, 140, 20)

CYAN = (30, 205, 225)
PURPLE = (160, 65, 220)
PINK = (235, 70, 150)

GREEN = (50, 210, 90)

WINDOW_COLOR = (105, 180, 220)
WINDOW_DARK = (35, 70, 95)

GRAY = (150, 150, 150)
LIGHT_GRAY = (215, 215, 215)

BROWN = (120, 75, 40)

# ============================================================
# FONTS
# ============================================================

font_tiny = pygame.font.Font(None, 22)
font_small = pygame.font.Font(None, 28)
font = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 64)
font_title = pygame.font.Font(None, 82)

# ============================================================
# ROAD
# ============================================================

ROAD_LEFT = 100
ROAD_RIGHT = 600
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

LANE_WIDTH = ROAD_WIDTH // 3

LANES = [
    ROAD_LEFT + LANE_WIDTH // 2,
    ROAD_LEFT + LANE_WIDTH + LANE_WIDTH // 2,
    ROAD_LEFT + 2 * LANE_WIDTH + LANE_WIDTH // 2
]

# ============================================================
# CAR SIZE
# ============================================================

CAR_WIDTH = 60
CAR_HEIGHT = 105

player_y = HEIGHT - 155

# ============================================================
# CAR TYPES
# ============================================================

car_types = [
    {
        "name": "SPORT",
        "color": BLUE,
        "dark": DARK_BLUE,
        "price": 0,
        "speed": 8,
        "health": 100
    },

    {
        "name": "RACER",
        "color": RED,
        "dark": DARK_RED,
        "price": 50,
        "speed": 9,
        "health": 100
    },

    {
        "name": "NEON",
        "color": PURPLE,
        "dark": (90, 25, 145),
        "price": 100,
        "speed": 10,
        "health": 115
    },

    {
        "name": "TURBO",
        "color": CYAN,
        "dark": (15, 110, 125),
        "price": 200,
        "speed": 11,
        "health": 130
    }
]

selected_car = 0

player_lane = 1
player_x = LANES[player_lane] - CAR_WIDTH // 2

# ============================================================
# GAME VARIABLES
# ============================================================

game_state = "MENU"

score = 0
coins = 0
high_score = 0

level = 1
health = 100
fuel = 100
nitro = 100

distance = 0

enemy_speed = 6

road_offset = 0

# ============================================================
# OBJECTS
# ============================================================

enemies = []
coin_objects = []
obstacles = []
particles = []
scenery = []

# ============================================================
# ANIMATION
# ============================================================

animation_time = 0
screen_shake = 0
collision_flash = 0

# ============================================================
# AUDIO
# ============================================================

AUDIO_FOLDER = "generated_audio"

os.makedirs(AUDIO_FOLDER, exist_ok=True)

def create_crash_sound(filename):
    sample_rate = 44100
    duration = 0.55
    total_samples = int(sample_rate * duration)

    frames = bytearray()

    for i in range(total_samples):

        t = i / sample_rate

        # Strong impact at the beginning
        impact = math.exp(-t * 18) * math.sin(
            2 * math.pi * 75 * t
        )

        # Metallic vibration
        metal = math.exp(-t * 9) * math.sin(
            2 * math.pi * 420 * t
        )

        # Random crash noise
        noise = random.uniform(-1, 1)

        # Noise is strongest immediately after impact
        noise_envelope = math.exp(-t * 10)

        value = (
            impact * 0.75
            + metal * 0.30
            + noise * noise_envelope * 0.45
        )

        # Quick fade-out
        fade = max(
            0,
            1 - t / duration
        )

        value *= fade

        sample = int(
            max(-1, min(1, value))
            * 32767
            * 0.75
        )

        frames.extend(
            struct.pack(
                "<h",
                sample
            )
        )

    with wave.open(filename, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)


def create_music(filename):

    """
    Creates a simple looping racing melody.
    """

    sample_rate = 44100

    notes = [
        261.63,
        329.63,
        392.00,
        329.63,
        293.66,
        349.23,
        440.00,
        349.23
    ]

    note_duration = 0.25

    total_duration = (
        len(notes)
        * note_duration
    )

    total_samples = int(
        sample_rate
        * total_duration
    )

    frames = bytearray()

    for i in range(total_samples):

        t = i / sample_rate

        note_index = int(
            t / note_duration
        )

        if note_index >= len(notes):

            note_index = len(notes) - 1

        frequency = notes[note_index]

        local_t = (
            t
            - note_index * note_duration
        )

        value = (
            math.sin(
                2
                * math.pi
                * frequency
                * local_t
            )
            * 0.13
        )

        # second harmonic

        value += (
            math.sin(
                2
                * math.pi
                * frequency
                * 2
                * local_t
            )
            * 0.04
        )

        sample = int(
            32767 * value
        )

        frames.extend(
            struct.pack(
                "<h",
                sample
            )
        )

    with wave.open(filename, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)


# Create audio files if necessary

engine_file = os.path.join(
    AUDIO_FOLDER,
    "engine.wav"
)

collision_file = os.path.join(
    AUDIO_FOLDER,
    "collision.wav"
)

coin_file = os.path.join(
    AUDIO_FOLDER,
    "coin.wav"
)

nitro_file = os.path.join(
    AUDIO_FOLDER,
    "nitro.wav"
)

music_file = os.path.join(
    AUDIO_FOLDER,
    "music.wav"
)

try:

    if not os.path.exists(engine_file):

        create_tone(
            engine_file,
            
        )

    if not os.path.exists(collision_file):

        create_tone(
            collision_file,
            90,
            0.35,
            0.6,
            "square"
        )

    if not os.path.exists(coin_file):

        create_tone(
            coin_file,
            880,
            0.15,
            0.45,
            "sine"
        )

    if not os.path.exists(nitro_file):

        create_tone(
            nitro_file,
            180,
            0.35,
            0.35,
            "sine"
        )

    if not os.path.exists(music_file):

        create_music(music_file)

except Exception as error:

    print(
        "Audio generation warning:",
        error
    )


# ============================================================
# LOAD SOUNDS
# ============================================================

engine_sound = None
collision_sound = None
coin_sound = None
nitro_sound = None

try:

    engine_sound = pygame.mixer.Sound(
        engine_file
    )

    collision_sound = pygame.mixer.Sound(
        collision_file
    )

    coin_sound = pygame.mixer.Sound(
        coin_file
    )

    nitro_sound = pygame.mixer.Sound(
        nitro_file
    )

    engine_sound.set_volume(0.18)
    collision_sound.set_volume(0.6)
    coin_sound.set_volume(0.5)
    nitro_sound.set_volume(0.35)

except Exception as error:

    print(
        "Sound loading warning:",
        error
    )


# ============================================================
# BACKGROUND MUSIC
# ============================================================

music_available = False

try:

    pygame.mixer.music.load(
        music_file
    )

    pygame.mixer.music.set_volume(
        0.18
    )

    music_available = True

except Exception as error:

    print(
        "Music loading warning:",
        error
    )


# ============================================================
# HIGH SCORE
# ============================================================

HIGH_SCORE_FILE = "highscore_v4.txt"


def load_high_score():

    try:

        if os.path.exists(
            HIGH_SCORE_FILE
        ):

            with open(
                HIGH_SCORE_FILE,
                "r"
            ) as file:

                return int(
                    file.read()
                )

    except:

        pass

    return 0


def save_high_score():

    global high_score

    if score > high_score:

        high_score = int(score)

        try:

            with open(
                HIGH_SCORE_FILE,
                "w"
            ) as file:

                file.write(
                    str(high_score)
                )

        except:

            pass


high_score = load_high_score()


# ============================================================
# RESET
# ============================================================

def reset_game():

    global player_lane
    global player_x
    global score
    global coins
    global level
    global health
    global fuel
    global nitro
    global distance
    global enemy_speed
    global road_offset
    global screen_shake
    global collision_flash

    player_lane = 1

    player_x = (
        LANES[player_lane]
        - CAR_WIDTH // 2
    )

    score = 0
    coins = 0

    level = 1

    health = car_types[
        selected_car
    ]["health"]

    fuel = 100
    nitro = 100

    distance = 0

    enemy_speed = 6

    road_offset = 0

    screen_shake = 0
    collision_flash = 0

    enemies.clear()
    coin_objects.clear()
    obstacles.clear()
    particles.clear()
    scenery.clear()

    for _ in range(6):

        create_scenery(
            random.randint(
                -HEIGHT,
                HEIGHT
            )
        )

    create_enemy()
    create_enemy()

    if music_available:

        try:

            pygame.mixer.music.play(
                -1
            )

        except:

            pass


# ============================================================
# SCENERY
# ============================================================

def create_scenery(y=None):

    side = random.choice(
        ["left", "right"]
    )

    if side == "left":

        x = random.randint(
            20,
            80
        )

    else:

        x = random.randint(
            620,
            680
        )

    if y is None:

        y = random.randint(
            -100,
            HEIGHT
        )

    scenery.append(
        {
            "x": x,
            "y": y,
            "type": random.choice(
                [
                    "tree",
                    "tree",
                    "sign",
                    "bush"
                ]
            ),
            "speed": random.uniform(
                0.8,
                1.2
            )
        }
    )


def update_scenery(speed):

    for item in scenery:

        item["y"] += (
            speed
            * item["speed"]
        )

    for item in scenery[:]:

        if item["y"] > HEIGHT + 100:

            scenery.remove(item)

            create_scenery(-80)


def draw_scenery():

    for item in scenery:

        x = int(item["x"])
        y = int(item["y"])

        if item["type"] == "tree":

            # trunk

            pygame.draw.rect(
                screen,
                BROWN,
                (
                    x - 6,
                    y + 25,
                    12,
                    35
                )
            )

            # leaves

            pygame.draw.circle(
                screen,
                GRASS_DARK,
                (
                    x,
                    y + 20
                ),
                25
            )

            pygame.draw.circle(
                screen,
                GRASS,
                (
                    x - 12,
                    y + 30
                ),
                18
            )

            pygame.draw.circle(
                screen,
                GRASS,
                (
                    x + 12,
                    y + 30
                ),
                18
            )

        elif item["type"] == "bush":

            pygame.draw.circle(
                screen,
                GRASS_DARK,
                (
                    x,
                    y + 15
                ),
                22
            )

            pygame.draw.circle(
                screen,
                GRASS,
                (
                    x + 15,
                    y + 10
                ),
                17
            )

        else:

            pygame.draw.rect(
                screen,
                GRAY,
                (
                    x - 3,
                    y + 10,
                    6,
                    35
                )
            )

            pygame.draw.rect(
                screen,
                RED,
                (
                    x - 22,
                    y - 5,
                    44,
                    25
                ),
                border_radius=4
            )


# ============================================================
# ROAD
# ============================================================

def draw_road():

    global road_offset

    screen.fill(GRASS)

    draw_scenery()

    pygame.draw.rect(
        screen,
        ROAD,
        (
            ROAD_LEFT,
            0,
            ROAD_WIDTH,
            HEIGHT
        )
    )

    # Road texture

    for y in range(
        0,
        HEIGHT,
        80
    ):

        current_y = (
            y
            + road_offset * 0.35
        ) % HEIGHT

        pygame.draw.line(
            screen,
            ROAD_LIGHT,
            (
                ROAD_LEFT + 10,
                current_y
            ),
            (
                ROAD_RIGHT - 10,
                current_y
            ),
            1
        )

    # Road borders

    pygame.draw.rect(
        screen,
        WHITE,
        (
            ROAD_LEFT,
            0,
            6,
            HEIGHT
        )
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            ROAD_RIGHT - 6,
            0,
            6,
            HEIGHT
        )
    )

    road_offset += enemy_speed

    if road_offset >= 100:

        road_offset = 0

    # Lane markings

    for lane in [1, 2]:

        x = (
            ROAD_LEFT
            + lane * LANE_WIDTH
        )

        for y in range(
            -100,
            HEIGHT + 100,
            100
        ):

            current_y = (
                y
                + road_offset
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 3,
                    current_y,
                    6,
                    48
                ),
                border_radius=2
            )


# ============================================================
# CAR DRAWING
# ============================================================

def draw_detailed_car(
    x,
    y,
    body_color,
    dark_color,
    player=False
):

    x = int(x)
    y = int(y)

    # shadow

    pygame.draw.ellipse(
        screen,
        (20, 20, 20),
        (
            x - 8,
            y + CAR_HEIGHT - 8,
            CAR_WIDTH + 16,
            18
        )
    )

    # wheels

    wheel_positions = [
        (x - 5, y + 20),
        (
            x + CAR_WIDTH - 4,
            y + 20
        ),
        (x - 5, y + 70),
        (
            x + CAR_WIDTH - 4,
            y + 70
        )
    ]

    for wx, wy in wheel_positions:

        pygame.draw.rect(
            screen,
            BLACK,
            (
                wx,
                wy,
                10,
                28
            ),
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            GRAY,
            (
                wx + 2,
                wy + 5,
                6,
                18
            ),
            border_radius=2
        )

    # main body

    pygame.draw.rect(
        screen,
        dark_color,
        (
            x + 4,
            y,
            CAR_WIDTH - 8,
            CAR_HEIGHT
        ),
        border_radius=16
    )

    pygame.draw.rect(
        screen,
        body_color,
        (
            x + 8,
            y + 4,
            CAR_WIDTH - 16,
            CAR_HEIGHT - 8
        ),
        border_radius=13
    )

    # hood

    pygame.draw.polygon(
        screen,
        body_color,
        [
            (x + 14, y + 5),
            (x + CAR_WIDTH - 14, y + 5),
            (x + CAR_WIDTH - 9, y + 35),
            (x + 9, y + 35)
        ]
    )

    # front windshield

    pygame.draw.polygon(
        screen,
        WINDOW_DARK,
        [
            (x + 13, y + 20),
            (x + CAR_WIDTH - 13, y + 20),
            (x + CAR_WIDTH - 18, y + 45),
            (x + 18, y + 45)
        ]
    )

    # windshield reflection

    pygame.draw.line(
        screen,
        WINDOW_COLOR,
        (
            x + 18,
            y + 23
        ),
        (
            x + CAR_WIDTH - 18,
            y + 23
        ),
        3
    )

    # rear window

    pygame.draw.polygon(
        screen,
        WINDOW_DARK,
        [
            (x + 18, y + 58),
            (x + CAR_WIDTH - 18, y + 58),
            (x + CAR_WIDTH - 14, y + 78),
            (x + 14, y + 78)
        ]
    )

    # center racing stripe

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + CAR_WIDTH // 2 - 3,
            y + 5,
            6,
            CAR_HEIGHT - 10
        )
    )

    # headlights

    pygame.draw.rect(
        screen,
        YELLOW,
        (
            x + 11,
            y + 5,
            13,
            8
        ),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        (
            x + CAR_WIDTH - 24,
            y + 5,
            13,
            8
        ),
        border_radius=3
    )

    # headlights glow

    pygame.draw.circle(
        screen,
        (255, 245, 150),
        (
            x + 17,
            y + 9
        ),
        3
    )

    pygame.draw.circle(
        screen,
        (255, 245, 150),
        (
            x + CAR_WIDTH - 17,
            y + 9
        ),
        3
    )

    # rear lights

    pygame.draw.rect(
        screen,
        RED,
        (
            x + 11,
            y + CAR_HEIGHT - 12,
            12,
            6
        ),
        border_radius=2
    )

    pygame.draw.rect(
        screen,
        RED,
        (
            x + CAR_WIDTH - 23,
            y + CAR_HEIGHT - 12,
            12,
            6
        ),
        border_radius=2
    )

    # spoiler

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + 8,
            y + CAR_HEIGHT - 4,
            CAR_WIDTH - 16,
            5
        ),
        border_radius=2
    )

    # player nitro flame

    if player:

        keys = pygame.key.get_pressed()

        if (
            keys[pygame.K_SPACE]
            and nitro > 0
        ):

            flame_length = random.randint(
                25,
                42
            )

            pygame.draw.polygon(
                screen,
                ORANGE,
                [
                    (
                        x + 14,
                        y + CAR_HEIGHT
                    ),
                    (
                        x + 30,
                        y
                        + CAR_HEIGHT
                        + flame_length
                    ),
                    (
                        x + 46,
                        y + CAR_HEIGHT
                    )
                ]
            )

            pygame.draw.polygon(
                screen,
                YELLOW,
                [
                    (
                        x + 22,
                        y + CAR_HEIGHT
                    ),
                    (
                        x + 30,
                        y
                        + CAR_HEIGHT
                        + flame_length
                        - 10
                    ),
                    (
                        x + 38,
                        y + CAR_HEIGHT
                    )
                ]
            )


# ============================================================
# PLAYER
# ============================================================

def draw_player():

    car = car_types[
        selected_car
    ]

    draw_detailed_car(
        player_x,
        player_y,
        car["color"],
        car["dark"],
        True
    )


# ============================================================
# ENEMIES
# ============================================================

def create_enemy():

    lane = random.randint(
        0,
        2
    )

    enemy = {
        "lane": lane,
        "x": LANES[lane]
        - CAR_WIDTH // 2,
        "y": -CAR_HEIGHT
        - random.randint(
            50,
            400
        ),
        "color": random.choice(
            [
                RED,
                ORANGE,
                PURPLE,
                CYAN,
                PINK
            ]
        ),
        "dark": DARK_RED,
        "speed": random.randint(
            0,
            3
        ),
        "design": random.randint(
            0,
            2
        )
    }

    enemies.append(
        enemy
    )


def draw_enemy(enemy):

    draw_detailed_car(
        enemy["x"],
        enemy["y"],
        enemy["color"],
        enemy["dark"],
        False
    )


# ============================================================
# COINS
# ============================================================

def create_coin():

    lane = random.randint(
        0,
        2
    )

    coin_objects.append(
        {
            "x": LANES[lane],
            "y": -30,
            "radius": 14,
            "rotation": random.randint(
                0,
                360
            )
        }
    )


def draw_coin(coin):

    x = int(
        coin["x"]
    )

    y = int(
        coin["y"]
    )

    rotation = coin[
        "rotation"
    ]

    radius = coin[
        "radius"
    ]

    width = int(
        abs(
            math.sin(
                math.radians(
                    rotation
                )
            )
        )
        * radius
        + 4
    )

    pygame.draw.ellipse(
        screen,
        YELLOW,
        (
            x - width,
            y - radius,
            width * 2,
            radius * 2
        )
    )

    pygame.draw.ellipse(
        screen,
        ORANGE,
        (
            x - width,
            y - radius,
            width * 2,
            radius * 2
        ),
        3
    )

    text = font_small.render(
        "$",
        True,
        ORANGE
    )

    screen.blit(
        text,
        (
            x - text.get_width() // 2,
            y - text.get_height() // 2
        )
    )


# ============================================================
# OBSTACLES
# ============================================================

def create_obstacle():

    lane = random.randint(
        0,
        2
    )

    obstacles.append(
        {
            "x": LANES[lane] - 22,
            "y": -55,
            "width": 44,
            "height": 44
        }
    )


def draw_obstacle(obstacle):

    x = int(
        obstacle["x"]
    )

    y = int(
        obstacle["y"]
    )

    # shadow

    pygame.draw.ellipse(
        screen,
        BLACK,
        (
            x - 5,
            y + 37,
            54,
            12
        )
    )

    # triangle

    pygame.draw.polygon(
        screen,
        ORANGE,
        [
            (x, y + 42),
            (x + 22, y),
            (x + 44, y + 42)
        ]
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (x + 22, y + 7),
            (x + 36, y + 37),
            (x + 8, y + 37)
        ]
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + 20,
            y + 15,
            5,
            13
        )
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            x + 22,
            y + 33
        ),
        2
    )


# ============================================================
# PARTICLES
# ============================================================

def create_particle(
    x,
    y,
    color
):

    particles.append(
        {
            "x": x,
            "y": y,
            "vx": random.uniform(
                -1.5,
                1.5
            ),
            "vy": random.uniform(
                1,
                4
            ),
            "life": random.randint(
                15,
                35
            ),
            "size": random.randint(
                2,
                5
            ),
            "color": color
        }
    )


def update_particles():

    for particle in particles:

        particle["x"] += (
            particle["vx"]
        )

        particle["y"] += (
            particle["vy"]
        )

        particle["life"] -= 1

    for particle in particles[:]:

        if particle["life"] <= 0:

            particles.remove(
                particle
            )


def draw_particles():

    for particle in particles:

        pygame.draw.circle(
            screen,
            particle["color"],
            (
                int(
                    particle["x"]
                ),
                int(
                    particle["y"]
                )
            ),
            particle["size"]
        )


# ============================================================
# COLLISION
# ============================================================

def check_collisions():

    global health
    global game_state
    global screen_shake
    global collision_flash

    player_rect = pygame.Rect(
        player_x + 7,
        player_y + 8,
        CAR_WIDTH - 14,
        CAR_HEIGHT - 16
    )

    for enemy in enemies[:]:

        enemy_rect = pygame.Rect(
            enemy["x"] + 7,
            enemy["y"] + 8,
            CAR_WIDTH - 14,
            CAR_HEIGHT - 16
        )

        if player_rect.colliderect(
            enemy_rect
        ):

            health -= 25

            screen_shake = 12
            collision_flash = 8

            for _ in range(20):

                create_particle(
                    player_x
                    + CAR_WIDTH // 2,
                    player_y
                    + CAR_HEIGHT // 2,
                    ORANGE
                )

            if collision_sound:

                collision_sound.play()

            enemies.remove(
                enemy
            )

            if health <= 0:

                health = 0

                save_high_score()

                game_state = "GAME_OVER"


    for obstacle in obstacles[:]:

        obstacle_rect = pygame.Rect(
            obstacle["x"],
            obstacle["y"],
            obstacle["width"],
            obstacle["height"]
        )

        if player_rect.colliderect(
            obstacle_rect
        ):

            health -= 15

            screen_shake = 8
            collision_flash = 5

            if collision_sound:

                collision_sound.play()

            obstacles.remove(
                obstacle
            )

            if health <= 0:

                health = 0

                save_high_score()

                game_state = "GAME_OVER"


# ============================================================
# COINS
# ============================================================

def collect_coins():

    global coins
    global score

    player_rect = pygame.Rect(
        player_x,
        player_y,
        CAR_WIDTH,
        CAR_HEIGHT
    )

    for coin in coin_objects[:]:

        coin_rect = pygame.Rect(
            coin["x"] - 15,
            coin["y"] - 15,
            30,
            30
        )

        if player_rect.colliderect(
            coin_rect
        ):

            coins += 1
            score += 10

            if coin_sound:

                coin_sound.play()

            for _ in range(8):

                create_particle(
                    coin["x"],
                    coin["y"],
                    YELLOW
                )

            coin_objects.remove(
                coin
            )


# ============================================================
# BARS
# ============================================================

def draw_bar(
    x,
    y,
    width,
    height,
    value,
    max_value,
    color,
    label
):

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x,
            y,
            width,
            height
        ),
        border_radius=5
    )

    fill = int(
        width
        * max(
            0,
            value / max_value
        )
    )

    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            fill,
            height
        ),
        border_radius=5
    )

    text = font_tiny.render(
        label,
        True,
        WHITE
    )

    screen.blit(
        text,
        (
            x,
            y - 19
        )
    )


# ============================================================
# HUD
# ============================================================

def draw_hud():

    score_text = font.render(
        f"Score: {int(score)}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (15, 12)
    )

    coin_text = font.render(
        f"Coins: {coins}",
        True,
        YELLOW
    )

    screen.blit(
        coin_text,
        (15, 48)
    )

    level_text = font.render(
        f"Level: {level}",
        True,
        CYAN
    )

    screen.blit(
        level_text,
        (
            500,
            12
        )
    )

    draw_bar(
        15,
        105,
        155,
        17,
        health,
        100,
        RED,
        "HEALTH"
    )

    draw_bar(
        15,
        150,
        155,
        17,
        fuel,
        100,
        ORANGE,
        "FUEL"
    )

    draw_bar(
        15,
        195,
        155,
        17,
        nitro,
        100,
        CYAN,
        "NITRO"
    )

    # Nitro instruction

    nitro_text = font_tiny.render(
        "SPACE = NITRO",
        True,
        WHITE
    )

    screen.blit(
        nitro_text,
        (
            WIDTH - 145,
            65
        )
    )


# ============================================================
# UPDATE GAME
# ============================================================

def update_game():

    global player_lane
    global player_x
    global fuel
    global nitro
    global score
    global level
    global distance
    global enemy_speed
    global screen_shake
    global collision_flash

    keys = pygame.key.get_pressed()

    # --------------------------------------------------------
    # MOVEMENT
    # --------------------------------------------------------

    if keys[pygame.K_LEFT]:

        if player_lane > 0:

            player_lane -= 1

            player_x = (
                LANES[player_lane]
                - CAR_WIDTH // 2
            )

            pygame.time.delay(80)

    if keys[pygame.K_RIGHT]:

        if player_lane < 2:

            player_lane += 1

            player_x = (
                LANES[player_lane]
                - CAR_WIDTH // 2
            )

            pygame.time.delay(80)

    # --------------------------------------------------------
    # NITRO
    # --------------------------------------------------------

    using_nitro = (
        keys[pygame.K_SPACE]
        and nitro > 0
    )

    if using_nitro:

        nitro -= 0.75

        if nitro < 0:

            nitro = 0

        if random.randint(
            1,
            3
        ) == 1:

            create_particle(
                player_x
                + CAR_WIDTH // 2,
                player_y
                + CAR_HEIGHT,
                random.choice(
                    [
                        ORANGE,
                        YELLOW,
                        CYAN
                    ]
                )
            )

    else:

        nitro += 0.10

        if nitro > 100:

            nitro = 100

    # --------------------------------------------------------
    # NITRO SOUND
    # --------------------------------------------------------

    if (
        using_nitro
        and nitro_sound
    ):

        if random.randint(
            1,
            20
        ) == 1:

            nitro_sound.play()

    # --------------------------------------------------------
    # FUEL
    # --------------------------------------------------------

    fuel -= 0.025

    if using_nitro:

        fuel -= 0.035

    if fuel <= 0:

        fuel = 0

        save_high_score()

        return "GAME_OVER"

    # --------------------------------------------------------
    # SPEED
    # --------------------------------------------------------

    current_speed = enemy_speed

    if using_nitro:

        current_speed += 8

    # --------------------------------------------------------
    # ENGINE SOUND
    # --------------------------------------------------------

    if engine_sound:

        engine_sound.set_volume(
            min(
                0.28,
                0.12
                + current_speed / 60
            )
        )

        if engine_sound.get_num_channels() == 0:

            engine_sound.play(
                loops=-1
            )

    # --------------------------------------------------------
    # DISTANCE
    # --------------------------------------------------------

    distance += (
        current_speed * 0.05
    )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score += (
        0.025 * current_speed
    )

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    new_level = (
        int(
            distance // 500
        )
        + 1
    )

    if new_level > level:

        level = new_level

        enemy_speed = min(
            18,
            6 + level
        )

    # --------------------------------------------------------
    # ENEMIES
    # --------------------------------------------------------

    for enemy in enemies:

        enemy["y"] += (
            current_speed
            + enemy["speed"]
        )

    for enemy in enemies[:]:

        if enemy["y"] > HEIGHT:

            enemies.remove(
                enemy
            )

            score += 5

    maximum_enemies = min(
        7,
        2 + level // 2
    )

    if len(enemies) < maximum_enemies:

        if random.randint(
            1,
            100
        ) <= 5:

            create_enemy()

    # --------------------------------------------------------
    # COINS
    # --------------------------------------------------------

    for coin in coin_objects:

        coin["y"] += current_speed

        coin["rotation"] += 8

    for coin in coin_objects[:]:

        if coin["y"] > HEIGHT:

            coin_objects.remove(
                coin
            )

    if random.randint(
        1,
        100
    ) <= 3:

        create_coin()

    # --------------------------------------------------------
    # OBSTACLES
    # --------------------------------------------------------

    for obstacle in obstacles:

        obstacle["y"] += current_speed

    for obstacle in obstacles[:]:

        if obstacle["y"] > HEIGHT:

            obstacles.remove(
                obstacle
            )

    if random.randint(
        1,
        100
    ) <= 2:

        create_obstacle()

    # --------------------------------------------------------
    # SCENERY
    # --------------------------------------------------------

    update_scenery(
        current_speed
    )

    # --------------------------------------------------------
    # PARTICLES
    # --------------------------------------------------------

    if random.randint(
        1,
        2
    ) == 1:

        create_particle(
            player_x + 10,
            player_y + CAR_HEIGHT,
            (130, 130, 130)
        )

    if random.randint(
        1,
        2
    ) == 1:

        create_particle(
            player_x + CAR_WIDTH - 10,
            player_y + CAR_HEIGHT,
            (130, 130, 130)
        )

    update_particles()

    # --------------------------------------------------------
    # COLLISIONS
    # --------------------------------------------------------

    check_collisions()

    collect_coins()

    # --------------------------------------------------------
    # SCREEN SHAKE
    # --------------------------------------------------------

    if screen_shake > 0:

        screen_shake -= 1

    if collision_flash > 0:

        collision_flash -= 1

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    draw_road()

    for coin in coin_objects:

        draw_coin(coin)

    for obstacle in obstacles:

        draw_obstacle(
            obstacle
        )

    for enemy in enemies:

        draw_enemy(enemy)

    draw_particles()

    draw_player()

    draw_hud()

    # --------------------------------------------------------
    # COLLISION FLASH
    # --------------------------------------------------------

    if collision_flash > 0:

        flash = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        flash.fill(
            (
                255,
                40,
                40,
                70
            )
        )

        screen.blit(
            flash,
            (0, 0)
        )

    return None


# ============================================================
# CAR SELECTION SCREEN
# ============================================================

def draw_car_selection():

    screen.fill(
        (20, 70, 30)
    )

    title = font_title.render(
        "SELECT YOUR CAR",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            55
        )
    )

    for i, car in enumerate(
        car_types
    ):

        x = 40 + i * 165
        y = 200

        if i == selected_car:

            border = YELLOW

            border_width = 5

        else:

            border = GRAY

            border_width = 2

        pygame.draw.rect(
            screen,
            (235, 235, 235),
            (
                x,
                y,
                145,
                310
            ),
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            border,
            (
                x,
                y,
                145,
                310
            ),
            border_width,
            border_radius=12
        )

        # Mini car

        draw_detailed_car(
            x + 43,
            y + 20,
            car["color"],
            car["dark"],
            False
        )

        # Name

        name = font_small.render(
            car["name"],
            True,
            BLACK
        )

        screen.blit(
            name,
            (
                x
                + 72
                - name.get_width() // 2,
                y + 140
            )
        )

        speed = font_tiny.render(
            f"Speed: {car['speed']}",
            True,
            BLACK
        )

        screen.blit(
            speed,
            (
                x
                + 72
                - speed.get_width() // 2,
                y + 175
            )
        )

        hp = font_tiny.render(
            f"Health: {car['health']}",
            True,
            BLACK
        )

        screen.blit(
            hp,
            (
                x
                + 72
                - hp.get_width() // 2,
                y + 205
            )
        )

        if car["price"] == 0:

            price_text = "FREE"

        else:

            price_text = (
                f"{car['price']} coins"
            )

        price = font_small.render(
            price_text,
            True,
            ORANGE
        )

        screen.blit(
            price,
            (
                x
                + 72
                - price.get_width() // 2,
                y + 245
            )
        )

    instruction = font.render(
        "LEFT / RIGHT = Select    ENTER = Start",
        True,
        WHITE
    )

    screen.blit(
        instruction,
        (
            WIDTH // 2
            - instruction.get_width() // 2,
            570
        )
    )

    back = font_small.render(
        "ESC = Back",
        True,
        LIGHT_GRAY
    )

    screen.blit(
        back,
        (
            WIDTH // 2
            - back.get_width() // 2,
            625
        )
    )


# ============================================================
# MENU
# ============================================================

def draw_menu():

    screen.fill(
        (20, 100, 35)
    )

    # Road

    pygame.draw.rect(
        screen,
        ROAD,
        (
            ROAD_LEFT,
            0,
            ROAD_WIDTH,
            HEIGHT
        )
    )

    for lane in [1, 2]:

        x = (
            ROAD_LEFT
            + lane * LANE_WIDTH
        )

        for y in range(
            0,
            HEIGHT,
            100
        ):

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 3,
                    y,
                    6,
                    50
                )
            )

    # Decorative cars

    draw_detailed_car(
        170,
        510,
        RED,
        DARK_RED
    )

    draw_detailed_car(
        470,
        510,
        BLUE,
        DARK_BLUE
    )

    title = font_title.render(
        "CAR RACING",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            90
        )
    )

    version = font_medium.render(
        "VERSION 4.1",
        True,
        CYAN
    )

    screen.blit(
        version,
        (
            WIDTH // 2
            - version.get_width() // 2,
            180
        )
    )

    start = font_large.render(
        "PRESS ENTER",
        True,
        WHITE
    )

    # Blink animation

    if (
        animation_time // 30
    ) % 2 == 0:

        screen.blit(
            start,
            (
                WIDTH // 2
                - start.get_width() // 2,
                300
            )
        )

    car = font.render(
        "C - Select Car",
        True,
        WHITE
    )

    screen.blit(
        car,
        (
            WIDTH // 2
            - car.get_width() // 2,
            390
        )
    )

    controls = font_small.render(
        "Arrow Keys = Drive    SPACE = Nitro    P = Pause",
        True,
        WHITE
    )

    screen.blit(
        controls,
        (
            WIDTH // 2
            - controls.get_width() // 2,
            430
        )
    )

    high = font.render(
        f"High Score: {high_score}",
        True,
        YELLOW
    )

    screen.blit(
        high,
        (
            WIDTH // 2
            - high.get_width() // 2,
            670
        )
    )


# ============================================================
# PAUSE
# ============================================================

def draw_pause():

    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT
        ),
        pygame.SRCALPHA
    )

    overlay.fill(
        (
            0,
            0,
            0,
            175
        )
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    title = font_title.render(
        "PAUSED",
        True,
        WHITE
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            280
        )
    )

    text = font_medium.render(
        "Press P to Resume",
        True,
        YELLOW
    )

    screen.blit(
        text,
        (
            WIDTH // 2
            - text.get_width() // 2,
            390
        )
    )


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    screen.fill(
        (15, 15, 20)
    )

    title = font_title.render(
        "GAME OVER",
        True,
        RED
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            130
        )
    )

    score_text = font_large.render(
        f"Score: {int(score)}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            WIDTH // 2
            - score_text.get_width() // 2,
            270
        )
    )

    coins_text = font.render(
        f"Coins: {coins}",
        True,
        YELLOW
    )

    screen.blit(
        coins_text,
        (
            WIDTH // 2
            - coins_text.get_width() // 2,
            350
        )
    )

    level_text = font.render(
        f"Level: {level}",
        True,
        CYAN
    )

    screen.blit(
        level_text,
        (
            WIDTH // 2
            - level_text.get_width() // 2,
            400
        )
    )

    high_text = font.render(
        f"High Score: {high_score}",
        True,
        YELLOW
    )

    screen.blit(
        high_text,
        (
            WIDTH // 2
            - high_text.get_width() // 2,
            450
        )
    )

    restart = font_medium.render(
        "R - RESTART",
        True,
        WHITE
    )

    screen.blit(
        restart,
        (
            WIDTH // 2
            - restart.get_width() // 2,
            550
        )
    )

    exit_text = font_small.render(
        "ESC - EXIT",
        True,
        GRAY
    )

    screen.blit(
        exit_text,
        (
            WIDTH // 2
            - exit_text.get_width() // 2,
            620
        )
    )


# ============================================================
# EVENT LOOP
# ============================================================

running = True

while running:

    clock.tick(FPS)

    animation_time += 1

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # ESC

            if event.key == pygame.K_ESCAPE:

                if game_state in [
                    "PLAYING",
                    "PAUSED"
                ]:

                    save_high_score()

                    game_state = "MENU"

                    if engine_sound:

                        engine_sound.stop()

                    if music_available:

                        pygame.mixer.music.stop()

                else:

                    running = False

            # =================================================
            # MENU
            # =================================================

            if game_state == "MENU":

                if event.key == pygame.K_RETURN:

                    reset_game()

                    game_state = "PLAYING"

                elif event.key == pygame.K_c:

                    game_state = "CAR_SELECT"

            # =================================================
            # CAR SELECT
            # =================================================

            elif game_state == "CAR_SELECT":

                if event.key == pygame.K_LEFT:

                    selected_car -= 1

                    if selected_car < 0:

                        selected_car = (
                            len(car_types) - 1
                        )

                elif event.key == pygame.K_RIGHT:

                    selected_car += 1

                    if selected_car >= len(
                        car_types
                    ):

                        selected_car = 0

                elif event.key == pygame.K_RETURN:

                    reset_game()

                    game_state = "PLAYING"

                elif event.key == pygame.K_ESCAPE:

                    game_state = "MENU"

            # =================================================
            # PLAYING
            # =================================================

            elif game_state == "PLAYING":

                if event.key == pygame.K_p:

                    game_state = "PAUSED"

                    if engine_sound:

                        engine_sound.stop()

            # =================================================
            # PAUSED
            # =================================================

            elif game_state == "PAUSED":

                if event.key == pygame.K_p:

                    game_state = "PLAYING"

            # =================================================
            # GAME OVER
            # =================================================

            elif game_state == "GAME_OVER":

                if event.key == pygame.K_r:

                    reset_game()

                    game_state = "PLAYING"

    # ========================================================
    # STATES
    # ========================================================

    if game_state == "MENU":

        if engine_sound:

            engine_sound.stop()

        draw_menu()

        pygame.display.flip()

    elif game_state == "CAR_SELECT":

        if engine_sound:

            engine_sound.stop()

        draw_car_selection()

        pygame.display.flip()

    elif game_state == "PLAYING":

        result = update_game()

        if result == "GAME_OVER":

            save_high_score()

            if engine_sound:

                engine_sound.stop()

            if music_available:

                pygame.mixer.music.stop()

            game_state = "GAME_OVER"

        pygame.display.flip()

    elif game_state == "PAUSED":

        draw_road()

        for coin in coin_objects:

            draw_coin(coin)

        for obstacle in obstacles:

            draw_obstacle(
                obstacle
            )

        for enemy in enemies:

            draw_enemy(enemy)

        draw_particles()

        draw_player()

        draw_hud()

        draw_pause()

        pygame.display.flip()

    elif game_state == "GAME_OVER":

        if engine_sound:

            engine_sound.stop()

        draw_game_over()

        pygame.display.flip()


# ============================================================
# EXIT
# ============================================================

save_high_score()

if engine_sound:

    engine_sound.stop()

if music_available:

    pygame.mixer.music.stop()

pygame.quit()

sys.exit()
