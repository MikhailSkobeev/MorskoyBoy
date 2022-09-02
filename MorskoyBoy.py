import os
from random import randrange
from random import choice


class BoardPart (object):
    main = 'map'
    radar = 'radar'
    weight = 'weight'
# Доска будет состоять из трёх частей:
# Карта поля
# Радар, на котором будут помечены корабли
# Вес клетки нужен будет для коэффициентов

#-----------------------------------------------------------

class Cell(object):
    empty_cell = ('О')
    ship_cell = ('■')
    destroyed_ship = ('X')
    damaged_ship = ('T')
    miss_cell = ('•')

#-----------------------------------------------------------

class Board(object):

    def __init__(self, size):
        self.size = size
        self.map = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.weight = [[1 for _ in range(size)] for _ in range(size)]

    def get_field_part(self, element):
        if element == BoardPart.main:
            return self.map
        if element == BoardPart.radar:
            return self.radar
        if element == BoardPart.weight:
            return self.weight


    def draw_field(self, element):

        field = self.get_field_part(element)
        weights = self.get_max_weight_cells()

        if element == BoardPart.weight:
            for x in range(self.size):
                for y in range(self.size):
                    if (x, y) in weights:
                        print(end='')
                    if field[x][y] < self.size:
                        print(" ", end='')
                    if field[x][y] == 0:
                        print(str("" + ". " + ""), end='')
                    else:
                        print(str("" + str(field[x][y]) + " "), end='')
                    print(end='')
                print()

        else:
            # Само поле рисуется так:
            for x in range(-1, self.size):
                for y in range(-1, self.size):
                    if x == -1 and y == -1:
                        print("  ", end="")
                        continue
                    if x == -1 and y >= 0:
                        print(y + 1, end=" ")
                        continue
                    if x >= 0 and y == -1:
                        print(Game.letters[x], end='')
                        continue
                    print(" " + str(field[x][y]), end='')
                print("")
        print("")

    # Функция проверяет помещается ли корабль на конкретную позицию конкретного поля,
    # будем использовать при расстановке кораблей, а также при вычислении веса клеток
    # False будет возвращаться, если не помещается корабль, и True, если корабль помещается
    def check_ship_fits(self, ship, element):

        field = self.get_field_part(element)

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:
            return False

        x = ship.x
        y = ship.y
        width = ship.width
        height = ship.height

        for c_x in range(x, x + height):
            for c_y in range(y, y + width):
                if str(field[c_x][c_y]) == Cell.miss_cell:
                    return False

        for c_x in range(x - 1, x + height + 1):
            for c_y in range(y - 1, y + width + 1):
                if c_x < 0 or c_x >= len(field) or c_y < 0 or c_y >= len(field):
                    continue
                if str(field[c_x][c_y]) in (Cell.ship_cell, Cell.destroyed_ship):
                    return False

        return True

    # Когда корабль уничтожен необходимо пометить все клетки вокруг него сыграными (Cell.miss_cell), а все клетки корабля - уничтожеными (Cell.destroyed_ship)
    def mark_destroyed_ship(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height

        for c_x in range(x - 1, x + height + 1):
            for c_y in range(y - 1, y + width + 1):
                if c_x < 0 or c_x >= len(field) or c_y < 0 or c_y >= len(field):
                    continue
                field[c_x][c_y] = Cell.miss_cell

        for c_x in range(x, x + height):
            for c_y in range(y, y + width):
                field[c_x][c_y] = Cell.destroyed_ship

# Добавление корабля: пробегаемся от позиции х у корабля по его высоте и ширине и помечаем на поле эти клетки
    def add_ship_to_field(self, ship, element):

        field = self.get_field_part(element)

        x, y = ship.x, ship.y
        width, height = ship.width, ship.height
# Благодаря, ссылке на корабль при дальнейшем, обращение мы будем знать здоровье корабль
        for c_x in range(x, x + height):
            for c_y in range(y, y + width):
                field[c_x][c_y] = ship

# Функция возвращает список координат с самым большим коэффициентом шанса попадания
    def get_max_weight_cells(self):
        weights = {}
        max_weight = 0
# Просто пробегаем по всем клеткам и заносим их в словарь с ключом который является значением в клетке
# и запоминаем максимальное значение
# Далее просто берём из словаря список координат с этим максимальным значением weights[max_weight]
        for x in range(self.size):
            for y in range(self.size):
                if self.weight[x][y] > max_weight:
                    max_weight = self.weight[x][y]
                weights.setdefault(self.weight[x][y], []).append((x, y))

        return weights[max_weight]

# Выставляем всем клеткам 1
# Пробегаем по всему полю, если находим раненый корабль - ставим клеткам выше ниже и по бокам
    def recalculate_weight_map(self, available_ships):
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                if self.radar[x][y] == Cell.damaged_ship:

                    self.weight[x][y] = 0

                    if x - 1 >= 0:
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0
                        self.weight[x - 1][y] *= 10
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0

                    if y - 1 >= 0:
                        self.weight[x][y - 1] *= 10
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 10

                    if x + 1 < self.size:
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0
                        self.weight[x + 1][y] *= 10
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0

# Перебираем все корабли оставшиеся у противника
# Если есть уничтоженный корабль, повреждённый или клетка с промахом, тогда ставим коэффициент 0
# Иначе прикидываем может ли этот корабль с этой клетки начинаться в какую-либо сторону,
# если он помещается, то прибавляем клетке коэффициент 1

# Проверяем, помещается ли корабль на доске
        for ship_size in available_ships:

            ship = Ship(ship_size, 1, 1, 0)
            for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] in (Cell.destroyed_ship, Cell.damaged_ship, Cell.miss_cell) \
                            or self.weight[x][y] == 0:
                        self.weight[x][y] = 0
                        continue

                    for rotation in range(0, 4):
                        ship.set_position(x, y, rotation)
                        if self.check_ship_fits(ship, BoardPart.radar):
                            self.weight[x][y] += 1


#-----------------------------------------------------------

class Game(object):
    letters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")
    ships_rules = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    field_size = len(letters)

    def __init__(self):
        self.players = []
        self.current_player = None
        self.next_player = None

        self.status = 'prepare'

    def start_game(self):
        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def status_check(self):
        # Переходим с prepare на in game, т.к было добавлено два игрока
        if self.status == 'prepare' and len(self.players) >= 2:
            self.status = 'in game'
            self.start_game()
            return True
        # Переходим в статус game over, если у следующего игрока осталось 0 кораблей
        if self.status == 'in game' and len(self.next_player.ships) == 0:
            self.status = 'game over'
            return True

# При добавлении игрока создаем для него поле
    def add_player(self, player):
        player.field = Board(Game.field_size)
        player.enemy_ships = list(Game.ships_rules)
        self.ships_setup(player)
        # высчитываем вес для клеток поля, это нужно будет только для ИИ
        player.field.recalculate_weight_map(player.enemy_ships)
        self.players.append(player)

# Делаем расстановку кораблей по правилам заданным в классе Game
    def ships_setup(self, player):
        for ship_size in Game.ships_rules:
            # Задаем количество попыток при выставлении кораблей, чтобы не попали в бесконечный цикл
            retry_count = 30

            # Создаем предварительно корабль, которому в дальнейшем будут присваиваться координаты
            ship = Ship(ship_size, 0, 0, 0)

            while True:

                Game.clear_screen()
                if player.auto_ship_setup is not True:
                    player.field.draw_field(BoardPart.main)
                    player.message.append('Куда поставить {} корабль: '.format(ship_size))
                    for _ in player.message:
                        print(_)
                else:
                    print('{}. Расставляем корабли...'.format(player.name))

                player.message.clear()

                x, y, r = player.get_input('ship_setup')
                # Если пользователь совершил неправильный ввод, делаем continue
                if x + y + r == 0:
                    continue

                ship.set_position(x, y, r)

                # Если корабль помещается на заданной позиции, добавляем игроку на поле корабль
                # также добавляем корабль в список кораблей игрока и переходим к следующему кораблю для расстановки
                if player.field.check_ship_fits(ship, BoardPart.main):
                    player.field.add_ship_to_field(ship, BoardPart.main)
                    player.ships.append(ship)
                    break

                # Сюда мы добираемся только если корабль не поместился
                # Пишем пользователю, что позиция неправильная, и отнимаем попытку на расстановку
                player.message.append('Неправильная позиция!')
                retry_count -= 1
                if retry_count < 0:
                    # после заданного количества неудачных попыток, карта обнуляется, и пользователь вводит всё заново
                    player.field.map = [[Cell.empty_cell for _ in range(Game.field_size)] for _ in
                                        range(Game.field_size)]
                    player.ships = []
                    self.ships_setup(player)
                    return True

    def draw(self):
        if not self.current_player.is_ai:
            self.current_player.field.draw_field(BoardPart.main)
            self.current_player.field.draw_field(BoardPart.radar)
        for line in self.current_player.message:
            print(line)

# В этой функции прописана смена игроков
    def switch_players(self):
        self.current_player, self.next_player = self.next_player, self.current_player

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')


class Player(object):

    def __init__(self, name, is_ai, skill, auto_ship):
        self.name = name
        self.is_ai = is_ai
        self.auto_ship_setup = auto_ship
        self.skill = skill
        self.message = []
        self.ships = []
        self.enemy_ships = []
        self.field = None

# Расстановка кораблей (input_type == "ship_setup")
# Совершение выстрела (input_type == "shot")
    def get_input(self, input_type):

        if input_type == "ship_setup":

            if self.is_ai or self.auto_ship_setup:
                user_input = str(choice(Game.letters)) + str(randrange(0, self.field.size)) + choice(["B", "D"])
            else:
                user_input = input().upper().replace(" ", "")

            if len(user_input) < 3:
                return 0, 0, 0

            x, y, r = user_input[0], user_input[1:-1], user_input[-1]

            if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.field_size + 1) or \
                    r not in ("B", "D"):
                self.message.append('Неправильный формат ввода!')
                return 0, 0, 0

            return Game.letters.index(x), int(y) - 1, 0 if r == 'B' else 1

        if input_type == "shot":

            if self.is_ai:
                if self.skill == 1:
                    x, y = choice(self.field.get_max_weight_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.field.size), randrange(0, self.field.size)
            else:
                user_input = input().upper().replace(" ", "")
                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.field_size + 1):
                    self.message.append('Неправильный формат ввода!')
                    return 500, 0
                x = Game.letters.index(x)
                y = int(y) - 1
            return x, y

# При совершении выстрела будет запрашиваться ввод данных с типом shot
    def make_shot(self, target_player):

        sx, sy = self.get_input('shot')

        if sx + sy == 500 or self.field.radar[sx][sy] != Cell.empty_cell:
            return 'retry'
        # На выстрел будет ответ - промазал, попал или убил, (в случае убил, возвращается корабль)
        shot_res = target_player.receive_shot((sx, sy))

        if shot_res == 'miss':
            self.field.radar[sx][sy] = Cell.miss_cell

        if shot_res == 'get':
            self.field.radar[sx][sy] = Cell.damaged_ship

        if type(shot_res) == Ship:
            destroyed_ship = shot_res
            self.field.mark_destroyed_ship(destroyed_ship, BoardPart.radar)
            self.enemy_ships.remove(destroyed_ship.size)
            shot_res = 'kill'

        # После совершения выстрела пересчитывается карта весов
        self.field.recalculate_weight_map(self.enemy_ships)

        return shot_res

    # Здесь игрок будет приниматься выстрел, результат выстрела:
    # попал (return "get")
    # промазал (return "miss")
    # убил корабль

    def receive_shot(self, shot):

        sx, sy = shot

        if type(self.field.map[sx][sy]) == Ship:
            ship = self.field.map[sx][sy]
            ship.hp -= 1

            if ship.hp <= 0:
                self.field.mark_destroyed_ship(ship, BoardPart.main)
                self.ships.remove(ship)
                return ship

            self.field.map[sx][sy] = Cell.damaged_ship
            return 'get'

        else:
            self.field.map[sx][sy] = Cell.miss_cell
            return 'miss'


class Ship:

    def __init__(self, size, x, y, rotation):

        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def __str__(self):
        return Cell.ship_cell

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):

        self.rotation = r

        if self.rotation == 0:
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:
            self.width = 1
            self.height = self.size
        elif self.rotation == 2:
            self.y = self.y - self.size + 1
            self.width = self.size
            self.height = 1
        elif self.rotation == 3:
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


if __name__ == '__main__':

    # Делаем список из двух игроков и задаем им основные параметры
    players = []
    players.append(Player(name='Username', is_ai=False, auto_ship=True, skill=1))
    players.append(Player(name='AI', is_ai=True, auto_ship=True, skill=1))

    # Создаем саму игру
    game = Game()

    while True:
        # каждое начало хода проверяем статус и дальше уже действуем исходя из статуса игры
        game.status_check()

        if game.status == 'prepare':
            game.add_player(players.pop(0))

        if game.status == 'in game':
            # В основной части игры мы очищаем экран добавляем сообщение для текущего игрока и отрисовываем игру
            Game.clear_screen()
            game.current_player.message.append("Ждём ввода координат: ")
            game.draw()
            # Очищаем список сообщений для игрока. В следующий ход он уже получит новый список сообщений
            game.current_player.message.clear()
            # Ждём результата выстрела на основе выстрела текущего игрока в следующего
            shot_result = game.current_player.make_shot(game.next_player)
            # В зависимости от результата отправляем сообщений и текущему игроку и следующему
            # Если промазал - передаем ход следующему игроку
            if shot_result == 'miss':
                game.next_player.message.append('На этот раз {}, промахнулся! '.format(game.current_player.name))
                game.next_player.message.append('Ваш ход {}!'.format(game.next_player.name))
                game.switch_players()
                continue
            elif shot_result == 'retry':
                game.current_player.message.append('Попробуйте еще раз!')
                continue
            elif shot_result == 'get':
                game.current_player.message.append('Отличный выстрел, продолжайте!')
                game.next_player.message.append('Наш корабль попал под обстрел!')
                continue
            elif shot_result == 'kill':
                game.current_player.message.append('Корабль противника уничтожен!')
                game.next_player.message.append('Плохие новости, наш корабль был уничтожен :')
                continue

        if game.status == 'game over':
            Game.clear_screen()
            game.next_player.field.draw_field(BoardPart.main)
            game.current_player.field.draw_field(BoardPart.main)
            print('Это был последний корабль {}'.format(game.next_player.name))
            print('{} выиграл матч! Поздравления!'.format(game.current_player.name))
            break

    print('Спасибо за игру!')
    input('')
