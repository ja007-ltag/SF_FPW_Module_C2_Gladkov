from random import randint
import string


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

        header = [n for n in string.ascii_uppercase[:self.size]]
        res += f"| \\ | {' | '.join(header)} |\n"
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
    def __init__(self, board_main, board_enemy):
        self.board_main = board_main
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
            cords = input("Ваш ход: ").replace(" ", "").upper()

            if len(cords) < 2:
                print("Пожалуйста, введите 2 координаты!")
                continue

            if not (cords[0] in string.ascii_uppercase and cords[1:].isdigit()):
                print("Введите латинскую букву и число!")
                continue

            return Dot(int(cords[1:]) - 1, ord(cords[0]) - ord("A"))


class Game:
    def __init__(self, size=6):
        self.size = size

        us_board = self.random_board()
        ai_board = self.random_board(hid=True)

        self.us = User(us_board, ai_board)
        self.ai = AI(ai_board, us_board)

    def try_board(self, hid):  # пытаемся создать доску
        size_ships = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size, hid=hid)
        attempts = 0
        for cur in size_ships:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None

                o_ship = randint(0, 1)
                if o_ship == 0:
                    d_x = randint(0, self.size - 1)
                    d_y = randint(0, self.size - cur)
                else:
                    d_x = randint(0, self.size - cur)
                    d_y = randint(0, self.size - 1)
                ship = Ship(Dot(d_x, d_y), cur, o_ship)

                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self, hid=False):
        board = None
        while board is None:
            board = self.try_board(hid)
        return board

    @staticmethod
    def greet():
        print('* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ *')
        print('*   Добро пожаловать в игру    *')
        print('*         Морской бой!         *')
        print('* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ *')
        print('*  Формат ввода: "шахматный":  *')
        print('*        буква и цифра.        *')
        print('*  Пробелы не имеют значения!  *')
        print('*  Например, "E2" или "e 4".   *')
        print('* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ *')
        print('*     Разработчик Гладков      *')
        print('* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ *')
        print()

    def loop(self):
        move_user = True
        while True:
            print("-"*20)
            print("Доска игрока:")
            print(self.us.board_main)
            print("-" * 20)
            print("Доска противника:")
            print(self.ai.board_main)
            print("-" * 20)

            if move_user:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if not repeat:
                move_user = not move_user

            if self.ai.board_main.count == len(self.ai.board_main.ships):
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board_main.count == len(self.us.board_main.ships):
                print("-" * 20)
                print("Компьютер выиграл!")
                break


if __name__ == "__main__":
    g = Game(size=6)
    g.loop()
