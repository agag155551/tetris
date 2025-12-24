import pygame
import game.tetris.tetris as tetris

pygame.init()

screen = pygame.display.set_mode((500, 1000))
pygame.display.set_caption("main")

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)

btn_start = pygame.Rect(0, 0, 140, 60)

chk_size = 24
pad = 20
gap = 12

chk_ghost = pygame.Rect(pad, screen.get_height() - pad - chk_size, chk_size, chk_size)
lbl_ghost_pos = (chk_ghost.right + 10, chk_ghost.y - 2)

chk_hold = pygame.Rect(pad, chk_ghost.y - gap - chk_size, chk_size, chk_size)
lbl_hold_pos = (chk_hold.right + 10, chk_hold.y - 2)

ghost_enabled = True
hold_enabled = True

state = "menu"
running = True

def draw_checkmark(surface, rect):
    x, y, w, h = rect
    pygame.draw.line(surface, (255, 255, 255), (x + 4, y + h // 2), (x + w // 2 - 1, y + h - 5), 3)
    pygame.draw.line(surface, (255, 255, 255), (x + w // 2 - 1, y + h - 5), (x + w - 4, y + 5), 3)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_start.collidepoint(event.pos):
                state = "tetris"
            elif chk_ghost.collidepoint(event.pos):
                ghost_enabled = not ghost_enabled
            elif chk_hold.collidepoint(event.pos):
                hold_enabled = not hold_enabled

    if state == "menu":
        screen.fill((30, 30, 40))

        #시작버튼
        btn_start.center = screen.get_rect().center
        pygame.draw.rect(screen, (70, 200, 70), btn_start, border_radius=10)
        text = font.render("Start", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=btn_start.center))

        #홀드체크박스
        pygame.draw.rect(screen, (0, 0, 0), chk_hold)
        pygame.draw.rect(screen, (200, 200, 200), chk_hold, 2)
        if hold_enabled:
            draw_checkmark(screen, chk_hold)
        label = small_font.render("Hold (A)", True, (220, 220, 220))
        screen.blit(label, lbl_hold_pos)

        #고스트체크박스
        pygame.draw.rect(screen, (0, 0, 0), chk_ghost)
        pygame.draw.rect(screen, (200, 200, 200), chk_ghost, 2)
        if ghost_enabled:
            draw_checkmark(screen, chk_ghost)
        label = small_font.render("Ghost preview", True, (220, 220, 220))
        screen.blit(label, lbl_ghost_pos)

        pygame.display.flip()

    elif state == "tetris":
        result = tetris.run(screen, ghost_enabled=ghost_enabled, hold_enabled=hold_enabled)
        if result == "menu":
            state = "menu"
        elif result == "quit":
            running = False

pygame.quit()