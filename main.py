import pygame
import random

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 300, 600
GRID_SIZE = 30
BOARD_WIDTH, BOARD_HEIGHT = 10, 20
BOARD_OFFSET_X, BOARD_OFFSET_Y = 0, 0

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'L': (255, 165, 0),
    'J': (0, 0, 255),
    'S': (0, 255, 0),
    'Z': (255, 0, 0)
}

# Tetromino shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'L': [[1, 0], [1, 0], [1, 1]],
    'J': [[0, 1], [0, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

class Tetromino:
    def __init__(self, shape_type):
        self.type = shape_type
        self.shape = SHAPES[shape_type]
        self.color = COLORS[shape_type]
        self.x = BOARD_WIDTH // 2 - len(self.shape[0])//2
        self.y = 0

    def rotate(self, board):
        # Rotate with wall kicks
        original_shape = self.shape
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        if self.collision(0, 0, board):
            self.shape = original_shape

    def collision(self, dx, dy, board):
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    if not (0 <= new_x < BOARD_WIDTH and new_y < BOARD_HEIGHT):
                        return True
                    if new_y >= 0 and board[new_y][new_x]:
                        return True
        return False

class Tetris:
    def __init__(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.bag = []
        self.current_piece = None
        self.next_pieces = []
        self.hold_piece = None
        self.score = 0
        self.lines = 0
        self.game_over = False
        
        # Initialize bag and pieces in correct order
        self.refill_bag()
        self.next_pieces = [self.create_new_piece() for _ in range(3)]  # First create next pieces
        self.new_piece()  # Then get current piece from next_pieces

     # Add new piece to end of queue

    def refill_bag(self):
        pieces = list('IOTLJSZ')
        random.shuffle(pieces)
        self.bag.extend(pieces)

    def create_new_piece(self):
        if not self.bag:
            self.refill_bag()
        return Tetromino(self.bag.pop(0))

    def new_piece(self):
        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.create_new_piece())

    def hold(self):
        if not self.hold_piece:
            self.hold_piece = self.current_piece
            self.new_piece()
        else:
            self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
        self.current_piece.x = BOARD_WIDTH // 2 - len(self.current_piece.shape[0])//2
        self.current_piece.y = 0

    def clear_lines(self):
        lines_cleared = 0
        new_board = []
        for row in self.board:
            if 0 not in row:
                lines_cleared += 1
            else:
                new_board.append(row)
        self.board = [[0]*BOARD_WIDTH for _ in range(lines_cleared)] + new_board
        self.lines += lines_cleared
        self.score += [0, 100, 300, 500, 800][lines_cleared]

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if self.current_piece.y + y < 0:
                        self.game_over = True
                        return
                    self.board[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.new_piece()

def draw_grid(surface):
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            rect = pygame.Rect(BOARD_OFFSET_X + x*GRID_SIZE, 
                             BOARD_OFFSET_Y + y*GRID_SIZE, 
                             GRID_SIZE-1, GRID_SIZE-1)
            pygame.draw.rect(surface, WHITE, rect, 1)

def draw_board(surface, game):
    for y, row in enumerate(game.board):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, cell,
                               (BOARD_OFFSET_X + x*GRID_SIZE,
                                BOARD_OFFSET_Y + y*GRID_SIZE,
                                GRID_SIZE-1, GRID_SIZE-1))

def draw_piece(surface, piece):
    for y, row in enumerate(piece.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(surface, piece.color,
                               (BOARD_OFFSET_X + (piece.x + x)*GRID_SIZE,
                                BOARD_OFFSET_Y + (piece.y + y)*GRID_SIZE,
                                GRID_SIZE-1, GRID_SIZE-1))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Modern Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    fall_time = 0

    while not game.game_over:
        screen.fill(BLACK)
        dt = clock.tick(60)
        fall_time += dt

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not game.current_piece.collision(-1, 0, game.board):
                        game.current_piece.x -= 1
                if event.key == pygame.K_RIGHT:
                    if not game.current_piece.collision(1, 0, game.board):
                        game.current_piece.x += 1
                if event.key == pygame.K_DOWN:
                    if not game.current_piece.collision(0, 1, game.board):
                        game.current_piece.y += 1
                if event.key == pygame.K_UP:
                    game.current_piece.rotate(game.board)
                if event.key == pygame.K_c:
                    game.hold()
                if event.key == pygame.K_SPACE:
                    while not game.current_piece.collision(0, 1, game.board):
                        game.current_piece.y += 1

        # Automatic falling
        if fall_time >= 500:
            if not game.current_piece.collision(0, 1, game.board):
                game.current_piece.y += 1
                fall_time = 0
            else:
                game.lock_piece()

        # Drawing
        draw_board(screen, game)
        draw_piece(screen, game.current_piece)
        draw_grid(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()