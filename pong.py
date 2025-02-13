import pygame, random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 10
FPS = 60
TARGET_SCORE = 10  # Updated target score

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (195, 195, 195)
DARK = (50, 50 ,50)

# Score
player_score = 0
opponent_score = 0

# Screen Setup
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def move(self, left, right, screen_width):
        if left and self.rect.left > 0:
            self.rect.x -= self.speed
        if right and self.rect.right < screen_width:
            self.rect.x += self.speed
            
    def ai_move(self, ball, screen_width):
        tolerance = 10  # Allowable range of no movement
        if ball.vel_y < 0:  # Ball moving toward the top paddle
            if abs(ball.rect.centerx - self.rect.centerx) > tolerance:
                if ball.rect.centerx < self.rect.centerx and self.rect.left > 0:
                    self.rect.x -= self.speed
                elif ball.rect.centerx > self.rect.centerx and self.rect.right < screen_width:
                    self.rect.x += self.speed

    def draw(self, window, color):
        pygame.draw.rect(window, color, self.rect)

class Ball:
    def __init__(self, x, y, radius, vel_x, vel_y):
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.resetting = False
        self.reset_timer = 0
        self.reset_waiting_time = 2000  # 2 seconds waiting period

    def update(self, width, height):
        if self.resetting:
            if pygame.time.get_ticks() - self.reset_timer > self.reset_waiting_time:
                self.resetting = False
                self.vel_x = random.choice([4, -4])  # Random initial horizontal speed
                self.vel_y = random.choice([4, -4])  # Random initial vertical speed
        else:
            self.rect.x += self.vel_x
            self.rect.y += self.vel_y

            # Bounce off walls
            if self.rect.left <= 0 or self.rect.right >= width:
                self.vel_x *= -1

            # Update scores and reset on top/bottom wall collision
            global player_score, opponent_score
            if self.rect.top <= 0:  # Ball passed the top paddle
                player_score += 1
                self.reset(width // 2, height // 2)
            elif self.rect.bottom >= height:  # Ball passed the bottom paddle
                opponent_score += 1
                self.reset(width // 2, height // 2)

    def reset(self, x, y):
        self.rect.center = (x, y)
        self.resetting = True
        self.reset_timer = pygame.time.get_ticks()

    def check_collision(self, paddle):
        # Check if the ball intersects with the paddle
        if self.rect.colliderect(paddle.rect):
            # Determine the side of the paddle hit
            if abs(self.rect.bottom - paddle.rect.top) < 10 and self.vel_y > 0:  # Bottom of the ball hits the top of the paddle
                self.vel_y *= -1
                self.rect.bottom = paddle.rect.top  # Prevent the ball from "sticking"
            elif abs(self.rect.top - paddle.rect.bottom) < 10 and self.vel_y < 0:  # Top of the ball hits the bottom of the paddle
                self.vel_y *= -1
                self.rect.top = paddle.rect.bottom  # Prevent the ball from "sticking"
            elif abs(self.rect.right - paddle.rect.left) < 10 and self.vel_x > 0:  # Right side of the ball hits the left of the paddle
                self.vel_x *= -1
                self.rect.right = paddle.rect.left  # Prevent the ball from "sticking"
            elif abs(self.rect.left - paddle.rect.right) < 10 and self.vel_x < 0:  # Left side of the ball hits the right of the paddle
                self.vel_x *= -1
                self.rect.left = paddle.rect.right  # Prevent the ball from "sticking"

    def draw(self, window, color):
        pygame.draw.ellipse(window, color, self.rect)

def render_game(window, paddles, ball, colors):
    window.fill(colors["background"])  # Clear the screen
    for paddle in paddles:
        paddle.draw(window, colors["paddle"])
    ball.draw(window, colors["ball"])  # Draw the ball
    draw_scores(window, player_score, opponent_score)  # Draw the scores
    pygame.display.update()  # Update the screen

def handle_input(keys, paddle):
    left = keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT]
    paddle.move(left, right, WIDTH)

def draw_scores(window, player_score, opponent_score):
    font = pygame.font.Font(None, 90)  # Choose font and size
    player_text = font.render(f"{player_score}", True, DARK)
    opponent_text = font.render(f"{opponent_score}", True, DARK)

    # Center the scores horizontally
    player_text_rect = player_text.get_rect(center=(WIDTH // 2, HEIGHT - PADDLE_HEIGHT - 120))
    opponent_text_rect = opponent_text.get_rect(center=(WIDTH // 2, PADDLE_HEIGHT + 120))

    # Draw the scores
    window.blit(player_text, player_text_rect)
    window.blit(opponent_text, opponent_text_rect)

def check_game_over():
    # Only display winner if a player reaches the target score
    if player_score >= TARGET_SCORE:
        return "Player Wins!"
    elif opponent_score >= TARGET_SCORE:
        return "Opponent Wins!"
    return None

def display_winner(window, message, colors):
    font = pygame.font.Font(None, 100)
    text = font.render(message, True, colors["ball"])
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    window.fill(colors["background"])  # Clear the screen
    window.blit(text, text_rect)
    pygame.display.update()

    # Track when the message started
    return pygame.time.get_ticks()

# Colors dictionary
COLORS = {
    "background": BLACK,
    "paddle": GREY,
    "ball": WHITE,
}

# Create Game Objects
bottom_paddle = Paddle(WIDTH // 2 - PADDLE_WIDTH // 2 , HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT, speed=5)
top_paddle = Paddle(WIDTH // 2 - PADDLE_WIDTH // 2, 10, PADDLE_WIDTH, PADDLE_HEIGHT, speed=4)
ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS, vel_x=5, vel_y=5)

# Main Game Loop
def main():
    global player_score, opponent_score
    clock = pygame.time.Clock()
    running = True
    winner_displayed = False
    winner_time = 0

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        handle_input(keys, bottom_paddle)

        if not winner_displayed:
            # Ball and paddle logic
            ball.update(WIDTH, HEIGHT)
            ball.check_collision(bottom_paddle)
            ball.check_collision(top_paddle)
            top_paddle.ai_move(ball, WIDTH)

            # Check for a winner
            winner = check_game_over()
            if winner:
                winner_displayed = True
                winner_time = display_winner(WIN, winner, COLORS)
        else:
            # Wait before restarting
            if pygame.time.get_ticks() - winner_time > 3000:  # 3-second delay
                winner_displayed = False
                player_score = 0
                opponent_score = 0
                ball.reset(WIDTH // 2, HEIGHT // 2)
                top_paddle.rect.x = WIDTH // 2 - PADDLE_WIDTH // 2
                bottom_paddle.rect.x = WIDTH // 2 - PADDLE_WIDTH // 2

        # Render the game
        render_game(WIN, [top_paddle, bottom_paddle], ball, COLORS)

main()
pygame.quit()
