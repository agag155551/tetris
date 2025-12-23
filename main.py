
import pygame
import game.tetris.tetris as tetris

pygame.init() 

screen = pygame.display.set_mode((500, 900)) 
pygame.display.set_caption("main")
font = pygame.font.SysFont(None, 40)

btn_start = pygame.Rect(150, 100, 100, 50)
state = "menu"

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == "menu" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if btn_start.collidepoint(event.pos):
                state = "tetris"

    if state == "menu":
        screen.fill((30, 30, 40))
        btn_start.center = screen.get_rect().center
        pygame.draw.rect(screen, (70, 200, 70), btn_start)
        text = font.render("Start", True, (0, 0, 0))
        text_rect = text.get_rect(center=btn_start.center)
        screen.blit(text, text_rect)
        pygame.display.flip() 

    elif state == "tetris":
        result = tetris.run(screen)
        if result == "menu":
            state = "menu"
        elif result == "quit":
            running = False

pygame.quit()