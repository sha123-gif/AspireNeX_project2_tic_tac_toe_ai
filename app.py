from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

# Initial board state (empty)
board = [' '] * 9
current_player = 'X' #user player sign
ai_player = 'O'  # AI player sign is 'O'

# Helper function to check if a player has won
def check_win(board, player):
    winning_positions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    for positions in winning_positions:
        if all(board[pos] == player for pos in positions):
            return True
    return False

# Helper function to check if the board is full (draw)
def check_draw(board):
    return ' ' not in board

# Minimax algorithm with Alpha-Beta Pruning
def minimax(board, depth, maximizing_player, alpha, beta):
    # Base cases: terminal states
    if check_win(board, ai_player):
        return 10 - depth # winning situation for user or ai player 
    elif check_win(board, current_player):
        return depth - 10 #loosing condition for ai player or user player 
    elif check_draw(board):
        return 0 # draw condition between the ai player and the user 

    if maximizing_player:
        max_eval = -math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = ai_player
                eval = minimax(board, depth + 1, False, alpha, beta)
                board[i] = ' '
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
        min_eval = math.inf
        for i in range(9):
            if board[i] == ' ':
                board[i] = current_player
                eval = minimax(board, depth + 1, True, alpha, beta)
                board[i] = ' '
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
        return min_eval

# Function to get optimal move using Minimax algorithm with Alpha-Beta Pruning
def get_optimal_move(board):
    best_move = -1
    best_eval = -math.inf
    alpha = -math.inf
    beta = math.inf

    for i in range(9):
        if board[i] == ' ':
            board[i] = ai_player
            eval = minimax(board, 0, False, alpha, beta)
            board[i] = ' '
            if eval > best_eval:
                best_eval = eval
                best_move = i
    return best_move

# Flask route for serving index.html and for handling the complete application procedures 
@app.route('/')
def index():
    board = [' '] * 9  # Replace with actual board data if needed when the game restarts
    return render_template('index.html', board=board)

# Flask route for making a move and then initating the condition according to the procedure
@app.route('/move', methods=['POST'])
def make_move():
    global board, current_player

    # Get position from POST request
    data = request.get_json()
    position = data['position']

    # Check if the move is valid
    if board[position] == ' ':
        board[position] = current_player

        # Check game status
        if check_win(board, current_player):
            return jsonify({'status': 'win', 'winner': current_player, 'board': board})
        elif check_draw(board):
            return jsonify({'status': 'draw', 'board': board})
        else:
            # AI makes a move and then checks whether the user is going to win or lose 
            ai_move = get_optimal_move(board)
            board[ai_move] = ai_player

            # Check game status after AI move
            if check_win(board, ai_player):
                return jsonify({'status': 'win', 'winner': ai_player, 'board': board})
            elif check_draw(board):
                return jsonify({'status': 'draw', 'board': board})
            else:
                return jsonify({'status': 'success', 'board': board})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid move'})

# Flask route for resetting the game
@app.route('/reset', methods=['POST'])
def reset_game():
    global board, current_player
    board = [' '] * 9
    current_player = 'X'
    return jsonify({'status': 'success', 'board': board})

if __name__ == '__main__':
    app.run(debug=True)
