import pygame
import random
import sys
import os

# ============================================================
# INITIALIZATION
# ============================================================

pygame.init()

WIDTH = 700
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Car Racing - Version 3")

clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

GREEN = (35, 145, 45)
DARK_GREEN = (25, 110, 35)
ROAD = (55, 55, 55)
ROAD_DARK = (45, 45, 45)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (220, 40, 40)
BLUE = (40, 120, 240)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 20)
PURPLE = (160, 60, 220)
CYAN = (30, 200, 220)
PINK = (240, 80, 150)

GRAY = (150, 150, 150)
LIGHT_GRAY = (210, 210, 210)

DARK_RED = (150, 20, 20)
DARK_BLUE = (20, 70, 160)

# ============================================================
# FONTS
# ============================================================

font_small = pygame.font.Font(None, 28)
font = pygame.font.Font(None, 38)
font_medium = pygame.font.Font(None, 48)
font_large = pygame.font.Font(None, 65)
font_title = pygame.font.Font(None, 85)

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
# PLAYER CAR
# ============================================================

CAR_WIDTH = 58
CAR_HEIGHT = 100

player_lane = 1

player_x = LANES[player_lane] - CAR_WIDTH // 2
player_y = HEIGHT - 150

# ============================================================
# CAR TYPES
# ============================================================

car_types = [
    {
        "name": "BLUE",
        "color": BLUE,
        "price": 0,
        "speed": 8,
        "health": 100
    },

    {
        "name": "RED",
        "color": RED,
        "price": 50,
        "speed": 9,
        "health": 100
    },

    {
        "name": "PURPLE",
        "color": PURPLE,
        "price": 100,
        "speed": 10,
        "health": 120
    },

    {
        "name": "CYAN",
        "color": CYAN,
        "price": 200,
        "speed": 11,
        "health": 130
    }
]

selected_car = 0

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
# OBJECT LISTS
# ============================================================

enemies = []
coin_objects = []
obstacles = []

# ============================================================
# HIGH SCORE
# ============================================================

HIGH_SCORE_FILE = "highscore_v3.txt"


def load_high_score():

    try:

        if os.path.exists(HIGH_SCORE_FILE):

            with open(HIGH_SCORE_FILE, "r") as file:

                return int(file.read())

    except:

        pass

    return 0


def save_high_score():

    global high_score

    if score > high_score:

        high_score = score

        try:

            with open(HIGH_SCORE_FILE, "w") as file:

                file.write(str(high_score))

        except:

            pass


high_score = load_high_score()

# ============================================================
# RESET GAME
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

    player_lane = 1

    player_x = (
        LANES[player_lane]
        - CAR_WIDTH // 2
    )

    score = 0
    coins = 0

    level = 1

    health = car_types[selected_car]["health"]

    fuel = 100

    nitro = 100

    distance = 0

    enemy_speed = 6

    enemies.clear()
    coin_objects.clear()
    obstacles.clear()

    # Initial enemies

    create_enemy()
    create_enemy()


# ============================================================
# DRAW GRASS
# ============================================================


def draw_grass():

    screen.fill(GREEN)

    # Animated grass marks

    for y in range(
        -50,
        HEIGHT + 100,
        50
    ):

        current_y = (
            y + road_offset
        ) % (HEIGHT + 100) - 50

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (20, current_y),
            (70, current_y),
            3
        )

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (630, current_y),
            (680, current_y),
            3
        )


# ============================================================
# DRAW ROAD
# ============================================================


def draw_road():

    global road_offset

    draw_grass()

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

    # Road edges

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

    # Road lane lines

    road_offset += enemy_speed

    if road_offset >= 100:

        road_offset = 0

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
                y + road_offset
            )

            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x - 4,
                    current_y,
                    8,
                    50
                )
            )


# ============================================================
# DRAW PLAYER
# ============================================================


def draw_player():

    color = car_types[selected_car]["color"]

    x = player_x
    y = player_y

    # Shadow

    pygame.draw.ellipse(
        screen,
        BLACK,
        (
            x - 6,
            y + CAR_HEIGHT - 8,
            CAR_WIDTH + 12,
            20
        )
    )

    # Body

    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            CAR_WIDTH,
            CAR_HEIGHT
        ),
        border_radius=13
    )

    # Front windshield

    pygame.draw.polygon(
        screen,
        LIGHT_GRAY,
        [
            (x + 10, y + 12),
            (x + CAR_WIDTH - 10, y + 12),
            (x + CAR_WIDTH - 15, y + 38),
            (x + 15, y + 38)
        ]
    )

    # Rear window

    pygame.draw.polygon(
        screen,
        LIGHT_GRAY,
        [
            (x + 15, y + 60),
            (x + CAR_WIDTH - 15, y + 60),
            (x + CAR_WIDTH - 10, y + 80),
            (x + 10, y + 80)
        ]
    )

    # Center stripe

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x + CAR_WIDTH // 2 - 3,
            y,
            6,
            CAR_HEIGHT
        )
    )

    # Wheels

    wheel_w = 9
    wheel_h = 27

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - 5,
            y + 15,
            wheel_w,
            wheel_h
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + CAR_WIDTH - 4,
            y + 15,
            wheel_w,
            wheel_h
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - 5,
            y + 58,
            wheel_w,
            wheel_h
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + CAR_WIDTH - 4,
            y + 58,
            wheel_w,
            wheel_h
        ),
        border_radius=4
    )

    # Headlights

    pygame.draw.rect(
        screen,
        YELLOW,
        (
            x + 8,
            y + 3,
            11,
            8
        ),
        border_radius=3
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        (
            x + CAR_WIDTH - 19,
            y + 3,
            11,
            8
        ),
        border_radius=3
    )

    # Nitro flame

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and nitro > 0:

        pygame.draw.polygon(
            screen,
            ORANGE,
            [
                (x + 15, y + CAR_HEIGHT),
                (x + 28, y + CAR_HEIGHT + 35),
                (x + 38, y + CAR_HEIGHT)
            ]
        )

        pygame.draw.polygon(
            screen,
            YELLOW,
            [
                (x + 22, y + CAR_HEIGHT),
                (x + 28, y + CAR_HEIGHT + 22),
                (x + 33, y + CAR_HEIGHT)
            ]
        )


# ============================================================
# CREATE ENEMY
# ============================================================


def create_enemy():

    lane = random.randint(0, 2)

    enemy = {

        "lane": lane,

        "x": LANES[lane] - CAR_WIDTH // 2,

        "y": -CAR_HEIGHT - random.randint(
            50,
            350
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

        "speed": random.randint(
            0,
            3
        )

    }

    enemies.append(enemy)


# ============================================================
# DRAW ENEMY
# ============================================================


def draw_enemy(enemy):

    x = enemy["x"]
    y = enemy["y"]
    color = enemy["color"]

    # Shadow

    pygame.draw.ellipse(
        screen,
        BLACK,
        (
            x - 5,
            y + CAR_HEIGHT - 8,
            CAR_WIDTH + 10,
            20
        )
    )

    # Body

    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            CAR_WIDTH,
            CAR_HEIGHT
        ),
        border_radius=13
    )

    # Window

    pygame.draw.polygon(
        screen,
        LIGHT_GRAY,
        [
            (x + 10, y + 12),
            (x + CAR_WIDTH - 10, y + 12),
            (x + CAR_WIDTH - 15, y + 38),
            (x + 15, y + 38)
        ]
    )

    # Rear window

    pygame.draw.polygon(
        screen,
        LIGHT_GRAY,
        [
            (x + 15, y + 60),
            (x + CAR_WIDTH - 15, y + 60),
            (x + CAR_WIDTH - 10, y + 80),
            (x + 10, y + 80)
        ]
    )

    # Wheels

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - 5,
            y + 15,
            9,
            27
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + CAR_WIDTH - 4,
            y + 15,
            9,
            27
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x - 5,
            y + 58,
            9,
            27
        ),
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + CAR_WIDTH - 4,
            y + 58,
            9,
            27
        ),
        border_radius=4
    )


# ============================================================
# CREATE COIN
# ============================================================


def create_coin():

    lane = random.randint(0, 2)

    coin = {

        "x": LANES[lane],

        "y": -30,

        "radius": 13

    }

    coin_objects.append(coin)


# ============================================================
# DRAW COIN
# ============================================================


def draw_coin(coin):

    x = int(coin["x"])
    y = int(coin["y"])

    pygame.draw.circle(
        screen,
        YELLOW,
        (x, y),
        coin["radius"]
    )

    pygame.draw.circle(
        screen,
        ORANGE,
        (x, y),
        coin["radius"],
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
# CREATE OBSTACLE
# ============================================================


def create_obstacle():

    lane = random.randint(0, 2)

    obstacle = {

        "x": LANES[lane] - 20,

        "y": -50,

        "width": 40,

        "height": 40

    }

    obstacles.append(obstacle)


# ============================================================
# DRAW OBSTACLE
# ============================================================


def draw_obstacle(obstacle):

    x = obstacle["x"]
    y = obstacle["y"]

    # Warning triangle

    pygame.draw.polygon(
        screen,
        ORANGE,
        [
            (x, y + 40),
            (x + 20, y),
            (x + 40, y + 40)
        ]
    )

    pygame.draw.polygon(
        screen,
        YELLOW,
        [
            (x + 20, y + 8),
            (x + 33, y + 35),
            (x + 7, y + 35)
        ]
    )

    # Exclamation mark

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x + 18,
            y + 15,
            4,
            12
        )
    )

    pygame.draw.circle(
        screen,
        BLACK,
        (
            x + 20,
            y + 31
        ),
        2
    )


# ============================================================
# COLLISION DETECTION
# ============================================================


def check_collisions():

    global health
    global game_state

    player_rect = pygame.Rect(
        player_x + 6,
        player_y + 8,
        CAR_WIDTH - 12,
        CAR_HEIGHT - 16
    )

    # Enemy collision

    for enemy in enemies[:]:

        enemy_rect = pygame.Rect(
            enemy["x"] + 6,
            enemy["y"] + 8,
            CAR_WIDTH - 12,
            CAR_HEIGHT - 16
        )

        if player_rect.colliderect(
            enemy_rect
        ):

            health -= 25

            enemies.remove(enemy)

            if health <= 0:

                health = 0

                save_high_score()

                game_state = "GAME_OVER"

    # Obstacle collision

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

            obstacles.remove(obstacle)

            if health <= 0:

                health = 0

                save_high_score()

                game_state = "GAME_OVER"


# ============================================================
# COIN COLLECTION
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
            coin["x"] - coin["radius"],
            coin["y"] - coin["radius"],
            coin["radius"] * 2,
            coin["radius"] * 2
        )

        if player_rect.colliderect(
            coin_rect
        ):

            coins += 1

            score += 10

            coin_objects.remove(
                coin
            )


# ============================================================
# DRAW BAR
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

    # Background

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

    # Fill

    fill_width = int(
        width * (
            value / max_value
        )
    )

    if fill_width < 0:

        fill_width = 0

    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            fill_width,
            height
        ),
        border_radius=5
    )

    # Label

    text = font_small.render(
        label,
        True,
        WHITE
    )

    screen.blit(
        text,
        (
            x,
            y - 22
        )
    )


# ============================================================
# HUD
# ============================================================


def draw_hud():

    # Score

    score_text = font.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (15, 15)
    )

    # Coins

    coin_text = font.render(
        f"Coins: {coins}",
        True,
        YELLOW
    )

    screen.blit(
        coin_text,
        (15, 55)
    )

    # Level

    level_text = font.render(
        f"Level: {level}",
        True,
        CYAN
    )

    screen.blit(
        level_text,
        (500, 15)
    )

    # Health

    draw_bar(
        15,
        115,
        150,
        18,
        health,
        100,
        RED,
        "Health"
    )

    # Fuel

    draw_bar(
        15,
        160,
        150,
        18,
        fuel,
        100,
        ORANGE,
        "Fuel"
    )

    # Nitro

    draw_bar(
        15,
        205,
        150,
        18,
        nitro,
        100,
        CYAN,
        "Nitro"
    )


# ============================================================
# CAR SELECTION
# ============================================================


def draw_car_selection():

    screen.fill(DARK_GREEN)

    title = font_title.render(
        "SELECT CAR",
        True,
        YELLOW
    )

    screen.blit(
        title,
        (
            WIDTH // 2
            - title.get_width() // 2,
            60
        )
    )

    for i, car in enumerate(
        car_types
    ):

        x = 70 + i * 160
        y = 250

        # Card

        card_color = (
            WHITE
            if i == selected_car
            else GRAY
        )

        pygame.draw.rect(
            screen,
            card_color,
            (
                x,
                y,
                130,
                270
            ),
            border_radius=12
        )

        # Mini car

        pygame.draw.rect(
            screen,
            car["color"],
            (
                x + 38,
                y + 25,
                54,
                100
            ),
            border_radius=10
        )

        # Windows

        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            (
                x + 46,
                y + 38,
                38,
                25
            ),
            border_radius=5
        )

        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            (
                x + 46,
                y + 78,
                38,
                20
            ),
            border_radius=5
        )

        # Name

        name_text = font_small.render(
            car["name"],
            True,
            BLACK
        )

        screen.blit(
            name_text,
            (
                x + 65
                - name_text.get_width() // 2,
                y + 140
            )
        )

        # Speed

        speed_text = font_small.render(
            f"Speed: {car['speed']}",
            True,
            BLACK
        )

        screen.blit(
            speed_text,
            (
                x + 65
                - speed_text.get_width() // 2,
                y + 175
            )
        )

        # Price

        if car["price"] == 0:

            price = "FREE"

        else:

            price = f"{car['price']} coins"

        price_text = font_small.render(
            price,
            True,
            BLACK
        )

        screen.blit(
            price_text,
            (
                x + 65
                - price_text.get_width() // 2,
                y + 210
            )
        )

    instruction = font.render(
        "LEFT / RIGHT  Select     ENTER  Start",
        True,
        WHITE
    )

    screen.blit(
        instruction,
        (
            WIDTH // 2
            - instruction.get_width() // 2,
            650
        )
    )


# ============================================================
# MENU
# ============================================================


def draw_menu():

    screen.fill(DARK_GREEN)

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

    # Lane lines

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
                    x - 4,
                    y,
                    8,
                    50
                )
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
            130
        )
    )

    version = font.render(
        "VERSION 3",
        True,
        CYAN
    )

    screen.blit(
        version,
        (
            WIDTH // 2
            - version.get_width() // 2,
            220
        )
    )

    start = font_large.render(
        "PRESS ENTER",
        True,
        WHITE
    )

    screen.blit(
        start,
        (
            WIDTH // 2
            - start.get_width() // 2,
            390
        )
    )

    car_text = font.render(
        "C - Select Car",
        True,
        WHITE
    )

    screen.blit(
        car_text,
        (
            WIDTH // 2
            - car_text.get_width() // 2,
            480
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
            550
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
            620
        )
    )


# ============================================================
# PAUSE
# ============================================================


def draw_pause():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 170)
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

    text = font.render(
        "Press P to Resume",
        True,
        YELLOW
    )

    screen.blit(
        text,
        (
            WIDTH // 2
            - text.get_width() // 2,
            400
        )
    )


# ============================================================
# GAME OVER
# ============================================================


def draw_game_over():

    screen.fill(BLACK)

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
            150
        )
    )

    score_text = font_large.render(
        f"Score: {score}",
        True,
        WHITE
    )

    screen.blit(
        score_text,
        (
            WIDTH // 2
            - score_text.get_width() // 2,
            280
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
            360
        )
    )

    level_text = font.render(
        f"Level Reached: {level}",
        True,
        CYAN
    )

    screen.blit(
        level_text,
        (
            WIDTH // 2
            - level_text.get_width() // 2,
            410
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
            460
        )
    )

    restart = font.render(
        "R - Restart",
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
        "ESC - Exit",
        True,
        GRAY
    )

    screen.blit(
        exit_text,
        (
            WIDTH // 2
            - exit_text.get_width() // 2,
            610
        )
    )


# ============================================================
# GAME UPDATE
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

    keys = pygame.key.get_pressed()

    # --------------------------------------------------------
    # PLAYER MOVEMENT
    # --------------------------------------------------------

    if keys[pygame.K_LEFT]:

        if player_lane > 0:

            player_lane -= 1

            player_x = (
                LANES[player_lane]
                - CAR_WIDTH // 2
            )

            pygame.time.delay(100)

    if keys[pygame.K_RIGHT]:

        if player_lane < 2:

            player_lane += 1

            player_x = (
                LANES[player_lane]
                - CAR_WIDTH // 2
            )

            pygame.time.delay(100)

    # --------------------------------------------------------
    # NITRO
    # --------------------------------------------------------

    using_nitro = False

    if (
        keys[pygame.K_SPACE]
        and nitro > 0
    ):

        using_nitro = True

        nitro -= 0.7

        if nitro < 0:

            nitro = 0

    else:

        # Recharge slowly

        nitro += 0.12

        if nitro > 100:

            nitro = 100

    # --------------------------------------------------------
    # FUEL
    # --------------------------------------------------------

    fuel -= 0.025

    if using_nitro:

        fuel -= 0.04

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
    # DISTANCE
    # --------------------------------------------------------

    distance += current_speed * 0.05

    # --------------------------------------------------------
    # LEVEL
    # --------------------------------------------------------

    new_level = int(
        distance // 500
    ) + 1

    if new_level > level:

        level = new_level

        enemy_speed = min(
            16,
            6 + level
        )

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    score += 0.02 * current_speed

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

            enemies.remove(enemy)

            score += 5

    # Keep enemies coming

    maximum_enemies = min(
        6,
        2 + level // 2
    )

    if len(enemies) < maximum_enemies:

        if random.randint(1, 100) <= 5:

            create_enemy()

    # --------------------------------------------------------
    # COINS
    # --------------------------------------------------------

    for coin in coin_objects:

        coin["y"] += current_speed

    for coin in coin_objects[:]:

        if coin["y"] > HEIGHT:

            coin_objects.remove(coin)

    if random.randint(1, 100) <= 3:

        create_coin()

    # --------------------------------------------------------
    # OBSTACLES
    # --------------------------------------------------------

    for obstacle in obstacles:

        obstacle["y"] += current_speed

    for obstacle in obstacles[:]:

        if obstacle["y"] > HEIGHT:

            obstacles.remove(obstacle)

    if random.randint(1, 100) <= 2:

        create_obstacle()

    # --------------------------------------------------------
    # COLLISIONS
    # --------------------------------------------------------

    check_collisions()

    collect_coins()

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    draw_road()

    for coin in coin_objects:

        draw_coin(coin)

    for obstacle in obstacles:

        draw_obstacle(obstacle)

    for enemy in enemies:

        draw_enemy(enemy)

    draw_player()

    draw_hud()

    return None


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    clock.tick(60)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # ESC
            # ------------------------------------------------

            if event.key == pygame.K_ESCAPE:

                running = False

            # ------------------------------------------------
            # MENU
            # ------------------------------------------------

            if game_state == "MENU":

                if event.key == pygame.K_RETURN:

                    reset_game()

                    game_state = "PLAYING"

                elif event.key == pygame.K_c:

                    game_state = "CAR_SELECT"

            # ------------------------------------------------
            # CAR SELECTION
            # ------------------------------------------------

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

                    game_state = "PLAYING"

                    reset_game()

                elif event.key == pygame.K_ESCAPE:

                    game_state = "MENU"

            # ------------------------------------------------
            # PLAYING
            # ------------------------------------------------

            elif game_state == "PLAYING":

                if event.key == pygame.K_p:

                    game_state = "PAUSED"

            # ------------------------------------------------
            # PAUSED
            # ------------------------------------------------

            elif game_state == "PAUSED":

                if event.key == pygame.K_p:

                    game_state = "PLAYING"

            # ------------------------------------------------
            # GAME OVER
            # ------------------------------------------------

            elif game_state == "GAME_OVER":

                if event.key == pygame.K_r:

                    reset_game()

                    game_state = "PLAYING"

    # ========================================================
    # GAME STATES
    # ========================================================

    if game_state == "MENU":

        draw_menu()

        pygame.display.update()

    elif game_state == "CAR_SELECT":

        draw_car_selection()

        pygame.display.update()

    elif game_state == "PLAYING":

        result = update_game()

        if result == "GAME_OVER":

            save_high_score()

            game_state = "GAME_OVER"

        pygame.display.update()

    elif game_state == "PAUSED":

        # Draw frozen game

        draw_road()

        for coin in coin_objects:

            draw_coin(coin)

        for obstacle in obstacles:

            draw_obstacle(obstacle)

        for enemy in enemies:

            draw_enemy(enemy)

        draw_player()

        draw_hud()

        draw_pause()

        pygame.display.update()

    elif game_state == "GAME_OVER":

        draw_game_over()

        pygame.display.update()


# ============================================================
# EXIT
# ============================================================

save_high_score()

pygame.quit()

sys.exit()