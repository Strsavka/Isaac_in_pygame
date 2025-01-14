import pygame as pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('isaac_front.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4

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
        self.rect.center = player.rect.center
        self.speed = 6
        self.delete = False
        if direction == 'left':
            self.direction = 'left'
        elif direction == 'right':
            self.direction = 'right'
        elif direction == 'up':
            self.direction = 'up'
        else:
            self.direction = 'down'

    def update(self):
        if self.delete:
            tear_sprites.remove(self)
        if self.direction == 'left':
            self.rect.x -= self.speed
            self.speed -= 0.05
        elif self.direction == 'right':
            self.rect.x += self.speed
            self.speed -= 0.05
        elif self.direction == 'up':
            self.rect.y -= self.speed
            self.speed -= 0.05
        else:
            self.rect.y += self.speed
            self.speed -= 0.05
        if self.rect.x < 100 or self.rect.x > 1100 or self.rect.y < 70 or self.rect.y > 570 or self.speed < 0:
            old_center = self.rect.center
            self.image = pygame.image.load('boom.png')
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            self.delete = True


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('The Binding of Isaac')
    screen_size = WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode(screen_size)
    all_sprites = pygame.sprite.Group()
    tear_sprites = pygame.sprite.Group()
    player = Player(550, 300)
    all_sprites.add(player)
    clock = pygame.time.Clock()
    background = pygame.image.load('night_podval.png')
    background = pygame.transform.scale(background, (1200, 700))
    running = True
    player_tear_kd = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_LEFT] and player_tear_kd == 0:
                    tear_sprites.add(Tear('left'))
                    player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_RIGHT] and player_tear_kd == 0:
                    tear_sprites.add(Tear('right'))
                    player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_UP] and player_tear_kd == 0:
                    tear_sprites.add(Tear('up'))
                    player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_DOWN] and player_tear_kd == 0:
                    tear_sprites.add(Tear('down'))
                    player_tear_kd = 120

        # Обновление всех спрайтов
        all_sprites.update()
        tear_sprites.update()

        # Отображение всех спрайтов
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        tear_sprites.draw(screen)
        pygame.display.flip()

        if player_tear_kd > 0:
            player_tear_kd -= 10
        clock.tick(60)

    pygame.quit()


