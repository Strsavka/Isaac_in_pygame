import pygame as pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('isaac_front.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 7

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        # Ограничение движения по экрану
        if self.rect.left < 100:
            self.rect.left = 100
        elif self.rect.right > 1100:
            self.rect.right = 1100
        if self.rect.top < 70:
            self.rect.top = 70
        elif self.rect.bottom > 570:
            self.rect.bottom = 570


class Tear(pygame.sprite.Sprite):
    def __init__(self, direction, *group):
        super().__init__(*group)
        self.image = pygame.image.load('tear.png')
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y
        if direction == 'left':
            self.direction = 'left'
        elif direction == 'right':
            self.direction = 'right'
        elif direction == 'up':
            self.direction = 'up'
        else:
            self.direction = 'down'

    def update(self):
        pass


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('The Binding of Isaac')
    screen_size = WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode(screen_size)
    all_sprites = pygame.sprite.Group()
    player = Player(550, 300)
    all_sprites.add(player)
    clock = pygame.time.Clock()
    background = pygame.image.load('night_podval.png')
    background = pygame.transform.scale(background, (1200, 700))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Обновление всех спрайтов
        all_sprites.update()

        # Отображение всех спрайтов
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


