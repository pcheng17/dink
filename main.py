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

def is_valid_sudoku(board, sudoku_size, num, pos):
    n = len(board)
    sr = sudoku_size[0]
    sc = sudoku_size[1]

    # Check this row
    for j in range(n):
        if board[pos[0]][j] == num and j != pos[1]:
            # print(f"Board isn't valid because ({pos[0]}, {j}) already is {num}")
            return False

    # Check this column
    for i in range(n):
        if board[i][pos[1]] == num and i != pos[0]:
            # print(f"Board isn't valid because ({i}, {pos[1]}) already is {num}")
            return False

    # Check this sub-block
    box_i = pos[0] // sr
    box_j = pos[1] // sc
    for i in range(sr):
        for j in range(sc):
            x = i + box_i * sr
            y = j + box_j * sc
            if board[x][y] == num and (x, y) != pos:
                # print(f"Board isn't valid because ({x}, {y}) already is {num}")
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

def go_dink(board, start, goal, sword, enemies, blocked):
    rows = len(board)
    cols = len(board[0])

    def is_dink_alive(path):
        has_sword = False
        curr_num = board[path[0][0]][path[0][1]]
        for pos, num in zip(path[1:], [board[i][j] for i, j in path[1:]]):
            if num + curr_num > 4:
                return False

            if pos in enemies:
                if not has_sword:
                    return False
                else:
                    if curr_num < num:
                        return False

            if pos == sword:
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
            if is_valid(new_path) and dst not in blocked[pos] and dst not in visited:
                visited.add(dst)
                queue.append((dst, new_path))

    return None

def solve(board_size, sudoku_size, start, goal, sword, enemies, blocked):
    print('Solving Dink...')
    board = [[0 for _ in range(board_size[0])] for _ in range(board_size[1])]
    for b in solve_sudoku(board, sudoku_size):
        if path := go_dink(b, start, goal, sword, enemies, blocked):
            return b, path

def blocked_by_pole(a, dir, blocked):
    match dir:
        case 'NE':
            b = (a[0]-1, a[1]+1)
        case 'SE':
            b = (a[0]+1, a[1]+1)
        case 'SW':
            b = (a[0]+1, a[1]-1)
        case 'NW':
            b = (a[0]-1, a[1]-1)
    blocked[a].add(b)
    blocked[b].add(a)
    return blocked

def blocked_by_wall(a, dir, blocked):
    match dir:
        case 'N':
            b = (a[0]-1, a[1])
        case 'E':
            b = (a[0], a[1]+1)
        case 'S':
            b = (a[0]+1, a[1])
        case 'W':
            b = (a[0], a[1]-1)
    blocked[a].add(b)
    blocked[b].add(a)
    return blocked

if __name__ == '__main__':
    # board_size = (4, 4)
    # sudoku_size = (2, 2)
    # start = (0, 0)
    # goal = (3, 3)
    # sword = (1, 0)
    # enemies = set()
    # enemies.add((0, 2))
    # enemies.add((0, 3))
    # enemies.add((1, 1))
    # enemies.add((1, 2))
    # enemies.add((1, 3))
    # enemies.add((2, 1))
    # enemies.add((2, 2))
    # enemies.add((3, 1))
    # enemies.add((3, 2))
    #
    # # Need to encode what squares can't be reached...
    # blocked = defaultdict(set)
    #
    # blocked = blocked_by_pole((0, 0), 'SE', blocked)
    # blocked = blocked_by_pole((0, 1), 'SW', blocked)
    # blocked = blocked_by_pole((0, 1), 'SE', blocked)
    # blocked = blocked_by_pole((0, 2), 'SW', blocked)
    #
    # blocked = blocked_by_wall((1, 0), 'S', blocked)
    #
    # blocked = blocked_by_pole((1, 0), 'SE', blocked)
    # blocked = blocked_by_pole((1, 1), 'SW', blocked)
    #
    # blocked = blocked_by_wall((1, 1), 'S', blocked)
    #
    # blocked = blocked_by_pole((1, 1), 'SE', blocked)
    # blocked = blocked_by_pole((1, 2), 'SW', blocked)
    # blocked = blocked_by_pole((1, 2), 'SE', blocked)
    # blocked = blocked_by_pole((1, 3), 'SW', blocked)
    #
    # blocked = blocked_by_pole((2, 0), 'SE', blocked)
    # blocked = blocked_by_pole((2, 1), 'SW', blocked)
    # blocked = blocked_by_pole((2, 1), 'SE', blocked)
    # blocked = blocked_by_pole((2, 2), 'SW', blocked)
    # blocked = blocked_by_wall((2, 2), 'S', blocked)
    # blocked = blocked_by_pole((2, 2), 'SE', blocked)
    # blocked = blocked_by_pole((2, 3), 'SW', blocked)
    # blocked = blocked_by_wall((2, 3), 'S', blocked)

    board_size = (3, 3)
    sudoku_size = (1, 3)
    start = (0, 2)
    goal = (2, 2)
    sword = (0, 0)
    enemies = set()
    enemies.add((1, 0))
    enemies.add((1, 1))
    enemies.add((1, 2))
    blocked = defaultdict(set)

    sol = solve(board_size, sudoku_size, start, goal, sword, enemies, blocked)
    if sol:
        print(sol[0])
        print(sol[1])
    else:
        print('uh oh')
