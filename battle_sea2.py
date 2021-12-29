from random import randint
import time


class MapException(Exception):
    pass


class MapUsedException(MapException):
    def __str__(self):
        return "Вы уже стреляли в эту точку"


class MapOutException(MapException):
    def __str__(self):
        return "Вы стреляете за пределы игрового поля"


class MapWrongShipException(MapException):
    pass


class Dot:    # точки
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):    # сравнение координат
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:  # корабли
    def __init__(self, point, length, route):
        self.point = point
        self.length = length
        self.route = route
        self.health = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.point.x
            cur_y = self.point.y

            if self.route == 0:    # корабль по горизонтали
                cur_x += i

            elif self.route == 1:    # корабль по вертикали
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Map:    # карта боя
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [['0'] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = " "
        res += " | 1 | 2 | 3 | 4 | 5 | 6 | "
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " | "

        if self.hid:
            res = res.replace('\u25A0', '0')
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):    # координаты вокруг каждой точки корабля
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise MapWrongShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = '\u25A0'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if d in self.busy:
            raise MapUsedException

        if self.out(d):
            raise MapOutException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.health -= 1
                self.field[d.x][d.y] = 'x'
                if ship.health == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен! ')
                    return True
                else:
                    print('Корабль ранен! ')
                    return True

        self.field[d.x][d.y] = '.'
        print('Мимо')
        return False

    def begin(self):    # создание пустого списка попаданий
        self.busy = []



class Player:    # игрок
    def __init__(self, map, enemy):
        self.map = map
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except MapException as e:
                print(e)


class AI(Player):    # компьютер
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print('Ход компьютера: ')
        time.sleep(randint(1, 5))
        print(f'{d.x + 1} {d.y + 1}')
        return d


class User(Player):    # человек
    def ask(self):
        while True:
            cords = input('Введите координаты для выстрела: ').split()


            if len(cords) != 2:
                print('Введите две координаты ')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите координаты цифрами ')
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_map()
        co = self.random_map()
        co.hid = True



        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_map(self):  # расстявляем корабли на карте
        lens = [3, 2, 2, 1, 1, 1, 1]    # длинна кораблей

        map = Map(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    map.add_ship(ship)
                    break
                except MapWrongShipException:
                    pass

        map.begin()
        # print(attempts)
        return map

    def random_map(self):
        map = None
        while map is None:
            map = self.try_map()
        return map

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")


    def print_maps(self):
        print("-" * 20)
        print("Карта пользователя:")
        print(self.us.map)
        print("-" * 20)
        print("Карта компьютера:")
        print(self.ai.map)


    def loop(self):
        num = 0
        while True:
            self.print_maps()
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.map.count == len(self.ai.map.ships):
                self.print_maps()
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.map.count == len(self.us.map.ships):
                self.print_maps()
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
            # print(num)



    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
