import re 
import copy
from collections import Counter

class Chess:
    def __init__(self): 
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
            0: "0",
            1: "p",
            5: "t",
            4: "f",
            3: "c",
            9: "r",
            7: "k",
            -1: "P",
            -5: "T",
            -4: "F",
            -3: "C",
            -9: "R",
            -7: "K"
        }

        self.piece_note_style = {
            1: "♙",   
            5: "♖",   
            3: "♘",  
            4: "♗",   
            9: "♕",  
            7: "♔", 
            -1: "♟",
            -5: "♜",  
            -3: "♞", 
            -4: "♝",  
            -9: "♛", 
            -7: "♚",
            0: " "    
        }

        self.piece = {
            0: "empty",
            1: "white_pawn",
            5: "white_rook",
            4: "white_bishop",
            3: "white_knight",
            9: "white_queen",
            7: "white_king",
            -1: "black_pawn",
            -5: "black_rook",
            -4: "black_bishop",
            -3: "black_knight",
            -9: "black_queen",
            -7: "black_king"
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
            [ 5, 3, 4, 7, 9, 4, 3, 5],
            [ 1, 1, 1, 1, 1, 1, 1, 1],
            [ 0, 0, 0, 0, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 0, 0, 0, 0],
            [ 0, 0, 0, 0, 0, 0, 0, 0],
            [-1,-1,-1,-1,-1,-1,-1,-1],
            [-5,-3,-4,-7,-9,-4,-3,-5]
        ]


    def check_repetition(self):
        serialized_boards = [tuple(tuple(row) for row in board) for board in self.list_game_board_move]
        counts = Counter(serialized_boards)
        
        if any(count >= 3 for count in counts.values()): 
            return True
        
        return False
    
    
    def promote_pawn(self, color):
        piece_map = {'Q': 9, 'R': 5, 'B': 4, 'N': 3}
        if not self.auto_promotion:
            while True:
                choice = input("Promotion mode (the queen: 'Q', the rook: 'R', the bishop: 'B' and the knight 'N')> ")
                if choice in piece_map:
                    return piece_map[choice] * (1 if color == 'white' else -1)
                
        else:
            return int(self.auto_promotion) * (1 if color == 'white' else -1)
        

    def valid_pawn_move(self, move):
        if move['end_value'] == 0: 
            if self.list_game_move:
                if (move['y_start_coordinate'] == 4 if move['start_value'] > 0 else move['y_start_coordinate'] == 3):
                    if self.board[move['y_start_coordinate']][move['x_end_coordinate']] == (-1 if move['start_value'] > 0 else 1):
                        if move['x_end_coordinate'] == move['x_start_coordinate']+1:
                            if self.list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return('en passant')
                            
                        elif move['x_end_coordinate'] == move['x_start_coordinate']-1:
                            if self.list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                                return('en passant')
                            
            if move['x_end_coordinate'] == move['x_start_coordinate']: 
                if move['name_piece_coor1'] == "white_pawn":     
                    if (
                        move['y_end_coordinate'] == move['y_start_coordinate'] + 1
                        or (
                            move['y_end_coordinate'] == move['y_start_coordinate'] + 2
                            and move['y_start_coordinate'] == 1
                            and self.board[move['y_start_coordinate'] + 1][move['x_start_coordinate']] == 0
                        )
                    ):
                        if move['y_end_coordinate'] == 7:
                            move["start_value"] = self.promote_pawn('white')
                        return('valid')
                    
                    else:
                        return('illegal')

                if move['name_piece_coor1'] == "black_pawn":
                    if (
                        move['y_start_coordinate'] == move['y_end_coordinate'] + 1
                        or (
                            move['y_start_coordinate'] == move['y_end_coordinate'] + 2
                            and move['y_start_coordinate'] == 6
                            and self.board[move['y_start_coordinate'] - 1][move['x_start_coordinate']] == 0
                        )
                    ):
                        if move['y_end_coordinate'] == 0:
                            move["start_value"] = self.promote_pawn('black')
                        return 'valid'
                    else:
                        return('illegal')

                if move['name_piece_coor1'] != "black_pawn" and move['name_piece_coor1'] != "white_pawn":
                    return('illegal')
                
            else: 
                return('illegal')

        elif move['end_value'] != 0:
            if move['name_piece_coor1'] == "white_pawn":
                if move['end_value'] > 0:
                    return('illegal')
                if (
                    abs(move['x_end_coordinate'] - move['x_start_coordinate']) == 1
                    and move['y_end_coordinate'] == move['y_start_coordinate'] + 1
                ):
                        if move['y_end_coordinate'] == 7:
                            move["start_value"] = self.promote_pawn('white')
                        return('valid')
                
                else:
                    return('illegal')


            if move['name_piece_coor1'] == "black_pawn":
                if move['end_value'] < 0:
                    return('illegal')
                if (
                    abs(move['x_end_coordinate'] - move['x_start_coordinate']) == 1
                    and move['y_end_coordinate'] == move['y_start_coordinate'] - 1
                ):
                    if move['y_end_coordinate'] == 0:
                        move["start_value"] = self.promote_pawn('black')
                    return('valid')
                
                else:
                    return('illegal')
                
            return('illegal')
        

    def valid_bishop_move(self, move):
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
                if self.board[y_start_coordinate][x_start_coordinate] != 0:
                        return('illegal')
                
                x_start_coordinate += x
                y_start_coordinate += y
                    
            return('valid')
        
        else:
            return('illegal')
        

    def valid_rook_move(self, move, debug=None):
        if move['end_value'] == 0 or (move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0):
            if move['y_start_coordinate'] == move['y_end_coordinate']:
                for i in range(min(move['x_start_coordinate'], move['x_end_coordinate']), max(move['x_start_coordinate'], move['x_end_coordinate'])):
                    if self.board[move['y_start_coordinate']][i] != 0 and [i] != [move['x_start_coordinate']] and [i] != [move['x_end_coordinate']]:
                        return('illegal')
                    
                if move['start_value'] == 5:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_white_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_big_white_castling'] = False
                elif move['start_value'] == -5:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_black_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_big_black_castling'] = False
                return('valid')
            
            elif move['x_start_coordinate'] == move['x_end_coordinate']:
                for i in range(min(move['y_start_coordinate'], move['y_end_coordinate']), max(move['y_start_coordinate'], move['y_end_coordinate'])):
                    if self.board[i][move['x_start_coordinate']] != 0 and [i] != [move['y_start_coordinate']] and [i] != [move['y_end_coordinate']]:
                        return('illegal')
                    
                if move['start_value'] == 5:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_big_white_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                        self.rook_m['rook_white_castling'] = False
                elif move['start_value'] == -5:
                    if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_big_black_castling'] = False
                    elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                        self.rook_m['rook_black_castling'] = False
                return('valid')
            
        return 'illegal'
    

    def valid_knight_move(self, move):
        if move['end_value'] == 0 or ((move['end_value'] > 0 and move['start_value'] < 0) or (move['end_value'] < 0 and move['start_value'] > 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 1:
                return('valid')
            
            elif abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 2:
                return('valid')
            
        else:
            return('illegal')
        

    def valid_king_move(self, move, castling_white=False, castling_black=False,big_castling_black=False,big_castling_white=False):
        if (
            move['end_value'] == 0
            and (
            castling_white if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0
            else castling_black
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and self.board[move['y_end_coordinate']][move['x_end_coordinate'] - 1] in (-5, 5)
        ):
            if self.is_check(('white' if self.board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'),self.board) != 'check':
                if self.board[move['y_end_coordinate']][move['x_end_coordinate']+1] == 0:
                    new_board = copy.deepcopy(self.board)
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-1] = self.board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                        if (self.rook_m['rook_white_castling'] == True if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else self.rook_m['rook_black_castling'] == True):
                            return 'casting'

        elif (
            move['end_value'] == 0
            and (
                big_castling_white if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0
                else big_castling_black
            )
            and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2
            and move['y_start_coordinate'] == move['y_end_coordinate']
            and self.board[move['y_end_coordinate']][move['x_end_coordinate'] + 2] in (-5, 5)
        ):
            if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'),self.board) != 'check':
                if self.board[move['y_end_coordinate']][move['x_end_coordinate']+1] == 0 and self.board[move['y_end_coordinate']][move['x_end_coordinate']-1] == 0:
                    new_board = copy.deepcopy(self.board)
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
                    new_board[move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+1] = self.board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                    if self.is_check(('white' if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                        if (self.rook_m['rook_big_white_castling'] == True if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else self.rook_m['rook_big_black_castling'] == True):
                            return 'big_casting'
                        
        if move['end_value'] == 0 or ((move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0)): 
            if abs(move['x_start_coordinate'] - move['x_end_coordinate']) <= 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) <= 1:
                return('valid')
            
            else:
                return('illegal')
            
        else:
            return('illegal')
        

    def give_move_info(self, all_move,debug=None):
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

            if start_value == 0:
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
        
        except:
            return('illegal')
        

    def valid_queen_move(self, move):
        if self.valid_rook_move(move) == 'valid' or self.valid_bishop_move(move) == 'valid':
            return('valid')
        
        else:
            return('illegal')
        

    def board_print(self, style,color,board_test):
        if style:
            board_rendu = [list(reversed([self.piece_note_style[e] for e in r])) for r in board_test] if color == 'white' else [[self.piece_note_style[e] for e in r] for r in board_test]
        else:    
            board_rendu = [list(reversed([self.piece_note[e] for e in r])) for r in board_test]
        if color == 'white':
            board_rendu.reverse()
        for row in board_rendu:
            print(row)
        return 


    def find_piece(self, board_test,f_piece):
        for x, row in enumerate(board_test): 
            for y, cell in enumerate(row): 
                if cell == f_piece:  
                    return (y + 1, x + 1)


    def is_check(self, color,board_actual):
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

        if color == 'white':
            white_king_position = self.find_piece(board_actual,7)
            try:
                white_king_position[0]
            except:
                return 'error'
            
            for i in range(white_king_position[0]-1,8):
                if board_actual[white_king_position[1]-1][i] in (-5,-9):
                    return 'check'
                
                if board_actual[white_king_position[1]-1][i] not in (0,7):
                    break

            for i in range(white_king_position[0]-1, -1, -1):
                if board_actual[white_king_position[1]-1][i] in (-5,-9):
                    return 'check'
                
                if board_actual[white_king_position[1]-1][i] not in (0,7):
                    break

            for i in range(white_king_position[1]-1,8):
                if board_actual[i][white_king_position[0]-1] in (-5,-9):
                    return 'check'
                
                if board_actual[i][white_king_position[0]-1] not in (0,7):
                    break

            for i in range(white_king_position[1]-1, -1, -1):
                if board_actual[i][white_king_position[0]-1] in (-5,-9):
                    return 'check'
                
                if board_actual[i][white_king_position[0]-1] not in (0,7):
                    break
            
            x = white_king_position[0] -1 
            y = white_king_position[1] -1
            while y <= 7 and x <= 7:
                if board_actual[y][x] in (-4,-9):
                    return 'check'
                
                if board_actual[y][x] not in (0,7):
                    break

                y += 1
                x += 1

            x = white_king_position[0] -1 
            y = white_king_position[1] -1
            while y >= 0 and x >= 0:
                if board_actual[y][x] in (-4,-9):
                    return 'check'
                
                if board_actual[y][x] not in (0,7):
                    break

                y -= 1
                x -= 1

            x = white_king_position[0] -1 
            y = white_king_position[1] -1
            while y <= 7 and x >= 0:
                if board_actual[y][x] in (-4,-9):
                    return 'check'
                
                if board_actual[y][x] not in (0,7):
                    break

                y += 1
                x -= 1
            
            x = white_king_position[0] -1 
            y = white_king_position[1] -1
            while y >= 0 and x <= 7:
                if board_actual[y][x] in (-4,-9):
                    return 'check'
                
                if board_actual[y][x] not in (0,7):
                    break

                y -= 1
                x += 1
            
            for p in knight_moves:
                x = white_king_position[0] -1 + p[0]
                y = white_king_position[1] -1 + p[1]
                if y >= 0 and x >= 0 and y <= 7 and x <= 7:
                    if board_actual[y][x] == -3:
                        return 'check'
            
            y = white_king_position[1]
            x = white_king_position[0] 
            if y >= 0 and y <= 7 and x >= 0 and x <= 7:
                if board_actual[y][x] == -1:
                    return 'check'
                
            x = white_king_position[0] - 2
            if y >= 0 and y <= 7 and x >= 0 and x <= 7:
                if board_actual[y][x] == -1:
                    return 'check'   

            x = white_king_position[0] -1
            y = white_king_position[1] -1
            king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]
            if board_actual[y][x] in (7,-7):
                for e in king_move:
                    y_c = y + e[0]
                    x_c = x + e[1]
                    if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board_actual[y_c][x_c] in (7,-7):
                        return 'check'

            return 'valid'
        

        if color == 'black':
            black_king_position = self.find_piece(board_actual,-7)
            try:
                black_king_position[0]
            except:
                return 'error'

            for i in range(black_king_position[0]-1,8):
                if board_actual[black_king_position[1]-1][i] in (5,9):
                    return 'check'
                
                if board_actual[black_king_position[1]-1][i] not in (-0,-7):
                    break

            for i in range(black_king_position[0]-1, -1, -1):
                if board_actual[black_king_position[1]-1][i] in (5,9):
                    return 'check'
                
                if board_actual[black_king_position[1]-1][i] not in (-0,-7):
                    break

            for i in range(black_king_position[1]-1,8):
                if board_actual[i][black_king_position[0]-1] in (5,9):
                    return 'check'
                
                if board_actual[i][black_king_position[0]-1] not in (-0,-7):
                    break

            for i in range(black_king_position[1]-1, -1, -1):
                if board_actual[i][black_king_position[0]-1] in (5,9):
                    return 'check'
                
                if board_actual[i][black_king_position[0]-1] not in (-0,-7):
                    break

            x = black_king_position[0] -1 
            y = black_king_position[1] -1
            while y <= 7 and x <= 7:
                if board_actual[y][x] in (4,9):
                    return 'check'
                
                if board_actual[y][x] not in (-0,-7):
                    break

                y += 1
                x += 1

            x = black_king_position[0] -1 
            y = black_king_position[1] -1
            while y >= 0 and x >= 0:
                if board_actual[y][x] in (4,9):
                    return 'check'
                
                if board_actual[y][x] not in (-0,-7):
                    break

                y -= 1
                x -= 1

            x = black_king_position[0] -1 
            y = black_king_position[1] -1
            while y <= 7 and x >= 0:
                if board_actual[y][x] in (4,9):
                    return 'check'
                
                if board_actual[y][x] not in (-0,-7):
                    break

                y += 1
                x -= 1
            
            x = black_king_position[0] -1
            y = black_king_position[1] -1
            while y >= 0 and x <= 7:
                if board_actual[y][x] in (4,9):
                    return 'check'
                
                if board_actual[y][x] not in (-0,-7):
                    break

                y -= 1
                x += 1

            for p in knight_moves:
                x = black_king_position[0] -1 + p[0]
                y = black_king_position[1] -1 + p[1]
                if y >= 0 and x >= 0 and y <= 7 and x <= 7:
                    if board_actual[y][x] == 3:
                        return 'check'
                    
            y = black_king_position[1]-2
            x = black_king_position[0] 
            if y >= 0 and y <= 7 and x >= 0 and x <= 7:
                if board_actual[y][x] == 1:
                    return 'check'
                
            x = black_king_position[0] - 2
            if y >= 0 and y <= 7 and x >= 0 and x <= 7:
                if board_actual[y][x] == 1:
                    return 'check'   

            x = black_king_position[0] -1
            y = black_king_position[1] -1
            king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]
            if board_actual[y][x] in (7,-7):
                for e in king_move:
                    y_c = y + e[0]
                    x_c = x + e[1]
                    if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board_actual[y_c][x_c] in (7,-7):
                        return 'check'
                
            return 'valid'
        
        else:
            exit('error color')


    def list_pawn_move(self, y,x):
        list_p_move = []
        direction = 1 if self.board[y][x] == 1 else -1 

        if self.board[y + direction][x] == 0:
            list_p_move.append([[y,x],[y + direction, x]])
            if (y == 1 and direction == 1) or (y == 6 and direction == -1):
                if self.board[y + 2 * direction][x] == 0:
                    list_p_move.append([[y,x],[y + 2 * direction, x]])

        if x + 1 <= 7 and self.board[y + direction][x + 1] * self.board[y][x] < 0:
            list_p_move.append([[y,x],[y + direction, x + 1]])

        if x - 1 >= 0 and self.board[y + direction][x - 1] * self.board[y][x] < 0: 
            list_p_move.append([[y,x],[y + direction, x - 1]])
        
        return list_p_move
    

    def list_knight_move(self, y,x):
        list_k_move = []
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

        if self.board[y][x] in (3,-3):
            for e in knight_moves:
                if y+e[0] >= 0 and y+e[0] <= 7 and x+e[1] >= 0 and x+e[1] <= 7:
                    if (self.board[y+e[0]][x+e[1]] <= 0 if self.board[y][x] == 3 else self.board[y+e[0]][x+e[1]] >= 0):
                        list_k_move.append([[y,x],[y+e[0],x+e[1]]])
        return list_k_move
    

    def list_bishop_move(self, y,x):
        list_b_move = []
        bishop_move = [(1,1),(-1,1),(-1,-1),(1,-1)]

        if self.board[y][x] in (4,-4):
            for e in bishop_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == 0:
                    list_b_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == 4 else self.board[y_c][x_c] > 0):
                    list_b_move.append([[y,x],[y_c,x_c]])

        return list_b_move
    

    def list_rook_move(self, y,x):
        list_r_move = []
        rook_move = [(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (5,-5):
            for e in rook_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == 0:
                    list_r_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == 5 else self.board[y_c][x_c] > 0):
                    list_r_move.append([[y,x],[y_c,x_c]])     

        return list_r_move
    

    def list_queen_move(self, y,x):
        list_q_move = []
        queen_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (9,-9):
            for e in queen_move:
                y_c = y + e[0]
                x_c = x + e[1]
                while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and self.board[y_c][x_c] == 0:
                    list_q_move.append([[y,x],[y_c,x_c]])
                    y_c = y_c + e[0]
                    x_c = x_c + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] < 0 if self.board[y][x] == 9 else self.board[y_c][x_c] > 0):
                    list_q_move.append([[y,x],[y_c,x_c]])    

        return list_q_move
    

    def list_king_move(self, y,x):
        list_k_move = []
        king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]

        if self.board[y][x] in (7,-7):
            for e in king_move:
                y_c = y + e[0]
                x_c = x + e[1]
                if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (self.board[y_c][x_c] >= 0 if self.board[y][x] == -7 else self.board[y_c][x_c] <= 0):
                    list_k_move.append([[y,x],[y_c,x_c]])

        if (
            (self.castling_p_white if self.board[y][x] > 0 else self.castling_p_black)
            and (self.rook_m['rook_white_castling'] if self.board[y][x] > 0 else self.rook_m['rook_black_castling'])
            and self.board[y][x] > 0
        ):
            if self.board[y][x-1] == 0 and self.board[y][x-2] == 0:
                new_board = copy.deepcopy(self.board)
                new_board[y][x-1] = self.board[y][x]
                new_board[y][x] = 0
                if self.is_check('white' if self.board[y][x] > 0 else 'black', new_board) != 'check':
                    list_k_move.append([[y,x],[y,x-2]])

        elif (
            (self.big_castling_p_white if self.board[y][x] > 0 else self.big_castling_p_black)
            and (self.rook_m['rook_big_white_castling'] if self.board[y][x] > 0 else self.rook_m['rook_big_black_castling'])
            and self.board[y][x] > 0
        ):
            if self.board[y][x+1] == 0 and self.board[y][x+2] == 0 and self.board[y][x+3] == 0:
                new_board = copy.deepcopy(self.board)
                new_board[y][x+1] = self.board[y][x] 
                new_board[y][x] = 0
                if self.is_check('white' if self.board[y][x] > 0 else 'black', new_board) != 'check':
                    list_k_move.append([[y,x],[y,x+2]])

        return list_k_move


    def list_all_legal_move(self, color):
        list_all_move = []

        for y_i in range(0,8):
            for x_i in range(0,8):
                if self.board[y_i][x_i] != 0 and ((color == 'white' and self.board[y_i][x_i] > 0) or (color == 'black' and self.board[y_i][x_i] < 0)):
                    n_move = []
                    if abs(self.board[y_i][x_i]) == 1:
                        n_move = self.list_pawn_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == 7:
                        n_move = self.list_king_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == 9:
                        n_move = self.list_queen_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == 5:
                        n_move = self.list_rook_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == 4:
                        n_move = self.list_bishop_move(y_i,x_i)
                    elif abs(self.board[y_i][x_i]) == 3:
                        n_move = self.list_knight_move(y_i,x_i)
                    if n_move:
                        for m in n_move:
                            new_board = copy.deepcopy(self.board)
                            new_board[m[0][0]][m[0][1]] = 0
                            new_board[m[1][0]][m[1][1]] = self.board[y_i][x_i]
                            if self.is_check(color, new_board) != 'check':
                                list_all_move.append(m)
                
        return list_all_move


    def is_checkmate(self, color, board_actual):
        if color in ('black','white'):
            if self.is_check(color, board_actual) == 'check':
                move = self.list_all_legal_move("black") if color == 'black' else self.list_all_legal_move("white")
                for m in move:
                    if self.board[m[0][0]][m[0][1]] not in (7,-7) or abs(m[0][1]-m[1][1]) != 2:
                        new_board = copy.deepcopy(board_actual)
                        new_board[m[0][0]][m[0][1]] = 0
                        new_board[m[1][0]][m[1][1]] = board_actual[m[0][0]][m[0][1]]
                        if self.is_check(color, new_board) != 'check':
                            return False
                        
                return True
            
        return False


    def validate_and_apply_move(self):
        result_valid_king = None
        result_valid_pion = None

        if self.is_checkmate(color='black',board_actual=self.board):
            print("✅---checkmate white win---✅")
            return 'checkmate'
        
        if self.is_checkmate(color='white',board_actual=self.board):
            print("✅---checkmate black win---✅")
            return 'checkmate'
        
        if self.info_move["start_value"] > 0:
            if self.is_check('black',self.board) != 'valid':
                print("🚫---invalid move black is in check---🚫")
                return
        else:
            if self.is_check('white',self.board) != 'valid':
                print("🚫---invalid move white is in check---🚫")
                return

        if self.info_move["start_value"] == 1 or self.info_move["start_value"] == -1:
            result_valid_pion = self.valid_pawn_move(self.info_move)
            if result_valid_pion not in {'valid', 'en passant'}:
                print("🚫---invalid move---🚫")
                return
            elif result_valid_pion == 'en passant':
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_end_coordinate"]] = 0
        elif self.info_move["start_value"] == 5 or self.info_move["start_value"] == -5:
            if self.valid_rook_move(self.info_move,debug=None) != 'valid':
                print("🚫---invalid move---🚫")
                return 
        elif self.info_move["start_value"] == 4 or self.info_move["start_value"] == -4:
            if self.valid_bishop_move(self.info_move) != 'valid':
                print("🚫---invalid move---🚫")
                return
        elif self.info_move["start_value"] == 3 or self.info_move["start_value"] == -3:
            if self.valid_knight_move(self.info_move) != 'valid':
                print("🚫---invalid move---🚫")
                return
        elif self.info_move["start_value"] == 7 or self.info_move["start_value"] == -7:
            result_valid_king = self.valid_king_move(self.info_move,castling_white=self.castling_p_white,castling_black=self.castling_p_black,big_castling_black=self.big_castling_p_black,big_castling_white=self.big_castling_p_white)
            if result_valid_king not in ['casting', 'big_casting','valid']:
                print("🚫---invalid move---🚫")
                return 
            elif result_valid_king == 'casting':
                print("casting !")
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-3] = 0
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]-1] = (5 if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else -5)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
            elif result_valid_king == 'big_casting':
                print("big casting !")
                new_board = copy.deepcopy(self.board)
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+4] = 0
                new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]+1] = (5 if self.board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] > 0 else -5)
                new_board[self.info_move["y_end_coordinate"]][self.info_move["x_end_coordinate"]] = self.info_move["start_value"]
            else:
                if self.info_move["start_value"] > 0:
                    self.castling_p_white, self.big_castling_p_white = (False, False)  
                else:
                    self.castling_p_black, self.big_castling_p_black = (False, False)   

        elif self.info_move["start_value"] == 9 or self.info_move["start_value"] == -9:
            if self.valid_queen_move(self.info_move) != 'valid':
                print("🚫---invalid move---🚫")
                return
        
        if result_valid_king not in ['big_casting', 'casting'] and result_valid_pion != 'en passant':
            new_board = copy.deepcopy(self.board)
            new_board[self.info_move["y_start_coordinate"]][self.info_move["x_start_coordinate"]] = 0
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
                print("🚫---invalid move black is in check---🚫")
                return
        else:
            if self.is_check('white',new_board) != 'valid':
                print("🚫---invalid move white is in check---🚫")
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
    

    def launch_partie(self, color="white", auto_promotion = "9"):
        if self.board[0][3] != 7:
            self.castling_p_white = False
            self.big_castling_p_white = False
        if self.board[0][0] != 5:
            self.rook_m['rook_white_castling'] = False
        if self.board[0][7] != 5:
            self.rook_m['rook_big_white_castling'] = False
        if self.board[7][3] != -7:
            self.castling_p_black = False
            self.big_castling_p_black = False
        if self.board[7][0] != -5:
            self.rook_m['rook_black_castling'] = False
        if self.board[7][7] != -5:
            self.rook_m['rook_big_black_castling'] = False

        self.auto_promotion = auto_promotion
        self.color_turn = color

        print("\033[1;32m╔═════════════ GAME START ═════════════╗")

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


    def play_move(self, all_move):
        print(f"> {all_move}")
        if not bool(re.match(r'^[a-h][1-8]\s[a-h][1-8]$', all_move)):
            print("🚫---invalid move---🚫 => valid move example: ✅--- e2 e4 ---✅")
            return 'illegal'
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


        if rep == 'checkmate':
            return 'checkmate'
        
        legal_white_move = self.list_all_legal_move("white")
        legal_black_move = self.list_all_legal_move("black")      

        if legal_white_move == [] and self.color_turn == "black":
            print("════════════════════════════════════════")
            print()
            self.board_print(True,'white',self.board)
            self.list_game_move.append(self.board)
            self.list_game_board_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            print()
            print("⏸ ═════════ Whites are pat ══════════ ⏸")
            return 'pat'
        
        if legal_black_move == [] and self.color_turn == "white":
            print("════════════════════════════════════════")
            print()
            self.board_print(True,'black',self.board)
            self.list_game_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
            self.list_game_board_move.append(self.board)
            print()
            print("⏸ ═════════ Blacks are pat ══════════ ⏸")
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
            return 'draw'
        
        if len(self.list_game_move) >= 50:
            no_capture_moves = all(self.board[move[1][0]][move[1][1]] == 0 for move in self.list_game_move[-50:])               

            if no_capture_moves:
                print("════════════════════════════════════════")
                print()
                if self.color_turn == "white":
                    self.board_print(True,'white',self.board)
                else:
                    self.board_print(True,'black',self.board)
                print()
                print("⏸ ═════ Draw by fifty-move rule ════ ⏸")
                return 'draw'
            
        def material_insufficiency(board_test):
            for row in board_test:
                for element in row:
                    if element not in [0, 7, -7]:
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
        if self.board[0][3] != 7:
            self.castling_p_white = False
            self.big_castling_p_white = False
        if self.board[0][0] != 5:
            self.rook_m['rook_white_castling'] = False
        if self.board[0][7] != 5:
            self.rook_m['rook_big_white_castling'] = False
        if self.board[7][3] != -7:
            self.castling_p_black = False
            self.big_castling_p_black = False
        if self.board[7][0] != -5:
            self.rook_m['rook_black_castling'] = False
        if self.board[7][7] != -5:
            self.rook_m['rook_big_black_castling'] = False

        self.auto_promotion = auto_promotion
        
        print("\033[1;32m╔═════════════ GAME START ═════════════╗")
        
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

        while True:
            for i in range(0,2):
                rep = None
                while rep != 'valid':
                    while True:
                        print()
                        all_move = input(">")
                        print()
                        if bool(re.match(r'^[a-h][1-8]\s[a-h][1-8]$', all_move)):
                            break
                        else:
                            print("🚫---invalid move---🚫 => valid move example: ✅--- e2 e4 ---✅")
                    
                    legal_white_move = self.list_all_legal_move("white")
                    legal_black_move = self.list_all_legal_move("black")


                    if legal_white_move == [] and i == 0:
                        print("════════════════════════════════════════")
                        print()
                        self.board_print(True,'white',self.board)
                        self.list_game_move.append(self.board)
                        self.list_game_board_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
                        print()
                        print("⏸ ═════════ Whites are pat ══════════ ⏸")
                        return 'pat'
                    if legal_black_move == [] and i == 1:
                        print("════════════════════════════════════════")
                        print()
                        self.board_print(True,'black',self.board)
                        self.list_game_move.append([[self.info_move['y_start_coordinate'], self.info_move['x_start_coordinate']],[self.info_move['y_end_coordinate'], self.info_move['x_end_coordinate']]])
                        self.list_game_board_move.append(self.board)
                        print()
                        print("⏸ ═════════ Blacks are pat ══════════ ⏸")
                        return 'pat'

                    self.info_move = self.give_move_info(all_move,debug=None)

                    if self.info_move == 'illegal':
                        print("🚫 ══════════ Invalid move ════════ 🚫")
                    elif (self.info_move['start_value'] > 0 and i == 1) or (self.info_move['start_value'] < 0 and i == 0):
                        print("🚫 ══════ It's not your turn ══════ 🚫")
                    else:
                        rep = self.validate_and_apply_move()

                    if rep == 'checkmate':
                        return 'checkmate'

                if self.check_repetition():
                    print("════════════════════════════════════════")
                    print()
                    if i == 0:
                        self.board_print(True,'white',self.board)
                    else:
                        self.board_print(True,'black',self.board)
                    print()
                    print("⏸ ═══════ Draw by repetition ═══════ ⏸")
                    return 'draw'
                
                if len(self.list_game_move) >= 50:
                    no_capture_moves = all(self.board[move[1][0]][move[1][1]] == 0 for move in self.list_game_move[-50:])               

                    if no_capture_moves:
                        print("════════════════════════════════════════")
                        print()
                        if i == 0:
                            self.board_print(True,'white',self.board)
                        else:
                            self.board_print(True,'black',self.board)
                        print()
                        print("⏸ ═════ Draw by fifty-move rule ════ ⏸")
                        return 'draw'

                def material_insufficiency(board_test):
                    for row in board_test:
                        for element in row:
                            if element not in [0, 7, -7]:
                                return False
                    return True

                if material_insufficiency(self.board):
                    print("════════════════════════════════════════")
                    print()
                    if i == 0:
                        self.board_print(True,'white',self.board) 
                    else:
                        self.board_print(True,'black',self.board)
                    print()
                    print("⏸ ══ Draw by insufficient material ═ ⏸")
                    return 'draw'
                
                if i == 0:
                    print()
                    print("⚫ ═══════════ Black play ═══════════ ⚫")
                    print()
                    self.board_print(True,'black',self.board)

                elif i == 1:
                    print()
                    print("⚪ ═══════════ White play ═══════════ ⚪")
                    print()
                    self.board_print(True,'white',self.board)    

if __name__ == "__main__":
    process = Chess()
    process.play(auto_promotion=False)  
