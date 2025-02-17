import chess
import chess.engine
import pygame
import time

# Initialize Pygame
pygame.init()
width, height = 600, 600
square_size = width // 8
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Chess AI")

# Load Stockfish Engine
engine = chess.engine.SimpleEngine.popen_uci(r"C:\Users\Matrix\Desktop\chess_py\stockfish\stockfish-windows-x86-64.exe")

# Chess Board Setup
game = chess.Board()

# Colors
WHITE = (238, 238, 210)
BLACK = (118, 150, 86)
HIGHLIGHT = (186, 202, 68)

# Load Piece Images
piece_images = {}
pieces = ['p', 'r', 'n', 'b', 'q', 'k']
colors = ['w', 'b']
for color in colors:
    for piece in pieces:
        piece_images[color + piece] = pygame.transform.scale(
            pygame.image.load(f"{color}{piece}.png"), (square_size, square_size)
        )

# Choose Player Color
player_color = None
flip_board = False
selected_square = None
highlight_moves = []

def choose_color():
    global player_color, flip_board
    font = pygame.font.Font(None, 60)
    white_text = font.render("Play as White", True, (0, 0, 0))
    black_text = font.render("Play as Black", True, (255, 255, 255))

    while player_color is None:
        screen.fill((150, 150, 150))
        pygame.draw.rect(screen, WHITE, (150, 200, 300, 100))
        pygame.draw.rect(screen, BLACK, (150, 350, 300, 100))
        screen.blit(white_text, (180, 230))
        screen.blit(black_text, (180, 380))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 150 <= x <= 450 and 200 <= y <= 300:
                    player_color = chess.WHITE
                elif 150 <= x <= 450 and 350 <= y <= 450:
                    player_color = chess.BLACK
                    flip_board = True

choose_color()

# AI plays first if user chose black
if player_color == chess.BLACK:
    ai_move = engine.play(game, chess.engine.Limit(depth=5))
    game.push(ai_move.move)

# Get legal moves for a square
def get_legal_moves(square):
    moves = []
    for move in game.legal_moves:
        if move.from_square == square:
            to_square = move.to_square
            row, col = divmod(to_square, 8)
            row = 7 - row
            if flip_board:
                row = 7 - row
                col = 7 - col
            moves.append((row, col))
    return moves

# Draw Chess Board
def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            if (row, col) in highlight_moves:
                color = HIGHLIGHT
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

# Draw Pieces
def draw_pieces():
    for square in chess.SQUARES:
        piece = game.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            row = 7 - row
            if flip_board:
                row = 7 - row
                col = 7 - col
            piece_key = ('b' if piece.color == chess.BLACK else 'w') + piece.symbol().lower()
            piece_image = piece_images.get(piece_key, None)
            if piece_image:
                screen.blit(piece_image, (col * square_size, row * square_size))

# Show Result Text
def show_result_text(text):
    font = pygame.font.Font(None, 60)
    text_surface = font.render(text, True, (255, 0, 0))
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))
    
    # Draw the text
    screen.blit(text_surface, text_rect)
    
    #pygame.display.flip()
    
    # Wait for a few seconds before closing
    time.sleep(15)
    return True  # Exit the game

# Main Loop
running = True
while running:
    screen.fill((0, 0, 0))

    # Check for game over
    if game.is_checkmate():
        winner = "Black Wins!" if game.turn == chess.WHITE else "White Wins!"
        if show_result_text(winner):
            running = False
        continue

    if game.is_stalemate() or game.is_insufficient_material():
        if show_result_text("Draw!"):
            running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            col, row = x // square_size, y // square_size

            if flip_board:
                col, row = 7 - col, 7 - row

            square = chess.square(col, 7 - row)

            if selected_square is None:
                if game.piece_at(square) and game.piece_at(square).color == player_color:
                    selected_square = square
                    highlight_moves = get_legal_moves(square)
            else:
                if square == selected_square:
                    selected_square = None
                    highlight_moves = []
                else:
                    move = chess.Move(selected_square, square)
                    if move in game.legal_moves:
                        game.push(move)
                        selected_square = None
                        highlight_moves = []

                        if not game.is_game_over():
                            ai_move = engine.play(game, chess.engine.Limit(depth=5))
                            game.push(ai_move.move)
                    else:
                        if game.piece_at(square) and game.piece_at(square).color == player_color:
                            selected_square = square
                            highlight_moves = get_legal_moves(square)

    draw_board()
    draw_pieces()
    pygame.display.flip()

engine.quit()
pygame.quit()