import pygame


def run(screen):
    pygame.display.set_caption("tetris")

    rect = pygame.Rect(0, 0, 25, 25)
    rect.center = screen.get_rect().center
    rect.top = screen.get_rect().top
    speed = 5

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            rect.x -= speed
        if keys[pygame.K_RIGHT]:
            rect.x += speed
        if keys[pygame.K_UP]:
            rect.y -= speed
        if keys[pygame.K_DOWN]:
            rect.y += speed

        rect.clamp_ip(screen.get_rect())

        screen.fill((50, 50, 50))
        pygame.draw.rect(screen, (200, 200, 200), rect)
        pygame.display.flip()
        clock.tick(60)