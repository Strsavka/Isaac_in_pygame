from random import randint, choice
import pygame as pygame
import sqlite3

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

floor_exit = pygame.sprite.Sprite()
floor_exit.image = pygame.image.load('open_up_door.png')
floor_exit.image = pygame.transform.scale(floor_exit.image, (100, 100))
floor_exit.rect = floor_exit.image.get_rect(center=(600, 350))
floor_exit.mask = pygame.mask.from_surface(floor_exit.image)

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


class Game:
    def __init__(self):
        # общие свойства
        self.map_show = False

        # группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.tear_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.bomb_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.map_icons_sprites = pygame.sprite.Group()
        self.exit_sprite = pygame.sprite.Group()

        self.exit_sprite.add(floor_exit)

        # стандартные значения в датабазу
        (self.base_hearts, self.base_level_of_enemies, self.base_speed, self.base_bombs, self.base_coins,
         self.base_firing_rate, self.base_type_of_player, self.base_tear_damage, self.first_win_streak,
         self.type_of_game, self.id, self.tear_size) = (3, 1, 6, 1, 5, 360, 'isaac', 1, 0, 'новая', 0, 50)

        # спрайт заднего фона
        self.background = pygame.sprite.Sprite()
        self.background.image = pygame.image.load('room.png')
        self.background.image = pygame.transform.scale(self.background.image, (1200, 700))
        self.background.rect = self.background.image.get_rect(topleft=(0, 0))
        self.all_sprites.add(self.background)

        self.list_of_room = ['enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy',
                             'enemy', 'enemy', 'enemy', 'enemy', 'default', 'default', 'default', 'default', 'default',
                             'default', 'default', 'default', 'boss', 'default']

        # спрайт сменяющевого фона
        self.changing_background = pygame.sprite.Sprite()
        self.changing_background.image = pygame.image.load('room.png')
        self.changing_background.image = pygame.transform.scale(self.changing_background.image, (1200, 700))
        self.changing_background.rect = self.changing_background.image.get_rect(topleft=(-1200, 0))
        self.all_sprites.add(self.changing_background)

        self.game_ended = False



    def update_game(self):
        # общие свойства
        self.map_show = False

        # группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.tear_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        self.bomb_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.map_icons_sprites = pygame.sprite.Group()

        # спрайт заднего фона
        self.background = pygame.sprite.Sprite()
        self.background.image = pygame.image.load('room.png')
        self.background.image = pygame.transform.scale(self.background.image, (1200, 700))
        self.background.rect = self.background.image.get_rect(topleft=(0, 0))
        self.all_sprites.add(self.background)

        # спрайт сменяющевого фона
        self.changing_background = pygame.sprite.Sprite()
        self.changing_background.image = pygame.image.load('room.png')
        self.changing_background.image = pygame.transform.scale(self.changing_background.image, (1200, 700))
        direction_of_changing = (1, 1)
        self.changing_background.rect = self.changing_background.image.get_rect(topleft=(-1200, 0))
        self.all_sprites.add(self.changing_background)

        self.list_of_room = ['enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy', 'enemy',
                             'enemy', 'enemy', 'enemy', 'enemy', 'default', 'default', 'default', 'default', 'default',
                             'default', 'default', 'default', 'boss', 'default']


game = Game()


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
                game.item_sprites.remove(self)
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
            player_getting.tear_size = (int(player_getting.tear_size[0] + 1), int(player_getting.tear_size[1] + 1))
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
            game.bomb_sprites.remove(self)
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
        self.items_getted = False
        self.type = type
        self.once = True
        self.coords = coords
        self.y_of_room, self.x_of_room = coords
        self.up_door, self.bottom_door, self.right_door, self.left_door = False, False, False, False
        if self.type == 'enemy' or self.type == 'boss':
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
        if self.type == 'boss':
            self.room_enemies.append(Boss(600, 350))

    def room_update(self):
        # Самостоятельный апдейт комнаты, обновляется только текущая комната
        # Здесь прописано заполнение комнаты врагами и открытие закрытие дверей
        if self.type == 'enemy' or self.type == 'boss':
            if floor.isaac_in[0] == self.y_of_room and floor.isaac_in[1] == self.x_of_room:
                if not self.cleared:
                    if not self.fulled:
                        for i in self.room_enemies:
                            game.enemy_sprites.add(i)
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
            if self.cleared and (self.type == 'enemy' or self.type == 'boss'):
                if self.once:
                    for i in range(2):
                        game.item_sprites.add(Item('Red_Heart', (randint(100, 1100), randint(100, 600)), player,
                                                   room=(self.y_of_room, self.x_of_room)))
                        game.item_sprites.add(
                            choice([Item('speed_potion', (randint(100, 1100), randint(100, 600)),
                                         player, room=(self.y_of_room, self.x_of_room)),
                                    Item('size_potion', (randint(100, 1100), randint(100, 600)),
                                         player, room=(self.y_of_room, self.x_of_room)),
                                    Item('strength_potion', (randint(100, 1100), randint(100, 600)),
                                         player, room=(self.y_of_room, self.x_of_room)),
                                    Item('damage_potion', (randint(100, 1100), randint(100, 600)),
                                         player, room=(self.y_of_room, self.x_of_room))]))
                    if self.type == 'boss':
                        for i in range(5):
                            game.item_sprites.add(
                                choice([Item('speed_potion', (randint(100, 1100), randint(100, 600)),
                                             player, room=(self.y_of_room, self.x_of_room)),
                                        Item('size_potion', (randint(100, 1100), randint(100, 600)),
                                             player, room=(self.y_of_room, self.x_of_room)),
                                        Item('strength_potion', (randint(100, 1100), randint(100, 600)),
                                             player, room=(self.y_of_room, self.x_of_room)),
                                        Item('damage_potion', (randint(100, 1100), randint(100, 600)),
                                             player, room=(self.y_of_room, self.x_of_room))]))
                    self.once = False


class Trader(pygame.sprite.Sprite):
    def __init__(self, pos, room=(0, 0)):
        super().__init__()
        self.image = pygame.image.load('data/trader.png')
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = pos
        self.mask = pygame.mask.from_surface(self.image)
        self.room = room

    def update(self):
        if self.room != floor.isaac_in:
            self.rect.center = (-1000000, -10000000)
        elif self.room == floor.isaac_in:
            self.rect.center = self.pos


class ItemTrade(Item):
    def add_to_inventory(self, player_getting):
        if self.name == 'bomb':
            if player_getting.inventory_money >= 2:
                player_getting.inventory_bombs += 1
                player_getting.inventory_money -= 2
                self.lying = False
        elif self.name == 'Red_Heart':
            if player_getting.inventory_money >= 5:
                if player_getting.health + 1 <= player_getting.max_health:
                    player_getting.health += 1
                    if player_getting.health + 1 <= player_getting.max_health:
                        player_getting.health += 1
                player_getting.inventory_money -= 5
                self.lying = False
        elif self.name == 'Half_Red_Heart':
            if player_getting.inventory_money >= 3:
                if player_getting.health + 1 <= player_getting.max_health:
                    player_getting.health += 1
                player_getting.inventory_money -= 3
                self.lying = False
        elif self.name == 'speed_potion':
            if player_getting.inventory_money >= 10:
                player_getting.speed += 1
                player_getting.inventory_money -= 10
                self.lying = False
        elif self.name == 'strength_potion':
            if player_getting.inventory_money >= 10:
                player_getting.shoot_dmg += 1
                player_getting.inventory_money -= 10
                self.lying = False
        elif self.name == 'damage_potion':
            if player_getting.inventory_money >= 10:
                player_getting.health -= 1
                player_getting.inventory_money -= 10
                self.lying = False
        elif self.name == 'size_potion':
            if player_getting.inventory_money >= 10:
                player_getting.tear_size = tuple(
                    [player_getting.tear_size[0] + 10, player_getting.tear_size[1] + 10])
                player_getting.inventory_money -= 10
                self.lying = False
        else:
            pass


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
                    room = choice(game.list_of_room)
                    if room == 'boss':
                        self.boss_room = (i, j)
                    del game.list_of_room[game.list_of_room.index(room)]
                    self.floor[i].append(Room(room, (i, j)))
        self.icon_map = []
        for i in range(5):
            self.icon_map.append([])
            for j in range(5):
                if i == 2 and j == 2:
                    self.icon_map[i].append(MapIcon(2, 2, type='start'))
                else:
                    self.icon_map[i].append(MapIcon(i, j))
                game.map_icons_sprites.add(self.icon_map[i][j])

        # важная переменная показывающая в какой комнате находится айзек
        self.isaac_in = (2, 2)

        # Создание спрайтов дверей
        self.right_door = pygame.sprite.Sprite()
        self.right_door.image = pygame.image.load('open_right_door.png')
        self.right_door.image = pygame.transform.scale(self.right_door.image, (50, 100))
        self.right_door.rect = self.right_door.image.get_rect(topleft=(1150, 300))
        self.right_door.mask = pygame.mask.from_surface(self.right_door.image)
        game.door_sprites.add(self.right_door)

        self.left_door = pygame.sprite.Sprite()
        self.left_door.image = pygame.image.load('open_left_door.png')
        self.left_door.image = pygame.transform.scale(self.left_door.image, (50, 100))
        self.left_door.rect = self.left_door.image.get_rect(topleft=(0, 300))
        self.left_door.mask = pygame.mask.from_surface(self.left_door.image)
        game.door_sprites.add(self.left_door)

        self.up_door = pygame.sprite.Sprite()
        self.up_door.image = pygame.image.load('open_up_door.png')
        self.up_door.image = pygame.transform.scale(self.up_door.image, (100, 50))
        self.up_door.rect = self.up_door.image.get_rect(topleft=(550, 0))
        self.up_door.mask = pygame.mask.from_surface(self.up_door.image)
        game.door_sprites.add(self.up_door)

        self.bottom_door = pygame.sprite.Sprite()
        self.bottom_door.image = pygame.image.load('open_bottom_door.png')
        self.bottom_door.image = pygame.transform.scale(self.bottom_door.image, (100, 50))
        self.bottom_door.rect = self.bottom_door.image.get_rect(topleft=(550, 650))
        self.bottom_door.mask = pygame.mask.from_surface(self.bottom_door.image)
        game.door_sprites.add(self.bottom_door)

        self.changing_rooms_true = False

    def changing_rooms(self, direction):
        # изображение изменения комнаты
        game.background.rect.x += 100 * direction[0]
        game.background.rect.y += 100 * direction[1]

        game.changing_background.rect.x += 100 * direction[0]
        game.changing_background.rect.y += 100 * direction[1]
        if game.changing_background.rect.topleft == (0, 0):
            floor.changing_rooms_true = False
            game.background.rect = game.background.image.get_rect(topleft=(0, 0))

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
    def __init__(self, x, y, type, speed, bombs, kd, health, damage, tear_size=(50, 50)):
        super().__init__()
        # прописываем параметры игрока
        if type == 'azazel':
            self.image = pygame.image.load('azazel.png')
            self.image = pygame.transform.scale(self.image, (100, 100))
        else:
            self.image = pygame.image.load('isaac_front.png')
            self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.change_room = False
        self.mask = pygame.mask.from_surface(self.image)
        self.type = type
        self.inventory_bombs = bombs  # кол-во бомб
        self.inventory_money = 0  # кол-во монет
        self.player_tear_kd = 0
        self.health = health * 2  # кол-во хп
        self.max_health = health * 2  # макс кол-во хп
        self.is_updating = True
        self.shoot_dmg = damage
        self.tear_size = (tear_size, tear_size)
        self.player_is_dead = False

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
        self.player_is_dead = True

    def getting_damage(self, dmg):
        self.health -= dmg


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('gaper.png')
        self.image = pygame.transform.scale(self.image, (112, 132))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2 + game.base_level_of_enemies
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 3 + game.base_level_of_enemies
        self.damaging_kd_short_range = 300
        self.shooting_kd = 660 - 60 * game.base_level_of_enemies
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
            game.tear_sprites.add(Tear('right', self.dmg_shooting, is_enemy=True, coords=self.rect.center))

        if int(player.rect.x) < int(self.rect.x) and abs(int(player.rect.x) - int(self.rect.x)) > abs(
                int(player.rect.y) - int(self.rect.y)):
            game.tear_sprites.add(Tear('left', self.dmg_shooting, is_enemy=True, coords=self.rect.center))

        if int(player.rect.y) > int(self.rect.y) and abs(int(player.rect.x) - int(self.rect.x)) < abs(
                int(player.rect.y) - int(self.rect.y)):
            game.tear_sprites.add(Tear('down', self.dmg_shooting, is_enemy=True, coords=self.rect.center))

        if int(player.rect.y) < int(self.rect.y) and abs(int(player.rect.x) - int(self.rect.x)) < abs(
                int(player.rect.y) - int(self.rect.y)):
            game.tear_sprites.add(Tear('up', self.dmg_shooting, is_enemy=True, coords=self.rect.center))

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
            self.image = pygame.transform.scale(self.image, size)
            self.rect.center = player.rect.center
        else:
            self.rect.center = coords
        self.speed = 10
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
            game.tear_sprites.remove(self)
        # столкновения(дописать урон)
        if pygame.sprite.collide_mask(self, player) and self.is_enemy:
            player.getting_damage(self.dmg)
            self.kill()
        for j in game.enemy_sprites:
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
        self.health = 3 + game.base_level_of_enemies
        self.damaging_kd_short_range = 300
        self.shooting_kd = 660 - 60 * game.base_level_of_enemies
        self.dmg_shooting = 2


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('data/boss.png')
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 7
        self.mask = pygame.mask.from_surface(self.image)
        self.health = 100
        self.damaging_kd_short_range = 300
        self.shooting_kd = 1800
        self.dmg_shooting = 0

    def shooting(self, player):
        pass


def save_game():
    cur.execute('''UPDATE saves SET streak_of_win = ? WHERE id = ?''',
                (game.first_win_streak, game.id))
    cur.execute('''UPDATE saves SET speed = ? WHERE id = ?''', (player.speed, game.id))
    cur.execute('''UPDATE saves SET hearts = ? WHERE id = ?''',
                (player.max_health / 2, game.id))
    cur.execute('''UPDATE saves SET firing_rate = ? WHERE id = ?''',
                (game.base_firing_rate, game.id))
    cur.execute('''UPDATE saves SET tear_damage = ? WHERE id = ?''',
                (player.shoot_dmg, game.id))
    cur.execute('''UPDATE saves SET bombs = ? WHERE id = ?''',
                (player.inventory_bombs, game.id))
    cur.execute('''UPDATE saves SET money = ? WHERE id = ?''',
                (player.inventory_money, game.id))
    cur.execute('''UPDATE saves SET level_of_hardness = ? WHERE id = ?''',
                (game.base_level_of_enemies, game.id))
    cur.execute('''UPDATE saves SET tear_size = ? WHERE id = ?''',
                (player.tear_size[0], game.id))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('The Binding of Isaac')

    # основной класс игры содержащий важные переменные для обновления данных, сохранения и загрузки при новой игре
    game = Game()

    # экран
    screen_size = WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode(screen_size)

    floor = Floor()

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
    start_restart = False
    first_entry = True
    player_kd = 0

    con = sqlite3.connect('saves.sqlite')
    cur = con.cursor()

    sd = 0

    font = pygame.font.Font(None, 30)

    intro_text = ['Нажмите ENTER чтобы начать игру,', 'чтобы выйти в меню - ESCAPE', '', 'Управление персонажем WASD',
                  'Атака через кнопки вверх вниз вправо влево', '',
                  'Начните новую игру или выберите сохранённую версию',
                  'Для перемотки используйте стрелки вправо/влево', '', 'Чтобы удалить нажмите DELETE', '',
                  'Чтобы изменить уровень сложности на загруженной игре', 'используйте вверх/вниз']

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
                if pygame.key.get_pressed()[pygame.K_LEFT] and player_kd == 0:
                    game.tear_sprites.add(Tear('left', player.shoot_dmg, size=player.tear_size))
                    player_kd = game.base_firing_rate
                if pygame.key.get_pressed()[pygame.K_RIGHT] and player_kd == 0:
                    game.tear_sprites.add(Tear('right', player.shoot_dmg, size=player.tear_size))
                    player_kd = game.base_firing_rate
                if pygame.key.get_pressed()[pygame.K_UP] and player_kd == 0:
                    game.tear_sprites.add(Tear('up', player.shoot_dmg, size=player.tear_size))
                    player_kd = game.base_firing_rate
                if pygame.key.get_pressed()[pygame.K_DOWN] and player_kd == 0:
                    game.tear_sprites.add(Tear('down', player.shoot_dmg, size=player.tear_size))
                    player_kd = game.base_firing_rate

            # только одноразовые действия требующие одного нажатия
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    # бомбочка
                    if event.key == pygame.K_e and player.inventory_bombs > 0 and player.is_updating:
                        game.bomb_sprites.add(Bomb(player.rect.center[0], player.rect.center[1]))
                        player.inventory_bombs -= 1

                    # чит-клавиша
                    if event.key == pygame.K_p:  # чит-клавиша(бета-тест)
                        game.item_sprites.add(Item('bomb', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))
                        game.item_sprites.add(Item('size_potion', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))
                        game.item_sprites.add(Item('Red_Heart', (randint(100, 900), randint(200, 500)), player, room=(2, 2)))

                    # вызов мини-карты
                    if event.key == pygame.K_TAB:
                        if game.map_show:
                            game.map_show = False
                        else:
                            game.map_show = True

                    # Выход в главное меню
                    if event.key == pygame.K_ESCAPE:
                        start_restart = False
                        if game.id == -1:
                            if player.player_is_dead:
                                pass
                            else:
                                cur.execute(
                                    '''INSERT INTO saves(streak_of_win,hearts,speed,bombs,money,tear_damage,type_of_player,
                                    firing_rate,level_of_hardness,type_of_game,tear_size) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
                                    (game.first_win_streak, player.max_health / 2, player.speed, player.inventory_bombs,
                                     player.inventory_money, player.shoot_dmg, player.type, game.base_firing_rate, game.base_level_of_enemies,
                                     'загруженная', player.tear_size[0]))
                        else:
                            if player.player_is_dead:
                                cur.execute('''DELETE FROM saves WHERE id = ?''', (game.id,))
                                con.commit()
                                sd = 0
                            else:
                                save_game()
                        con.commit()
                        player.kill()

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
                    game.changing_background.rect = game.changing_background.image.get_rect(topleft=(-1200, 0))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].right_door is True and
                        pygame.sprite.collide_mask(player, floor.right_door)):
                    floor.changing_map_icons((0, 1))
                    floor.isaac_in = (floor.isaac_in[0], floor.isaac_in[1] + 1)
                    player.rect = player.image.get_rect(center=(100, 350))
                    player.change_room = True
                    direction_of_changing = (-1, 0)
                    game.changing_background.rect = game.changing_background.image.get_rect(topleft=(1200, 0))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].up_door is True and
                        pygame.sprite.collide_mask(player, floor.up_door)):
                    floor.changing_map_icons((-1, 0))
                    floor.isaac_in = (floor.isaac_in[0] - 1, floor.isaac_in[1])
                    player.rect = player.image.get_rect(center=(600, 600))
                    player.change_room = True
                    direction_of_changing = (0, 1)
                    game.changing_background.rect = game.changing_background.image.get_rect(topleft=(0, -700))

                if (floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].bottom_door is True and
                        pygame.sprite.collide_mask(player, floor.bottom_door)):
                    floor.changing_map_icons((1, 0))
                    floor.isaac_in = (floor.isaac_in[0] + 1, floor.isaac_in[1])
                    player.rect = player.image.get_rect(center=(600, 100))
                    player.change_room = True
                    direction_of_changing = (0, -1)
                    game.changing_background.rect = game.changing_background.image.get_rect(topleft=(0, 700))

                if (pygame.sprite.collide_mask(player, floor_exit) and floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].cleared
                        and floor.isaac_in == floor.boss_room):
                    game.game_ended = True
                    start_restart = False
                    game.first_win_streak += 1
                    save_game()
                    con.commit()

            # переход в другую комнату
            if player.change_room:
                game.door_sprites.remove(floor.up_door, floor.left_door, floor.bottom_door, floor.right_door)
                if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].left_door:
                    game.door_sprites.add(floor.left_door)
                if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].right_door:
                    game.door_sprites.add(floor.right_door)
                if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].up_door:
                    game.door_sprites.add(floor.up_door)
                if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].bottom_door:
                    game.door_sprites.add(floor.bottom_door)
                player.change_room = False
                floor.changing_rooms_true = True

            if floor.changing_rooms_true:
                floor.changing_rooms(direction_of_changing)

            floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].room_update()

            # апдейты всех спрайтов
            game.all_sprites.update()
            game.tear_sprites.update()
            game.bomb_sprites.update()
            game.item_sprites.update()
            game.enemy_sprites.update()
            floor.update()

            # отрисовка всех деталей
            screen.fill((0, 0, 0))
            game.all_sprites.draw(screen)
            bomb_counter = bomb_counter_font.render(str(player.inventory_bombs), True, 'WHITE')
            screen.blit(bomb_counter, (50, 50))
            money_counter = money_counter_font.render(str(player.inventory_money), True, 'WHITE')
            screen.blit(money_counter, (50, 100))
            game.enemy_sprites.draw(screen)
            game.door_sprites.draw(screen)
            if floor.floor[floor.isaac_in[0]][floor.isaac_in[1]].cleared and floor.isaac_in == floor.boss_room:
                game.exit_sprite.draw(screen)
            game.tear_sprites.draw(screen)
            game.bomb_sprites.draw(screen)
            game.item_sprites.draw(screen)

            if game.map_show:
                game.map_icons_sprites.draw(screen)
            screen.blit(bomb_icon, (0, 50))
            screen.blit(money_icon, (0, 100))
            draw_health_bar(0, 0, player.health, player.max_health)

            # кд стрельбы игрока
            if player_kd > 0:
                player_kd -= 10
            clock.tick(60)
        elif first_entry:
            screen.blit(first_page, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        first_entry = False
                if event.type == pygame.QUIT:
                    running = False

        elif game.game_ended:
            screen.blit(menu, (0, 0))
            res_text = [f'Поздравляем, вы закончили этаж №{game.first_win_streak}', f'Персонаж:{game.base_type_of_player}',
                         f'Win streak:{game.first_win_streak}',
                         f'Скорость:{game.base_speed}', f'Красные Сердца:{game.base_hearts}',
                         f'Урон:{game.base_tear_damage}', f'Бомбы:{game.base_bombs}', f'Монеты:{game.base_coins}', '',
                        'Нажмите Enter игра сохранится сама']

            text_coord = 10
            for line in res_text:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                res_rect = string_rendered.get_rect()
                text_coord += 10
                res_rect.top = text_coord
                res_rect.x = 10
                text_coord += res_rect.height
                screen.blit(string_rendered, res_rect)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.game_ended = False
                        sd = 0
                if event.type == pygame.QUIT:
                    running = False

        else:
            screen.blit(menu, (0, 0))
            text_coord = 10
            data = cur.execute('''SELECT * FROM saves''').fetchall()
            list_of_orders = [*(data) + [[-1, 'isaac', 0, 6, 360, 4, 1, 1, 2, 5, 'новая', 50]]]
            (game.base_hearts, game.base_level_of_enemies, game.base_speed, game.base_bombs, game.base_coins,
             game.base_firing_rate, game.base_type_of_player, game.base_tear_damage, game.first_win_streak,
             game.type_of_game, game.id, game.tear_size) = (list_of_orders[sd][5], list_of_orders[sd][7], list_of_orders[sd][3],
                                            list_of_orders[sd][8], list_of_orders[sd][9], list_of_orders[sd][4],
                                            list_of_orders[sd][1], list_of_orders[sd][6], list_of_orders[sd][2],
                                            list_of_orders[sd][10], list_of_orders[sd][0], list_of_orders[sd][11])

            data_text = [f'Начать игру: {game.type_of_game} #ID:{game.id}', f'Персонаж:{game.base_type_of_player}',
                         f'Win streak:{game.first_win_streak}',
                         f'Скорость:{game.base_speed}', f'Красные Сердца:{game.base_hearts}',
                         f'Урон:{game.base_tear_damage}', f'Бомбы:{game.base_bombs}', f'Монеты:{game.base_coins}', '',
                         f'Уровень сложности:{game.base_level_of_enemies}']

            for line in intro_text:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 10
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)

            text_coord = 10

            for line in data_text:
                data_rendered = font.render(line, 1, pygame.Color('black'))
                data_rect = data_rendered.get_rect()
                text_coord += 10
                data_rect.top = text_coord
                data_rect.x = 650
                text_coord += data_rect.height
                screen.blit(data_rendered, data_rect)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game.update_game()
                        floor = Floor()
                        sd = 0
                        player = Player(200, 200, game.base_type_of_player, game.base_speed, game.base_bombs,
                                        game.base_firing_rate, game.base_hearts, game.base_tear_damage, tear_size=game.tear_size)
                        game.all_sprites.add(player)
                        start_restart = True

                    if event.key == pygame.K_RIGHT:
                        if sd == len(list_of_orders) - 1:
                            sd = 0
                        else:
                            sd += 1

                    if event.key == pygame.K_LEFT:
                        if sd == 0:
                            sd = len(list_of_orders) - 1
                        else:
                            sd -= 1

                    if event.key == pygame.K_UP:
                        if game.base_level_of_enemies < 5:
                            game.base_level_of_enemies += 1
                            cur.execute('''UPDATE saves SET level_of_hardness = ? WHERE id = ?''',
                                        (game.base_level_of_enemies, game.id))
                            con.commit()

                    if event.key == pygame.K_DOWN:
                        if game.base_level_of_enemies > 1:
                            game.base_level_of_enemies -= 1
                            cur.execute('''UPDATE saves SET level_of_hardness = ? WHERE id = ?''',
                                        (game.base_level_of_enemies, game.id))
                            con.commit()

                    if event.key == pygame.K_DELETE:
                        if game.id != -1:
                            cur.execute('''DELETE FROM saves WHERE id = ?''', (game.id,))
                            con.commit()
                            sd = 0

                if event.type == pygame.QUIT:
                    running = False

        pygame.display.flip()
    pygame.quit()
