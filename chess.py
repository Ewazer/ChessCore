from constants import *

class Board:
    def __init__(self):
        """
        Initialize the game state.
        Sets up the initial board configuration, creates a history log for board states,
        and initializes an empty record for moves made.
        """

        self.board = self.init_board()
        self.board_history = [self.copy_board()]
        self.move_history = []
        self.side_to_move = WHITE
        self.counter_halfmove_without_capture = 0
        self.castling_rights = set("KQkq")
        self.position_has_loaded = False
        self.position_hash_history = {self.get_position_hash(): 1}


    @staticmethod
    def init_board():
        """
        Initialize the chess board to the standard starting position.

        Returns:
            list: 2D matrix representing the initial board state.

        Note: 
            When defining the table, the coordinates are intentionally reversed because this is how board is managed.
        """

        return [
            [ ROOK, KNIGHT, BISHOP, KING, QUEEN, BISHOP, KNIGHT, ROOK],
            [ PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN],
            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [ EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [-PAWN,-PAWN,-PAWN,-PAWN,-PAWN,-PAWN,-PAWN,-PAWN],
            [-ROOK,-KNIGHT,-BISHOP,-KING,-QUEEN,-BISHOP,-KNIGHT,-ROOK]
        ]
    

    def setting_castling_rights(self):
        """Update castling rights based on the current board state."""

        rights = set()

        if self.board[0][3] == KING:
            if self.board[0][7] == ROOK:
                rights.add("K")
            if self.board[0][0] == ROOK:
                rights.add("Q")

        if self.board[7][3] == -KING:
            if self.board[7][7] == -ROOK:
                rights.add("k")
            if self.board[7][0] == -ROOK:
                rights.add("q")

        self.castling_rights = rights


    def load_board(self, board, side = WHITE):
        """
        Load a custom board configuration.

        Args:
            board (list): 2D matrix representing the board state, oriented from White's perspective (row 0 = first White rank, column 0 = 'a' file).
            Pieces must be encoded using the following constants:
            EMPTY = 0
            PAWN = 1
            KNIGHT = 3
            BISHOP = 4
            ROOK = 5
            KING = 7
            QUEEN = 9
            Black pieces are represented by the corresponding negative value (e.g., -PAWN for a black pawn).
            side (int): Board.WHITE (1) or Board.BLACK (-1).

        Returns:
            None

        Note:
            Ignoring the fact that the parts were moved beforehand is irrelevant because it's only used with load.
        """

        self.board = [e[::-1] for e in board[::-1]]
        self.board_history = [self.copy_board()]
        self.move_history = []
        self.counter_halfmove_without_capture = 0
        self.setting_castling_rights()
        self.side_to_move = side
        self.position_has_loaded = True

    
    @staticmethod
    def find_piece(board, f_piece):
        """
        Find the coordinates of a specific piece on the board.

        Args:
            board_test (list): 2D list representing the board state.
            f_piece (int): Piece to find.

        Returns:
            tuple or None: (col, row) if found, else None.

        Note:
            This function is used only to search for a king, so we assume there is only one piece on the chessboard.
        """

        for x, row in enumerate(board): 
            for y, cell in enumerate(row): 
                if cell == f_piece:  
                    return (y + 1, x + 1)
        return None
    
    
    def copy_board(self):
        """Create a deep copy of the board."""

        return [row[:] for row in self.board]
    
    
    def add_to_history(self, move):
        """
        Add a move to history and save board state.
        
        Args:
            move (dict): Move information with keys 'from', 'to', 'piece', etc.
        """

        self.move_history.append(move)
        self.board_history.append(self.copy_board())
        self.position_hash_history[self.get_position_hash()] = self.position_hash_history.get(self.get_position_hash(), 0) + 1


    def undo_move(self):
        """
        Undo the last move. 
        
        Returns:
            bool: True if undo successful, False if no moves to undo

        Note:
            Ignoring the fact that the parts were moved beforehand is irrelevant because it's only used with load_board().
        """

        if len(self.board_history) <= 1:
            return False
        
        self.board_history.pop()
        self.board = [row[:] for row in self.board_history[-1]]
        self.move_history.pop()
        self.change_side()
        self.setting_castling_rights()
        return True
    
    
    def get_position_hash(self):
        """
        Generate a hash of the current board position.
        Useful for detecting repetitions.
        """

        return hash((
            tuple(tuple(r) for r in self.board),
            self.side_to_move,
            tuple(sorted(self.castling_rights)),
        ))
    

    def update_board(self, board_to_copy, move, change_side_to_move = True, active_counter_halfmove_without_capture = True, update_history=True):
        """
        Update the internal board state based on a move and a new board configuration.
        This method handles:
        - Updating the halfmove clock (for the 50-move rule) based on pawn moves or captures.
        - Updating castling rights if the King or Rook moves, or if a Rook is captured.
        - Applying the new board state.
        - Optionally switching the side to move.
        - Optionally updating the move and board history.

        Args:
            board_to_copy (list): A 2D list representing the new state of the board to apply.
            move (dict): A dictionary containing move details ('x_start_coordinate', 'y_start_coordinate', 'x_end_coordinate', 'y_end_coordinate').
            change_side_to_move (bool, optional): Whether to switch the active player after the update. Defaults to True.
            active_counter_halfmove_without_capture (bool, optional): Whether to update the halfmove clock counter. Defaults to True.

        Returns:
            None
        """
        
        if active_counter_halfmove_without_capture:
            reset_halfmove_clock = False

            if abs(self.board[move['y_start_coordinate']][move['x_start_coordinate']]) == PAWN:
                reset_halfmove_clock = True
            elif self.board[move['y_end_coordinate']][move['x_end_coordinate']] != EMPTY:
                reset_halfmove_clock = True

            if not reset_halfmove_clock:
                self.counter_halfmove_without_capture += 1
            else:
                self.counter_halfmove_without_capture = 0

        if self.board[move['y_start_coordinate']][move['x_start_coordinate']] == KING*self.side_to_move:
            if self.side_to_move == WHITE:
                self.castling_rights.discard("K")
                self.castling_rights.discard("Q")
            else:
                self.castling_rights.discard("k")
                self.castling_rights.discard("q")

        elif self.board[move['y_start_coordinate']][move['x_start_coordinate']] == ROOK*self.side_to_move:
            if self.side_to_move == WHITE:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                    self.castling_rights.discard("Q")
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                    self.castling_rights.discard("K")
            else:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                    self.castling_rights.discard("q")
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                    self.castling_rights.discard("k")

        if self.board[move['y_end_coordinate']][move['x_end_coordinate']] == ROOK*-self.side_to_move:
            if self.side_to_move == WHITE:
                if move['x_end_coordinate'] == 0 and move['y_end_coordinate'] == 7:
                    self.castling_rights.discard("q")
                elif move['x_end_coordinate'] == 7 and move['y_end_coordinate'] == 7:
                    self.castling_rights.discard("k")
            else:
                if move['x_end_coordinate'] == 0 and move['y_end_coordinate'] == 0:
                    self.castling_rights.discard("Q")
                elif move['x_end_coordinate'] == 7 and move['y_end_coordinate'] == 0:
                    self.castling_rights.discard("K")

        
        self.board = [row[:] for row in board_to_copy]

        if change_side_to_move:
            self.change_side()

        if update_history:
            self.add_to_history(move)


    def change_side(self):
        """Change the side to move."""

        self.side_to_move *= -1


    @staticmethod
    def material_insufficiency(board):
        """
        Determine if the board has insufficient material to continue the game.

        Args:
            board (list): 2D list representing the board state.
            
        Returns:
            bool: True if only kings remain (insufficient material), False otherwise.
        """
        
        for row in board:
            for element in row:
                if element not in [EMPTY, KING, -KING]:
                    return False
        return True


class MoveParser:
    @staticmethod
    def give_move_info(all_move, board, debug=False):
        """
        Extract move information from a move string and validate coordinates.
        Args:
            all_move (str): Move in the format "e2 e4".
            board (list): 2D list representing the board state.
            debug (bool, optional): Print debug info if True.
        Returns:
            dict or 'illegal': Move details as dict, or 'illegal' if invalid.
        """

        try:
            all_move = all_move.split(" ")

            start_move = all_move[0]
            end_move = all_move[1]


            x_start_coordinate = start_move[:1]
            y_start_coordinate = int(start_move[1:]) - 1


            if x_start_coordinate in coordinate:
                x_start_coordinate = int(coordinate[x_start_coordinate]) - 1

            else:
                return 'illegal'
    
            start_value = board[y_start_coordinate][x_start_coordinate]

            if start_value == EMPTY:
                return 'illegal'

            x_end_coordinate = end_move[:1]
            y_end_coordinate = int(end_move[1:]) - 1

            if x_end_coordinate in coordinate:
                x_end_coordinate = int(coordinate[x_end_coordinate]) - 1
            else:
                return 'illegal'

            end_value = board[y_end_coordinate][x_end_coordinate]

            name_piece_coor1 = piece[start_value]
            name_piece_coor2 = piece[end_value]

            if debug:
                print("----move----")
                print(f'{start_move} and {end_move}')
                print()
                print("----coordonnées----")
                print("coordinate valide matrice 1:", x_start_coordinate,"and",y_start_coordinate)
                print("coordinate valide matrice 2:", x_end_coordinate,"and",y_end_coordinate)
                print()
                print("----piece----")
                print("start_value:",start_value,"end_value:",end_value)
                print("start_value:",name_piece_coor1,"end_value:",name_piece_coor2)
                print()

            move = {
                "start_move":start_move,
                "end_move":end_move,
                "x_start_coordinate":x_start_coordinate,
                "y_start_coordinate":y_start_coordinate,
                "x_end_coordinate":x_end_coordinate,
                "y_end_coordinate":y_end_coordinate,
                "start_value":start_value,
                "end_value":end_value,
                "name_piece_coor1":name_piece_coor1,
                "name_piece_coor2":name_piece_coor2
            }

            return move
        
        except (IndexError, ValueError, KeyError):
            return 'illegal'

    @staticmethod
    def is_valid_move_format(all_move):
        """
        Validate if the move string has the correct format.

        A valid move must be 5 characters long: source square (letter + number),
        a space, and destination square (letter + number).

        Args:
            all_move (str): The move string to validate (e.g., "e2 e4").

        Returns:
            bool: True if the move format is valid, False otherwise.
        """

        return (len(all_move) == 5 and
        all_move[0] in 'abcdefgh' and
        all_move[3] in 'abcdefgh' and
        all_move[1] in '12345678' and
        all_move[2] == ' ' and
        all_move[4] in '12345678')


class Validator:
    @staticmethod
    def promote_pawn(side, promotion_value=None, auto_promotion_value=QUEEN):
        """
        Handle pawn promotion for the given color.

        Args:
            side (int): 1 for white or -1 for black.
            auto_promotion (bool): Whether to automatically promote pawns.
            auto_promotion_value (int): The piece to promote to if auto_promotion is True.
    
        Returns:
            int or 'invalid': Promotion value or 'invalid' if not set.
        """
        if promotion_value:
            return promotion_value * side
        
        elif auto_promotion_value:
            return auto_promotion_value * side

        else:
            print("\033[31mPlease set auto_promotion or provide a promotion piece. Exemple: 'e7 e8q' for queen promotion (the queen: 'q', the rook: 'r', the bishop: 'b' and the knight 'n').\033[0m")
            return 'invalid'
        

    @staticmethod
    def valid_pawn_move(move, move_history, board, promotion_value=None, auto_promotion_value=QUEEN):
        """
        Validate a pawn move, including en passant and promotion.
        Args:
            move (dict): Move details with coordinates and piece info.
            move_history (list): List of previous moves made in the game.
            board (list): Current board state.
        Returns:
            str: 'valid', 'illegal', 'en passant', or 'invalid'.
        """

        if move['end_value'] == EMPTY: 
            if move_history:
                if (move['y_start_coordinate'] == 4 if move['start_value'] > 0 else move['y_start_coordinate'] == 3):
                    if board[move['y_start_coordinate']][move['x_end_coordinate']] == (-PAWN if move['start_value'] > 0 else PAWN):
                        if move['x_end_coordinate'] == move['x_start_coordinate']+1:
                            if move_history[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return 'en passant'
                            
                        elif move['x_end_coordinate'] == move['x_start_coordinate']-1:
                            if move_history[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return 'en passant'
                            
            if move['x_end_coordinate'] == move['x_start_coordinate']: 
                if move['name_piece_coor1'] == "white_pawn":     
                    if (
                        move['y_end_coordinate'] == move['y_start_coordinate'] + 1
                        or (
                            move['y_end_coordinate'] == move['y_start_coordinate'] + 2
                            and move['y_start_coordinate'] == 1
                            and board[move['y_start_coordinate'] + 1][move['x_start_coordinate']] == EMPTY
                        )
                    ):
                        if move['y_end_coordinate'] == 7:
                            move["start_value"] = Validator.promote_pawn(WHITE, promotion_value=promotion_value, auto_promotion_value=auto_promotion_value)
                            if move["start_value"] == 'invalid':
                                return 'invalid'
                            
                        return 'valid'
                    
                    else:
                        return 'illegal'

                if move['name_piece_coor1'] == "black_pawn":
                    if (
                        move['y_start_coordinate'] == move['y_end_coordinate'] + 1
                        or (
                            move['y_start_coordinate'] == move['y_end_coordinate'] + 2
                            and move['y_start_coordinate'] == 6
                            and board[move['y_start_coordinate'] - 1][move['x_start_coordinate']] == EMPTY
                        )
                    ):
                        if move['y_end_coordinate'] == 0:
                            move["start_value"] = Validator.promote_pawn(BLACK, promotion_value=promotion_value, auto_promotion_value=auto_promotion_value)
                            if move["start_value"] == 'invalid':
                                return 'invalid'
                            
                        return 'valid'
                    else:
                        return 'illegal'

                if move['name_piece_coor1'] != "black_pawn" and move['name_piece_coor1'] != "white_pawn":
                    return 'illegal'
                
            else: 
                return 'illegal'

        elif move['end_value'] != EMPTY:
            if move['name_piece_coor1'] == "white_pawn":
                if move['end_value'] > 0:
                    return 'illegal'
                if (
                    abs(move['x_end_coordinate'] - move['x_start_coordinate']) == 1
                    and move['y_end_coordinate'] == move['y_start_coordinate'] + 1
                ):
                        if move['y_end_coordinate'] == 7:
                            move["start_value"] = Validator.promote_pawn(WHITE, promotion_value=promotion_value, auto_promotion_value=auto_promotion_value)
                            if move["start_value"] == 'invalid':
                                return 'invalid'
                            
                        return 'valid'
                
                else:
                    return 'illegal'


            if move['name_piece_coor1'] == "black_pawn":
                if move['end_value'] < 0:
                    return('illegal')
                if (
                    abs(move['x_end_coordinate'] - move['x_start_coordinate']) == 1
                    and move['y_end_coordinate'] == move['y_start_coordinate'] - 1
                ):
                    if move['y_end_coordinate'] == 0:
                        move["start_value"] = Validator.promote_pawn(BLACK, promotion_value=promotion_value, auto_promotion_value=auto_promotion_value)
                        if move["start_value"] == 'invalid':
                            return 'invalid'
                        
                    return 'valid'
                
                else:
                    return 'illegal'
                
            return 'illegal'
        

    @staticmethod
    def valid_bishop_move(move, board):
        """
        Validate a bishop (or queen as bishop) move.
        Args:
            move (dict): Move details with coordinates and piece info.
            board (list): Current board state.
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        if (move['name_piece_coor1'] in ('black_bishop', 'black_queen') and move['end_value'] < 0) or \
           (move['name_piece_coor1'] in ('white_bishop', 'white_queen') and move['end_value'] > 0):
            return 'illegal'
        
        if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == abs(move['y_start_coordinate'] - move['y_end_coordinate']):
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1:
                return 'valid'
            
            x = 1 if move['x_start_coordinate'] < move['x_end_coordinate'] else -1
            y = 1 if move['y_start_coordinate'] < move['y_end_coordinate'] else -1

            x_start_coordinate = move['x_start_coordinate'] + x
            y_start_coordinate = move['y_start_coordinate'] + y

            while x_start_coordinate != move['x_end_coordinate']:
                if board[y_start_coordinate][x_start_coordinate] != EMPTY:
                        return 'illegal'
                
                x_start_coordinate += x
                y_start_coordinate += y
                    
            return 'valid'
        
        else:
            return 'illegal'
        

    @staticmethod
    def valid_rook_move(move, board):
        """
        Validate a rook move and update castling rights.
        Args:
            move (dict): Move details with coordinates and piece values.
            debug (optional): Debug flag.
            board (list): Current board state.
    
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        if move['end_value'] == EMPTY or (move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0):
            if move['y_start_coordinate'] == move['y_end_coordinate']:
                for i in range(min(move['x_start_coordinate'], move['x_end_coordinate']), max(move['x_start_coordinate'], move['x_end_coordinate'])):
                    if board[move['y_start_coordinate']][i] != EMPTY and [i] != [move['x_start_coordinate']] and [i] != [move['x_end_coordinate']]:
                        return 'illegal'
                    
                return('valid')
            
            elif move['x_start_coordinate'] == move['x_end_coordinate']:
                for i in range(min(move['y_start_coordinate'], move['y_end_coordinate']), max(move['y_start_coordinate'], move['y_end_coordinate'])):
                    if board[i][move['x_start_coordinate']] != EMPTY and [i] != [move['y_start_coordinate']] and [i] != [move['y_end_coordinate']]:
                        return 'illegal'
                    
                return 'valid'
            
        return 'illegal'
    
    
    @staticmethod
    def valid_knight_move(move):
        """
        Validate if a knight move is legal.
        Args:
            move (dict): Move details with start/end coordinates and values.
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        if move['end_value'] == EMPTY or ((move['end_value'] > 0 and move['start_value'] < 0) or (move['end_value'] < 0 and move['start_value'] > 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 1:
                return 'valid'
            
            elif abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 2:
                return 'valid'
            
        else:
            return 'illegal'
        

    @staticmethod
    def valid_queen_move(move, board):
        """
        Validate if the queen move is legal.
        Args:
            move (str): Chess move in algebraic notation.
        Returns:
            str: 'valid' if the move is legal, 'illegal' otherwise.
        """

        if Validator.valid_rook_move(move, board) == 'valid' or Validator.valid_bishop_move(move, board) == 'valid':
            return 'valid'
        
        else:
            return 'illegal'
        
        
    @staticmethod
    def valid_king_move(move, castling_rights, board):
        """
        Validate king moves, including castling and big castling.
        
        Args:
            move (dict): Move details with coordinates and piece values.
            board (list): Current board state.
            castling_rights (set): Current castling rights.
        Returns:
            str: 'casting', 'big_casting', 'valid', or 'illegal'.
        """

        if (
            move['end_value'] == EMPTY
            and (
            "K" in castling_rights if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else "k" in castling_rights
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and board[move['y_end_coordinate']][move['x_end_coordinate'] - 1] in (-ROOK, ROOK)
        ):
            if GameState.is_check((1 if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else -1), board) != 'check':
                if board[move['y_end_coordinate']][move['x_end_coordinate']+1] == EMPTY:
                    new_board = [row[:] for row in board]
                    new_board[move["y_start_coordinate"]][move["x_start_coordinate"]] = EMPTY
                    new_board[move["y_start_coordinate"]][move["x_start_coordinate"]-1] = board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if GameState.is_check((1 if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else -1), new_board) != 'check':
                        if ("K" in castling_rights if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else "k" in castling_rights):
                            return 'casting'

        elif (
            move['end_value'] == EMPTY
            and (
                "Q" in castling_rights if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0
                else "q" in castling_rights
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and board[move['y_end_coordinate']][move['x_end_coordinate'] + 2] in (-ROOK, ROOK)
        ):
            if GameState.is_check((1 if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else -1), board) != 'check':
                if board[move['y_end_coordinate']][move['x_end_coordinate']+1] == EMPTY and board[move['y_end_coordinate']][move['x_end_coordinate']-1] == EMPTY:
                    new_board = [row[:] for row in board]
                    new_board[move["y_start_coordinate"]][move["x_start_coordinate"]] = EMPTY
                    new_board[move["y_start_coordinate"]][move["x_start_coordinate"]+1] = board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if GameState.is_check((1 if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else -1), new_board) != 'check':
                        if ("Q" in castling_rights if board[move["y_start_coordinate"]][move["x_start_coordinate"]] > 0 else "q" in castling_rights):
                            return 'big_casting'
                        
        if move['end_value'] == EMPTY or ((move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) <= 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) <= 1:
                return 'valid'
            
            else:
                return 'illegal'
            
        else:
            return 'illegal'
        

class MoveGen:
    @staticmethod
    def list_pawn_move(y, x, board):
        """
        Generate all legal pawn moves from a given position.
        Args:
            y (int): Row index of the pawn.
            x (int): Column index of the pawn.
            board (list): Current board state.
        Returns:
            list: List of possible pawn moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_p_move = []
        direction = 1 if board[y][x] == PAWN else -1 

        if board[y + direction][x] == EMPTY:
            list_p_move.append([[y,x],[y + direction, x]])
            if (y == 1 and direction == 1) or (y == 6 and direction == -1):
                if board[y + 2 * direction][x] == EMPTY:
                    list_p_move.append([[y,x],[y + 2 * direction, x]])

        if x + 1 <= 7 and board[y + direction][x + 1] * board[y][x] < 0:
            list_p_move.append([[y,x],[y + direction, x + 1]])

        if x - 1 >= 0 and board[y + direction][x - 1] * board[y][x] < 0: 
            list_p_move.append([[y,x],[y + direction, x - 1]])
        
        return list_p_move
    

    @staticmethod
    def list_knight_move(y, x, board):
        """
        Generate all valid knight moves from a given position.
        Args:
            y (int): Row index of the knight.
            x (int): Column index of the knight.
            board (list): Current board state.  
        Returns:
            list: List of valid knight moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_k_move = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

        if board[y][x] in (KNIGHT,-KNIGHT):
            for e in knight_moves:
                if y+e[0] >= 0 and y+e[0] <= 7 and x+e[1] >= 0 and x+e[1] <= 7:
                    if (board[y+e[0]][x+e[1]] <= 0 if board[y][x] == KNIGHT else board[y+e[0]][x+e[1]] >= 0):
                        list_k_move.append([[y,x],[y+e[0],x+e[1]]])
        return list_k_move
    

    @staticmethod
    def list_bishop_move(y, x, board):
        """
        Generate all legal bishop moves from a given position.
        Args:
            y (int): Row index of the bishop.
            x (int): Column index of the bishop.
            board (list): Current board state.
        Returns:
            list: List of possible bishop moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_b_move = []
        bishop_move = [(1,1),(-1,1),(-1,-1),(1,-1)]

        if board[y][x] in (BISHOP,-BISHOP):
            for e in bishop_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == EMPTY:
                    list_b_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == BISHOP else board[y_c][x_c] > 0):
                    list_b_move.append([[y,x],[y_c,x_c]])

        return list_b_move
    

    @staticmethod
    def list_rook_move(y, x, board):
        """
        Generate all legal rook moves from a given position.
        Args:
            y (int): Row index of the rook.
            x (int): Column index of the rook.
            board (list): Current board state.
        Returns:
            list: List of possible rook moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_r_move = []
        rook_move = [(0,1),(0,-1),(-1,0),(1,0)]

        if board[y][x] in (ROOK,-ROOK):
            for e in rook_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == EMPTY:
                    list_r_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == ROOK else board[y_c][x_c] > 0):
                    list_r_move.append([[y,x],[y_c,x_c]])     

        return list_r_move
    

    @staticmethod
    def list_queen_move(y, x, board):
        """
        Generate all valid queen moves from the given position.
        Args:
            y (int): Row index of the queen.
            x (int): Column index of the queen.
            board (list): Current board state.
        Returns:
            list: List of valid queen moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_q_move = []
        queen_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if board[y][x] in (QUEEN,-QUEEN):
            for e in queen_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == EMPTY:
                    list_q_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == QUEEN else board[y_c][x_c] > 0):
                    list_q_move.append([[y,x],[y_c,x_c]])    

        return list_q_move
    
    
    @staticmethod
    def list_king_move(y, x, castling_rights, board):
        """
        Generate all legal king moves (including castling) from position (y, x).
        Args:
            y (int): Row index of the king.
            x (int): Column index of the king.
            castling_rights (set): Current castling rights.
            board (list): Current board state.
        Returns:
            list: List of possible king moves as [[from_y, from_x], [to_y, to_x]].
        """

        list_k_move = []
        king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if board[y][x] in (KING,-KING):
            for e in king_move:
                y_c = y + e[0]
                x_c = x + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] >= 0 if board[y][x] == -KING else board[y_c][x_c] <= 0):
                    list_k_move.append([[y,x],[y_c,x_c]])

        if (
            ("K" in castling_rights if board[y][x] > 0 else "k" in castling_rights)
            and board[y][x] > 0
        ):
            if board[y][x-1] == EMPTY and board[y][x-2] == EMPTY:
                new_board = [row[:] for row in board]
                new_board[y][x-1] = board[y][x]
                new_board[y][x] = EMPTY
                if GameState.is_check(1 if board[y][x] > 0 else -1, new_board) != 'check':
                    list_k_move.append([[y,x],[y,x-2]])

        if (
            ("Q" in castling_rights if board[y][x] > 0 else "q" in castling_rights)
            and board[y][x] > 0
            and board[y][x] > 0
        ):
            if board[y][x+1] == EMPTY and board[y][x+2] == EMPTY and board[y][x+3] == EMPTY:
                new_board = [row[:] for row in board]
                new_board[y][x+1] = board[y][x] 
                new_board[y][x] = EMPTY
                if GameState.is_check(1 if board[y][x] > 0 else -1, new_board) != 'check':
                    list_k_move.append([[y,x],[y,x+2]])

        return list_k_move


    @staticmethod
    def list_all_legal_move(side, board, castling_rights = {}):
        """
        List all legal moves for the given color, excluding moves that leave the king in check.
        
        Args:
            side (int): 1 for white or -1 for black.
            board (list): A 2D list representing the current state of the chess board.
            castling_rights (set, optional): Current castling rights.
        
        Returns:
            list: List of legal moves as tuples of start and end positions.
        """

        list_all_move = []

        for y_i in range(0,8):
            for x_i in range(0,8):
                if board[y_i][x_i] != EMPTY and ((side == 1 and board[y_i][x_i] > 0) or (side == -1 and board[y_i][x_i] < 0)):
                    n_move = []
                    if abs(board[y_i][x_i]) == PAWN:
                        n_move = MoveGen.list_pawn_move(y_i,x_i, board)
                    elif abs(board[y_i][x_i]) == KING:
                        n_move = MoveGen.list_king_move(y_i,x_i, castling_rights, board)
                    elif abs(board[y_i][x_i]) == QUEEN:
                        n_move = MoveGen.list_queen_move(y_i,x_i, board)
                    elif abs(board[y_i][x_i]) == ROOK:
                        n_move = MoveGen.list_rook_move(y_i,x_i, board)
                    elif abs(board[y_i][x_i]) == BISHOP:
                        n_move = MoveGen.list_bishop_move(y_i,x_i, board)
                    elif abs(board[y_i][x_i]) == KNIGHT:
                        n_move = MoveGen.list_knight_move(y_i,x_i, board)
                    if n_move:
                        for m in n_move:
                            new_board = [row[:] for row in board]
                            new_board[m[0][0]][m[0][1]] = EMPTY
                            new_board[m[1][0]][m[1][1]] = board[y_i][x_i]
                            if GameState.is_check(side, new_board) != 'check':
                                list_all_move.append(m)
                
        return list_all_move


    @staticmethod
    def list_all_piece_move(y, x, piece_value, board, castling_rights = {}):
        """
        Generate all possible moves for a given piece on the board.

        Args:
            x (int): The x-coordinate (column) of the piece.
            y (int): The y-coordinate (row) of the piece.
            piece_value (int): The value representing the type and color of the piece.
            board (list): The current state of the chess board.

        Returns:
            list: A list of possible moves for the specified piece.
        """

        if abs(piece_value) == PAWN:
            return MoveGen.list_pawn_move(y, x, board)
        elif abs(piece_value) == KNIGHT:
            return MoveGen.list_knight_move(y, x, board)
        elif abs(piece_value) == BISHOP:
            return MoveGen.list_bishop_move(y, x, board)
        elif abs(piece_value) == ROOK:
            return MoveGen.list_rook_move(y, x, board)
        elif abs(piece_value) == QUEEN:
            return MoveGen.list_queen_move(y, x, board)
        elif abs(piece_value) == KING:
            return MoveGen.list_king_move(y, x, castling_rights, board)
        else:
            return


class GameState:
    @staticmethod
    def is_check(side, board_actual):
        """
        Check if the king of the given color is in check.
        Args:
            side (int): 1 for white or -1 for black.
            board_actual (list): Current board state.
        Returns:
            str: 'check', 'valid', or 'error'.
        """

        KING_TO_CHECK = KING*side

        OPPOSING_PAWN = -PAWN*side
        OPPOSING_KNIGHT = -KNIGHT*side
        OPPOSING_BISHOP = -BISHOP*side
        OPPOSING_ROOK = -ROOK*side
        OPPOSING_QUEEN = -QUEEN*side
        OPPOSING_KING = -KING_TO_CHECK

        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        king_position = Board.find_piece(board_actual, KING_TO_CHECK)

        try:
            king_position[0]
        except:
            return 'error'

        for i in range(king_position[0] - 1, 8):
            if board_actual[king_position[1] - 1][i] in (OPPOSING_ROOK, OPPOSING_QUEEN):
                return 'check'
            if board_actual[king_position[1] - 1][i] not in (EMPTY, -OPPOSING_KING):
                break

        for i in range(king_position[0] - 1, -1, -1):
            if board_actual[king_position[1] - 1][i] in (OPPOSING_ROOK, OPPOSING_QUEEN):
                return 'check'
            if board_actual[king_position[1] - 1][i] not in (EMPTY, -OPPOSING_KING):
                break

        for i in range(king_position[1] - 1, 8):
            if board_actual[i][king_position[0] - 1] in (OPPOSING_ROOK, OPPOSING_QUEEN):
                return 'check'
            if board_actual[i][king_position[0] - 1] not in (EMPTY, -OPPOSING_KING):
                break

        for i in range(king_position[1] - 1, -1, -1):
            if board_actual[i][king_position[0] - 1] in (OPPOSING_ROOK, OPPOSING_QUEEN):
                return 'check'
            if board_actual[i][king_position[0] - 1] not in (EMPTY, -OPPOSING_KING):
                break

        x = king_position[0] - 1
        y = king_position[1] - 1
        while y <= 7 and x <= 7:
            if board_actual[y][x] in (OPPOSING_BISHOP, OPPOSING_QUEEN):
                return 'check'
            if board_actual[y][x] not in (EMPTY, -OPPOSING_KING):
                break
            y += 1
            x += 1

        x = king_position[0] - 1
        y = king_position[1] - 1
        while y >= 0 and x >= 0:
            if board_actual[y][x] in (OPPOSING_BISHOP, OPPOSING_QUEEN):
                return 'check'
            if board_actual[y][x] not in (EMPTY, -OPPOSING_KING):
                break
            y -= 1
            x -= 1

        x = king_position[0] - 1
        y = king_position[1] - 1
        while y <= 7 and x >= 0:
            if board_actual[y][x] in (OPPOSING_BISHOP, OPPOSING_QUEEN):
                return 'check'
            if board_actual[y][x] not in (EMPTY, -OPPOSING_KING):
                break
            y += 1
            x -= 1

        x = king_position[0] - 1
        y = king_position[1] - 1
        while y >= 0 and x <= 7:
            if board_actual[y][x] in (OPPOSING_BISHOP, OPPOSING_QUEEN):
                return 'check'
            if board_actual[y][x] not in (EMPTY, -OPPOSING_KING):
                break
            y -= 1
            x += 1

        for p in knight_moves:
            x = king_position[0] - 1 + p[0]
            y = king_position[1] - 1 + p[1]
            if 0 <= y <= 7 and 0 <= x <= 7:
                if board_actual[y][x] == OPPOSING_KNIGHT:
                    return 'check'

        if side == WHITE:
            y = king_position[1]
            x = king_position[0]
            if 0 <= y <= 7 and 0 <= x <= 7:
                if board_actual[y][x] == OPPOSING_PAWN:
                    return 'check'

            x = king_position[0] - 2
            if 0 <= y <= 7 and 0 <= x <= 7:
                if board_actual[y][x] == OPPOSING_PAWN:
                    return 'check'
        else:
            y = king_position[1] - 2
            x = king_position[0]
            if 0 <= y <= 7 and 0 <= x <= 7:
                if board_actual[y][x] == OPPOSING_PAWN:
                    return 'check'

            x = king_position[0] - 2
            if 0 <= y <= 7 and 0 <= x <= 7:
                if board_actual[y][x] == OPPOSING_PAWN:
                    return 'check'

        x = king_position[0] - 1
        y = king_position[1] - 1
        king_move = [(1, 1), (-1, 1), (-1, -1), (1, -1),
                    (0, 1), (0, -1), (-1, 0), (1, 0)]
        if board_actual[y][x] in (OPPOSING_KING, -OPPOSING_KING):
            for e in king_move:
                y_c = y + e[0]
                x_c = x + e[1]
                if 0 <= y_c <= 7 and 0 <= x_c <= 7 and \
                board_actual[y_c][x_c] in (OPPOSING_KING, -OPPOSING_KING):
                    return 'check'

        return 'valid'


    @staticmethod
    def is_checkmate(side, board_actual):
        """
        Determine if the given color is in checkmate on the provided board.
        Args:
            side (int): 1 for white or -1 for black.
            board_actual (list): Current board state.
        Returns:
            bool: True if checkmate, False otherwise.
        """

        if side in (1, -1):
            if GameState.is_check(side, board_actual) == 'check':
                # Rook rights don't matter since you can't rook if you're in check.                
                move = MoveGen.list_all_legal_move(side, board_actual)
                
                for m in move:
                    if board_actual[m[0][0]][m[0][1]] not in (KING,-KING) or abs(m[0][1]-m[1][1]) != 2:
                        new_board = [e[:] for e in board_actual] 
                        new_board[m[0][0]][m[0][1]] = EMPTY
                        new_board[m[1][0]][m[1][1]] = board_actual[m[0][0]][m[0][1]]
                        if GameState.is_check(side, new_board) != 'check':
                            return False
                        
                return True
            
        return False
    
    def check_repetition(hash, position_hash_history):
        """
        Check if a board position has occurred at least three times (threefold repetition).

        Args:
            hash (int): The hash value representing the current board position.
            position_hash_history (dict): A dictionary mapping position hashes to their occurrence counts.
            
        Returns:
            bool: True if any board position has occurred at least three times, False otherwise.
        """

        return position_hash_history.get(hash, 0) >= 3


class ChessDisplay:
    piece_note_style = {
        PAWN: "♙",   
        ROOK: "♖",   
        KNIGHT: "♘",  
        BISHOP: "♗",   
        QUEEN: "♕",  
        KING: "♔", 
        -PAWN: "♟",
        -ROOK: "♜",  
        -KNIGHT: "♞", 
        -BISHOP: "♝",  
        -QUEEN: "♛", 
        -KING: "♚",
        EMPTY: " "    
    }

    @staticmethod
    def print_board(side, board):
        """
        Print the chess board in the specified style and orientation.

        Args:
            side (int): 1 for white or -1 for black, determines board orientation.
            board (list): 2D list representing the board state.

        Returns:
            None
        """
        
        board_rendu = [list(reversed([ChessDisplay.piece_note_style[e] for e in r])) for r in board] if side == 1 else [[ChessDisplay.piece_note_style[e] for e in r] for r in board]

        
        if side == 1:
            board_rendu.reverse()

        for row in board_rendu:
            print(row)
        return

    
    @staticmethod
    def print_game_start(board, side=1):
        """
        Print the initial chess board setup.

        Args:
            side (int): 1 for white or -1 for black, determines board orientation.
        Returns:
            None
        """

        print("╔═════════════ GAME START ═════════════╗")

        print()
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == 1 else "⚫ ═══════════ Black play ═══════════ ⚫")
        print()

        ChessDisplay.print_board(side, board)
        return


    @staticmethod
    def print_turn(side):
        """
        Print the current chess board state.

        Args:
            side (int): 1 for white or -1 for black, determines board orientation.

        Returns:
            None
        """

        print()
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == WHITE else "⚫ ═══════════ Black play ═══════════ ⚫")
        print()
        return


    @staticmethod
    def print_invalid_move(reason=None):
        """
        Print a message indicating an invalid move.

        Returns:
            None
        """

        print("🚫 ══════════ Invalid move ══════════ 🚫")

        if reason:
            print(f"Reason: {reason}")
        return


    @staticmethod
    def print_game_already_over():
        """
        Print a message indicating the game is already over.

        Returns:
            None
        """

        print("🚫 ════════ The game is over ════════ 🚫")
        return
    

    @staticmethod
    def print_game_over(winner, board, side=None):
        """
        Print the game over message with the winner.

        Args:
            winner (int): 1 for white or -1 for black.
            board (list): The board state.
            side (int, optional): Board orientation (1 for white, -1 for black).

        Returns:
            None
        """
        
        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(winner if side is None else side, board)
        print()
        print(f"╚════════ CHECKMATE {'WHITE' if winner == 1 else 'BLACK'} WIN ═════════╝")
        return


    @staticmethod
    def print_draw(d_type, board, side = 1):
        """
        Print a message indicating the game ended in a draw.

        Returns:
            None
        """
        
        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(side, board)
        print()

        if d_type == 'insufficient_material':
            print("⏸ ══ Draw by insufficient material ═ ⏸")

        elif d_type == 'fifty_move_rule':
            print("⏸ ═════ Draw by fifty-move rule ════ ⏸")

        elif d_type == 'threefold_repetition':
            print("⏸ ═══════ Draw by repetition ═══════ ⏸")
        return


    @staticmethod
    def print_stalemate(board, side_in_pat, side = None):
        """
        Print a message indicating the game ended in stalemate.

        Args:
            board (list): The board state.
            side_in_pat (int): The side that is in stalemate (1 for white, -1 for black).
            side (int, optional): Board orientation (1 for white, -1 for black).

        Returns:
            None
        """

        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(side if side is not None else side_in_pat, board)
        print()
        print("⏸ ══════ Whites are stalemate ═══════ ⏸" if side_in_pat == 1 else "⏸ ══════ Blacks are stalemate ═══════ ⏸")
        return


    @staticmethod
    def print_move(move):
        """
        Print the given chess move.
        
        Returns:
            None
        """

        print(f"> {move}")
        print()
        return

    
    @staticmethod
    def print_invalid_format():
        """
        Print a message indicating the move format is invalid.

        Returns:
            None
        """

        print("🚫 ═════════ Invalid format ═════════ 🚫")
        print("Valid move example: ✅--- e2 e4 ---✅")
        return


    @staticmethod
    def print_row_as_list(row):
        """
        Convert a row of the chess board into a list of strings, replacing empty cells with a visible placeholder.
        
        Args:
            row (list): A list representing a row of the chess board.

        Returns:
            None
        """

        import re
        
        EMPTY_CHAR = "#"  
        parts = []

        for cell in row:
            raw = re.compile(r"\x1b\[[0-9;]*m").sub("", cell)     
            if raw == " ":
                cell = cell.replace(" ", EMPTY_CHAR)
            parts.append(f"'{cell}'")

        print("[" + ", ".join(parts) + "]")


    @staticmethod
    def color_to_code(color):
        """
        Convert a color name to its corresponding ANSI escape code.

        Args:
            color (str): The color name ("red", "green", "yellow", "blue", "magenta", "cyan").

        Returns:
            tuple: A tuple containing the start and end ANSI escape codes for the specified color.
        """

        if color == "red":
            return "\033[31m", "\033[0m"
        elif color == "green": 
            return "\033[32m", "\033[0m"
        elif color == "yellow":
            return "\033[33m", "\033[0m"
        elif color == "blue":
            return "\033[34m", "\033[0m"
        elif color == "magenta":
            return "\033[35m", "\033[0m"
        elif color == "cyan":
            return "\033[36m", "\033[0m"
        else:
            return None, None

    
    @staticmethod
    def print_last_move_highlighted(color, board, last_move, side = 1):
        """
        Highlight the last move made on the chess board with a specific color.

        Args:
            color (str): The color code name for highlighting ("red", "green", "yellow", "blue", "magenta", "cyan").
            board (list): The current state of the chess board, represented as a 2D list.
            last_move (list): A list containing the start and end coordinates of the move, formatted as [[from_y, from_x], [to_y, to_x]].
            side (int): 1 for white or -1 for black, determines board orientation.

        Returns:
            None
        """

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return
        
        board_rendu = [list(reversed([ChessDisplay.piece_note_style[e] for e in r])) for r in board] if side == 1 else [[ChessDisplay.piece_note_style[e] for e in r] for r in board]
            
        board_rendu[last_move[0][0]][last_move[0][1]] = f"{start_highlight}{board_rendu[last_move[0][0]][last_move[0][1]]}{end_highlight}"
        board_rendu[last_move[1][0]][last_move[1][1]] = f"{start_highlight}{board_rendu[last_move[1][0]][last_move[1][1]]}{end_highlight}"
                                                                                               
        if side == 1:
            board_rendu.reverse()
        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)
        return


    @staticmethod
    def print_highlighted_legal_move(y, x, color, board, side = 1):
        """
        Highlights and prints all legal moves for a piece at the given position on the chess board.

        Args:
            y (int): Row index of the piece.
            x (int): Column index of the piece.
            color (str): Color name for highlighting moves (e.g., "red", "green", "yellow", etc.).
            board (list): 2D list representing the current chess board state.
            side (int): 1 for white or -1 for black, determines board orientation.

        Returns:
            None
        """
        
        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return

        board_rendu = [list(reversed([ChessDisplay.piece_note_style[e] for e in r])) for r in board] if side == 1 else [[ChessDisplay.piece_note_style[e] for e in r] for r in board]

        list_move = MoveGen.list_all_piece_move(y, x, board[y][x], board)
        for e in list_move:
            board_rendu[e[0][0]][e[0][1]] = f"{start_highlight}{board_rendu[e[0][0]][e[0][1]]}{end_highlight}"
            board_rendu[e[1][0]][e[1][1]] = f"{start_highlight}{board_rendu[e[1][0]][e[1][1]]}{end_highlight}"

        if side == 1:
            board_rendu.reverse()
        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)
        return


    @staticmethod
    def print_highlighted_all_legal_move(color, board, side = 1, castling_rights = {}):
        """
        Highlights and prints all legal moves for the current player on the chess board.

        Args:
            color (str): Color name for highlighting moves (e.g., "red", "green", "yellow", etc.).
            board (list): 2D list representing the current chess board state.
            side (int): 1 for white or -1 for black, determines board orientation.
            castling_rights (str, optional): Current castling rights ("KQkq").

        Returns:
            None
        """

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return

        board_rendu = [list(reversed([ChessDisplay.piece_note_style[e] for e in r])) for r in board] if side == 1 else [[ChessDisplay.piece_note_style[e] for e in r] for r in board]

        color_to_play = 1*side
        list_move = MoveGen.list_all_legal_move(color_to_play, board, castling_rights=castling_rights)
        for e in list_move:
            board_rendu[e[0][0]][e[0][1]] = f"{start_highlight}{board_rendu[e[0][0]][e[0][1]]}{end_highlight}"
            board_rendu[e[1][0]][e[1][1]] = f"{start_highlight}{board_rendu[e[1][0]][e[1][1]]}{end_highlight}"

        if side == 1:
            board_rendu.reverse()
        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)
        return


class ChessCore:
    def __init__(self):
        self.board = Board()
        self.party_over = False
        self.auto_promotion_value = False
    

    @staticmethod
    def give_promotion_value(auto_promotion):
        """
        Convert promotion string to corresponding piece value.
        Args:
            auto_promotion (str): Promotion setting for pawns, ("queen", "rook", "bishop", "knight").
        Returns:
            int: Corresponding piece value for promotion.
        """

        promotion_dict = {
            "queen": QUEEN,
            "rook": ROOK,
            "bishop": BISHOP,
            "knight": KNIGHT
        }

        return promotion_dict.get(auto_promotion, False)


    def launch_partie(self, side="white", auto_promotion = False):
        """
        Initialize and start a chess game, setting turn color.
        Args:
            side (str): 'white' or 'black' to set the starting player.
            auto_promotion (str or bool): Promotion setting for pawns, ("queen", "rook", "bishop", "knight") or False for disable auto-promotion.
        Returns:
            None
        """

        self.auto_promotion = ChessCore.give_promotion_value(auto_promotion)
        
        if side == "black":
            self.board.change_side()

        ChessDisplay.print_game_start(self.board.board, self.board.side_to_move)
        return


    def play_move(self, all_move, print_move=True):
        """
        Play a move in the chess game, handling move validation, special rules, and game end conditions.
        Args:
            all_move (str): Move in algebraic notation (e.g., 'e2 e4' or 'e7 e8q').
            print_move (bool, optional): Whether to print the move. Defaults to True.
        Returns:
            str: 'valid', 'invalid', 'illegal', 'checkmate', 'stalemate', or 'draw' depending on the move result.
        """

        if self.party_over:
            ChessDisplay.print_game_already_over()
            return 'illegal'
        
        if print_move:
            ChessDisplay.print_move(all_move)

        self.promotion_value = None

        if len(all_move) == 6:
            if all_move[-1] in ('q','r','b','n'):
                self.promotion_value = {'q':QUEEN,'r':ROOK,'b':BISHOP,'n':KNIGHT}[all_move[-1]]
                all_move = all_move[:-1]

                if not MoveParser.is_valid_move_format(all_move):
                    ChessDisplay.print_invalid_format()
                    self.promotion_value = None
                    return 'illegal'
                
            else:
                return 'illegal'
        
        elif not MoveParser.is_valid_move_format(all_move):
            ChessDisplay.print_invalid_format()
            return 'illegal'

        self.info_move = MoveParser.give_move_info(all_move, self.board.board)

        if self.info_move == 'illegal':
            ChessDisplay.print_invalid_move("Illegal move coordinates.")
            return 'invalid'
        
        elif (self.info_move['start_value'] > 0 and self.board.side_to_move == BLACK) or (self.info_move['start_value'] < 0 and self.board.side_to_move == WHITE):
            ChessDisplay.print_invalid_move("It's not your turn.")
            return 'invalid'
        
        else:
            if self.board.position_has_loaded and not self.board.move_history:
                rep = self.check_loaded_position()
                if rep:
                    return rep
                
            rep = self.validate_and_apply_move()

        if rep is None:
            return 'invalid'

        # side_to_move has changed after a valid move

        if GameState.is_checkmate(self.board.side_to_move, self.board.board):
            ChessDisplay.print_game_over(self.board.side_to_move, self.board.board)
            self.party_over = True
            return 'checkmate'
        
        legal_move = MoveGen.list_all_legal_move(WHITE, self.board.board, self.board.castling_rights) if self.board.side_to_move == WHITE else MoveGen.list_all_legal_move(BLACK, self.board.board, self.board.castling_rights)      

        if legal_move == []:
            ChessDisplay.print_draw('stalemate', self.board.board, self.board.side_to_move*-1)
            self.party_over = True
            return 'draw'

        if GameState.check_repetition(self.board.get_position_hash(),self.board.position_hash_history):
            ChessDisplay.print_draw('threefold_repetition', self.board.board, self.board.side_to_move*-1)
            self.party_over = True
            return 'draw'
        
        if self.board.counter_halfmove_without_capture >= 100:
            ChessDisplay.print_draw('fifty_move_rule', self.board.board, self.board.side_to_move*-1)
            self.party_over = True
            return 'draw'

        if Board.material_insufficiency(self.board.board):
            ChessDisplay.print_draw('insufficient_material', self.board.board, self.board.side_to_move*-1)
            self.party_over = True
            return 'draw'

        ChessDisplay.print_turn(self.board.side_to_move)
        ChessDisplay.print_board(self.board.side_to_move, self.board.board)
        
        return 'valid'
    

    def check_loaded_position(self):
        """
        Check the loaded chess position for checkmate or stalemate and print the appropriate game status.
        
        Returns:
            str: 'checkmate' if the position is a checkmate for either side, 'stalemate' if no legal moves are available, otherwise None.
        """

        if GameState.is_checkmate(-1,self.board.board):
            ChessDisplay.print_game_over(WHITE ,self.board.board)
            return 'checkmate'
        
        if GameState.is_checkmate(1,self.board.board):
            ChessDisplay.print_game_over(BLACK ,self.board.board)
            return 'checkmate'
        
        legal_move = MoveGen.list_all_legal_move(WHITE, self.board.board) if self.board.side_to_move == BLACK else MoveGen.list_all_legal_move(BLACK, self.board.board)      

        if legal_move == []:
            ChessDisplay.print_draw('stalemate', self.board.board, self.color_turn)
            return 'stalemate'
        
        return
        

    def validate_and_apply_move(self):
        """
        Validate the current move, apply it to the board if legal, and handle special cases (check, checkmate, stalemate, castling, en passant).
        Returns:
            str or None: 'valid' or None if the move is invalid.
        """
        
        if GameState.is_check(self.board.side_to_move*-1,self.board.board) != 'valid':
            ChessDisplay.print_invalid_move("Invalid move black is in check.")
            return

        return_valid_pawn_move = None
        return_valid_king_move = None
            
        if self.info_move["start_value"] == PAWN or self.info_move["start_value"] == -PAWN:
            return_valid_pawn_move = Validator.valid_pawn_move(self.info_move, self.board.move_history, self.board.board, promotion_value=self.promotion_value, auto_promotion_value=self.auto_promotion_value)
            
            if return_valid_pawn_move not in ('valid', 'en passant'):
                ChessDisplay.print_invalid_move()
                return
            
            elif return_valid_pawn_move == 'en passant':
                new_board = self.board.copy_board()
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_end_coordinate"]] = EMPTY
                
        elif self.info_move["start_value"] == ROOK or self.info_move["start_value"] == -ROOK:
            if Validator.valid_rook_move(self.info_move, self.board.board) != 'valid':
                ChessDisplay.print_invalid_move()
                return 
            
        elif self.info_move["start_value"] == BISHOP or self.info_move["start_value"] == -BISHOP:
            if Validator.valid_bishop_move(self.info_move, self.board.board) != 'valid':
                ChessDisplay.print_invalid_move()
                return
            
        elif self.info_move["start_value"] == KNIGHT or self.info_move["start_value"] == -KNIGHT:
            if Validator.valid_knight_move(self.info_move) != 'valid':
                ChessDisplay.print_invalid_move()
                return

        elif self.info_move["start_value"] == KING or self.info_move["start_value"] == -KING:
            return_valid_king_move = Validator.valid_king_move(self.info_move, self.board.castling_rights, self.board.board)
            if return_valid_king_move not in ['casting', 'big_casting','valid']:
                ChessDisplay.print_invalid_move()
                return 
            
            elif return_valid_king_move == 'casting':
                new_board = self.board.copy_board()
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-3] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-1] = (ROOK if self.board.side_to_move > 0 else -ROOK)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
            
            elif return_valid_king_move == 'big_casting':
                new_board = self.board.copy_board()
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+4] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+1] = (ROOK if self.board.side_to_move > 0 else -ROOK)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]

        elif self.info_move["start_value"] == QUEEN or self.info_move["start_value"] == -QUEEN:
            if Validator.valid_queen_move(self.info_move, self.board.board) != 'valid':
                ChessDisplay.print_invalid_move()
                return
        
        if return_valid_king_move not in ['big_casting', 'casting'] and return_valid_pawn_move != 'en passant':
            new_board = self.board.copy_board()
            new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
            new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]

        if return_valid_pawn_move == 'en passant':
            self.board.counter_halfmove_without_capture = 0

        if GameState.is_check(self.board.side_to_move,new_board) != 'valid':
            ChessDisplay.print_invalid_move("You cannot put yourself in check.")
            return
        
        self.board.update_board(new_board, self.info_move)

        return 'valid'


    def play(self, side="white", auto_promotion = False):
        """
        Play a chess game loop for the given color.
        
        Args:
            color (str): 'white' or 'black'.
            auto_promotion (str or bool): Promotion setting for pawns, ("queen", "rook", "bishop", "knight") or False for disable auto-promotion.

        Returns:
            str: 'checkmate', 'pat', or 'draw' when the game ends.
        """

        self.launch_partie(side=side, auto_promotion=auto_promotion)
        
        while True:
            all_move = input("> ")
            result = self.play_move(all_move, print_move=False)
            if result == 'checkmate':
                return 'checkmate'
            
            elif result == 'pat':
                return 'pat'
            
            elif result == 'draw':
                return 'draw'
            

if __name__ == "__main__":
    process = ChessCore()
    process.play()
