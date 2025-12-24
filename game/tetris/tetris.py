import pygame
import random
#123123123
#배경 크기
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 50

SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE

DROP_DELAY = 700
SOFT_DROP_DELAY = 50

#좌/우 연속 이동
MOVE_DAS = 160
MOVE_ARR = 45

#유예기간
LOCK_DELAY = 500

#무한 스핀 방지
LOCK_RESET_LIMIT = 15
MAX_GROUNDED_TIME = 2500

#회전 최대 횟수
MAX_ROTATIONS_PER_PIECE = 15

#고스트미리보기 투명도
GHOST_ALPHA = 90

BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
LIGHT_GRAY = (35, 35, 35)
WHITE = (240, 240, 240)

def draw_checkerboard(screen):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = DARK_GRAY if (x + y) % 2 == 0 else LIGHT_GRAY
            pygame.draw.rect(
                screen,
                color,
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )


#블럭 모양
SHAPES = {
    "I": [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "O": [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "T": [
        [0, 1, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "S": [
        [0, 1, 1, 0],
        [1, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "Z": [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "J": [
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "L": [
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
}

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 0, 240),
    "L": (240, 160, 0),
}


def rotate_matrix_cw(mat):
    return [list(row) for row in zip(*mat[::-1])]


def generate_rotations(base):
    rots = []
    cur = base
    for _ in range(4):
        if cur not in rots:
            rots.append(cur)
        cur = rotate_matrix_cw(cur)
    return rots


ROTATIONS = {k: generate_rotations(v) for k, v in SHAPES.items()}


def matrix_to_cells(mat):
    cells = []
    for y in range(4):
        for x in range(4):
            if mat[y][x] == 1:
                cells.append((x, y))
    return cells


class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.color = COLORS[kind]
        self.rotations = ROTATIONS[kind]
        self.rot = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

    def cells(self, rot=None):
        r = self.rot if rot is None else rot
        return matrix_to_cells(self.rotations[r])


def new_board():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def is_valid(board, piece, dx=0, dy=0, rot=None):
    px = piece.x + dx
    py = piece.y + dy
    for cx, cy in piece.cells(rot):
        x = px + cx
        y = py + cy
        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            return False
        if board[y][x] != 0:
            return False
    return True


def lock_piece(board, piece):
    for cx, cy in piece.cells():
        x = piece.x + cx
        y = piece.y + cy
        if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
            board[y][x] = piece.color


def clear_lines(board):
    new_rows = [row for row in board if not all(row)]
    cleared = GRID_HEIGHT - len(new_rows)
    for _ in range(cleared):
        new_rows.insert(0, [0 for _ in range(GRID_WIDTH)])
    return new_rows, cleared


def draw_board_blocks(screen, board):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if board[y][x] != 0:
                pygame.draw.rect(
                    screen,
                    board[y][x],
                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )


def draw_piece(screen, piece):
    for cx, cy in piece.cells():
        x = piece.x + cx
        y = piece.y + cy
        pygame.draw.rect(
            screen,
            piece.color,
            (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )


def get_from_bag(bag):
    if not bag:
        bag.extend(["I", "O", "T", "S", "Z", "J", "L"])
        random.shuffle(bag)
    return bag.pop()


def try_rotate_with_kicks(board, piece):
    new_rot = (piece.rot + 1) % len(piece.rotations)
    kicks = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
    for dx, dy in kicks:
        if is_valid(board, piece, dx=dx, dy=dy, rot=new_rot):
            piece.rot = new_rot
            piece.x += dx
            piece.y += dy
            return True
    return False


def compute_ghost_y(board, piece):
    drop = 0
    for _ in range(GRID_HEIGHT):
        if is_valid(board, piece, dy=drop + 1):
            drop += 1
        else:
            break
    return piece.y + drop, drop


def draw_ghost_piece(screen, board, piece):
    ghost_y, drop = compute_ghost_y(board, piece)
    if drop == 0:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    r, g, b = piece.color
    ghost_color = (r, g, b, GHOST_ALPHA)

    for cx, cy in piece.cells():
        x = (piece.x + cx) * CELL_SIZE
        y = (ghost_y + cy) * CELL_SIZE
        pygame.draw.rect(overlay, ghost_color, (x, y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(
            overlay,
            (255, 255, 255, min(160, GHOST_ALPHA + 60)),
            (x, y, CELL_SIZE, CELL_SIZE),
            2
        )

    screen.blit(overlay, (0, 0))


def draw_preview_box_1cell(screen, kind, box_x, box_y, enabled=True):
    pad = 6
    box_size = CELL_SIZE

    bg = (10, 10, 10) if enabled else (25, 25, 25)
    border = WHITE if enabled else (140, 140, 140)

    pygame.draw.rect(screen, bg, (box_x, box_y, box_size, box_size))
    pygame.draw.rect(screen, border, (box_x, box_y, box_size, box_size), 2)

    if kind is None or not enabled:
        return

    mini = max(4, (box_size - 2 * pad) // 4)
    mat = SHAPES[kind]
    color = COLORS[kind]

    cells = [(x, y) for y in range(4) for x in range(4) if mat[y][x] == 1]
    min_x = min(x for x, _ in cells)
    max_x = max(x for x, _ in cells)
    min_y = min(y for _, y in cells)
    max_y = max(y for _, y in cells)
    bw = (max_x - min_x + 1)
    bh = (max_y - min_y + 1)

    draw_w = bw * mini
    draw_h = bh * mini
    start_x = box_x + (box_size - draw_w) // 2
    start_y = box_y + (box_size - draw_h) // 2

    for x, y in cells:
        xx = start_x + (x - min_x) * mini
        yy = start_y + (y - min_y) * mini
        pygame.draw.rect(screen, color, (xx, yy, mini, mini))


def run(screen, ghost_enabled=True, hold_enabled=True):
    pygame.display.set_caption("Tetris")

    board = new_board()
    bag = []

    # 미리보기
    next_queue = [get_from_bag(bag), get_from_bag(bag)]
    current = Piece(get_from_bag(bag))

    if not is_valid(board, current):
        return "menu"

    clock = pygame.time.Clock()
    last_drop_time = pygame.time.get_ticks()

    #좌/우 연속이동
    dir_current = 0
    dir_start_time = 0
    dir_last_step_time = 0
    last_dir_preference = 0  # -1 or 1

    #무한 방지
    lock_start_time = None
    grounded_since = None
    lock_reset_count = 0

    #회전 횟수 제한
    rotate_count = 0

    #홀드
    hold_kind = None
    hold_used_since_lock = False

    def grounded(piece):
        return not is_valid(board, piece, dy=1)

    def try_move(dx):
        nonlocal current
        if is_valid(board, current, dx=dx, dy=0):
            current.x += dx
            return True
        return False

    def reset_lock_state():
        nonlocal lock_start_time, grounded_since, lock_reset_count
        lock_start_time = None
        grounded_since = None
        lock_reset_count = 0

    def spawn_from_next(now):
        nonlocal current, next_queue, last_drop_time, rotate_count
        kind = next_queue.pop(0)
        next_queue.append(get_from_bag(bag))
        current = Piece(kind)
        if not is_valid(board, current):
            return False
        last_drop_time = now
        reset_lock_state()
        rotate_count = 0
        return True

    def spawn_from_kind(kind, now):
        nonlocal current, last_drop_time, rotate_count
        current = Piece(kind)
        if not is_valid(board, current):
            return False
        last_drop_time = now
        reset_lock_state()
        rotate_count = 0
        return True

    def lock_and_spawn(now):
        nonlocal board, hold_used_since_lock, rotate_count
        lock_piece(board, current)
        board, _ = clear_lines(board)
        reset_lock_state()
        rotate_count = 0
        hold_used_since_lock = False
        return spawn_from_next(now)

    while True:
        now = pygame.time.get_ticks()
        moved_or_rotated = False

        # ===== 이벤트(단발 동작) =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

                # 마지막 방향 우선순위(동시 입력 시)
                if event.key == pygame.K_LEFT:
                    last_dir_preference = -1
                elif event.key == pygame.K_RIGHT:
                    last_dir_preference = 1

                if event.key == pygame.K_UP:
                    if rotate_count < MAX_ROTATIONS_PER_PIECE:
                        if try_rotate_with_kicks(board, current):
                            rotate_count += 1
                            moved_or_rotated = True

                #하드 드랍
                if event.key == pygame.K_SPACE:
                    while is_valid(board, current, dy=1):
                        current.y += 1
                    if not lock_and_spawn(now):
                        return "menu"
                    continue

                #홀드
                if event.key == pygame.K_a and hold_enabled:
                    if not hold_used_since_lock:
                        hold_used_since_lock = True
                        reset_lock_state()

                        if hold_kind is None:
                            hold_kind = current.kind
                            if not spawn_from_next(now):
                                return "menu"
                        else:
                            temp = current.kind
                            if not spawn_from_kind(hold_kind, now):
                                return "menu"
                            hold_kind = temp

        #지속 입력
        pressed = pygame.key.get_pressed()
        left_held = pressed[pygame.K_LEFT]
        right_held = pressed[pygame.K_RIGHT]
        soft_drop = pressed[pygame.K_DOWN]

        #동시 입력 우선순위
        if left_held and not right_held:
            new_dir = -1
            last_dir_preference = -1
        elif right_held and not left_held:
            new_dir = 1
            last_dir_preference = 1
        elif left_held and right_held:
            new_dir = last_dir_preference if last_dir_preference != 0 else 0
        else:
            new_dir = 0

        #방향 변경
        if new_dir != dir_current:
            dir_current = new_dir
            if dir_current != 0:
                dir_start_time = now
                dir_last_step_time = now
                if try_move(dir_current):
                    moved_or_rotated = True
            else:
                dir_start_time = 0
                dir_last_step_time = 0

        #같은 방향 유지
        if dir_current != 0:
            if now - dir_start_time >= MOVE_DAS:
                if now - dir_last_step_time >= MOVE_ARR:
                    steps = (now - dir_last_step_time) // MOVE_ARR
                    steps = min(int(steps), 12)
                    any_moved = False
                    for _ in range(steps):
                        if try_move(dir_current):
                            any_moved = True
                            dir_last_step_time += MOVE_ARR
                        else:
                            dir_last_step_time = now
                            break
                    if any_moved:
                        moved_or_rotated = True

        #자동 낙하
        delay = SOFT_DROP_DELAY if soft_drop else DROP_DELAY
        if now - last_drop_time >= delay:
            last_drop_time = now
            if is_valid(board, current, dy=1):
                current.y += 1

        #무한방지
        if grounded(current):
            if grounded_since is None:
                grounded_since = now
            if lock_start_time is None:
                lock_start_time = now

            if moved_or_rotated:
                if lock_reset_count < LOCK_RESET_LIMIT:
                    lock_start_time = now
                    lock_reset_count += 1
                
            if (
                (now - lock_start_time) >= LOCK_DELAY
                or (grounded_since is not None and (now - grounded_since) >= MAX_GROUNDED_TIME)
            ):
                if not lock_and_spawn(now):
                    return "menu"
        else:
            reset_lock_state()

        #그리기
        draw_checkerboard(screen)
        draw_board_blocks(screen, board)

        pad = 6

        #홀드미리보기
        if hold_enabled:
            hold_x = pad
            hold_y = pad
            draw_preview_box_1cell(screen, hold_kind, hold_x, hold_y, enabled=True)

        #다음블럭미리보기
        next_x = SCREEN_WIDTH - CELL_SIZE - pad
        next_y1 = pad
        next_y2 = pad + CELL_SIZE + pad

        draw_preview_box_1cell(screen, next_queue[0], next_x, next_y1, enabled=True)
        draw_preview_box_1cell(screen, next_queue[1], next_x, next_y2, enabled=True)

        #고스트
        if ghost_enabled:
            draw_ghost_piece(screen, board, current)

        #현재 블록
        draw_piece(screen, current)

        pygame.display.flip()
        clock.tick(60)
