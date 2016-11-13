# board size 8x8
# 2 rounds
# 1 second per move
# single thread only
import random


class Move:
    """Stores the move coordinates with the points gained by playing it"""

    def __init__(self, move, points):
        self.move = move
        self.points = points


class MyPlayer:
    """Player targets the highest gain for current move"""

    def __init__(self, my_color, opponent_color):
        self.name = 'skalaja7'  # username student id
        self.my_color = my_color
        self.opponent_color = opponent_color
        self.space = -1
        # for debugging and further implementation
        self.valid_moves = []

    def move(self, board):
        valid_moves = self.get_valid_moves(board, self.my_color)
        # return greedy move
        self.valid_moves = valid_moves
        max = 0
        move = None
        # find maximum
        for item in valid_moves:
            if item.points > max:
                max = item.points
                move = item.move
        return move

    def get_valid_moves(self, board, symbol):
        valid_moves = []
        # returns all valid moves for given symbol on a current board
        # Check all fields, and find out how many points I get if I play there
        for x in range(8):
            for y in range(8):
                # exam free spaces only
                if board[x][y] == self.space:
                    gain = self.check_move(board, x, y, symbol)
                    if gain > 0:
                        valid_moves.append(Move((x, y), gain))
        if valid_moves == []:
            return None
        else:
            return valid_moves

    def check_move(self, board, x, y, symbol):
        # inspect if the field is a valid move for a given symbol
        # Check all directions for other symbol and count the possible points
        # h and v are directional vectors
        points = 0
        for h in [-1, 0, 1]:
            for v in [-1, 0, 1]:
                if v != 0 or h != 0:
                    if is_field_legit(x + h, y + v):
                        examined = board[x + h][y + v]
                        if examined != self.space and examined != symbol:
                            points += self.count_points(board, x + h, y + v, h, v)
        # return points gain for current move
        # returns 0 if the move is not valid
        return points

    def count_points(self, board, x, y, horizontal_direction, vertical_direction):
        # Count how many stones are in a given direction - basically returns the point gain for a move
        # k is a scalar multipliers for directional vectors
        # returns 0 if the move is not valid
        symbol = board[x][y]
        if symbol == self.space:
            return 0
        count = 1
        for k in range(1, 9):
            if is_field_legit(x + k * horizontal_direction, y + k * vertical_direction):
                if board[x + k * horizontal_direction][y + k * vertical_direction] == self.space:
                    return 0
                elif board[x + k * horizontal_direction][y + k * vertical_direction] == symbol:
                    count += 1
                else:
                    return count
            else:
                return 0
        return count


def is_field_legit(x, y):
    # checks if the field is located within a board
    return 0 <= x < 8 and 0 <= y < 8


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
    move = player.move(sample_board)
    for item in player.valid_moves:
        sample_board[item.move[0]][item.move[1]] = "X"

    for row in sample_board:
        print(row)

    for item in player.valid_moves:
        print(item.move, " - ", item.points)

    print("returned: ", move)
