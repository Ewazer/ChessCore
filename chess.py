from constants import *

class Board:
    def __init__(self):
        """Initialize the board with the standard starting position and game state."""

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
        Create the standard starting chess position.

        Returns:
            list: 2D list (8x8) representing the board.
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
        Load a custom board position.

        Args:
            board (list): 2D list (8x8) representing the board.
            side (int): Side to move (WHITE=1 or BLACK=-1).
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
        Find the coordinates of a piece on the board.

        Args:
            board (list): 2D list (8x8) representing the board.
            f_piece (int): Piece value to find.

        Returns:
            tuple or None: (col, row) if found, else None.
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
        Add a move to history and save the current board state.
        
        Args:
            move (dict): Move details with coordinates.
        """

        self.move_history.append(move)
        self.board_history.append(self.copy_board())
        self.position_hash_history[self.get_position_hash()] = self.position_hash_history.get(self.get_position_hash(), 0) + 1


    def undo_move(self):
        """
        Undo the last move.
        
        Returns:
            bool: True if successful, False if no moves to undo.
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
        """Generate a hash of the current position for repetition detection."""

        return hash((
            tuple(tuple(r) for r in self.board),
            self.side_to_move,
            tuple(sorted(self.castling_rights)),
        ))
    

    def update_board(self, board_to_copy, move, change_side_to_move = True, active_counter_halfmove_without_capture = True, update_history=True):
        """
        Apply a new board state and update game metadata.

        Args:
            board_to_copy (list): 2D list (8x8) representing the new board state.
            move (dict): Move details with coordinates.
            change_side_to_move (bool): Switch side after update. Defaults to True.
            active_counter_halfmove_without_capture (bool): Update halfmove clock. Defaults to True.
            update_history (bool): Save to history. Defaults to True.
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
        Check if only kings remain on the board.

        Args:
            board (list): 2D list (8x8) representing the board.
            
        Returns:
            bool: True if insufficient material, False otherwise.
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
        Parse a move string and extract move information.

        Args:
            all_move (str): Move string (e.g., "e2 e4").
            board (list): 2D list (8x8) representing the board.
            debug (bool): Print debug info. Defaults to False.

        Returns:
            dict or str: Move details dict, or 'illegal' if invalid.
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
        Check if a move string has valid format (e.g., "e2 e4").

        Args:
            all_move (str): Move string to validate.

        Returns:
            bool: True if valid format, False otherwise.
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
        Get the promoted piece value.

        Args:
            side (int): Side color (WHITE=1 or BLACK=-1).
            promotion_value (int): Piece to promote to, or None.
            auto_promotion_value (int): Default promotion piece.
    
        Returns:
            int or str: Piece value, or 'invalid' if not set.
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
        Validate a pawn move (includes en passant and promotion).

        Args:
            move (dict): Move details with coordinates.
            move_history (list): List of previous moves.
            board (list): 2D list (8x8) representing the board.
            promotion_value (int): Piece to promote to, or None.
            auto_promotion_value (int): Default promotion piece.

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
        Validate a diagonal move (bishop or queen).

        Args:
            move (dict): Move details with coordinates.
            board (list): 2D list (8x8) representing the board.

        Returns:
            str: 'valid' or 'illegal'.
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
        Validate a rook move (horizontal or vertical).

        Args:
            move (dict): Move details with coordinates.
            board (list): 2D list (8x8) representing the board.
    
        Returns:
            str: 'valid' or 'illegal'.
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
        Validate a knight move (L-shape).

        Args:
            move (dict): Move details with coordinates.

        Returns:
            str: 'valid' or 'illegal'.
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
        Validate a queen move (combines rook and bishop moves).

        Args:
            move (dict): Move details with coordinates.
            board (list): 2D list (8x8) representing the board.

        Returns:
            str: 'valid' or 'illegal'.
        """

        if Validator.valid_rook_move(move, board) == 'valid' or Validator.valid_bishop_move(move, board) == 'valid':
            return 'valid'
        
        else:
            return 'illegal'
        
        
    @staticmethod
    def valid_king_move(move, castling_rights, board):
        """
        Validate a king move (includes castling).
        
        Args:
            move (dict): Move details with coordinates.
            castling_rights (set): Current castling rights (e.g., {'K', 'Q', 'k', 'q'}).
            board (list): 2D list (8x8) representing the board.

        Returns:
            str: 'castling', 'big_castling', 'valid', or 'illegal'.
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
        Generate all pawn moves from position (y, x).

        Args:
            y (int): Row index.
            x (int): Column index.
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all knight moves from position (y, x).

        Args:
            y (int): Row index.
            x (int): Column index.
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all bishop moves from position (y, x).

        Args:
            y (int): Row index.
            x (int): Column index.
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all rook moves from position (y, x).

        Args:
            y (int): Row index.
            x (int): Column index.
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all queen moves from position (y, x).

        Args:
            y (int): Row index.
            x (int): Column index.
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all king moves from position (y, x), including castling.

        Args:
            y (int): Row index.
            x (int): Column index.
            castling_rights (set): Current castling rights (e.g., {'K', 'Q', 'k', 'q'}).
            board (list): 2D list (8x8) representing the board.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all legal moves for a side (excluding moves leaving king in check).
        
        Args:
            side (int): Side color (WHITE=1 or BLACK=-1).
            board (list): 2D list (8x8) representing the board.
            castling_rights (set): Current castling rights. Defaults to empty.
        
        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Generate all moves for a specific piece.

        Args:
            y (int): Row index.
            x (int): Column index.
            piece_value (int): Piece type and color value.
            board (list): 2D list (8x8) representing the board.
            castling_rights (set): Castling rights for king moves. Defaults to empty.

        Returns:
            list: Moves as [[from_y, from_x], [to_y, to_x]].
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
        Check if a king is in check.

        Args:
            side (int): Side color (WHITE=1 or BLACK=-1).
            board_actual (list): 2D list (8x8) representing the board.

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
        Check if a side is in checkmate.

        Args:
            side (int): Side color (WHITE=1 or BLACK=-1).
            board_actual (list): 2D list (8x8) representing the board.

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
        Check for threefold repetition.

        Args:
            hash (int): Position hash to check.
            position_hash_history (dict): Hash occurrence counts.
            
        Returns:
            bool: True if position occurred 3+ times, False otherwise.
        """

        return position_hash_history.get(hash, 0) >= 3


class ChessDisplay:
    enable_print = True

    def print_diseabled(f):
        def wrapper(*args, **kwargs):
            if not ChessDisplay.enable_print:
                return None
            return f(*args, **kwargs)
        return wrapper


    @staticmethod
    @print_diseabled
    def print_board(side, board):
        """
        Print the chess board.

        Args:
            side (int): Orientation (WHITE=1 or BLACK=-1).
            board (list): 2D list (8x8) representing the board.
        """
        
        board_rendu = [list(reversed([piece_note_style[e] for e in r])) for r in board] if side == 1 else [[piece_note_style[e] for e in r] for r in board]

        
        if side == 1:
            board_rendu.reverse()

        for row in board_rendu:
            print(row)
        return


    @staticmethod
    @print_diseabled
    def print_game_start(board, side=1):
        """
        Print the game start message and board.

        Args:
            board (list): 2D list (8x8) representing the board.
            side (int): Orientation (WHITE=1 or BLACK=-1). Defaults to 1.
        """

        print("╔═════════════ GAME START ═════════════╗")

        print()
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == 1 else "⚫ ═══════════ Black play ═══════════ ⚫")
        print()

        ChessDisplay.print_board(side, board)
        return


    @staticmethod
    @print_diseabled
    def print_turn(side):
        """
        Print which side's turn it is.

        Args:
            side (int): Side to play (WHITE=1 or BLACK=-1).
        """

        print()
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == WHITE else "⚫ ═══════════ Black play ═══════════ ⚫")
        print()
        return


    @staticmethod
    @print_diseabled
    def print_invalid_move(reason=None):
        """
        Print an invalid move message.

        Args:
            reason (str): Optional reason for the invalid move.
        """

        print("🚫 ══════════ Invalid move ══════════ 🚫")

        if reason:
            print(f"Reason: {reason}")
        return


    @staticmethod
    @print_diseabled
    def print_game_already_over():
        """Print a message indicating the game is already over."""

        print("🚫 ════════ The game is over ════════ 🚫")
        return
    

    @staticmethod
    @print_diseabled
    def print_game_over(winner, board, side=None):
        """
        Print the checkmate message.

        Args:
            winner (int): Winning side (WHITE=1 or BLACK=-1).
            board (list): 2D list (8x8) representing the board.
            side (int): Board orientation. Defaults to winner.
        """
        
        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(winner if side is None else side, board)
        print()
        print(f"╚════════ CHECKMATE {'WHITE' if winner == 1 else 'BLACK'} WIN ═════════╝")
        return


    @staticmethod
    @print_diseabled
    def print_draw(d_type, board, side = 1):
        """
        Print a draw message.

        Args:
            d_type (str): Draw type ('insufficient_material', 'fifty_move_rule', 'threefold_repetition').
            board (list): 2D list (8x8) representing the board.
            side (int): Board orientation. Defaults to 1.
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
    @print_diseabled
    def print_stalemate(board, side_in_pat, side = None):
        """
        Print a stalemate message.

        Args:
            board (list): 2D list (8x8) representing the board.
            side_in_pat (int): Side in stalemate (WHITE=1 or BLACK=-1).
            side (int): Board orientation. Defaults to side_in_pat.
        """

        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(side if side is not None else side_in_pat, board)
        print()
        print("⏸ ══════ Whites are stalemate ═══════ ⏸" if side_in_pat == 1 else "⏸ ══════ Blacks are stalemate ═══════ ⏸")
        return


    @staticmethod
    @print_diseabled
    def print_move(move):
        """
        Print a chess move.
        
        Args:
            move (str): Move string to print.
        """

        print(f"> {move}")
        print()
        return

    
    @staticmethod
    @print_diseabled
    def print_invalid_format():
        """Print an invalid format message with example."""

        print("🚫 ═════════ Invalid format ═════════ 🚫")
        print("Valid move example: ✅--- e2 e4 ---✅")
        return


    @staticmethod
    def print_row_as_list(row):
        """
        Print a board row with empty cells shown as '#'.
        
        Args:
            row (list): Row of piece symbols.
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
        Convert a color name to ANSI codes.

        Args:
            color (str): Color name ("red", "green", "yellow", "blue", "magenta", "cyan").

        Returns:
            tuple: (start_code, end_code) or (None, None) if invalid.
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
        Print the board with the last move highlighted.

        Args:
            color (str): Highlight color name.
            board (list): 2D list (8x8) representing the board.
            last_move (list): Move as [[from_y, from_x], [to_y, to_x]].
            side (int): Board orientation. Defaults to 1.
        """

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return
        
        board_rendu = [list(reversed([piece_note_style[e] for e in r])) for r in board] if side == 1 else [[piece_note_style[e] for e in r] for r in board]
            
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
        Print the board with legal moves for a piece highlighted.

        Args:
            y (int): Row index.
            x (int): Column index.
            color (str): Highlight color name.
            board (list): 2D list (8x8) representing the board.
            side (int): Board orientation. Defaults to 1.
        """
        
        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return

        board_rendu = [list(reversed([piece_note_style[e] for e in r])) for r in board] if side == 1 else [[piece_note_style[e] for e in r] for r in board]

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
        Print the board with all legal moves highlighted.

        Args:
            color (str): Highlight color name.
            board (list): 2D list (8x8) representing the board.
            side (int): Side to move (WHITE=1 or BLACK=-1). Defaults to 1.
            castling_rights (set): Current castling rights. Defaults to empty.
        """

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(side, board)
            return

        board_rendu = [list(reversed([piece_note_style[e] for e in r])) for r in board] if side == 1 else [[piece_note_style[e] for e in r] for r in board]

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
        Convert promotion name to piece value.

        Args:
            auto_promotion (str): Piece name ("queen", "rook", "bishop", "knight").

        Returns:
            int or False: Piece value, or False if invalid.
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
        Start a new chess game.

        Args:
            side (str): Starting side ('white' or 'black'). Defaults to 'white'.
            auto_promotion (str or False): Auto-promotion piece name, or False to disable.
        """

        self.auto_promotion = ChessCore.give_promotion_value(auto_promotion)
        
        if side == "black":
            self.board.change_side()

        ChessDisplay.print_game_start(self.board.board, self.board.side_to_move)
        return


    def play_move(self, all_move, print_move=True):
        """
        Play a move and handle game logic.

        Args:
            all_move (str): Move string (e.g., 'e2 e4' or 'e7 e8q').
            print_move (bool): Print the move. Defaults to True.

        Returns:
            str: 'valid', 'invalid', 'illegal', 'checkmate', or 'draw'.
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
        Check if a loaded position is checkmate or stalemate.
        
        Returns:
            str or None: 'checkmate', 'stalemate', or None if game continues.
        """

        if GameState.is_checkmate(-1,self.board.board):
            ChessDisplay.print_game_over(WHITE ,self.board.board)
            return 'checkmate'
        
        if GameState.is_checkmate(1,self.board.board):
            ChessDisplay.print_game_over(BLACK ,self.board.board)
            return 'checkmate'
        
        legal_move = MoveGen.list_all_legal_move(WHITE, self.board.board) if self.board.side_to_move == BLACK else MoveGen.list_all_legal_move(BLACK, self.board.board)      

        if legal_move == []:
            ChessDisplay.print_draw('stalemate', self.board.board, self.board.side_to_move)
            return 'stalemate'
        
        return
        

    def validate_and_apply_move(self):
        """
        Validate and apply the current move to the board.

        Returns:
            str or None: 'valid' if successful, None if invalid.
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
        Run an interactive chess game loop.
        
        Args:
            side (str): Starting side ('white' or 'black'). Defaults to 'white'.
            auto_promotion (str or False): Auto-promotion piece name, or False to disable.

        Returns:
            str: 'checkmate', 'pat', or 'draw' when game ends.
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
            

    def reset_game(self):
        """Reset the game to its initial state."""

        self.board = Board()
        self.party_over = False
        return


    def load_board(self, board):
        """
        Load a custom board position.

        Args:
            board (list): 2D list (8x8) representing the board.
        """

        self.board.load_board(board)
        return


if __name__ == "__main__":
    process = ChessCore()
    process.play()
