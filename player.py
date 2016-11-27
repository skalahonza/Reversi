# board size 8x8
# 2 rounds
# 1 second per move
# single thread only
from copy import deepcopy

# board mask represents the strategic value for each field
board_mask = [[120, -20, 20, 5, 5, 20, -20, 120],
              [-20, -40, -5, -5, -5, -5, -40, -20],
              [20, -5, 15, 3, 3, 15, -5, 20],
              [5, -5, 3, 3, 3, 3, -5, 5],
              [5, -5, 3, 3, 3, 3, -5, 5],
              [20, -5, 15, 3, 3, 15, -5, 20],
              [-20, -40, -5, -5, -5, -5, -40, -20],
              [120, -20, 20, 5, 5, 20, -20, 120]
              ]

# Values for endgame boards are big constants.
MAX_SCORE = 1176  # biggest score achievable
MIN_SCORE = -MAX_SCORE


class Move:
    """Stores the move coordinates with the points gained by playing it"""

    def __init__(self, move, points):
        self.move = move
        self.points = points


class MyPlayer:
    """ Predict the game 4 moves ahead """

    def __init__(self, my_color, opponent_color):
        self.name = 'skalaja7'  # username student id
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.space = -1
        # for debugging and further implementation
        self.valid_moves = []

    def move(self, board):
        self.valid_moves = self.get_valid_moves(board, self.my_color)
        if not self.valid_moves:
            return None
        move = self.alpha_beta_search(self.my_color, board, MIN_SCORE, MAX_SCORE, 4, self.eval_board)
        return move.move

    def alpha_beta_search(self, symbol, board, alpha, beta, depth, evaluate):
        """
        Find the best legal move for player, searching to the given depth. Standard alpha beta algorithm
        :rtype: Move
        :param symbol: player color
        :param board: playing board
        :param alpha: Maximum gain for me
        :param beta: Max opponent gain
        :param depth: How many moves ahead I see
        :param evaluate: Function that computes the board value
        :return: The considering given amount of moves
        """
        # last examined board - return the board value for current symbol
        if depth == 0:
            return Move(None, evaluate(board, symbol))

        def value(board, alpha, beta):
            # Compute the board value for the opponent of the current symbol
            return -self.alpha_beta_search(self.find_opponent(symbol), board, -beta, -alpha, depth - 1, evaluate).points

        moves = self.get_valid_moves(board, symbol)
        if not moves:
            if not self.get_valid_moves(board, self.find_opponent(symbol)):
                # last round - return the last board score
                return Move(None, self.final_value(symbol, board))
            # cannot play this round - return the board value unchanged
            return Move(None, value(board, alpha, beta))

        best_move = moves[0]
        best_move.points = alpha
        for move in moves:
            if alpha >= beta:
                # Skip those moves, that would bring disadvantage to the opponent
                # The opponent will not play badly on purpose - no need to evaluate those nodes
                # Expect the best possible move from the opponent
                break
            val = value(self.simulate_move(board, move.move, symbol), alpha, beta)
            if val > alpha:
                # Found new maximum - replace old maximum
                alpha = val
                best_move = move
                best_move.points = alpha
        return best_move

    def final_value(self, symbol, board):
        """If I win the last board return MAX_SCORE so the alpha beta uses this branch"""
        score = self.score(board, symbol)
        if score < 0:
            return MIN_SCORE
        elif score > 0:
            return MAX_SCORE
        return score

    @staticmethod
    def find_opponent(symbol):
        # Find the opponent for the given symbol
        # Symbol = 1 --> returns 0
        # Symbol = 0 --> returns 1
        if symbol == 1:
            return 0
        elif symbol == 0:
            return 1
        else:
            return -1

    def score(self, board, symbol):
        """ Counts number of stones minus opponents stones """
        score = 0
        for r in range(8):
            for c in range(8):
                if board[r][c] == symbol:
                    score += 1
                elif board[r][c] == self.find_opponent(symbol):
                    score -= 1
        return score

    def eval_board(self, board, symbol):
        """ Evaluates board for the given symbol """
        score = 0
        for r in range(8):
            for c in range(8):
                if board[r][c] == symbol:
                    score += board_mask[r][c]
                elif board[r][c] == self.find_opponent(symbol):
                    score -= board_mask[r][c]
        return score

    def get_valid_moves(self, board, symbol):
        """
        Check all fields, and find out how many points I get if I play there
        :param board: The board that the moves should be found on
        :param symbol: Examined symbol (player color)
        :return: Collection ofall valid moves for given symbol on a current board
        """
        valid_moves = []
        for r in range(8):
            for c in range(8):
                # exam free spaces only
                if board[r][c] == self.space:
                    gain = self.check_move(board, r, c, symbol)
                    if gain > 0:
                        valid_moves.append(Move((r, c), gain))
        if not valid_moves:
            return None
        else:
            return valid_moves

    def check_move(self, board, r, c, symbol):
        """
        Inspects if the field is a valid move for a given symbol
        Check all directions for other symbol and count the possible points
        :param board:
        :param r: row
        :param c: column
        :param symbol: examined symbol
        :return: minimum of points, that the move provides, returns 0 if the move is not valid
        """
        points = 0
        # h and v are directional vectors
        for h in [-1, 0, 1]:
            for v in [-1, 0, 1]:
                if v != 0 or h != 0:
                    if is_field_legit(r + h, c + v):
                        examined = board[r + h][c + v]
                        if examined != self.space and examined != symbol:
                            points += self.count_points(board, r + h, c + v, h, v)
                        # If I can flip some stones - the move is valid
                        if points > 0:
                            return points
        return points

    def count_points(self, board, r, c, horizontal_direction, vertical_direction):
        """
        Count how many stones are in a given direction
        :param board:
        :param r:
        :param c:
        :param horizontal_direction:
        :param vertical_direction:
        :return: 0 if the move is not valid - space found between stones
        """
        symbol = board[r][c]
        count = 1
        # k is a scalar multipliers for directional vectors
        for k in range(1, 9):
            if is_field_legit(r + k * horizontal_direction, c + k * vertical_direction):
                if board[r + k * horizontal_direction][c + k * vertical_direction] == self.space:
                    return 0
                elif board[r + k * horizontal_direction][c + k * vertical_direction] == symbol:
                    count += 1
                else:
                    return count
            else:
                return 0
        return count

    def simulate_move(self, board, move, symbol):
        """ Performs a move on the board and returns a new (transformed) board """
        if move == None:
            return board
        r = move[0]
        c = move[1]
        board_copy = deepcopy(board)
        board_copy[r][c] = symbol

        for v in [-1, 0, 1]:
            for h in [-1, 0, 1]:
                stones = []
                if v == 0 == h:
                    continue
                row = r
                col = c
                row += v
                col += h
                while is_field_legit(row, col):
                    # if it is other symbol
                    if board_copy[row][col] != symbol and board_copy[row][col] != self.space:
                        stones.append((row, col))
                    # if space found - oon t flip this line
                    elif board_copy[row][col] == self.space:
                        break
                    # same symbol found flip all stones
                    elif board_copy[row][col] == symbol:
                        for a, b in stones:
                            board_copy[a][b] = symbol
                        break
                    row += v
                    col += h
        return board_copy


def is_field_legit(r, c):
    """
    checks if the field is located within a board
    :rtype: bool
    """
    return 0 <= r < 8 and 0 <= c < 8


# Tests
if __name__ == "__main__":
    sample_board = [
        [-1, -1, -1, -1, -1, -1, -1, 0],
        [-1, -1, -1, 1, -1, -1, 0, -1],
        [-1, -1, -1, -1, 1, 0, 1, 1],
        [-1, -1, -1, 0, 0, 1, -1, -1],
        [-1, -1, 0, 0, 0, 1, -1, -1],
        [-1, -1, 0, 0, 0, -1, -1, -1],
        [-1, -1, 0, -1, 0, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1],
    ]
    player = MyPlayer(1, 0)
    for row in sample_board:
        print(row)
    print("------------")
    pmove = player.move(sample_board)
    """for item in player.valid_moves:
        sample_board[item.move[0]][item.move[1]] = "X"""

    for row in sample_board:
        print(row)

    for item in player.valid_moves:
        print(item.move, " - ", item.points)

    print("returned: ", pmove)
    playBoard = player.simulate_move(sample_board, pmove, player.my_color)
    print("------------")
    for row in playBoard:
        print(row)
