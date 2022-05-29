from random import randint


# --- Классы исключений ---
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUserException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # отвечает за сравнение двух объектов (и использование ==, !=, in, count и т.п.)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # отвечает за вывод, которым можно создавать список, например
    # print(a) -- Dot(1, 1) или print([a, b, c]) -- [Dot(1, 1), Dot(3, 2), Dot(1, 1)]
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:  # Корабли
    def __init__(self, dot, size, o):
        self.dot = dot  # точка носа корабля - Dot(x, y)
        self.size = size  # размер корабля (1,2,3 палубный)
        self.o = o  # ориентация корабля (0-горизонтальный, 1-вертикальный)
        self.lives = size  # текущее количество жизней

    @property
    def dots(self):  # генерация всех точек корабля
        ship_dots = []

        for i in range(self.size):
            if self.o == 0:
                ship_dots.append(Dot(self.dot.x, self.dot.y + i))
            elif self.o == 1:
                ship_dots.append(Dot(self.dot.x + i, self.dot.y))

        return ship_dots

    def shot_hit(self, shot_dots):
        return shot_dots in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid  # скрытая ли доска
        self.size = size

        self.count = 0  # кол-во пораженных кораблей

        self.field = [[" "] * size for _ in range(size)]

        self.busy = []  # список занятых клеток
        self.ships = []  # список кораблей

    def __str__(self):
        sep_line = f"{'+---' * (self.size + 1)}+\n"
        res = sep_line

        header = [f"{n:2} " for n in range(1, self.size + 1)]
        res += f"| \\ |{'|'.join(header)}|\n"
        res += sep_line
        for i, row in enumerate(self.field):
            res += f"|{i + 1:2} | {' | '.join(row)} |\n"
            res += sep_line

        if self.hid:
            res = res.replace("■", " ")
        return res

    def out(self, dot):  # находится ли точка за пределами доски
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def contour(self, ship, verb=False):
        near = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()

        if dot in self.busy:
            raise BoardUserException()

        self.busy.append(dot)

        for ship in self.ships:
            if ship.shot_hit(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "x"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board_my, board_enemy):
        self.board_my = board_my
        self.board_enemy = board_enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.board_enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x+1} {dot.y+1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Пожалуйста, введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit() and y.isdigit()):
                print("Пожалуйста, введите числа!")
                continue

            x, y = int(x), int(y)
            return Dot(x-1, y-1)


if __name__ == '__main__':
    pass
