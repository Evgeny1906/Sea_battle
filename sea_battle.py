from random import randint



class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f" Dot({self.x}, {self.y})"

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за поле!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, decks, bow, o):
        self.deck = decks
        self.bow = bow
        self.o = o
        self.lives = decks
    @property
    def dots(self):
        ship_dot = []
        for i in range(self.deck):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i
            ship_dot.append(Dot(cur_x, cur_y))
        return ship_dot

    def shooten(self, shoot):
        return shoot in self.dots

class Field:
    def __init__(self, hid=False, size = 10):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [['   'for i in range(self.size)] for j in range(self.size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        f1 = self.field[0].copy()
        for f_ in range(self.size):
            f1[f_] = str(f_+1)
        field_ = f"   {'   '.join(f1)}"

        for num_h, f in enumerate(self.field):
            abc = ['A', 'B', 'C', 'D', 'E', "F", 'G', 'H', 'I', 'J']
            field_ += f"\n{abc[num_h]}|{'|'.join(f)}|"

            if self.hid:
                field_ = field_.replace(" ■ ", "   ")

        return field_
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.field[d.x][d.y] = " ■ "
            self.busy.append(d)

        self.ships.append(ship)
        self.contur(ship)

    def contur(self, ship, verb=False):
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
                        self.field[cur.x][cur.y] = " . "
                    self.busy.append(cur)
    def shoot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = " X "
                if ship.lives == 0:
                    self.count += 1
                    self.contur(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = " * "
        print("Промазал, мазила!")
        return False

    def begin(self):
        self.busy = []

class Game:
    def __init__(self):


        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = Ai(co, pl)
        self.us = User(pl, co)
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        float = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        field = Field()
        attepts = 0
        for d in float:
            while True:
                attepts += 1
                if attepts == 2000:
                    return None
                ship = Ship(d, Dot(randint(0, 9), randint(0, 9)), randint(0, 1))
                try:
                    field.add_ship(ship)
                    break

                except BoardWrongShipException:
                    pass
        field.begin()
        return field

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: A 5 ")


    def loop(self):
        name = input(f"\nВведите ваше имя: \t").title()
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print(f"Ходит {name}!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 10:
                print("-" * 20)
                print(f"Выиграл {name}!")
                break

            if self.us.board.count == 10:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
    def start(self):
        self.loop()

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
        self.abc = ['A', 'B', 'C', 'D', 'E', "F", 'G', 'H', 'I', 'J']
    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shoot(target)
                return repeat
            except BoardException as e:
                print(e)
class Ai(Player):
    def ask(self):
        d = Dot(randint(0, 9), randint(0, 9))
        print(f"Ход компьютера: {self.abc[d.x]} {d.y+1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").title()
            cords = cords.split()
            if len(cords) != 2:
                print(" Введите 2 координаты через пробел! ")
                continue

            x, y = cords

            if not x.isalpha():
                print(" Первое значение должна быть буква")
                continue
            elif not y.isdigit():
                print("Второе значение должна быть цифра")
                continue
            try:
                x = self.abc.index(x)
            except ValueError:
                print(f"Нет буквы '{x}' на доске")
                continue


            x, y = int(x), int(y)

            return Dot(x, y - 1)


st = Game()
st.greet()
st.loop()