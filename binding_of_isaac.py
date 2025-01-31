import pygame as pygame

# Загрузка изображений сердца
heart_full = pygame.image.load("heart_full.png")
heart_half = pygame.image.load("heart_half.png")
heart_empty = pygame.image.load("heart_empty.png")
heart_full = pygame.transform.scale(heart_full, (50, 50))
heart_half = pygame.transform.scale(heart_half, (50, 50))
heart_empty = pygame.transform.scale(heart_empty, (50, 50))

# Размеры одного сегмента сердца
HEART_WIDTH = 50
HEART_HEIGHT = 50


def draw_health_bar(x, y, health, max_health):
    # Рассчитываем количество полных сердец
    full_hearts = int(health // 2)
    empty_hearts = (max_health - health) // 2
    e = full_hearts

    # Отображаем полные сердца
    for i in range(full_hearts):
        screen.blit(heart_full, (x + i * HEART_WIDTH, y))

    # Остаток от деления на 2 определяет состояние следующего сердца
    remainder = health % 2

    if remainder == 1:
        screen.blit(heart_half, (x + full_hearts * HEART_WIDTH, y))
        e += 1
    for i in range(empty_hearts):
        screen.blit(heart_empty, (x + (i + e) * HEART_WIDTH, y))


class Item(pygame.sprite.Sprite):
    def __init__(self, name, pos, player_getting, room=(0, 0)):
        super().__init__()
        self.player_getting = player_getting
        self.name = name
        self.image = pygame.image.load(self.name + '.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        self.speed = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.lying = True
        self.room = room
        self.updating = True

    def update(self):
        if self.updating:
            if pygame.sprite.collide_mask(self, self.player_getting):
                self.add_to_inventory(player)
            if not self.lying:
                item_sprites.remove(self)
                return
        if self.room != floor.isaac_in:
            self.rect.center = (-1000000, -10000000)
            self.updating = False
        elif self.room == floor.isaac_in:
            self.rect.center = self.pos
            self.updating = True

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
        if -100 < player.rect.center[0] - self.rect.center[0] < 100 and -100 < player.rect.center[1] - self.rect.center[
            1] < 100:
            player.getting_damage(1)
        self.alive = False


class Room:  # class of rooms
    def __init__(self, type, coords, items=None, items_winning=None):
        self.type_of_room = type  # тип комнаты для будущей сокровищницы, магазина, комнаты босса...
        self.items_in_room = items
        self.items_for_clear = items_winning
        self.cleared = False  # зачищена ли комната

        self.y_of_room, self.x_of_room = coords
        self.up_door, self.bottom_door, self.right_door, self.left_door = False, False, False, False
        # уникальное для каждой комнаты наличие той или иной двери
        if self.y_of_room > 0:
            self.up_door = True
        if self.y_of_room < 4:
            self.bottom_door = True
        if self.x_of_room < 4:
            self.right_door = True
        if self.x_of_room > 0:
            self.left_door = True

    def update(self):
        self.items_in_room.update()
        if self.cleared:
            self.items_for_clear.update()


class Floor:  # класс обработка всех комнат вместе
    def __init__(self):
        # заполнение этажа комнатами
        self.floor = []
        for i in range(5):
            self.floor.append([])
            for j in range(5):
                self.floor[i].append(Room('default', (i, j)))

        # важная переменная показывающая в какой комнате находится айзек
        self.isaac_in = (2, 2)

        # Создание спрайтов дверей
        self.right_door = pygame.sprite.Sprite()
        self.right_door.image = pygame.image.load('right_door.png')
        self.right_door.image = pygame.transform.scale(self.right_door.image, (50, 100))
        self.right_door.rect = self.right_door.image.get_rect(topleft=(1150, 300))
        self.right_door.mask = pygame.mask.from_surface(self.right_door.image)
        door_sprites.add(self.right_door)

        self.left_door = pygame.sprite.Sprite()
        self.left_door.image = pygame.image.load('left_door.png')
        self.left_door.image = pygame.transform.scale(self.left_door.image, (50, 100))
        self.left_door.rect = self.left_door.image.get_rect(topleft=(0, 300))
        self.left_door.mask = pygame.mask.from_surface(self.left_door.image)
        door_sprites.add(self.left_door)

        self.up_door = pygame.sprite.Sprite()
        self.up_door.image = pygame.image.load('up_door.png')
        self.up_door.image = pygame.transform.scale(self.up_door.image, (100, 50))
        self.up_door.rect = self.up_door.image.get_rect(topleft=(550, 0))
        self.up_door.mask = pygame.mask.from_surface(self.up_door.image)
        door_sprites.add(self.up_door)

        self.bottom_door = pygame.sprite.Sprite()
        self.bottom_door.image = pygame.image.load('bottom_door.png')
        self.bottom_door.image = pygame.transform.scale(self.bottom_door.image, (100, 50))
        self.bottom_door.rect = self.bottom_door.image.get_rect(topleft=(550, 650))
        self.bottom_door.mask = pygame.mask.from_surface(self.bottom_door.image)
        door_sprites.add(self.bottom_door)

        self.changing_rooms_true = False

    def changing_rooms(self, direction):
        # изображение изменения комнаты
        background.rect.x += 100 * direction[0]
        background.rect.y += 100 * direction[1]

        changing_background.rect.x += 100 * direction[0]
        changing_background.rect.y += 100 * direction[1]
        if changing_background.rect.topleft == (0, 0):
            floor.changing_rooms_true = False
            background.rect = background.image.get_rect(topleft=(0, 0))

    def update(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # прописываем параметры игрока
        self.image = pygame.image.load('isaac_front.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 10
        self.change_room = False
        self.mask = pygame.mask.from_surface(self.image)

        self.inventory_bombs = 10  # кол-во бомб
        self.inventory_money = 0  # кол-во монет
        self.player_tear_kd = 0
        self.health = 6  # кол-во хп
        self.max_health = 6  # макс кол-во хп
        self.soul_health = 0  # сердца душ(если хочешь реализовать, то надо переписывать логику отображения сердец)
        self.is_updating = True

    def update(self):
        # ходьба
        if self.is_updating:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_d]:
                self.rect.x += self.speed
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_s]:
                self.rect.y += self.speed

            # ограничение по комнате
            if self.rect.centerx < 50:
                self.rect.centerx = 50
            if self.rect.centerx > 1150:
                self.rect.centerx = 1150
            if self.rect.centery < 50:
                self.rect.centery = 50
            if self.rect.centery > 605:
                self.rect.centery = 605

        if player.health < 1:  # проверка на закончившиеся хп
            player.dead()

    def dead(self):
        self.image = pygame.image.load('dead.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.is_updating = False

    def getting_damage(self, dmg):
        self.health -= dmg


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('monstro.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 3
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 3


class Tear(pygame.sprite.Sprite):
    def __init__(self, direction, *group):
        super().__init__(*group)
        # параметры слезы
        self.image = pygame.image.load('tear.png')
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.speed = 6
        # напрвление стрельбы
        if direction == 'left':
            self.direction = 'left'
        elif direction == 'right':
            self.direction = 'right'
        elif direction == 'up':
            self.direction = 'up'
        else:
            self.direction = 'down'

    def update(self):
        # движение стрельбы
        if self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed
        elif self.direction == 'up':
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed
        if self.rect.x < 50 or self.rect.x > 1150 or self.rect.y < 50 or self.rect.y > 650 or self.speed < 0:
            old_center = self.rect.center
            tear_sprites.remove(self)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('The Binding of Isaac')

    # экран
    screen_size = WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode(screen_size)

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tear_sprites = pygame.sprite.Group()
    door_sprites = pygame.sprite.Group()
    item_sprites = pygame.sprite.Group()
    bomb_sprites = pygame.sprite.Group()

    # ОБЪЕКТ ЭТАЖ
    floor = Floor()

    background = pygame.sprite.Sprite()
    background.image = pygame.image.load('room.png')
    background.image = pygame.transform.scale(background.image, (1200, 700))
    background.rect = background.image.get_rect(topleft=(0, 0))
    all_sprites.add(background)

    changing_background = pygame.sprite.Sprite()
    changing_background.image = pygame.image.load('room.png')
    changing_background.image = pygame.transform.scale(changing_background.image, (1200, 700))
    direction_of_changing = (1, 1)
    changing_background.rect = changing_background.image.get_rect(topleft=(-1200, 0))
    all_sprites.add(changing_background)

    # объект игрок
    player = Player(550, 300)
    all_sprites.add(player)

    # часики
    clock = pygame.time.Clock()

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
    player_tear_kd = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # стрельба
            if pygame.key.get_pressed()[pygame.K_LEFT] and player_tear_kd == 0 and player.is_updating:
                tear_sprites.add(Tear('left'))
                player_tear_kd = 60
            if pygame.key.get_pressed()[pygame.K_RIGHT] and player_tear_kd == 0 and player.is_updating:
                tear_sprites.add(Tear('right'))
                player_tear_kd = 60
            if pygame.key.get_pressed()[pygame.K_UP] and player_tear_kd == 0 and player.is_updating:
                tear_sprites.add(Tear('up'))
                player_tear_kd = 60
            if pygame.key.get_pressed()[pygame.K_DOWN] and player_tear_kd == 0 and player.is_updating:
                tear_sprites.add(Tear('down'))
                player_tear_kd = 60

            # бомбочка
            if pygame.key.get_pressed()[pygame.K_e] and player.inventory_bombs > 0 and player.is_updating:
                bomb_sprites.add(Bomb(player.rect.center[0], player.rect.center[1]))
                player.inventory_bombs -= 1

            # чит-клавиша
            if pygame.key.get_pressed()[pygame.K_p]:  # чит-клавиша(бета-тест)
                item_sprites.add(Item('bomb', (300, 300), player, room=(2, 2)))
                item_sprites.add(Item('Penny', (600, 300), player, room=(2, 2)))
                item_sprites.add(Item('Half_Red_Heart', (700, 300), player, room=(2, 2)))
                player.getting_damage(1)

            # проверка перехода в другую комнату
        if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].left_door is True and
                pygame.sprite.collide_mask(player, floor.left_door)):
            floor.isaac_in = (floor.isaac_in[0], floor.isaac_in[1] - 1)
            player.rect = player.image.get_rect(center=(1100, 350))
            player.change_room = True
            direction_of_changing = (1, 0)
            changing_background.rect = changing_background.image.get_rect(topleft=(-1200, 0))

        if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].right_door is True and
                pygame.sprite.collide_mask(player, floor.right_door)):
            floor.isaac_in = (floor.isaac_in[0], floor.isaac_in[1] + 1)
            player.rect = player.image.get_rect(center=(100, 350))
            player.change_room = True
            direction_of_changing = (-1, 0)
            changing_background.rect = changing_background.image.get_rect(topleft=(1200, 0))

        if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].up_door is True and
                pygame.sprite.collide_mask(player, floor.up_door)):
            floor.isaac_in = (floor.isaac_in[0] - 1, floor.isaac_in[1])
            player.rect = player.image.get_rect(center=(600, 600))
            player.change_room = True
            direction_of_changing = (0, 1)
            changing_background.rect = changing_background.image.get_rect(topleft=(0, -700))

        if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].bottom_door is True and
                pygame.sprite.collide_mask(player, floor.bottom_door)):
            floor.isaac_in = (floor.isaac_in[0] + 1, floor.isaac_in[1])
            player.rect = player.image.get_rect(center=(600, 100))
            player.change_room = True
            direction_of_changing = (0, -1)
            changing_background.rect = changing_background.image.get_rect(topleft=(0, 700))

            # переход в другую комнату
        if player.change_room:
            door_sprites.remove(floor.up_door, floor.left_door, floor.bottom_door, floor.right_door)
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].left_door:
                door_sprites.add(floor.left_door)
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].right_door:
                door_sprites.add(floor.right_door)
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].up_door:
                door_sprites.add(floor.up_door)
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].bottom_door:
                door_sprites.add(floor.bottom_door)
            player.change_room = False
            floor.changing_rooms_true = True

        if floor.changing_rooms_true:
            floor.changing_rooms(direction_of_changing)

        # апдейты всех спрайтов
        all_sprites.update()
        tear_sprites.update()
        bomb_sprites.update()
        item_sprites.update()

        # отрисовка всех деталей
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        bomb_counter = bomb_counter_font.render(str(player.inventory_bombs), True, 'WHITE')
        screen.blit(bomb_counter, (50, 50))
        money_counter = money_counter_font.render(str(player.inventory_money), True, 'WHITE')
        screen.blit(money_counter, (50, 100))
        door_sprites.draw(screen)
        tear_sprites.draw(screen)
        bomb_sprites.draw(screen)
        item_sprites.draw(screen)
        screen.blit(bomb_icon, (0, 50))
        screen.blit(money_icon, (0, 100))
        draw_health_bar(0, 0, player.health, player.max_health)
        pygame.display.flip()

        # кд стрельбы игрока(оно вообще работает?)
        if player_tear_kd > 0:
            player_tear_kd -= 10
        clock.tick(60)

    pygame.quit()

