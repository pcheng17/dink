from collections import defaultdict, deque
from typing import Tuple, List, Optional
import sys

DIRECTIONS = {
    'N': (-1, 0),
    'E': (0, 1),
    'S': (1, 0),
    'W': (0, -1),
    'NE': (-1, 1),
    'SE': (1, 1),
    'SW': (1, -1),
    'NW': (-1, -1),
}

class GameMap:
    def __init__(
        self,
        board_size: Tuple[int, int],
        sudoku_size: Tuple[int, int],
        start: Tuple[int, int],
        goal: Tuple[int, int],
        **kwargs
    ):
        self.board_size = board_size
        self.sudoku_size = sudoku_size
        self.start = start
        self.goal = goal

        # If board exists as an arg, I expect it to be a list of lists
        value = kwargs.get('board', self._initialize_empty_board())
        if not isinstance(value, list):
            raise TypeError(f"board must be a list, got {type(value)}")
        if not all(isinstance(row, list) for row in value):
            raise TypeError("board must be a list of lists")
        self.board = value

        # If sword exists as an arg, I expect it to be a tuple
        value = kwargs.get('sword', None)
        if value is not None and not isinstance(value, tuple):
            raise TypeError(f"sword must be a tuple, got {type(value)}")
        self.sword = value

        # I expect all of these to be lists
        self.monsters = set(self._validate_list(kwargs.get('monsters', []), 'monsters'))
        self.poles = set(self._validate_list(kwargs.get('poles', []), 'poles'))
        self.hwalls = set(self._validate_list(kwargs.get('hwalls', []), 'hwalls'))
        self.vwalls = set(self._validate_list(kwargs.get('vwalls', []), 'vwalls'))
        self.constraints = self._validate_list(kwargs.get('constraints', []), 'constraints')

        self.blocked = self._initialize_blocked()

    def _validate_list(self, value, field):
        if not isinstance(value, list):
            raise TypeError(f"{field} must be a list, got {type(value)}")
        return value

    def _initialize_empty_board(self):
        return [[0 for _ in range(self.board_size[0])] for _ in range(self.board_size[1])]

    def _is_valid(self, pos):
        return 0 <= pos[0] < self.board_size[0] and 0 <= pos[1] < self.board_size[1]

    def _blocked_by_poles(self, poles, blocked):
        for i, j in poles:
            a = (i-1, j-1)
            b = (i-1, j)
            c = (i, j-1)
            d = (i, j)
            if self._is_valid(a) and self._is_valid(d):
                blocked[a].add(d)
                blocked[d].add(a)
            if self._is_valid(b) and self._is_valid(c):
                blocked[b].add(c)
                blocked[c].add(b)

    def _blocked_by_hwalls(self, blocked):
        for i, j in self.hwalls:
            t = (i-1, j)
            b = (i, j)
            if self._is_valid(t) and self._is_valid(b):
                blocked[t].add(b)
                blocked[b].add(t)
            poles = [(i, j), (i, j+1)]
            self._blocked_by_poles(poles, blocked)

    def _blocked_by_vwalls(self, blocked):
        for i, j in self.vwalls:
            r = (i, j)
            l = (i, j-1)
            if self._is_valid(r) and self._is_valid(l):
                blocked[r].add(l)
                blocked[l].add(r)
            poles = [(i, j), (i+1, j)]
            self._blocked_by_poles(poles, blocked)

    def _initialize_blocked(self):
        blocked = defaultdict(set)
        self._blocked_by_poles(self.poles, blocked)
        self._blocked_by_hwalls(blocked)
        self._blocked_by_vwalls(blocked)
        return blocked

class Constraint:
    def check(self, gm: GameMap, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        raise NotImplementedError()

class MaximumSumConstraint(Constraint):
    def __init__(self, max_sum: int):
        self.max_sum = max_sum

    def check(self, gm, from_pos, to_pos):
        return gm.board[from_pos[0]][from_pos[1]] + gm.board[to_pos[0]][to_pos[1]] <= self.max_sum

class ModuloSumConstraint(Constraint):
    def __init__(self, mod: int, allowed: List[int]):
        self.mod = mod
        self.allowed = allowed

    def check(self, gm, from_pos, to_pos):
        return (gm.board[from_pos[0]][from_pos[1]] + gm.board[to_pos[0]][to_pos[1]]) % self.mod in self.allowed

def is_valid_sudoku(board, sudoku_size, num, pos):
    n = len(board)
    sr = sudoku_size[0]
    sc = sudoku_size[1]

    # Check this row
    for j in range(n):
        if board[pos[0]][j] == num and j != pos[1]:
            return False

    # Check this column
    for i in range(n):
        if board[i][pos[1]] == num and i != pos[0]:
            return False

    # Check this sub-block
    box_i = pos[0] // sr
    box_j = pos[1] // sc
    for i in range(sr):
        for j in range(sc):
            x = i + box_i * sr
            y = j + box_j * sc
            if board[x][y] == num and (x, y) != pos:
                return False;

    return True

def find_empty_spot(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def solve_sudoku(board, sudoku_size):
    rows = len(board)
    n = rows

    empty = find_empty_spot(board)
    if not empty:
        yield [row[:] for row in board]
        return

    i, j = empty
    for k in range(1, n+1):
        if is_valid_sudoku(board, sudoku_size, k, empty):
            board[i][j] = k
            yield from solve_sudoku(board, sudoku_size)
            board[i][j] = 0

def go_dink(gm):
    rows = len(gm.board)
    cols = len(gm.board[0])

    def is_dink_alive(path):
        has_sword = False
        cpos = path[0]

        for npos in path[1:]:
            if gm.constraints and any(not c.check(gm, cpos, npos) for c in gm.constraints):
                return False

            if npos in gm.monsters:
                if not has_sword:
                    return False
                else:
                    if gm.board[cpos[0]][cpos[1]] <= gm.board[npos[0]][npos[1]]:
                        return False

            if gm.sword and npos == gm.sword:
                has_sword = True

            cpos = npos

        return True

    def is_valid(path):
        last = path[-1]
        return 0 <= last[0] < rows and 0 <= last[1] < cols and is_dink_alive(path)

    visited = {gm.start}
    queue = deque([(gm.start, [gm.start])])

    while queue:
        pos, path = queue.popleft()

        if pos == gm.goal:
            return path

        for dx, dy in DIRECTIONS.values():
            dst = (pos[0] + dx, pos[1] + dy)
            new_path = path + [dst]
            if dst not in gm.blocked[pos] and dst not in visited and is_valid(new_path):
                visited.add(dst)
                queue.append((dst, new_path))

    return None

def solve(gm: GameMap):
    print('Solving Dink...')
    solutions = []
    for b in solve_sudoku(gm.board, gm.sudoku_size):
        if path := go_dink(gm):
            solutions.append((b, path))
    return solutions

def create_act(id) -> Optional[GameMap]:
    match id:
        case 'p1':
            return GameMap(
                board_size = (3, 3),
                sudoku_size = (1, 3),
                start = (0, 0),
                goal = (0, 1),
                poles = [(2, 2)],
                vwalls = [(0, 1)],
                constraints = [ModuloSumConstraint(2, [0])],
            )
        case 'p3':
            return GameMap(
                board_size = (3, 3),
                sudoku_size = (1, 3),
                start = (0, 2),
                goal = (2, 2),
                sword = (0, 0),
                monsters = [(1, 0), (1, 1), (1, 2)],
                constraints = [MaximumSumConstraint(4)],
            )
        case 'e0':
            return GameMap(
                board_size = (4, 4),
                sudoku_size = (2, 2),
                start = (0, 0),
                goal = (3, 3),
                sword = (1, 0),
                monsters = [(0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1), (3, 2)],
                poles = [(1, 1), (1, 2), (2, 3), (3, 1)],
                hwalls = [(2, 0), (2, 1), (3, 2), (3, 3)],
            )
        case _:
            return None

if __name__ == '__main__':
    id = 'e0'
    gm = create_act(id)
    if gm is None:
        print(f"Invalid Act id: {id}")
        sys.exit(1)

    if sols := solve(gm):
        for b, p in sols:
            print(b, p)
    else:
        print('No solution found')

