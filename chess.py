import re 
import copy
from collections import Counter

class Chess:
    EMPTY = 0
    PAWN = 1
    KNIGHT = 3
    BISHOP = 4
    ROOK = 5
    KING = 7
    QUEEN = 9

    def __init__(self): 
        """
        Initialize chess board, piece representations, castling rights, and game state.
        Sets up coordinate mappings, piece notations, Unicode styles, castling flags, move history, and the initial board layout.
        """

        self.coordinate = {
            "a":8,
            "b":7,
            "c":6,
            "d":5,
            "e":4,
            "f":3,
            "g":2,
            "h":1,
            8:"a",
            7:"b",
            6:"c",
            5:"d",
            4:"e",
            3:"f",
            2:"g",
            1:"h"
        }

        self.piece_note = {
            self.EMPTY: "0",
            self.PAWN: "p",
            self.ROOK: "t",
            self.BISHOP: "f",
            self.KNIGHT: "c",
            self.QUEEN: "r",
            self.KING: "k",
            -self.PAWN: "P",
            -self.ROOK: "T",
            -self.BISHOP: "F",
            -self.KNIGHT: "C",
            -self.QUEEN: "R",
            -self.KING: "K"
        }

        self.piece_note_style = {
            self.PAWN: "♙",   
            self.ROOK: "♖",   
            self.KNIGHT: "♘",  
            self.BISHOP: "♗",   
            self.QUEEN: "♕",  
            self.KING: "♔", 
            -self.PAWN: "♟",
            -self.ROOK: "♜",  
            -self.KNIGHT: "♞", 
            -self.BISHOP: "♝",  
            -self.QUEEN: "♛", 
            -self.KING: "♚",
            self.EMPTY: " "    
        }

        self.piece = {
            self.EMPTY: "empty",
            self.PAWN: "white_pawn",
            self.ROOK: "white_rook",
            self.BISHOP: "white_bishop",
            self.KNIGHT: "white_knight",
            self.QUEEN: "white_queen",
            self.KING: "white_king",
            -self.PAWN: "black_pawn",
            -self.ROOK: "black_rook",
            -self.BISHOP: "black_bishop",
            -self.KNIGHT: "black_knight",
            -self.QUEEN: "black_queen",
            -self.KING: "black_king"
        }

        self.info_move = {}
        self.castling_p_white = True
        self.castling_p_black = True 
        self.big_castling_p_white = True 
        self.big_castling_p_black = True
        self.rook_m = {'rook_white_castling' : True, 'rook_black_castling' : True, 'rook_big_white_castling' : True, 'rook_big_black_castling' : True}
        self.list_game_move =[]
        self.list_game_board_move =[]

        self.board = [
            [ self.ROOK, self.KNIGHT, self.BISHOP, self.KING, self.QUEEN, self.BISHOP, self.KNIGHT, self.ROOK],
            [ self.PAWN, self.PAWN, self.PAWN, self.PAWN, self.PAWN, self.PAWN, self.PAWN, self.PAWN],
            [ self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY],
            [ self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY],
            [ self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY],
            [ self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY, self.EMPTY],
            [-self.PAWN,-self.PAWN,-self.PAWN,-self.PAWN,-self.PAWN,-self.PAWN,-self.PAWN,-self.PAWN],
            [-self.ROOK,-self.KNIGHT,-self.BISHOP,-self.KING,-self.QUEEN,-self.BISHOP,-self.KNIGHT,-self.ROOK]
        ]

        self.party_over = False
        self.auto_promotion_value = False

    def load_board(self, board):
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

        Returns:
            None
        """

        self.board = [e[::-1] for e in board[::-1]]

    def check_repetition(self):
        """
        Check for threefold repetition in the game history.

        Returns:
            bool: True if any board position has occurred at least three times, False otherwise.
        """

        serialized_boards = [tuple(tuple(row) for row in board) for board in self.list_game_board_move]
        counts = Counter(serialized_boards)
        
        if any(count >= 3 for count in counts.values()): 
            return True
        
        return False
    
    
    def promote_pawn(self, color):
        """
        Handle pawn promotion for the given color.

        Args:
            color (str): 'white' or 'black'.

        Returns:
            int or 'invalid': Promotion value or 'invalid' if not set.
        """

        if not self.auto_promotion:
            if self.auto_promotion_value:
                return self.auto_promotion_value * (1 if color == 'white' else -1)
            else:
                print("Please set auto_promotion or provide a promotion piece. Exemple: 'e7 e8q' for queen promotion (the queen: 'q', the rook: 'r', the bishop: 'b' and the knight 'n'). ")
                return 'invalid'
        else:
            return int(self.auto_promotion_value) * (1 if color == 'white' else -1)
        

    def valid_pawn_move(self, move):
        """
        Validate a pawn move, including en passant and promotion.
        Args:
            move (dict): Move details with coordinates and piece info.
        Returns:
            str: 'valid', 'illegal', 'en passant', or 'invalid'.
        """
        EMPTY = self.EMPTY
        PAWN = self.PAWN

        if move['end_value'] == EMPTY: 
            if self.list_game_move:
                if (move['y_start_coordinate'] == 4 if move['start_value'] > 0 else move['y_start_coordinate'] == 3):
                    if self.board[move['y_start_coordinate']][move['x_end_coordinate']] == (-PAWN if move['start_value'] > 0 else PAWN):
                        if move['x_end_coordinate'] == move['x_start_coordinate']+1:
                            if self.list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return 'en passant'
                            
                        elif move['x_end_coordinate'] == move['x_start_coordinate']-1:
                            if self.list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return 'en passant'
                            
            if move['x_end_coordinate'] == move['x_start_coordinate']: 
                if move['name_piece_coor1'] == "white_pawn":     
                    if (
                        move['y_end_coordinate'] == move['y_start_coordinate'] + 1
                        or (
                            move['y_end_coordinate'] == move['y_start_coordinate'] + 2
                            and move['y_start_coordinate'] == 1
                            and self.board[move['y_start_coordinate'] + 1][move['x_start_coordinate']] == EMPTY
                        )
                    ):
                        if move['y_end_coordinate'] == 7:
                            move["start_value"] = self.promote_pawn('white')
                            if move["start_value"] == 'invalid':
                                return 'invalid'
                            
                        return'valid'
                    
                    else:
                        return'illegal'

                if move['name_piece_coor1'] == "black_pawn":
                    if (
                        move['y_start_coordinate'] == move['y_end_coordinate'] + 1
                        or (
                            move['y_start_coordinate'] == move['y_end_coordinate'] + 2
                            and move['y_start_coordinate'] == 6
                            and self.board[move['y_start_coordinate'] - 1][move['x_start_coordinate']] == EMPTY
                        )
                    ):
                        if move['y_end_coordinate'] == 0:
                            move["start_value"] = self.promote_pawn('black')
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
                            move["start_value"] = self.promote_pawn('white')
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
                        move["start_value"] = self.promote_pawn('black')
                        if move["start_value"] == 'invalid':
                            return 'invalid'
                        
                    return 'valid'
                
                else:
                    return 'illegal'
                
            return 'illegal'
        

    def valid_bishop_move(self, move):
        """
        Validate a bishop (or queen as bishop) move.
        Args:
            move (dict): Move details with coordinates and piece info.
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        EMPTY = self.EMPTY
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
                if self.board[y_start_coordinate][x_start_coordinate] != EMPTY:
                        return('illegal')
                
                x_start_coordinate += x
                y_start_coordinate += y
                    
            return('valid')
        
        else:
            return('illegal')
        

    def valid_rook_move(self, move, debug=None):
        """
        Validate a rook move and update castling rights.
        Args:
            move (dict): Move details with coordinates and piece values.
            debug (optional): Debug flag.
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        EMPTY = self.EMPTY
        ROOK = self.ROOK

        if move['end_value'] == EMPTY or (move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0):
            if move['y_start_coordinate'] == move['y_end_coordinate']:
                for i in range(min(move['x_start_coordinate'], move['x_end_coordinate']), max(move['x_start_coordinate'], move['x_end_coordinate'])):
                    if self.board[move['y_start_coordinate']][i] != EMPTY and [i] != [move['x_start_coordinate']] and [i] != [move['x_end_coordinate']]:
                        return('illegal')
                    
                if move['start_value'] == ROOK:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_white_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_big_white_castling'] = False
                elif move['start_value'] == -ROOK:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_black_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_big_black_castling'] = False
                return('valid')
            
            elif move['x_start_coordinate'] == move['x_end_coordinate']:
                for i in range(min(move['y_start_coordinate'], move['y_end_coordinate']), max(move['y_start_coordinate'], move['y_end_coordinate'])):
                    if self.board[i][move['x_start_coordinate']] != EMPTY and [i] != [move['y_start_coordinate']] and [i] != [move['y_end_coordinate']]:
                        return('illegal')
                    
                if move['start_value'] == ROOK:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_big_white_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_white_castling'] = False
                elif move['start_value'] == -ROOK:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_big_black_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_black_castling'] = False
                return('valid')
            
        return 'illegal'
    

    def valid_knight_move(self, move):
        """
        Validate if a knight move is legal.
        Args:
            move (dict): Move details with start/end coordinates and values.
        Returns:
            str: 'valid' if move is legal, 'illegal' otherwise.
        """

        EMPTY = self.EMPTY
        if move['end_value'] == EMPTY or ((move['end_value'] > 0 and move['start_value'] < 0) or (move['end_value'] < 0 and move['start_value'] > 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 1:
                return('valid')
            
            elif abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 2:
                return('valid')
            
        else:
            return('illegal')
        

    def valid_king_move(self, move, castling_white=False, castling_black=False,big_castling_black=False,big_castling_white=False):
        """
        Validate king moves, including castling and big castling.
        Args:
            move (dict): Move details with coordinates and piece values.
            castling_white (bool): White short castling allowed.
            castling_black (bool): Black short castling allowed.
            big_castling_black (bool): Black long castling allowed.
            big_castling_white (bool): White long castling allowed.
        Returns:
            str: 'casting', 'big_casting', 'valid', or 'illegal'.
        """

        EMPTY = self.EMPTY
        ROOK = self.ROOK

        if (
            move['end_value'] == EMPTY
            and (
            castling_white if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0
            else castling_black
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and self.board[move['y_end_coordinate']][move['x_end_coordinate'] - 1] in (-ROOK, ROOK)
        ):
            if self.is_check(('white' if self.board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'),self.board) != 'check':
                if self.board[move['y_end_coordinate']][move['x_end_coordinate']+1] == EMPTY:
                    new_board = copy.deepcopy(self.board)
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-1] = self.board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                        if (self.rook_m['rook_white_castling'] == True if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else self.rook_m['rook_black_castling'] == True):
                            return 'casting'

        elif (
            move['end_value'] == EMPTY
            and (
                big_castling_white if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0
                else big_castling_black
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and self.board[move['y_end_coordinate']][move['x_end_coordinate'] + 2] in (-ROOK, ROOK)
        ):
            if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'),self.board) != 'check':
                if self.board[move['y_end_coordinate']][move['x_end_coordinate']+1] == EMPTY and self.board[move['y_end_coordinate']][move['x_end_coordinate']-1] == EMPTY:
                    new_board = copy.deepcopy(self.board)
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+1] = self.board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                        if (self.rook_m['rook_big_white_castling'] == True if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else self.rook_m['rook_big_black_castling'] == True):
                            return 'big_casting'
                        
        if move['end_value'] == EMPTY or ((move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) <= 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) <= 1:
                return('valid')
            
            else:
                return('illegal')
            
        else:
            return('illegal')
        

    def give_move_info(self, all_move,debug=None):
        """
        Extract move information from a move string and validate coordinates.
        Args:
            all_move (str): Move in the format "e2 e4".
            debug (bool, optional): Print debug info if True.
        Returns:
            dict or 'illegal': Move details as dict, or 'illegal' if invalid.
        """

        EMPTY = self.EMPTY
        try:
            all_move = all_move.split(" ")

            start_move = all_move[0]
            end_move = all_move[1]


            x_start_coordinate = start_move[:1]
            y_start_coordinate = int(start_move[1:]) - 1


            if x_start_coordinate in self.coordinate:
                x_start_coordinate = int(self.coordinate[x_start_coordinate]) - 1

            else:
                return('illegal')

            start_value = self.board[y_start_coordinate][x_start_coordinate]

            if start_value == EMPTY:
                return('illegal')

            x_end_coordinate = end_move[:1]
            y_end_coordinate = int(end_move[1:]) - 1

            if x_end_coordinate in self.coordinate:
                x_end_coordinate = int(self.coordinate[x_end_coordinate]) - 1
            else:
                print("invalide coordinate invalide")
                return('illegal')

            end_value = self.board[y_end_coordinate][x_end_coordinate]

            name_piece_coor1 = self.piece[start_value]
            name_piece_coor2 = self.piece[end_value]

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

            return(move)
        
        except (IndexError, ValueError, KeyError):
            return('illegal')
        

    def valid_queen_move(self, move):
        """
        Validate if the queen move is legal.
        Args:
            move (str): Chess move in algebraic notation.
        Returns:
            str: 'valid' if the move is legal, 'illegal' otherwise.
        """

        if self.valid_rook_move(move) == 'valid' or self.valid_bishop_move(move) == 'valid':
            return('valid')
        
        else:
            return('illegal')
        

    def board_print(self, style,color,board_test):
        """
        Print the chess board in the specified style and orientation.

        Args:
            style (bool): If True, use note style for pieces.
            color (str): 'white' or 'black', determines board orientation.
            board_test (list): 2D list representing the board state.

        Returns:
            None
        """
        
        if style:
            board_rendu = [list(reversed([self.piece_note_style[e] for e in r])) for r in board_test] if color == 'white' else [[self.piece_note_style[e] for e in r] for r in board_test]
        else:    
            board_rendu = [list(reversed([self.piece_note[e] for e in r])) for r in board_test]
        if color == 'white':
            board_rendu.reverse()
        for row in board_rendu:
            print(row)
        return 


    def find_piece(self, board_test, f_piece):
        """
        Find the coordinates of a specific piece on the board.

        Args:
            board_test (list): 2D list representing the board state.
            f_piece (int): Piece to find.

        Returns:
            tuple or None: (col, row) if found, else None.
        """

        for x, row in enumerate(board_test): 
            for y, cell in enumerate(row): 
                if cell == f_piece:  
                    return (y + 1, x + 1)
        return
    

    def is_check(self, color, board_actual):
        """
        Check if the king of the given color is in check.
        Args:
            color (str): 'white' or 'black'.
            board_actual (list): Current board state.
        Returns:
            str: 'check', 'valid', or 'error'.
        """

        EMPTY = self.EMPTY
        PAWN = self.PAWN
        KNIGHT = self.KNIGHT
        BISHOP = self.BISHOP
        ROOK = self.ROOK
        QUEEN = self.QUEEN
        KING = self.KING

        KING_TO_CHECK = KING if color == 'white' else -KING

        OPPOSING_PAWN = -PAWN if color == 'white' else PAWN
        OPPOSSING_KNIGHT = -KNIGHT if color == 'white' else KNIGHT
        OPPOSING_BISHOP = -BISHOP if color == 'white' else BISHOP
        OPPOSING_ROOK = -ROOK if color == 'white' else ROOK
        OPPOSING_QUEEN = -QUEEN if color == 'white' else QUEEN
        OPPOSING_KING = -KING_TO_CHECK

        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        king_position = self.find_piece(board_actual, KING_TO_CHECK)
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
                if board_actual[y][x] == OPPOSSING_KNIGHT:
                    return 'check'

        if color == 'white':
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



    def list_pawn_move(self, y,x):
        """
        Generate all legal pawn moves from a given position.
        Args:
            y (int): Row index of the pawn.
            x (int): Column index of the pawn.
        Returns:
            list: List of possible pawn moves as [[from_y, from_x], [to_y, to_x]].
        """

        EMPTY = self.EMPTY
        PAWN = self.PAWN
        list_p_move = []
        direction = 1 if self.board[y][x] == PAWN else -1 

        if self.board[y + direction][x] == EMPTY:
            list_p_move.append([[y,x],[y + direction, x]])
            if (y == 1 and direction == 1) or (y == 6 and direction == -1):
                if self.board[y + 2 * direction][x] == EMPTY:
                    list_p_move.append([[y,x],[y + 2 * direction, x]])

        if x + 1 <= 7 and self.board[y + direction][x + 1] * self.board[y][x] < 0:
            list_p_move.append([[y,x],[y + direction, x + 1]])

        if x - 1 >= 0 and self.board[y + direction][x - 1] * self.board[y][x] < 0: 
            list_p_move.append([[y,x],[y + direction, x - 1]])
        
        return list_p_move
    

    def list_knight_move(self, y,x):
        """
        Generate all valid knight moves from a given position.
        Args:
            y (int): Row index of the knight.
            x (int): Column index of the knight.
        Returns:
            list: List of valid knight moves as [[from_y, from_x], [to_y, to_x]].
        """

        KNIGHT = self.KNIGHT
        list_k_move = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

        if self.board[y][x] in (KNIGHT,-KNIGHT):
            for e in knight_moves:
                if y+e[0] >= 0 and y+e[0] <= 7 and x+e[1] >= 0 and x+e[1] <= 7:
                    if (self.board[y+e[0]][x+e[1]] <= 0 if self.board[y][x] == KNIGHT else self.board[y+e[0]][x+e[1]] >= 0):
                        list_k_move.append([[y,x],[y+e[0],x+e[1]]])
        return list_k_move
    

    def list_bishop_move(self, y,x):
        """
        Generate all legal bishop moves from a given position.
        Args:
            y (int): Row index of the bishop.
            x (int): Column index of the bishop.
        Returns:
            list: List of possible bishop moves as [[from_y, from_x], [to_y, to_x]].
        """

        EMPTY = self.EMPTY
        BISHOP = self.BISHOP
        list_b_move = []
        bishop_move = [(1,1),(-1,1),(-1,-1),(1,-1)]

        if self.board[y][x] in (BISHOP,-BISHOP):
            for e in bishop_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == EMPTY:
                    list_b_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == BISHOP else self.board[y_c][x_c] > 0):
                    list_b_move.append([[y,x],[y_c,x_c]])

        return list_b_move
    

    def list_rook_move(self, y,x):
        """
        Generate all legal rook moves from a given position.
        Args:
            y (int): Row index of the rook.
            x (int): Column index of the rook.
        Returns:
            list: List of possible rook moves as [[from_y, from_x], [to_y, to_x]].
        """

        EMPTY = self.EMPTY
        ROOK = self.ROOK
        list_r_move = []
        rook_move = [(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (ROOK,-ROOK):
            for e in rook_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == EMPTY:
                    list_r_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == ROOK else self.board[y_c][x_c] > 0):
                    list_r_move.append([[y,x],[y_c,x_c]])     

        return list_r_move
    

    def list_queen_move(self, y,x):
        """
        Generate all valid queen moves from the given position.
        Args:
            y (int): Row index of the queen.
            x (int): Column index of the queen.
        Returns:
            list: List of valid queen moves as [[from_y, from_x], [to_y, to_x]].
        """

        EMPTY = self.EMPTY
        QUEEN = self.QUEEN
        list_q_move = []
        queen_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (QUEEN,-QUEEN):
            for e in queen_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == EMPTY:
                    list_q_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == QUEEN else self.board[y_c][x_c] > 0):
                    list_q_move.append([[y,x],[y_c,x_c]])    

        return list_q_move
    

    def list_king_move(self, y,x):
        """
        Generate all legal king moves (including castling) from position (y, x).
        Args:
            y (int): Row index of the king.
            x (int): Column index of the king.
        Returns:
            list: List of possible king moves as [[from_y, from_x], [to_y, to_x]].
        """

        EMPTY = self.EMPTY
        KING = self.KING
        list_k_move = []
        king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (KING,-KING):
            for e in king_move:
                y_c = y + e[0]
                x_c = x + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] >= 0 if self.board[y][x] == -KING else self.board[y_c][x_c] <= 0):
                    list_k_move.append([[y,x],[y_c,x_c]])

        if (
            (self.castling_p_white if self.board[y][x] > 0 else self.castling_p_black)
            and (self.rook_m['rook_white_castling'] if self.board[y][x] > 0 else self.rook_m['rook_black_castling'])
            and self.board[y][x] > 0
        ):
            if self.board[y][x-1] == EMPTY and self.board[y][x-2] == EMPTY:
                new_board = copy.deepcopy(self.board)
                new_board[y][x-1] = self.board[y][x]
                new_board[y][x] = EMPTY
                if self.is_check('white' if self.board[y][x] > 0 else 'black', new_board) != 'check':
                    list_k_move.append([[y,x],[y,x-2]])

        if (
            (self.big_castling_p_white if self.board[y][x] > 0 else self.big_castling_p_black)
            and (self.rook_m['rook_big_white_castling'] if self.board[y][x] > 0 else self.rook_m['rook_big_black_castling'])
            and self.board[y][x] > 0
        ):
            if self.board[y][x+1] == EMPTY and self.board[y][x+2] == EMPTY and self.board[y][x+3] == EMPTY:
                new_board = copy.deepcopy(self.board)
                new_board[y][x+1] = self.board[y][x] 
                new_board[y][x] = EMPTY
                if self.is_check('white' if self.board[y][x] > 0 else 'black', new_board) != 'check':
                    list_k_move.append([[y,x],[y,x+2]])

        return list_k_move


    def list_all_legal_move(self, color):
        """
        List all legal moves for the given color, excluding moves that leave the king in check.
        Args:
            color (str): 'white' or 'black'.
        Returns:
            list: List of legal moves as tuples of start and end positions.
        """

        EMPTY = self.EMPTY
        PAWN = self.PAWN
        KNIGHT = self.KNIGHT
        BISHOP = self.BISHOP
        ROOK = self.ROOK
        QUEEN = self.QUEEN
        KING = self.KING
        list_all_move = []

        for y_i in range(0,8):
            for x_i in range(0,8):
                if self.board[y_i][x_i] != EMPTY and ((color == 'white' and self.board[y_i][x_i] > 0) or (color == 'black' and self.board[y_i][x_i] < 0)):
                    n_move = []
                    if abs(self.board[y_i][x_i]) == PAWN:
                        n_move = self.list_pawn_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == KING:
                        n_move = self.list_king_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == QUEEN:
                        n_move = self.list_queen_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == ROOK:
                        n_move = self.list_rook_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == BISHOP:
                        n_move = self.list_bishop_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == KNIGHT:
                        n_move = self.list_knight_move(y_i,x_i)
                    if n_move:
                        for m in n_move:
                            new_board = copy.deepcopy(self.board)
                            new_board[m[0][0]][m[0][1]] = EMPTY
                            new_board[m[1][0]][m[1][1]] = self.board[y_i][x_i]
                            if self.is_check(color, new_board) != 'check':
                                list_all_move.append(m)
                
        return list_all_move


    def is_checkmate(self, color, board_actual):
        """
        Determine if the given color is in checkmate on the provided board.
        Args:
            color (str): 'white' or 'black'.
            board_actual (list): Current board state.
        Returns:
            bool: True if checkmate, False otherwise.
        """

        EMPTY = self.EMPTY
        KING = self.KING
        if color in ('black','white'):
            if self.is_check(color, board_actual) == 'check':
                move = self.list_all_legal_move("black") if color == 'black' else self.list_all_legal_move("white")
                for m in move:
                    if self.board[m[0][0]][m[0][1]] not in (KING,-KING) or abs(m[0][1]-m[1][1]) != 2:
                        new_board = copy.deepcopy(board_actual)
                        new_board[m[0][0]][m[0][1]] = EMPTY
                        new_board[m[1][0]][m[1][1]] = board_actual[m[0][0]][m[0][1]]
                        if self.is_check(color, new_board) != 'check':
                            return False
                        
                return True
            
        return False
    

    def launch_partie(self, color="white", auto_promotion = "9"):
        """
        Initialize and start a chess game, setting castling rights and turn color.
        Args:
            color (str): 'white' or 'black' to set the starting player.
            auto_promotion (str): Promotion setting for pawns.
        Returns:
            None
        """

        ROOK = self.ROOK
        KING = self.KING
        if self.board[0][3] != KING:
            self.castling_p_white = False
            self.big_castling_p_white = False
        if self.board[0][0] != ROOK:
            self.rook_m['rook_white_castling'] = False
        if self.board[0][7] != ROOK:
            self.rook_m['rook_big_white_castling'] = False
        if self.board[7][3] != -KING:
            self.castling_p_black = False
            self.big_castling_p_black = False
        if self.board[7][0] != -ROOK:
            self.rook_m['rook_black_castling'] = False
        if self.board[7][7] != -ROOK:
            self.rook_m['rook_big_black_castling'] = False

        self.auto_promotion = auto_promotion
        self.color_turn = color

        print("╔═════════════ GAME START ═════════════╗")

        if color == "white":
            print()
            print("⚪ ═══════════ White play ═══════════ ⚪")
            print()

            self.board_print(True,'white',self.board)
        else:
            print()
            print("⚫ ═══════════ Black play ═══════════ ⚫")
            print()

            self.board_print(True,'black',self.board)
        return


    def validate_and_apply_move(self):
        """
        Validate the current move, apply it to the board if legal, and handle special cases (check, checkmate, stalemate, castling, en passant).
        Returns:
            str or None: 'valid', 'checkmate', 'pat', or None if the move is invalid.
        """

        EMPTY = self.EMPTY
        PAWN = self.PAWN
        KNIGHT = self.KNIGHT
        BISHOP = self.BISHOP
        ROOK = self.ROOK
        QUEEN = self.QUEEN
        KING = self.KING
        result_valid_king = None
        result_valid_pion = None

        if not self.list_game_move:
            if self.is_checkmate(color='black',board_actual=self.board):
                print()
                print("╚════════ CHECKMATE WHITE WIN ═════════╝")
                return 'checkmate'
            
            if self.is_checkmate(color='white',board_actual=self.board):
                print()
                print("╚════════ CHECKMATE BLACK WIN ═════════╝")
                return 'checkmate'
            
            legal_move = self.list_all_legal_move("white") if self.color_turn == "black" else self.list_all_legal_move("black")      

            if legal_move == [] and self.color_turn == "black":
                print("════════════════════════════════════════")
                print()
                self.board_print(True,'white',self.board)
                self.list_game_move.append(self.board)
                self.list_game_board_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
                print()
                print("⏸ ═════════ Whites are pat ══════════ ⏸")
                return 'pat'
            
            if legal_move == [] and self.color_turn == "white":
                print("════════════════════════════════════════")
                print()
                self.board_print(True,'black',self.board)
                self.list_game_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
                self.list_game_board_move.append(self.board)
                print()
                print("⏸ ═════════ Blacks are pat ══════════ ⏸")
                return 'pat'          
        
        if self.info_move["start_value"] > 0:
            if self.is_check('black',self.board) != 'valid':
                print("🚫 Invalid move black is in check ═ 🚫")
                return
        else:
            if self.is_check('white',self.board) != 'valid':
                print("🚫 Invalid move white is in check ═ 🚫")
                return

        if self.info_move["start_value"] == PAWN or self.info_move["start_value"] == -PAWN:
            result_valid_pion = self.valid_pawn_move(self.info_move)
            if result_valid_pion not in {'valid', 'en passant'}:
                print("🚫 ══════════ Invalid move ════════ 🚫")
                return
            elif result_valid_pion == 'en passant':
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_end_coordinate"]] = EMPTY
        elif self.info_move["start_value"] == ROOK or self.info_move["start_value"] == -ROOK:
            if self.valid_rook_move(self.info_move,debug=None) != 'valid':
                print("🚫 ══════════ Invalid move ════════ 🚫")
                return 
        elif self.info_move["start_value"] == BISHOP or self.info_move["start_value"] == -BISHOP:
            if self.valid_bishop_move(self.info_move) != 'valid':
                print("🚫 ══════════ Invalid move ════════ 🚫")
                return
        elif self.info_move["start_value"] == KNIGHT or self.info_move["start_value"] == -KNIGHT:
            if self.valid_knight_move(self.info_move) != 'valid':
                print("🚫 ══════════ Invalid move ════════ 🚫")
                return
        elif self.info_move["start_value"] == KING or self.info_move["start_value"] == -KING:
            result_valid_king = self.valid_king_move(self.info_move,castling_white=self.castling_p_white,castling_black=self.castling_p_black,big_castling_black=self.big_castling_p_black,big_castling_white=self.big_castling_p_white)
            if result_valid_king not in ['casting', 'big_casting','valid']:
                print("🚫 ══════════ Invalid move ════════ 🚫")
                return 
            elif result_valid_king == 'casting':
                print("casting !")
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-3] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-1] = (ROOK if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else -ROOK)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
            elif result_valid_king == 'big_casting':
                print("big casting !")
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+4] = EMPTY
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+1] = (ROOK if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else -ROOK)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
            else:
                if self.info_move["start_value"] > 0:
                    self.castling_p_white, self.big_castling_p_white = (False, False)  
                else:
                    self.castling_p_black, self.big_castling_p_black = (False, False)   

        elif self.info_move["start_value"] == QUEEN or self.info_move["start_value"] == -QUEEN:
            if self.valid_queen_move(self.info_move) != 'valid':
                print("🚫---invalid move---🚫")
                return
        
        if result_valid_king not in ['big_casting', 'casting'] and result_valid_pion != 'en passant':
            new_board = copy.deepcopy(self.board)
            new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = EMPTY
            new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
        elif result_valid_king  != 'big_casting':
            if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0: 
                self.castling_p_white = False
            else:
                self.castling_p_black = False
        else:
            if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0: 
                self.big_castling_p_white = False
            else:
                self.big_castling_p_black = False


        if self.info_move["start_value"] < 0:
            if self.is_check('black',new_board) != 'valid':
                print("🚫 Invalid move black is in check = 🚫")
                return
        else:
            if self.is_check('white',new_board) != 'valid':
                print("🚫 Invalid move white is in check = 🚫")
                return
        
        self.board = copy.deepcopy(new_board)
        
        if self.is_checkmate(color='black',board_actual=self.board):
            print("════════════════════════════════════════")
            print()
            self.list_game_move.append(self.board)
            self.list_game_board_move.append([[self.info_move['y_start_coordinate'],self.info_move["x_start_coordinate"]],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            self.board_print(True,'black',self.board)
            print()
            print("╚════════ CHECKMATE WHITE WIN ═════════╝")
            return 'checkmate'
        if self.is_checkmate(color='white',board_actual=self.board):
            print("════════════════════════════════════════")
            print()
            self.list_game_move.append(self.board)
            self.list_game_board_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            print()
            self.board_print(True,'white',self.board)
            print("╚════════ CHECKMATE BLACK WIN ═════════╝")
            return 'checkmate'

        self.list_game_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
        self.list_game_board_move.append(self.board)
        return 'valid'


    def play_move(self, all_move, print_move=True):
        """
        Play a move in the chess game, handling move validation, special rules, and game end conditions.
        Args:
            all_move (str): Move in algebraic notation (e.g., 'e2 e4' or 'e7 e8q').
            print_move (bool, optional): Whether to print the move. Defaults to True.
        Returns:
            str: 'valid', 'invalid', 'illegal', 'checkmate', 'pat', or 'draw' depending on the move result.
        """

        EMPTY = self.EMPTY
        KNIGHT = self.KNIGHT
        BISHOP = self.BISHOP
        ROOK = self.ROOK
        QUEEN = self.QUEEN
        KING = self.KING
        if self.party_over:
            print("🚫 ═══════ The game is over ═══════ 🚫")
            return 'illegal'
        
        if print_move:
            print(f"> {all_move}")

        if not self.auto_promotion:
            if not bool(re.match(r'^[a-h][1-8]\s[a-h][1-8]$', all_move)):
                print("🚫--- Invalid move ---🚫 => valid move example: ✅--- e2 e4 ---✅")
                return 'illegal'
        else:
            if all_move[-1] in ('q','r','b','n'):
                self.auto_promotion_value = {'q':QUEEN,'r':ROOK,'b':BISHOP,'n':KNIGHT}[all_move[-1]]
                all_move = all_move[:-1]

                if not bool(re.match(r'^[a-h][1-8]\s[a-h][1-8]$', all_move)):
                    print("🚫--- Invalid move ---🚫 => valid move example: ✅--- e7 e8q ---✅")
                    return 'illegal'

            elif not bool(re.match(r'^[a-h][1-8]\s[a-h][1-8]$', all_move)):
                print("🚫--- Invalid move ---🚫 => valid move example: ✅--- e2 e4 ---✅")

        print()

        self.info_move = self.give_move_info(all_move,debug=None)

        if self.info_move == 'illegal':
            print("🚫 ══════════ Invalid move ════════ 🚫")
            return 'invalid'
        elif (self.info_move['start_value'] > 0 and self.color_turn == "black") or (self.info_move['start_value'] < 0 and self.color_turn == "white"):
            print("🚫 ══════ It's not your turn ══════ 🚫")
            return 'invalid'
        else:
            rep = self.validate_and_apply_move()

        if rep == 'checkmate' or rep == 'pat':
            self.party_over = True
            return 'checkmate'
        elif rep is None:
            return 'invalid'
        
        legal_move = self.list_all_legal_move("white") if self.color_turn == "black" else self.list_all_legal_move("black")      

        if legal_move == [] and self.color_turn == "black":
            print("════════════════════════════════════════")
            print()
            self.board_print(True,'white',self.board)
            self.list_game_move.append(self.board)
            self.list_game_board_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            print()
            print("⏸ ═════════ Whites are pat ══════════ ⏸")
            self.party_over = True
            return 'pat'
        
        if legal_move == [] and self.color_turn == "white":
            print("════════════════════════════════════════")
            print()
            self.board_print(True,'black',self.board)
            self.list_game_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            self.list_game_board_move.append(self.board)
            print()
            print("⏸ ═════════ Blacks are pat ══════════ ⏸")
            self.party_over = True
            return 'pat'
        
        if self.check_repetition():
            print("════════════════════════════════════════")
            print()
            if self.color_turn == "white":
                self.board_print(True,'white',self.board)
            else:
                self.board_print(True,'black',self.board)
            print()
            print("⏸ ═══════ Draw by repetition ═══════ ⏸")
            self.party_over = True
            return 'draw'
        
        if len(self.list_game_move) >= 50:
            no_capture_moves = all(self.board[move[1][0]][move[1][1]] == EMPTY for move in self.list_game_move[-50:])               

            if no_capture_moves:
                print("════════════════════════════════════════")
                print()
                if self.color_turn == "white":
                    self.board_print(True,'white',self.board)
                else:
                    self.board_print(True,'black',self.board)
                print()
                print("⏸ ═════ Draw by fifty-move rule ════ ⏸")
                self.party_over = True
                return 'draw'
            
        def material_insufficiency(board_test):
            for row in board_test:
                for element in row:
                    if element not in [EMPTY, KING, -KING]:
                        return False
            return True

        if material_insufficiency(self.board):
            print("════════════════════════════════════════")
            print()
            if self.color_turn == "white":
                self.board_print(True,'white',self.board) 
            else:
                self.board_print(True,'black',self.board)
            print()
            print("⏸ ══ Draw by insufficient material ═ ⏸")
            self.party_over = True
            return 'draw'
            
        if self.color_turn == "white":
            print()
            print("⚫ ═══════════ Black play ═══════════ ⚫")
            print()
            self.board_print(True,'black',self.board)

        elif self.color_turn == "black":
            print()
            print("⚪ ═══════════ White play ═══════════ ⚪")
            print()
            self.board_print(True,'white',self.board)    
        
        self.color_turn = "black" if self.color_turn == "white" else "white"
        return 'valid'
    

    def play(self, color="white", auto_promotion = "9"):
        """
        Play a chess game loop for the given color.
        Args:
            color (str): 'white' or 'black'.
            auto_promotion (str): Promotion piece code.
        Returns:
            str: 'checkmate', 'pat', or 'draw' when the game ends.
        """

        self.launch_partie(color=color, auto_promotion=auto_promotion)
        
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
    process = Chess()
    process.play(auto_promotion=False)    
