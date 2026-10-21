
import pygame
import random
import os

# -------------------- INITIALIZE --------------------

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

START_DELAY = 150
MIN_DELAY = 50
SPEED_INCREASE = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Snake Game")

clock = pygame.time.Clock()

# -------------------- COLORS --------------------

BACKGROUND = (20, 25, 40)
GREEN = (50, 220, 125)
BODY_GREEN = (35, 170, 100)
RED = (255, 70, 80)
WHITE = (255, 255, 255)

# -------------------- FONTS --------------------

font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 18)
title_font = pygame.font.SysFont("Arial", 48)

# -------------------- LOAD HIGH SCORE --------------------

HIGH_SCORE_FILE = "highscore.txt"

try:
    with open(HIGH_SCORE_FILE, "r") as file:
        high_score = int(file.read())
except (FileNotFoundError, ValueError):
    high_score = 0

# -------------------- SNAKE --------------------

def create_snake():
    return [
        [100, 100],
        [80, 100],
        [60, 100]
    ]


snake = create_snake()

dx = CELL_SIZE
dy = 0

# -------------------- FOOD --------------------

def create_food(snake):
    empty_cells = [
        [x, y]
        for x in range(0, WIDTH, CELL_SIZE)
        for y in range(0, HEIGHT, CELL_SIZE)
        if [x, y] not in snake
    ]

    if empty_cells:
        return random.choice(empty_cells)

    return None


food = create_food(snake)

# -------------------- SCORE AND SPEED --------------------

score = 0
MOVE_DELAY = START_DELAY
move_timer = 0

# -------------------- GAME STATES --------------------

running = True
started = False
paused = False
game_over = False
won = False


# -------------------- RESTART GAME --------------------

def restart_game():
    global snake, dx, dy, food
    global score, MOVE_DELAY, move_timer
    global started, paused, game_over, won

    snake = create_snake()

    dx = CELL_SIZE
    dy = 0

    food = create_food(snake)

    score = 0
    MOVE_DELAY = START_DELAY
    move_timer = 0

    started = True
    paused = False
    game_over = False
    won = False


# -------------------- MAIN GAME LOOP --------------------

while running:

    elapsed = clock.tick(60)
    move_timer += elapsed

    # Handle events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            # Start game
            if not started and event.key == pygame.K_RETURN:
                started = True
                move_timer = 0

            # Restart after Game Over
            elif game_over and event.key == pygame.K_r:
                restart_game()

            # Pause or resume
            elif (
                started
                and not game_over
                and event.key == pygame.K_SPACE
            ):
                paused = not paused
                move_timer = 0

            # Control snake
            elif started and not game_over and not paused:

                if event.key == pygame.K_RIGHT and dx == 0:
                    dx = CELL_SIZE
                    dy = 0

                elif event.key == pygame.K_LEFT and dx == 0:
                    dx = -CELL_SIZE
                    dy = 0

                elif event.key == pygame.K_UP and dy == 0:
                    dx = 0
                    dy = -CELL_SIZE

                elif event.key == pygame.K_DOWN and dy == 0:
                    dx = 0
                    dy = CELL_SIZE

    # -------------------- MOVE SNAKE --------------------

    if (
        started
        and not paused
        and not game_over
        and move_timer >= MOVE_DELAY
    ):

        new_head = [
            snake[0][0] + dx,
            snake[0][1] + dy
        ]

        # Wall collision
        if (
            new_head[0] < 0
            or new_head[0] >= WIDTH
            or new_head[1] < 0
            or new_head[1] >= HEIGHT
        ):
            game_over = True

        else:

            # Check food collision
            ate_food = (
                food is not None
                and new_head == food
            )

            # Add new head
            snake.insert(0, new_head)

            if ate_food:
                score += 1

                # Update and save high score
                if score > high_score:
                    high_score = score

                    with open(HIGH_SCORE_FILE, "w") as file:
                        file.write(str(high_score))

                # Increase speed
                MOVE_DELAY = max(
                    MIN_DELAY,
                    START_DELAY - score * SPEED_INCREASE
                )

                # Generate new food
                food = create_food(snake)

                # Win if the board is full
                if food is None:
                    won = True
                    game_over = True

            else:
                # Remove tail during normal movement
                snake.pop()

            # Check collision with own body
            if new_head in snake[1:]:
                game_over = True

        move_timer = 0

    # -------------------- DRAW BACKGROUND --------------------

    screen.fill(BACKGROUND)

    # -------------------- DRAW FOOD --------------------

    if food is not None:
        pygame.draw.rect(
            screen,
            RED,
            (food[0], food[1], CELL_SIZE, CELL_SIZE),
            border_radius=4
        )

    # -------------------- DRAW SNAKE --------------------

    for index, segment in enumerate(snake):

        color = GREEN if index == 0 else BODY_GREEN

        pygame.draw.rect(
            screen,
            color,
            (
                segment[0],
                segment[1],
                CELL_SIZE,
                CELL_SIZE
            ),
            border_radius=4
        )

    # -------------------- CURRENT SCORE AND SPEED --------------------

    score_text = font.render(
        f"Score: {score}", True, WHITE
    )
    screen.blit(score_text, (10, 10))

    speed_text = small_font.render(
        f"Speed: {round(1000 / MOVE_DELAY, 1)} moves/sec",
        True,
        WHITE
    )
    screen.blit(speed_text, (10, 48))

    # -------------------- START SCREEN --------------------

    if not started:

        title_text = title_font.render(
            "SNAKE GAME", True, GREEN
        )

        instruction_text = font.render(
            "Press ENTER to Start", True, WHITE
        )

        screen.blit(
            title_text,
            (
                WIDTH // 2 - title_text.get_width() // 2,
                HEIGHT // 2 - 60
            )
        )

        screen.blit(
            instruction_text,
            (
                WIDTH // 2 - instruction_text.get_width() // 2,
                HEIGHT // 2 + 10
            )
        )

    # -------------------- PAUSE SCREEN --------------------

    elif paused and not game_over:

        pause_text = title_font.render(
            "PAUSED", True, WHITE
        )

        resume_text = font.render(
            "Press SPACE to Resume", True, GREEN
        )

        screen.blit(
            pause_text,
            (
                WIDTH // 2 - pause_text.get_width() // 2,
                HEIGHT // 2 - 40
            )
        )

        screen.blit(
            resume_text,
            (
                WIDTH // 2 - resume_text.get_width() // 2,
                HEIGHT // 2 + 20
            )
        )

    # -------------------- GAME OVER SCREEN --------------------

    if game_over:

        message = "YOU WIN!" if won else "GAME OVER!"

        over_text = title_font.render(
            message,
            True,
            GREEN if won else RED
        )

        high_score_text = font.render(
            f"High Score: {high_score}",
            True,
            WHITE
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            WHITE
        )

        # Center the Game Over message
        screen.blit(
            over_text,
            (
                WIDTH // 2 - over_text.get_width() // 2,
                HEIGHT // 2 - 80
            )
        )

        # Display high score only after Game Over
        screen.blit(
            high_score_text,
            (
                WIDTH // 2 - high_score_text.get_width() // 2,
                HEIGHT // 2 - 20
            )
        )

        screen.blit(
            restart_text,
            (
                WIDTH // 2 - restart_text.get_width() // 2,
                HEIGHT // 2 + 35
            )
        )

    pygame.display.update()

# -------------------- QUIT --------------------

pygame.quit()
