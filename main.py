from collections import defaultdict, deque

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

def is_valid(pos, board_size):
    return 0 <= pos[0] < board_size[0] and 0 <= pos[1] < board_size[1]

def create_empty_board(board_size):
    return [[0 for _ in range(board_size[0])] for _ in range(board_size[1])]

def blocked_by_poles(poles, board_size, blocked):
    for i, j in poles:
        a = (i-1, j-1)
        b = (i-1, j)
        c = (i, j-1)
        d = (i, j)
        if is_valid(a, board_size) and is_valid(d, board_size):
            blocked[a].add(d)
            blocked[d].add(a)
        if is_valid(b, board_size) and is_valid(c, board_size):
            blocked[b].add(c)
            blocked[c].add(b)

def blocked_by_hwalls(walls, board_size, blocked):
    for i, j in walls:
        t = (i-1, j)
        b = (i, j)
        if is_valid(t, board_size) and is_valid(b, board_size):
            blocked[t].add(b)
            blocked[b].add(t)
        poles = [(i, j), (i, j+1)]
        blocked_by_poles(poles, board_size, blocked)

def blocked_by_vwalls(walls, board_size, blocked):
    for i, j in walls:
        r = (i, j)
        l = (i, j-1)
        if is_valid(r, board_size) and is_valid(l, board_size):
            blocked[r].add(l)
            blocked[l].add(r)
        poles = [(i, j), (i+1, j)]
        blocked_by_poles(poles, board_size, blocked)


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

def go_dink(board, start, goal, sword, enemies, blocked, constraint = None):
    rows = len(board)
    cols = len(board[0])

    def is_dink_alive(path):
        has_sword = False
        curr_num = board[path[0][0]][path[0][1]]
        for pos, num in zip(path[1:], [board[i][j] for i, j in path[1:]]):
            if constraint and not constraint(curr_num, num):
                return False

            if pos in enemies:
                if not has_sword:
                    return False
                else:
                    if curr_num < num:
                        return False

            if sword and pos == sword:
                has_sword = True

            curr_num = num

        return True

    def is_valid(path):
        last = path[-1]
        return 0 <= last[0] < rows and 0 <= last[1] < cols and is_dink_alive(path)

    visited = {start}
    queue = deque([(start, [start])])

    while queue:
        pos, path = queue.popleft()

        if pos == goal:
            return path

        for dx, dy in DIRECTIONS.values():
            dst = (pos[0] + dx, pos[1] + dy)
            new_path = path + [dst]
            if dst not in blocked[pos] and dst not in visited and is_valid(new_path):
                visited.add(dst)
                queue.append((dst, new_path))

    return None

def solve(board, sudoku_size, start, goal, sword, enemies, blocked, constraint = None):
    print('Solving Dink...')
    solutions = []
    for b in solve_sudoku(board, sudoku_size):
        if path := go_dink(b, start, goal, sword, enemies, blocked, constraint):
            solutions.append((b, path))
    return solutions

if __name__ == '__main__':
    episode = 'e0'

    match episode:
        case 'p1':
            # Prelude 1
            board_size = (3, 3)
            board = create_empty_board(board_size)
            sudoku_size = (1, 3)
            start = (0, 0)
            goal = (0, 1)
            sword = None
            enemies = set()
            poles = [(2, 2)]
            hwalls = []
            vwalls = [(0, 1)]
            constraint = lambda x, y: (x + y) % 2 == 0

            blocked = defaultdict(set)
            blocked_by_poles(poles, board_size, blocked)
            blocked_by_hwalls(hwalls, board_size, blocked)
            blocked_by_vwalls(vwalls, board_size, blocked)
        case 'p3':
            # Prelude 3
            board_size = (3, 3)
            board = create_empty_board(board_size)
            sudoku_size = (1, 3)
            start = (0, 2)
            goal = (2, 2)
            sword = (0, 0)
            enemies = set([(1, 0), (1, 1), (1, 2)])
            constraint = lambda x, y: (x + y) <= 4
            blocked = defaultdict(set)
        case 'e0':
            # Episode 0
            board_size = (4, 4)
            board = create_empty_board(board_size)
            sudoku_size = (2, 2)
            start = (0, 0)
            goal = (3, 3)
            sword = (1, 0)
            enemies = set([(0, 2), (0, 3), (1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (3, 1), (3, 2)])
            poles = [(1, 1), (1, 2), (2, 3), (3, 1)]
            hwalls = [(2, 0), (2, 1), (3, 2), (3, 3)]
            vwalls = []
            constraint = None

            blocked = defaultdict(set)
            blocked_by_poles(poles, board_size, blocked)
            blocked_by_hwalls(hwalls, board_size, blocked)
            blocked_by_vwalls(vwalls, board_size, blocked)

    if sols := solve(board, sudoku_size, start, goal, sword, enemies, blocked, constraint):
        for b, p in sols:
            print(b, p)
    else:
        print('uh oh')
