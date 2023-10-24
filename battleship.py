"""Play the Battleship with your computer!
Classes: DotNames(enum.Enum)
         Dot
         Ship
         Board
         Player
         PlayerHuman(Player)
         PlayerComputer(Player)
         Game
"""

import enum
import random
from time import sleep

RULES = ["Hello! It's the Battleship! Glad to see you!\n"
         "Add your ships: one three-decker ship, two two-decker ships and four one-decker ship.\n"
         "Enter the beginning and the end of the ship (or just the beginning for one-decker ship)\n"
         "in format 'A1A2' or something like that. The ships shouldn't touch each other.\n"
         "If you want to rebuild whole board, enter 'AGAIN'.\n"
         "Empty fields are literally empty, healthy ship is \u25B2, burn ship is \u25B3, \n"
         "and killed ship is X. Contour appear around killed ship, it's \u25E6.\n",
         "To fire enter coordinates in the same format, 'A1'. If you miss, field becomes M.\n"
         "You can't fire in M. You can fire in contour but what for?"]


class OutOfBoard(IndexError):
    pass


class FieldIsOccupied(Exception):
    pass


class IncorrectShip(Exception):
    pass


class OtherShipIsNear(Exception):
    pass


class AllTheseShipsAreUsed(Exception):
    pass


class ActionWasNotDone(Exception):
    pass


class YouHitTheTarget(ActionWasNotDone):
    pass


class AlreadyShot(Exception):
    pass


class InputRecognitionError(ValueError):
    pass


def main():
    game = Game()
    game.start()


class DotNames(enum.Enum):
    """Class with all possible states of dot"""

    empty = " "
    contour = "\u25E6"  # ◦
    ship = "\u25B2"     # ▲
    burn = "\u25B3"     # △
    killed = "X"
    miss = "M"


class Dot:
    """Class of dot's coordinates and state"""

    def __init__(self, x: int, y: int, state=DotNames.empty):
        """Init the dot"""
        self.x = x
        self.y = y
        self.state = state

    def __eq__(self, other):
        """Equality of two dots"""

        return self.x == other.x and self.y == other.y

    def __str__(self):

        return self.state.value

    def copy(self):
        """Copy the dot"""

        return Dot(self.x, self.y, self.state)


class Ship:
    """
    Class create ship, check the correctness of ship,
    create list with all ship's dots,
    ship's lives is quantity of alive decks
    """

    def __init__(self, begin: Dot, end=None):
        """Create new ship with begin and end if ship is correct"""

        self.begin = begin
        if end is None:
            self.end = begin
        else:
            self.end = end

        try:
            self.check_correct_ship()
        except IncorrectShip as error:
            print(error)
            raise ActionWasNotDone("Please try again")

        self.lives = self.__len__()
        self.all_dots = []
        self.find_all_dots()

    def check_correct_ship(self):
        """Ship must be located on one line and not longer 3"""

        if not ((self.begin.x == self.end.x
                or self.begin.y == self.end.y)
                and len(self) <= 3):
            raise IncorrectShip("This ship is incorrect")

    def __len__(self):
        """Return ship's length"""

        return max(abs(self.begin.x - self.end.x), abs(self.begin.y - self.end.y)) + 1

    def find_all_dots(self):
        """Create list with all ship's dots, make them ship state"""

        if len(self) == 1:
            self.all_dots = [self.begin]
        elif len(self) == 2:
            self.all_dots = [self.begin, self.end]
        else:
            self.all_dots = [
                self.begin,
                # find middle dot:
                Dot(x=(self.begin.x + self.end.x) // 2, y=(self.begin.y + self.end.y) // 2),
                self.end]

        for dot in self.all_dots:
            dot.state = DotNames.ship


class Board:
    """
    Class create board, add ships if place is empty else raise error,
    add contour, delete contour, create list of all ships;
    make shoot and raise error if this dot is already shoot
    """

    def __init__(self, hidden=False):
        """Create the board"""

        self.board_list = [[Dot(x, y) for x in range(6)] for y in range(6)]
        self.ship_list = []
        self.hidden = hidden

    def add_ship(self, ship: Ship):
        """
        Check the correctness of ship's location
        and add it on the board and in the ships list,
        also add contour on the board
        """

        try:
            self.can_we_add_another_ship(ship)

            for dot in ship.all_dots:
                if not Board.is_dot_on_board(dot):
                    raise OutOfBoard("The dot(s) is out of board")
                if not isinstance(self.board_list[dot.x][dot.y], Dot):
                    raise FieldIsOccupied("This field is occupied")
                elif self.board_list[dot.x][dot.y].state == DotNames.contour:
                    raise OtherShipIsNear("Too close to other ship")
                elif self.board_list[dot.x][dot.y].state == DotNames.empty:
                    self.board_list[dot.x][dot.y] = len(self.ship_list)
        except (FieldIsOccupied, OtherShipIsNear, OutOfBoard, IncorrectShip, AllTheseShipsAreUsed) as error:
            print(error)
            raise ActionWasNotDone("Please try again")
        else:
            self.ship_list.append(ship)
            self.add_contour(ship)

    def can_we_add_another_ship(self, ship: Ship):
        """Check the quantity of added ships with given length"""

        if len(self.ship_list) == 0:
            return
        if (((len(ship) == 3 and                           # all 3-decker are used
                max(len(some_ship) for some_ship in self.ship_list)) == 3)
                or ((len(ship) == 2 and                    # all 2-decker are used
                     len([some_ship for some_ship in self.ship_list if len(some_ship) == 2]) == 2))
                or ((len(ship) == 1 and                    # all 1-decker are used
                     len([some_ship for some_ship in self.ship_list if len(some_ship) == 1]) == 4))):
            raise AllTheseShipsAreUsed("All ships with this length are used")

    def add_contour(self, ship):
        """Create the contour of the ship, add it to the board"""

        contour = []
        for dot in ship.all_dots:
            contour.extend([Dot(i, j, state=DotNames.contour)
                            for i in range(dot.x - 1, dot.x + 2)
                            for j in range(dot.y - 1, dot.y + 2)])
        contour = [dot for dot in contour if Board.is_dot_on_board(dot)]

        for dot in contour:
            if (isinstance(self.board_list[dot.x][dot.y], Dot)
                    and self.board_list[dot.x][dot.y].state == DotNames.empty):
                self.board_list[dot.x][dot.y] = dot

    def delete_contour(self):
        """Delete contour from the board"""

        for line in self.board_list:
            for dot in line:
                if isinstance(dot, Dot) and dot.state == DotNames.contour:
                    dot.state = DotNames.empty

    def shoot(self, dot: Dot):
        """Make a shoot"""

        if isinstance(self.board_list[dot.x][dot.y], int):
            self.shoot_at_ship(dot, index=self.board_list[dot.x][dot.y])
        elif self.board_list[dot.x][dot.y].state == DotNames.miss:
            raise AlreadyShot("You already shot in this dot")
        elif (self.board_list[dot.x][dot.y].state == DotNames.empty or
              self.board_list[dot.x][dot.y].state == DotNames.contour):
            self.board_list[dot.x][dot.y].state = DotNames.miss

    def shoot_at_ship(self, dot: Dot, index: int):
        """Make a shoot in ship. If ship's lives is gone, make ship killed"""

        ship = self.ship_list[index]
        if ship.lives == 0:
            raise AlreadyShot("You already shot in this dot")
        else:
            for dot_in_ship in ship.all_dots:

                if dot_in_ship == dot:
                    if dot_in_ship.state == DotNames.ship:
                        dot_in_ship.state = DotNames.burn
                        ship.lives -= 1
                    else:
                        raise AlreadyShot("You already shot in this dot")
            if ship.lives == 0:
                for dot_in_ship in ship.all_dots:
                    dot_in_ship.state = DotNames.killed
                self.add_contour(ship)
            raise YouHitTheTarget("You hit the target! Shoot again")

    def show_board(self):
        """Print the board. Hide ships if hidden (for computer) else show its"""

        __sep = " | "
        strings = ["A", "B", "C", "D", "E", "F"]
        columns = [" "] + [f"{_num}" for _num in range(1, 7)]
        print(__sep.join(columns), end=__sep + "\n")

        if self.hidden:
            self.show_board_hidden(strings, __sep)
        else:
            for i in range(6):
                print(strings[i], end=__sep)
                for j in range(6):
                    if isinstance(self.board_list[i][j], int):
                        ship = self.ship_list[self.board_list[i][j]]
                        new_dot = None
                        for dot in ship.all_dots:
                            if dot == Dot(i, j):
                                new_dot = dot
                        print(new_dot, end=__sep)
                    else:
                        print(self.board_list[i][j], end=__sep)
                print("")

    def show_board_hidden(self, strings, __sep):
        """Print the board. Hide ships if hidden (for computer)"""

        for i in range(6):
            print(strings[i], end=__sep)
            for j in range(6):
                if isinstance(self.board_list[i][j], int):
                    ship = self.ship_list[self.board_list[i][j]]
                    new_dot = None
                    for dot in ship.all_dots:
                        if dot == Dot(i, j):
                            if dot.state == DotNames.ship:
                                new_dot = dot.copy()
                                new_dot.state = DotNames.empty
                            else:
                                new_dot = dot.copy()
                    print(new_dot, end=__sep)
                else:
                    print(self.board_list[i][j], end=__sep)
            print("")

    @staticmethod
    def is_dot_on_board(dot):
        """Check dot is on the board"""

        if (0 <= dot.x < 6) and (0 <= dot.y < 6):
            return True
        else:
            return False


class Player:
    """Parent class for players"""

    def fill_board(self):
        pass


class PlayerHuman(Player):
    """
    Class for human. Make a board, add ships by input,
    make shoot by input, raise an error if something wrong
    """

    def __init__(self):
        """Create a board and fill it with ships"""

        self.board = Board(hidden=False)
        self.fill_board()

    def fill_board(self):
        """Fill the board with ships by input"""

        global RULES
        print(RULES[0])
        ships_amount = 0

        while ships_amount < 7:
            self.board.show_board()
            coord = input("add your ship, enter 'AGAIN' if you want to start again\n")
            coord = PlayerHuman.clean_input(coord)
            if coord == "AGAIN":
                self.board = Board(hidden=False)
                self.fill_board()

            try:
                if len(coord) != 2 and len(coord) != 4:
                    raise InputRecognitionError("Sorry, I don't understand\nPlease try again")
                if len(coord) == 2:
                    coord = coord * 2
                if not(coord[0].isalpha() and coord[1].isdigit() and
                       coord[2].isalpha() and coord[3].isdigit()):
                    raise InputRecognitionError("Sorry, I don't understand\nPlease try again")
                dot_1 = Dot(ord(coord[0]) - 65, int(coord[1]) - 1)  # because ord("A") is 65
                dot_2 = Dot(ord(coord[2]) - 65, int(coord[3]) - 1)  # because ord("A") is 65
                self.board.add_ship(Ship(dot_1, dot_2))
            except (InputRecognitionError, IncorrectShip, ActionWasNotDone) as error:
                print(error)
                continue
            else:
                ships_amount += 1

        self.board.delete_contour()
        self.board.show_board()

    @staticmethod
    def human_shoot() -> Dot:
        """Make a shoot by input"""

        move = input("Your turn\n")
        move = PlayerHuman.clean_input(move)

        if len(move) != 2 and not (move[0].isalpha() and move[1].isdigit()):
            raise InputRecognitionError("Sorry, I don't understand")
        dot = Dot(ord(move[0]) - 65, int(move[1]) - 1)  # because ord("A") is 65
        if not Board.is_dot_on_board(dot):
            raise OutOfBoard("The dot(s) is out of board")

        return dot

    @staticmethod
    def clean_input(some_text: str):
        """Delete all marks and spaces from text and make it upper case"""

        table = some_text.maketrans(',.?:;!-', "       ")
        some_text = some_text.translate(table)
        some_text = some_text.replace(" ", "")
        some_text = some_text.upper()
        return some_text


class PlayerComputer(Player):
    """
    Class for computer moves:
        creates board with random ships placement;
        shoots in random dot, when hit, shoots near
    """

    def __init__(self):
        """Create the board with ships"""

        self.board = Board(hidden=True)
        self.fill_board()
        self.board.delete_contour()
        self.next_shoot_dots = []   # need for shoot

    def fill_board(self):
        """Fill the board with ships"""

        free_dots = [(x, y) for x in range(6) for y in range(6)]
        # add one 3-decker ship:
        self.board.add_ship(Ship(*PlayerComputer.three_or_two_decker_ship(3, free_dots)))
        free_dots = self.remove_occupied_dots(free_dots)
        # add two 2-decker ship:
        for i in range(2):
            self.board.add_ship(Ship(*PlayerComputer.three_or_two_decker_ship(2, free_dots)))
            free_dots = self.remove_occupied_dots(free_dots)
        # add four 1-decker ship:67
        for i in range(4):
            if len(self.board.ship_list) == 7:
                break
            self.board.add_ship(Ship(PlayerComputer.one_decker_ship(free_dots)))
            free_dots = self.remove_occupied_dots(free_dots)

    def remove_occupied_dots(self, free_dots):
        """
        Recreate list with free dots for choose place to ship;
        recreate whole board if free dots ran out and not all ships are in place
        """

        new_free_dots = free_dots.copy()

        for dot in free_dots:
            same_dot_on_board = self.board.board_list[dot[0]][dot[1]]
            if (isinstance(same_dot_on_board, int) or
                    same_dot_on_board.state == DotNames.contour):
                new_free_dots.remove(dot)

        if not new_free_dots and len(self.board.ship_list) < 7:
            self.__init__()

        return new_free_dots

    @staticmethod
    def three_or_two_decker_ship(deck_amount: int, free_dots: list):
        """Random choose the beginning and the end of three- and two-decker ships"""

        n = deck_amount - 1
        coord_begin = random.choice(free_dots)
        coord_end = None
        list_coord_end = [(coord_begin[0] + n, coord_begin[1]), (coord_begin[0] - n, coord_begin[1]),
                          (coord_begin[0], coord_begin[1] + n), (coord_begin[0], coord_begin[1] - n)]
        list_coord_end = [item for item in list_coord_end if item in free_dots]

        if not list_coord_end:
            PlayerComputer.three_or_two_decker_ship(deck_amount, free_dots)
        else:
            coord_end = random.choice(list_coord_end)
        dot_begin = Dot(x=coord_begin[0], y=coord_begin[1])
        dot_end = Dot(x=coord_end[0], y=coord_end[1])

        return [dot_begin, dot_end]

    @staticmethod
    def one_decker_ship(free_dots: list):
        """Random choose the beginning of one-decker ships"""

        coord_begin = random.choice(free_dots)
        dot_begin = Dot(x=coord_begin[0], y=coord_begin[1])
        return dot_begin

    def comp_shoot(self, board: Board):
        """Almost random shoot
        if hit, add dots in next_shoot_dots, raise ActionWasNotDone
        """

        if self.next_shoot_dots:
            dot = random.choice(self.next_shoot_dots)
            try:
                board.shoot(dot)         # SHOOT
                self.next_shoot_dots.remove(dot)
                self.clean_next_shoot_dots(board)
            except YouHitTheTarget:
                self.next_shoot_dots.remove(dot)
                self.comp_hit_the_target(dot.x, dot.y, board)
            except (AlreadyShot, ActionWasNotDone):
                self.next_shoot_dots.remove(dot)
                self.clean_next_shoot_dots(board)
                raise

        else:
            x, y = PlayerComputer.random_coord()
            if (isinstance(board.board_list[x][y], Dot) and  # computer wouldn't shoot in the contour
                    board.board_list[x][y].state == DotNames.contour):
                raise ActionWasNotDone
            try:
                board.shoot(Dot(x, y))         # SHOOT
            except YouHitTheTarget:
                self.comp_hit_the_target(x, y, board)
            except AlreadyShot:
                raise ActionWasNotDone

    def comp_hit_the_target(self, x, y, board):
        """Add neighboring cells at self.next_shoot_dots"""

        self.next_shoot_dots.extend([Dot(x + 1, y), Dot(x - 1, y), Dot(x, y + 1), Dot(x, y - 1)])
        self.clean_next_shoot_dots(board)
        print("Your board:")
        board.show_board()
        print("I hit the target! Let me think...")
        raise ActionWasNotDone

    def clean_next_shoot_dots(self, board):
        """Delete from next_shoot_dots list dots out of board and contour-dots"""

        self.next_shoot_dots = [dot for dot in self.next_shoot_dots
                                if Board.is_dot_on_board(dot)
                                and not ((isinstance(board.board_list[dot.x][dot.y], Dot) and
                                         board.board_list[dot.x][dot.y].state == DotNames.contour))]

    @staticmethod
    def random_coord():
        """Return random coordinates"""

        return random.randrange(6), random.randrange(6)


class Game:
    """Whole game"""

    def __init__(self):
        """New game"""

        self.human_first = random.randrange(2)  # 1 if human is first, else 0
        self.human = PlayerHuman()
        sleep(2)
        self.computer = PlayerComputer()

    def start(self):
        """Start the game"""

        global RULES
        print("I'm ready too\nMy board:")
        self.computer.board.show_board()
        print(RULES[1])
        if self.human_first:
            print("You go first")
        else:
            print("I go first")
        self.game_moves()
        self.play_again()

    def game_moves(self):
        """Moves one by one"""

        if self.human_first:
            player_1_shoot = self.human_move
            player_2_shoot = self.comp_move
        else:
            player_1_shoot = self.comp_move
            player_2_shoot = self.human_move

        while Game.lives_amount(self.human) > 0 and Game.lives_amount(self.computer) > 0:
            player_1_shoot(self.human, self.computer)
            if Game.lives_amount(self.human) == 0 or Game.lives_amount(self.computer) == 0:
                return
            player_2_shoot(self.human, self.computer)

    @staticmethod
    def human_move(human, computer):
        """Human move"""

        while True:
            if not Game.lives_amount(computer):
                print("You win!")
                return
            try:
                print("My board:")
                computer.board.show_board()
                computer.board.shoot(human.human_shoot())
                break
            except (YouHitTheTarget, ActionWasNotDone, AlreadyShot, OutOfBoard, InputRecognitionError) as error:
                if not Game.lives_amount(computer):
                    computer.board.show_board()
                    print("You win!")
                    return
                print(error)
                continue
        print("My board:")
        computer.board.show_board()

    @staticmethod
    def comp_move(human, computer):
        """Computer move"""

        while True:
            sleep(1)
            if not Game.lives_amount(human):
                print("You loose")
                return
            try:
                computer.comp_shoot(human.board)
                break
            except (ActionWasNotDone, AlreadyShot, YouHitTheTarget):
                continue
        print("My turn\nYour board:")
        human.board.show_board()
        if not Game.lives_amount(human):
            print("You loose")
            return

    @staticmethod
    def lives_amount(player):
        """Count amount of lives of all ships"""

        return sum([ship.lives for ship in player.board.ship_list])

    @staticmethod
    def play_again():
        """Ask player about repeat and start new game or say goodbye"""

        print("Maybe one more time?")
        answer = input("YES or NO\n")
        answer = PlayerHuman.clean_input(answer)

        if answer == "NO":
            print("Ok, bye! Have a nice day")
        elif answer == "YES":
            main()
        else:
            print("Sorry, I don't understand")
            Game.play_again()


if __name__ == '__main__':
    main()
else:
    print('battleship loaded as a module')
