from random import randint, choice
import pygame as pygame

# Загрузка изображений сердца
heart_full = pygame.image.load("heart_full.png")
heart_half = pygame.image.load("heart_half.png")
heart_empty = pygame.image.load("heart_empty.png")
heart_full = pygame.transform.scale(heart_full, (50, 50))
heart_half = pygame.transform.scale(heart_half, (50, 50))
heart_empty = pygame.transform.scale(heart_empty, (50, 50))

# Загрузка иконок комнат
im_seen_room = pygame.image.load('seen_room_icon.png')
im_seen_room = pygame.transform.scale(im_seen_room, (40, 32))
im_not_seen_room = pygame.image.load('not_seen_room_icon.png')
im_not_seen_room = pygame.transform.scale(im_not_seen_room, (40, 32))
im_now_room = pygame.image.load('now_room_icon.png')
im_now_room = pygame.transform.scale(im_now_room, (40, 32))

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
        self.image = pygame.image.load('data/' + self.name + '.png')
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
        elif self.name == 'speed_potion':
            player_getting.speed += 1
        elif self.name == 'strength_potion':
            player_getting.shoot_dmg += 1
        elif self.name == 'damage_potion':
            player_getting.health -= 1
        elif self.name == 'size_potion':
            player_getting.tear_size[0] += 5
            player_getting.tear_size[1] += 5
        else:
            pass
        self.lying = False


class Bomb(pygame.sprite.Sprite):
    def __init__(self, radius=10, explosion_radius=50, damage=20, speed=0):
        super().__init__()

        # Основные параметры бомбы
        self.image = pygame.image.load('data/bomb.png')
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
        if (-100 < player.rect.center[0] - self.rect.center[0] < 100 and -100 <
                player.rect.center[1] - self.rect.center[1] < 100):
            player.getting_damage(1)
        self.alive = False


class Room:  # class of rooms
    def __init__(self, type, coords, items=None, items_winning=None):
        self.items_in_room = items
        self.items_for_clear = items_winning
        self.room_enemies = []
        self.fulled = False  # заполнение комнаты врагами
        self.type = type
        self.y_of_room, self.x_of_room = coords
        self.up_door, self.bottom_door, self.right_door, self.left_door = False, False, False, False
        if self.type == 'enemy':
            self.open_up_door, self.open_bottom_door, self.open_right_door, self.open_left_door = False, False, False, False
            self.cleared = False
        else:
            self.open_up_door, self.open_bottom_door, self.open_right_door, self.open_left_door = True, True, True, True
            self.cleared = True
        # уникальное для каждой комнаты наличие той или иной двери
        if self.y_of_room > 0:
            self.up_door = True
        if self.y_of_room < 4:
            self.bottom_door = True
        if self.x_of_room < 4:
            self.right_door = True
        if self.x_of_room > 0:
            self.left_door = True
        if self.type == 'enemy':
            for i in range(randint(1, 5)):
                self.room_enemies.append(
                    choice([Enemy(randint(100, 1100), randint(100, 600)), Horf(randint(100, 1100), randint(100, 600))]))

    def room_update(self):
        # Самостоятельный апдейт комнаты, обновляется только текущая комната
        # Здесь прописано заполнение комнаты врагами и открытие закрытие дверей
        if self.type == 'enemy':
            if floor.isaac_in[0] == self.y_of_room and floor.isaac_in[1] == self.x_of_room:
                if not self.cleared:
                    if not self.fulled:
                        for i in self.room_enemies:
                            enemy_sprites.add(i)
                        self.fulled = True
                        floor.left_door.image = pygame.image.load('closed_left_door.png')
                        floor.right_door.image = pygame.image.load('closed_right_door.png')
                        floor.up_door.image = pygame.image.load('closed_up_door.png')
                        floor.bottom_door.image = pygame.image.load('closed_bottom_door.png')
                else:
                    self.open_up_door, self.open_bottom_door, self.open_right_door, self.open_left_door = True, True, True, True
                    floor.left_door.image = pygame.image.load('open_left_door.png')
                    floor.right_door.image = pygame.image.load('open_right_door.png')
                    floor.up_door.image = pygame.image.load('open_up_door.png')
                    floor.bottom_door.image = pygame.image.load('open_bottom_door.png')
            if not bool(self.room_enemies):
                self.cleared = True
            else:
                self.cleared = False
                floor.left_door.image = pygame.image.load('closed_left_door.png')
                floor.right_door.image = pygame.image.load('closed_right_door.png')
                floor.up_door.image = pygame.image.load('closed_up_door.png')
                floor.bottom_door.image = pygame.image.load('closed_bottom_door.png')


class Floor:  # класс обработка всех комнат вместе
    def __init__(self):
        # заполнение этажа комнатами
        self.floor = []
        for i in range(5):
            self.floor.append([])
            for j in range(5):
                if i == 2 and j == 2:
                    self.floor[i].append(Room('default', (i, j)))
                else:
                    self.floor[i].append(Room(choice(['default', 'enemy', 'enemy']), (i, j)))
        self.icon_map = []
        for i in range(5):
            self.icon_map.append([])
            for j in range(5):
                if i == 2 and j == 2:
                    self.icon_map[i].append(MapIcon(2, 2, type='start'))
                else:
                    self.icon_map[i].append(MapIcon(i, j))
                map_icons_sprites.add(self.icon_map[i][j])

        # важная переменная показывающая в какой комнате находится айзек
        self.isaac_in = (2, 2)

        # Создание спрайтов дверей
        self.right_door = pygame.sprite.Sprite()
        self.right_door.image = pygame.image.load('open_right_door.png')
        self.right_door.image = pygame.transform.scale(self.right_door.image, (50, 100))
        self.right_door.rect = self.right_door.image.get_rect(topleft=(1150, 300))
        self.right_door.mask = pygame.mask.from_surface(self.right_door.image)
        door_sprites.add(self.right_door)

        self.left_door = pygame.sprite.Sprite()
        self.left_door.image = pygame.image.load('open_left_door.png')
        self.left_door.image = pygame.transform.scale(self.left_door.image, (50, 100))
        self.left_door.rect = self.left_door.image.get_rect(topleft=(0, 300))
        self.left_door.mask = pygame.mask.from_surface(self.left_door.image)
        door_sprites.add(self.left_door)

        self.up_door = pygame.sprite.Sprite()
        self.up_door.image = pygame.image.load('open_up_door.png')
        self.up_door.image = pygame.transform.scale(self.up_door.image, (100, 50))
        self.up_door.rect = self.up_door.image.get_rect(topleft=(550, 0))
        self.up_door.mask = pygame.mask.from_surface(self.up_door.image)
        door_sprites.add(self.up_door)

        self.bottom_door = pygame.sprite.Sprite()
        self.bottom_door.image = pygame.image.load('open_bottom_door.png')
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

    def changing_map_icons(self, next_room):
        icon = self.icon_map[self.isaac_in[0]][self.isaac_in[1]]
        icon.image = im_seen_room
        icon.type = 'seen'
        next_icon = self.icon_map[self.isaac_in[0] + next_room[0]][self.isaac_in[1] + next_room[1]]
        next_icon.image = im_now_room

    def update(self):
        pass


class MapIcon(pygame.sprite.Sprite):
    def __init__(self, x, y, type='non_seen'):
        super().__init__()
        self.type = type
        if self.type == 'start':
            self.image = im_now_room
            self.type = 'non_seen'
        else:
            self.image = im_not_seen_room
        self.rect = self.image.get_rect(topleft=(960 + 45 * y, 20 + 37 * x))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, type, speed, bombs, kd, health, damage):
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
        self.max_health = 10  # макс кол-во хп
        self.soul_health = 0  # сердца душ(если хочешь реализовать, то надо переписывать логику отображения сердец)
        self.is_updating = True
        self.shoot_dmg = 1
        self.tear_size = (50, 50)

    def update(self):
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
        self.image = pygame.image.load('gaper.png')
        self.image = pygame.transform.scale(self.image, (112, 132))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 3
        self.damaging_kd_short_range = 300
        self.shooting_kd = 600
        self.dmg_shooting = 1

    def moving(self, player):
        if player.rect.x > self.rect.x:
            self.rect.x += self.speed
        if player.rect.x < self.rect.x:
            self.rect.x -= self.speed
        if player.rect.y > self.rect.y:
            self.rect.y += self.speed
        if player.rect.y < self.rect.y:
            self.rect.y -= self.speed
        # ограничение по комнате
        if self.rect.centerx < 50:
            self.rect.centerx = 50
        if self.rect.centerx > 1150:
            self.rect.centerx = 1150
        if self.rect.centery < 50:
            self.rect.centery = 50
        if self.rect.centery > 605:
            self.rect.centery = 605

    def shooting(self, player):
        if int(player.rect.x) > int(self.rect.x) and abs(int(player.rect.x) - int(self.rect.x)) > abs(
                int(player.rect.y) - int(self.rect.y)):
            tear_sprites.add(Tear('right', self.dmg_shooting, is_enemy=True, coords=self.rect.center))
        if int(player.rect.x) < int(self.rect.x) and abs(int(player.rect.x) - int(self.rect.x)) > abs(
                int(player.rect.y) - int(self.rect.y)):
            tear_sprites.add(Tear('left', self.dmg_shooting, is_enemy=True, coords=self.rect.center))
        if int(player.rect.y) > int(self.rect.y) and abs(int(player.rect.x) - int(self.rect.x)) < abs(
                int(player.rect.y) - int(self.rect.y)):
            tear_sprites.add(Tear('down', self.dmg_shooting, is_enemy=True, coords=self.rect.center))
        if int(player.rect.y) < int(self.rect.y) and abs(int(player.rect.x) - int(self.rect.x)) < abs(
                int(player.rect.y) - int(self.rect.y)):
            tear_sprites.add(Tear('up', self.dmg_shooting, is_enemy=True, coords=self.rect.center))

    def update(self):
        if pygame.sprite.collide_mask(self, player) and self.damaging_kd_short_range == 0:
            player.getting_damage(1)
            self.damaging_kd_short_range = 600
        if self.damaging_kd_short_range > 0:
            self.damaging_kd_short_range -= 10
        if self.shooting_kd > -20:
            self.shooting_kd -= 10
        if self.shooting_kd < 0:
            self.shooting(player)
            self.shooting_kd = 600
        if self.health < 1:  # проверка на закончившиеся хп
            del floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_enemies[
                floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_enemies.index(self)]
            self.kill()
        self.moving(player)

    def getting_damage(self, dmg):
        self.health -= dmg


class Tear(pygame.sprite.Sprite):
    def __init__(self, direction, damage, is_enemy=False, coords=None, size=(40, 40), *group):
        super().__init__(*group)
        # параметры слезы
        if not is_enemy:
            self.image = pygame.image.load('tear.png')
        else:
            self.image = pygame.image.load('tear2.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        if not is_enemy:
            self.rect.center = player.rect.center
            self.image = pygame.transform.scale(self.image, size)
        else:
            self.rect.center = coords
        self.speed = 6
        self.is_enemy = is_enemy
        self.mask = pygame.mask.from_surface(self.image)
        # напрвление стрельбы
        if direction == 'left':
            self.direction = 'left'
        elif direction == 'right':
            self.direction = 'right'
        elif direction == 'up':
            self.direction = 'up'
        else:
            self.direction = 'down'
        self.dmg = damage

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
            tear_sprites.remove(self)
        # столкновения(дописать урон)
        if pygame.sprite.collide_mask(self, player) and self.is_enemy:
            player.getting_damage(self.dmg)
            self.kill()
        for j in enemy_sprites:
            if pygame.sprite.collide_mask(self, j) and not self.is_enemy:
                j.getting_damage(self.dmg)
                self.kill()
        if floor.changing_rooms_true:
            self.kill()


class Horf(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('Horf.png')
        self.image = pygame.transform.scale(self.image, (112, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 4
        self.damaging_kd_short_range = 300
        self.shooting_kd = 600
        self.dmg_shooting = 2


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
    enemy_sprites = pygame.sprite.Group()
    map_icons_sprites = pygame.sprite.Group()

    # ОБЪЕКТ ЭТАЖ
    floor = Floor()

    # спрайт заднего фона
    background = pygame.sprite.Sprite()
    background.image = pygame.image.load('room.png')
    background.image = pygame.transform.scale(background.image, (1200, 700))
    background.rect = background.image.get_rect(topleft=(0, 0))
    all_sprites.add(background)

    # спрайт сменяющевого фона
    changing_background = pygame.sprite.Sprite()
    changing_background.image = pygame.image.load('room.png')
    changing_background.image = pygame.transform.scale(changing_background.image, (1200, 700))
    direction_of_changing = (1, 1)
    changing_background.rect = changing_background.image.get_rect(topleft=(-1200, 0))
    all_sprites.add(changing_background)

    # объект игрок
    player = Player(550, 300, 'isaac', 10, 10, 0, 3, 3)
    all_sprites.add(player)

    # часики
    clock = pygame.time.Clock()

    bomb_icon = pygame.image.load('data/bomb.png')
    bomb_icon = pygame.transform.scale(bomb_icon, (50, 50))
    bomb_counter_font = pygame.font.SysFont("Times New Roman", 50)
    money_counter_font = pygame.font.SysFont("Times New Roman", 50)
    money_icon = pygame.image.load('data/Penny.png')
    money_icon = pygame.transform.scale(money_icon, (50, 50))
    health_empty_icon = pygame.image.load('heart_empty.png')
    health_empty_icon = pygame.transform.scale(health_empty_icon, (50, 50))
    health_half_icon = pygame.image.load('heart_half.png')
    health_half_icon = pygame.transform.scale(health_half_icon, (50, 50))
    health_full_icon = pygame.image.load('heart_full.png')
    health_full_icon = pygame.transform.scale(health_full_icon, (50, 50))

    first_page = pygame.image.load('repentance.png')
    menu = pygame.image.load('menu.png')

    running = True
    player_tear_kd = 0
    map_show = False
    start_restart = False
    first_entry = True

    font = pygame.font.Font(None, 30)

    intro_text = ['Нажмите ENTER чтобы начать игру, чтобы выйти ESCAPE',
                  'Перед выходом из игры сохраните накопившиеся результаты', '', 'Управление персонажем WASD',
                  'Атака через кнопки вверх вниз вправо влево', '',
                  'Начните новую игру или выберите сохранённую версию']

    # Игровой цикл
    while running:
        if start_restart:
            if player.is_updating:
                # ходьба с зажатием клавиши
                if pygame.key.get_pressed()[pygame.K_a]:
                    player.rect.x -= player.speed
                if pygame.key.get_pressed()[pygame.K_d]:
                    player.rect.x += player.speed
                if pygame.key.get_pressed()[pygame.K_w]:
                    player.rect.y -= player.speed
                if pygame.key.get_pressed()[pygame.K_s]:
                    player.rect.y += player.speed

                # Стрельба очередью зажатием клавиши
                if pygame.key.get_pressed()[pygame.K_LEFT] and player_tear_kd == 0:
                    tear_sprites.add(Tear('left', player.shoot_dmg))
                    player_tear_kd = 90
                if pygame.key.get_pressed()[pygame.K_RIGHT] and player_tear_kd == 0:
                    tear_sprites.add(Tear('right', player.shoot_dmg))
                    player_tear_kd = 90
                if pygame.key.get_pressed()[pygame.K_UP] and player_tear_kd == 0:
                    tear_sprites.add(Tear('up', player.shoot_dmg))
                    player_tear_kd = 90
                if pygame.key.get_pressed()[pygame.K_DOWN] and player_tear_kd == 0:
                    tear_sprites.add(Tear('down', player.shoot_dmg))
                    player_tear_kd = 90

            # только одноразовые действия требующие одного нажатия
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # бомбочка
                    if event.key == pygame.K_e and player.inventory_bombs > 0 and player.is_updating:
                        bomb_sprites.add(Bomb(player.rect.center[0], player.rect.center[1]))
                        player.inventory_bombs -= 1

                    # чит-клавиша
                    if event.key == pygame.K_p:  # чит-клавиша(бета-тест)
                        item_sprites.add(Item('bomb', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))
                        item_sprites.add(Item('Penny', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))
                        item_sprites.add(Item('Red_Heart', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))
                        floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_enemies.append(Enemy(randint(100, 900),
                                                                                                    randint(200, 500)))
                        enemy_sprites.add(floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_enemies[-1])

                    # вызов мини-карты
                    if event.key == pygame.K_TAB:
                        if map_show:
                            map_show = False
                        else:
                            map_show = True

                    # Выход в главное меню
                    if event.key == pygame.K_ESCAPE:
                        start_restart = False

            # непопадает под условия выше, обновления в течение цикла
            # проверка перехода в другую комнату
            # важно также проверка на зачистку комнаты
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].cleared:
                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].left_door is True and
                        pygame.sprite.collide_mask(player, floor.left_door)):
                    floor.changing_map_icons((0, -1))
                    floor.isaac_in = (floor.isaac_in[0], floor.isaac_in[1] - 1)
                    player.rect = player.image.get_rect(center=(1100, 350))
                    player.change_room = True
                    direction_of_changing = (1, 0)
                    changing_background.rect = changing_background.image.get_rect(topleft=(-1200, 0))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].right_door is True and
                        pygame.sprite.collide_mask(player, floor.right_door)):
                    floor.changing_map_icons((0, 1))
                    floor.isaac_in = (floor.isaac_in[0], floor.isaac_in[1] + 1)
                    player.rect = player.image.get_rect(center=(100, 350))
                    player.change_room = True
                    direction_of_changing = (-1, 0)
                    changing_background.rect = changing_background.image.get_rect(topleft=(1200, 0))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].up_door is True and
                        pygame.sprite.collide_mask(player, floor.up_door)):
                    floor.changing_map_icons((-1, 0))
                    floor.isaac_in = (floor.isaac_in[0] - 1, floor.isaac_in[1])
                    player.rect = player.image.get_rect(center=(600, 600))
                    player.change_room = True
                    direction_of_changing = (0, 1)
                    changing_background.rect = changing_background.image.get_rect(topleft=(0, -700))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].bottom_door is True and
                        pygame.sprite.collide_mask(player, floor.bottom_door)):
                    floor.changing_map_icons((1, 0))
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

            floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_update()

            # апдейты всех спрайтов
            all_sprites.update()
            tear_sprites.update()
            bomb_sprites.update()
            item_sprites.update()
            enemy_sprites.update()
            floor.update()

            # отрисовка всех деталей
            screen.fill((0, 0, 0))
            all_sprites.draw(screen)
            bomb_counter = bomb_counter_font.render(str(player.inventory_bombs), True, 'WHITE')
            screen.blit(bomb_counter, (50, 50))
            money_counter = money_counter_font.render(str(player.inventory_money), True, 'WHITE')
            screen.blit(money_counter, (50, 100))
            enemy_sprites.draw(screen)
            door_sprites.draw(screen)
            tear_sprites.draw(screen)
            bomb_sprites.draw(screen)
            item_sprites.draw(screen)
            if map_show:
                map_icons_sprites.draw(screen)
            screen.blit(bomb_icon, (0, 50))
            screen.blit(money_icon, (0, 100))
            draw_health_bar(0, 0, player.health, player.max_health)
            # кд стрельбы игрока
            if player_tear_kd > 0:
                player_tear_kd -= 10
            clock.tick(60)
        elif first_entry:
            screen.blit(first_page, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        first_entry = False
                if event.type == pygame.QUIT:
                    running = False
        else:
            screen.blit(menu, (0, 0))
            text_coord = 10
            for line in intro_text:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 10
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        start_restart = True
                    if event.key == pygame.K_n:
                        # общие свойства
                        player_tear_kd = 0
                        map_show = False

                        # группы спрайтов
                        all_sprites = pygame.sprite.Group()
                        tear_sprites = pygame.sprite.Group()
                        door_sprites = pygame.sprite.Group()
                        item_sprites = pygame.sprite.Group()
                        bomb_sprites = pygame.sprite.Group()
                        enemy_sprites = pygame.sprite.Group()
                        map_icons_sprites = pygame.sprite.Group()

                        # спрайт заднего фона
                        background = pygame.sprite.Sprite()
                        background.image = pygame.image.load('room.png')
                        background.image = pygame.transform.scale(background.image, (1200, 700))
                        background.rect = background.image.get_rect(topleft=(0, 0))
                        all_sprites.add(background)

                        # спрайт сменяющевого фона
                        changing_background = pygame.sprite.Sprite()
                        changing_background.image = pygame.image.load('room.png')
                        changing_background.image = pygame.transform.scale(changing_background.image, (1200, 700))
                        direction_of_changing = (1, 1)
                        changing_background.rect = changing_background.image.get_rect(topleft=(-1200, 0))
                        all_sprites.add(changing_background)

                        # ОБЪЕКТ ЭТАЖ
                        floor = Floor()
                        player = Player(550, 300, 'isaac', 10, 10, 0, 3, 3)
                        all_sprites.add(player)

                        start_restart = True
                if event.type == pygame.QUIT:
                    running = False
        pygame.display.flip()
    pygame.quit()
