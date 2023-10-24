from battleship import *


class PlayerComputerWithLogs:
    """
    Class for computer moves:
        creates board with random ships placement;
        shoots in random dot, when hit, shoots near
    """

    def __init__(self):
        """Create the board with ships"""

        self.board = Board(hidden=False)
        self.fill_board()
        self.board.delete_contour()
        self.board.show_board()

    def fill_board(self):
        """Fill the board with ships"""

        free_dots = [(x, y) for x in range(6) for y in range(6)]

        self.board.add_ship(Ship(*PlayerComputerWithLogs.three_or_two_decker_ship(3, free_dots)))
        free_dots = self.remove_occupied_dots(free_dots)
        self.board.show_board()
        print(free_dots)

        for i in range(2):
            self.board.add_ship(Ship(*PlayerComputerWithLogs.three_or_two_decker_ship(2, free_dots)))
            free_dots = self.remove_occupied_dots(free_dots)
            self.board.show_board()
            print(free_dots)

        for i in range(4):
            if len(self.board.ship_list) == 7:
                break
            self.board.add_ship(Ship(PlayerComputerWithLogs.one_decker_ship(free_dots)))
            free_dots = self.remove_occupied_dots(free_dots)
            self.board.show_board()

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
            PlayerComputerWithLogs.three_or_two_decker_ship(deck_amount, free_dots)
        else:
            coord_end = random.choice(list_coord_end)
        dot_begin = Dot(x=coord_begin[0], y=coord_begin[1])
        dot_end = Dot(x=coord_end[0], y=coord_end[1])

        return [dot_begin, dot_end]

    @staticmethod
    def one_decker_ship(free_dots: list):
        """Random choose the beginning of one-decker ships"""

        print(free_dots)
        coord_begin = random.choice(free_dots)
        dot_begin = Dot(x=coord_begin[0], y=coord_begin[1])
        return dot_begin


"""  TEST  """

comp = PlayerComputerWithLogs()
