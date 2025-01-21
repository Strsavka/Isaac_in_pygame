import pygame as pygame


class Item(pygame.sprite.Sprite):
    def __init__(self, name, pos, player_getting):
        super().__init__()
        self.player_getting = player_getting
        self.name = name
        self.image = pygame.image.load(self.name + '.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.speed = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.lying = True

    def update(self):
        if pygame.sprite.collide_mask(self, self.player_getting):
            self.add_to_inventory(player)
        if not self.lying:
            item_sprites.remove(self)
            return

    def add_to_inventory(self, player_getting):
        if self.name == 'bomb':
            player_getting.inventory_bombs += 1
        elif self.name == 'Penny':
            player_getting.inventory_money += 1
        elif self.name == 'Red_Heart':
            if player_getting.health + 1 <= player_getting.max_health:
                player_getting.health += 1
                if player_getting.health + 1 <= player_getting.max_health:
                    player_getting.health += 1
        elif self.name == 'Half_Red_Heart':
            if player_getting.health + 1 <= player_getting.max_health:
                player_getting.health += 1
        self.lying = False


class Bomb(pygame.sprite.Sprite):
    def __init__(self, radius=10, explosion_radius=50, damage=20, speed=0):
        super().__init__()

        # Основные параметры бомбы
        self.image = pygame.image.load('bomb.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (player.rect.center[0], player.rect.center[1] + 50)
        self.mask = pygame.mask.from_surface(self.image)
        self.radius = radius
        self.explosion_radius = explosion_radius
        self.damage = damage
        self.speed = speed
        self.timer = 120  # Время до взрыва (в кадрах)
        self.alive = True

    def update(self):
        if not self.alive:
            bomb_sprites.remove(self)
            return

        # Обновление таймера
        self.timer -= 1
        if self.timer <= 0:
            self.explode()

    def explode(self):
        # Логика взрыва
        old_center = self.rect.center
        self.image = pygame.image.load('boom.png')
        self.rect = self.image.get_rect()
        self.rect.center = old_center
        self.alive = False


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('isaac_front.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4
        self.mask = pygame.mask.from_surface(self.image)
        self.inventory_bombs = 10  # кол-во бомб
        self.inventory_money = 0  # кол-во монет
        self.player_tear_kd = 0
        self.health = 6  # кол-во хп
        self.max_health = 6  # макс кол-во хп
        self.soul_health = 0  # сердца душ(если хочешь реализовать, то надо переписывать логику отображения сердец)

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

        if player.health < 1:  # проверка на закончившиеся хп
            player.dead()

    def dead(self):  # прописать механику смерти надо
        pass


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
    item_sprites = pygame.sprite.Group()
    bomb_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    background = pygame.image.load('night_podval.png')
    background = pygame.transform.scale(background, (1200, 700))
    bomb_icon = pygame.image.load('bomb.png')
    bomb_icon = pygame.transform.scale(bomb_icon, (50, 50))
    bomb_counter_font = pygame.font.SysFont("Times New Roman", 50)
    money_counter_font = pygame.font.SysFont("Times New Roman", 50)
    money_icon = pygame.image.load('Penny.png')
    money_icon = pygame.transform.scale(money_icon, (50, 50))
    health_empty_icon = pygame.image.load('heart_empty.png')
    health_empty_icon = pygame.transform.scale(health_empty_icon, (50, 50))
    health_half_icon = pygame.image.load('heart_half.png')
    health_half_icon = pygame.transform.scale(health_half_icon, (50, 50))
    health_full_icon = pygame.image.load('heart_full.png')
    health_full_icon = pygame.transform.scale(health_full_icon, (50, 50))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_LEFT] and player.player_tear_kd == 0:
                    tear_sprites.add(Tear('left'))
                    player.player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_RIGHT] and player.player_tear_kd == 0:
                    tear_sprites.add(Tear('right'))
                    player.player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_UP] and player.player_tear_kd == 0:
                    tear_sprites.add(Tear('up'))
                    player.player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_DOWN] and player.player_tear_kd == 0:
                    tear_sprites.add(Tear('down'))
                    player.player_tear_kd = 120
                if pygame.key.get_pressed()[pygame.K_e] and player.inventory_bombs > 0:
                    bomb_sprites.add(Bomb(player.rect.center[0], player.rect.center[1]))
                    player.inventory_bombs -= 1
                if pygame.key.get_pressed()[pygame.K_p]:  # чит-клавиша(бета-тест)
                    item_sprites.add(Item('bomb', (300, 300), player))
                    item_sprites.add(Item('Penny', (600, 300), player))
                    player.health -= 1

        # Обновление всех спрайтов
        all_sprites.update()
        tear_sprites.update()
        bomb_sprites.update()
        item_sprites.update()

        # Отображение всех спрайтов
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        bomb_counter = bomb_counter_font.render(str(player.inventory_bombs), True, 'WHITE')
        screen.blit(bomb_counter, (50, 50))
        money_counter = money_counter_font.render(str(player.inventory_money), True, 'WHITE')
        screen.blit(money_counter, (50, 100))
        all_sprites.draw(screen)
        tear_sprites.draw(screen)
        bomb_sprites.draw(screen)
        item_sprites.draw(screen)
        screen.blit(bomb_icon, (0, 50))
        screen.blit(money_icon, (0, 100))
        player_counting_health = player.health  # логика отображения хп
        player_counting_health_place = 0
        while player_counting_health > 0:
            if player_counting_health - 2 >= 0:
                player_counting_health -= 2
                screen.blit(health_full_icon, (player_counting_health_place, 0))
                player_counting_health_place += 50
            else:
                player_counting_health -= 1
                screen.blit(health_half_icon, (player_counting_health_place, 0))
                player_counting_health_place += 50
        player_counting_health_2 = player.max_health - player.health
        while player_counting_health_2 > 1:
            if player_counting_health_2 - 2 >= 0:
                player_counting_health_2 -= 2
                screen.blit(health_empty_icon, (player_counting_health_place, 0))
                player_counting_health_place += 50
        pygame.display.flip()

        if player.player_tear_kd > 0:
            player.player_tear_kd -= 10
        clock.tick(60)

    pygame.quit()
