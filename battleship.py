"""Play the Battleship with your computer!
Classes:
"""

import enum


class OutOfDesk(IndexError):
    pass


class FieldIsOccupied(Exception):
    pass


class IncorrectShip(Exception):
    pass


class OtherShipIsNear(Exception):
    pass


class AllTheseShipsAreUsed(Exception):
    pass


class AlreadyShoot(Exception):
    pass


class DotNames(enum.Enum):
    """All possible states of dot"""

    empty = 1
    contour = 2
    ship = 3
    burn = 4
    killed = 5
    miss = 6


class Dot:
    """Dot's coordinates and state"""

    def __init__(self, x: int, y: int, state=DotNames.empty):
        """Init the dot"""
        self.x = x
        self.y = y
        self.state = state

    def __eq__(self, other):                              # maybe must be rewritten or delete at all
        """Equality of two dots"""
        return self.x == other.x and self.y == other.y


class Ship:
    """Ship and something about ship"""
    def __init__(self, begin: Dot, end=None):
        self.begin = begin
        self.end = end
        self.lives = self.__len__()
        self.id = len(Ship.__dict__)

    def is_single_deck(self):
        if self.end is None:
            self.end = self.begin

    def check_correct_ship(self):
        return (self.begin.x == self.end.x
                and self.begin.x - self.end.x <= 3
                or self.begin.y == self.end.y
                and self.begin.y - self.end.y <= 3)

    def __len__(self):
        return max(self.begin.x - self.end.x, self.begin.y - self.end.y) + 1

    def find_all_dots(self):
        if len(self) == 1:
            self.all_dots = [self.begin]
        elif len(self) == 2:
            self.all_dots = [self.begin, self.end]
        else:
            self.all_dots = [self.begin,
                             # find middle dot:
                             Dot(x=(self.begin.x + self.end.x) / 2, y=(self.begin.y + self.end.y) / 2),
                             self.end]
        for dot in self.all_dots:
            dot.state = DotNames.ship
