import re 
import copy
import time
import random
from collections import Counter

coordinate = {
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

piece_note = {
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

piece_note_style = {
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

piece = {
    0: "vide",
    1: "pion_blanc",
    5: "tour_blanc",
    4: "fou_blanc",
    3: "cavalier_blanc",
    9: "reine_blanc",
    7: "roi_blanc",
    -1: "pion_noir",
    -5: "tour_noir",
    -4: "fou_noir",
    -3: "cavalier_noir",
    -9: "reine_noir",
    -7: "roi_noir"
}

def check_repetition():
    serialized_boards = [tuple(tuple(row) for row in board) for board in list_game_board_move]
    counts = Counter(serialized_boards)
    for board, count in counts.items():
        if count >= 3:
            return True
    return False

def valid_pion_move(move,promotion):
  if move['end_value'] == 0: 
      if list_game_move:
        if (move['y_start_coordinate'] == 5 if move['start_value'] > 0 else move['y_start_coordinate'] == 3):
            if board[move['y_start_coordinate']][move['x_end_coordinate']] == (-1 if move['start_value'] > 0 else 1):
                print(list_game_move[-1])
                print([[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]])
                if move['x_end_coordinate'] == move['x_start_coordinate']+1:
                    if list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                        return('en passant')
                elif move['x_end_coordinate'] == move['x_start_coordinate']-1:
                    if list_game_move[-1] == [[(move['y_start_coordinate']+2 if move['start_value'] > 0 else move['y_start_coordinate']-2),move['x_end_coordinate']],[move['y_start_coordinate'],move['x_end_coordinate']]]:
                        return('en passant')
      if move['x_end_coordinate'] == move['x_start_coordinate']: 
          if move['name_piece_coor1'] == "pion_blanc":     
              if move['y_end_coordinate'] == move['y_start_coordinate'] + 1 or (move['y_end_coordinate'] == move['y_start_coordinate'] + 2 and move['y_start_coordinate'] == 1 and board[move['y_start_coordinate'] + 1][move['x_start_coordinate']] == 0):
                  if move['y_end_coordinate'] == 7:
                    if promotion:
                        print()
                        print("----promotion mode 👑----")
                        while True:
                            promotion_piece = input("enter a piece: the queen: 'Q', the rook: 'R', the bishop: 'B' and the knight 'N'> ") 
                            print()
                            if promotion_piece == 'Q':
                                move["start_value"] = 9
                                return('valid')
                                
                            if promotion_piece == 'R':
                                move["start_value"] = 5
                                return('valid')

                            if promotion_piece == 'B':
                                move["start_value"] = 4
                                return('valid')

                            if promotion_piece == 'N':
                                move["start_value"] = 3
                                return('valid')
                    else:
                        move["start_value"] = 9
                        return('valid')
                  return('valid')
              else:
                  return('illegal')

          if move['name_piece_coor1'] == "pion_noir":
            if move['y_start_coordinate'] == move['y_end_coordinate'] + 1 or (move['y_start_coordinate'] == move['y_end_coordinate'] + 2 and move['y_start_coordinate'] == 6 and board[move['y_start_coordinate'] - 1][move['x_start_coordinate']] == 0):
                if move['y_end_coordinate'] == 0:
                    if promotion:
                        print()
                        print("----promotion mode 👑----")
                        while True:
                            promotion_piece = input("enter a piece: the queen: 'Q', the rook: 'R', the bishop: 'B' and the knight 'N'> ") 
                            print()
                            if promotion_piece == 'Q':
                                move["start_value"] = -9
                                return('valid')
                                
                            if promotion_piece == 'R':
                                move["start_value"] = -5
                                return('valid')

                            if promotion_piece == 'B':
                                move["start_value"] = -4
                                return('valid')

                            if promotion_piece == 'N':
                                move["start_value"] = -3
                                return('valid')  
                    else:
                        move["start_value"] = -9
                        return('valid')
                return('valid')
            else:
                return('illegal')

          if move['name_piece_coor1'] != "pion_noir" and move['name_piece_coor1'] != "pion_blanc":
              return('illegal')
      else: 
          return('illegal')

  elif move['end_value'] != 0:
      if move['name_piece_coor1'] == "pion_blanc":
          if move['end_value'] > 0:
              return('illegal')
          if (move['x_end_coordinate'] == move['x_start_coordinate'] + 1 or move['x_end_coordinate'] == move['x_start_coordinate'] - 1) and move['y_end_coordinate'] == move['y_start_coordinate'] + 1:
                if move['y_end_coordinate'] == 7:
                    if promotion:
                        print()
                        print("----promotion mode 👑----")
                        while True:
                            promotion_piece = input("enter a piece: the queen: 'Q', the rook: 'R', the bishop: 'B' and the knight 'N'> ") 
                            print()
                            if promotion_piece == 'Q':
                                move["start_value"] = 9
                                return('valid')
                                
                            if promotion_piece == 'R':
                                move["start_value"] = 5
                                return('valid')

                            if promotion_piece == 'B':
                                move["start_value"] = 4
                                return('valid')

                            if promotion_piece == 'N':
                                move["start_value"] = 3
                                return('valid')
                    else:
                        move["start_value"] = 9
                        return('valid')
                return('valid')
          else:
              return('illegal')


      if move['name_piece_coor1'] == "pion_noir":
          if move['end_value'] < 0:
              return('illegal')
          if (move['x_end_coordinate'] == move['x_start_coordinate'] + 1 or move['x_end_coordinate'] == move['x_start_coordinate'] - 1) and move['y_end_coordinate'] == move['y_start_coordinate'] - 1:
            if move['y_end_coordinate'] == 0:
                if promotion:
                    print()
                    print("----promotion mode 👑----")
                    while True:
                        promotion_piece = input("enter a piece: the queen: 'Q', the rook: 'R', the bishop: 'B' and the knight 'N'> ") 
                        print()
                        if promotion_piece == 'Q':
                            move["start_value"] = -9
                            return('valid')
                            
                        if promotion_piece == 'R':
                            move["start_value"] = -5
                            return('valid')

                        if promotion_piece == 'B':
                            move["start_value"] = -4
                            return('valid')

                        if promotion_piece == 'N':
                            move["start_value"] = -3
                            return('valid')  
                else:
                    move["start_value"] = -9
                    return('valid')
            return('valid')
          else:
            return('illegal')
      return

def valid_bishop_move(move):
    if (move['name_piece_coor1'] in ('fou_noir,reine_noir') and move['end_value'] < 0) or(move['name_piece_coor1'] in ('fou_blanc','reine_blanc') and move['end_value'] > 0):
        return('illegal')
    
    if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == abs(move['y_start_coordinate'] - move['y_end_coordinate']):
        if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1:
            return 'valid'
        
        x = 1 if move['x_start_coordinate'] < move['x_end_coordinate'] else -1
        y = 1 if move['y_start_coordinate'] < move['y_end_coordinate'] else -1

        x_start_coordinate = move['x_start_coordinate'] + x
        y_start_coordinate = move['y_start_coordinate'] + y

        while x_start_coordinate != move['x_end_coordinate']:
            if board[y_start_coordinate][x_start_coordinate] != 0:
                    return('illegal')
            x_start_coordinate += x
            y_start_coordinate += y
                 
        return('valid')
    else:
        return('illegal')

def valid_rook_move(move, debug=None):
    global rook_m
    if move['end_value'] == 0 or (move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0):
        if move['y_start_coordinate'] == move['y_end_coordinate']:
            for i in range(min(move['x_start_coordinate'], move['x_end_coordinate']), max(move['x_start_coordinate'], move['x_end_coordinate'])):
                if board[move['y_start_coordinate']][i] != 0 and [i] != [move['x_start_coordinate']] and [i] != [move['x_end_coordinate']]:
                    return('illegal')
            if move['start_value'] == 5:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                    rook_m['rook_white_castling'] = False
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                    rook_m['rook_big_white_castling'] = False
            elif move['start_value'] == -5:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                    rook_m['rook_black_castling'] = False
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                    rook_m['rook_big_black_castling'] = False
            return('valid')
        elif move['x_start_coordinate'] == move['x_end_coordinate']:
            for i in range(min(move['y_start_coordinate'], move['y_end_coordinate']), max(move['y_start_coordinate'], move['y_end_coordinate'])):
                if board[i][move['x_start_coordinate']] != 0 and [i] != [move['y_start_coordinate']] and [i] != [move['y_end_coordinate']]:
                    return('illegal')
            if move['start_value'] == 5:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 0:
                    rook_m['rook_big_white_castling'] = False
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 0:
                    rook_m['rook_white_castling'] = False
            elif move['start_value'] == -5:
                if move['x_start_coordinate'] == 0 and move['y_start_coordinate'] == 7:
                    rook_m['rook_big_black_castling'] = False
                elif move['x_start_coordinate'] == 7 and move['y_start_coordinate'] == 7:
                    rook_m['rook_black_castling'] = False
            return('valid')
    return 'illegal'

def valid_knight_move(move):
    if move['end_value'] == 0 or ((move['end_value'] > 0 and move['start_value'] < 0) or (move['end_value'] < 0 and move['start_value'] > 0)): 
        if abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 1:
            return('valid')
        elif abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 2:
            return('valid')
    else:
        return('illegal')

def valid_king_move(move, castling_white=False, castling_black=False,big_castling_black=False,big_castling_white=False):
    if move['end_value'] == 0 and (castling_white if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else castling_black) and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 0 and board[move['y_end_coordinate']][move['x_end_coordinate']-1] in (-5,5):
        if is_check(('white' if board[move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else 'black'),board) != 'check':
            if board[move['y_end_coordinate']][move['x_end_coordinate']+1] == 0:
                new_board = copy.deepcopy(board)
                new_board[move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
                new_board[move["y_start_coordinate"]][info_move["x_start_coordinate"]-1] = board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                if is_check(('white' if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                    if (rook_m['rook_white_castling'] == True if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else rook_m['rook_black_castling'] == True):
                        return 'casting'
    elif move['end_value'] == 0 and (big_castling_white if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else big_castling_black) and abs(move['x_start_coordinate'] - move['x_end_coordinate']) == 2 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) == 0 and board[move['y_end_coordinate']][move['x_end_coordinate']+2] in (-5,5):
        if is_check(('white' if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else 'black'),board) != 'check':
            if board[move['y_end_coordinate']][move['x_end_coordinate']+1] == 0 and board[move['y_end_coordinate']][move['x_end_coordinate']-1] == 0:
                new_board = copy.deepcopy(board)
                new_board[move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
                new_board[move["y_start_coordinate"]][info_move["x_start_coordinate"]+1] = board[move["y_start_coordinate"]][move["x_start_coordinate"]]
                if is_check(('white' if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else 'black'), new_board) != 'check':
                    if (rook_m['rook_big_white_castling'] == True if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else rook_m['rook_big_black_castling'] == True):
                        return 'big_casting'
    if move['end_value'] == 0 or ((move['end_value'] < 0 and move['start_value'] > 0) or (move['end_value'] > 0 and move['start_value'] < 0)): 
        if abs(move['x_start_coordinate'] - move['x_end_coordinate']) <= 1 and abs(move['y_start_coordinate'] - move['y_end_coordinate']) <= 1:
            return('valid')
        else:
            return('illegal')
    else:
        return('illegal')

def give_move_info(all_move,debug=None):
    try:
        all_move = all_move.split(" ")

        start_move = all_move[0]
        end_move = all_move[1]


        x_start_coordinate = start_move[:1]
        y_start_coordinate = int(start_move[1:]) - 1


        if x_start_coordinate in coordinate:
            x_start_coordinate = int(coordinate[x_start_coordinate]) - 1

        else:
            return('illegal')

        start_value = board[y_start_coordinate][x_start_coordinate]

        if start_value == 0:
            return('illegal')

        x_end_coordinate = end_move[:1]
        y_end_coordinate = int(end_move[1:]) - 1

        if x_end_coordinate in coordinate:
            x_end_coordinate = int(coordinate[x_end_coordinate]) - 1
        else:
            print("invalide coordinate invalide")
            return('illegal')

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

        return(move)
    except:
        return('illegal')

def valid_queen_move(move):
    if valid_rook_move(move) == 'valid' or valid_bishop_move(move) == 'valid':
        return('valid')
    else:
        return('illegal')

def board_print(style,color,board):
    if style:
        board_rendu = [list(reversed([piece_note_style[e] for e in r])) for r in board] if color == 'white' else [[piece_note_style[e] for e in r] for r in board]
    else:    
        board_rendu = [list(reversed([piece_note[e] for e in r])) for r in board]
    if color == 'white':
        board_rendu.reverse()
    for row in board_rendu:
        print(row)

def find_piece(board,piece):
    for x in range(len(board)):
        for y in range(len(board[x])):
            if board[x][y] == piece:
                return (y+1,x+1)

def is_check(color,board_actual):
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]

    if color == 'white':
        white_king_position = find_piece(board_actual,7)

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
        black_king_position = find_piece(board_actual,-7)
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

def list_pion_move(y,x):
    list_p_move = []
    direction = 1 if board[y][x] == 1 else -1 
    if board[y + direction][x] == 0:
        list_p_move.append([[y,x],[y + direction, x]])
        if (y == 1 and direction == 1) or (y == 6 and direction == -1):
            if board[y + 2 * direction][x] == 0:
                list_p_move.append([[y,x],[y + 2 * direction, x]])
    if x + 1 <= 7 and board[y + direction][x + 1] * board[y][x] < 0:
        list_p_move.append([[y,x],[y + direction, x + 1]])
    if x - 1 >= 0 and board[y + direction][x - 1] * board[y][x] < 0: 
        list_p_move.append([[y,x],[y + direction, x - 1]])
    
    return list_p_move

def list_knight_move(y,x):
    list_k_move = []
    knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),(1, 2), (1, -2), (-1, 2), (-1, -2)]
    if board[y][x] in (3,-3):
        for e in knight_moves:
            if y+e[0] >= 0 and y+e[0] <= 7 and x+e[1] >= 0 and x+e[1] <= 7:
                if (board[y+e[0]][x+e[1]] <= 0 if board[y][x] == 3 else board[y+e[0]][x+e[1]] >= 0):
                    list_k_move.append([[y,x],[y+e[0],x+e[1]]])
    return list_k_move

def list_bishop_move(y,x):
    list_b_move = []
    bishop_move = [(1,1),(-1,1),(-1,-1),(1,-1)]
    if board[y][x] in (4,-4):
        for e in bishop_move:
            y_c = y + e[0]
            x_c = x + e[1]
            while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == 0:
                list_b_move.append([[y,x],[y_c,x_c]])
                y_c = y_c + e[0]
                x_c = x_c + e[1]
            if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == 4 else board[y_c][x_c] > 0):
                list_b_move.append([[y,x],[y_c,x_c]])
    return list_b_move

def list_rook_move(y,x):
    list_r_move = []
    rook_move = [(0,1),(0,-1),(-1,0),(1,0)]
    if board[y][x] in (5,-5):
        for e in rook_move:
            y_c = y + e[0]
            x_c = x + e[1]
            while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == 0:
                list_r_move.append([[y,x],[y_c,x_c]])
                y_c = y_c + e[0]
                x_c = x_c + e[1]
            if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == 5 else board[y_c][x_c] > 0):
                list_r_move.append([[y,x],[y_c,x_c]])       
    return list_r_move

def list_queen_move(y,x):
    list_q_move = []
    queen_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]
    if board[y][x] in (9,-9):
        for e in queen_move:
            y_c = y + e[0]
            x_c = x + e[1]
            while y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and board[y_c][x_c] == 0:
                list_q_move.append([[y,x],[y_c,x_c]])
                y_c = y_c + e[0]
                x_c = x_c + e[1]
            if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] < 0 if board[y][x] == 9 else board[y_c][x_c] > 0):
                list_q_move.append([[y,x],[y_c,x_c]])       
    return list_q_move

def list_king_move(y,x):
    list_k_move = []
    king_move = [(1,1),(-1,1),(-1,-1),(1,-1),(0,1),(0,-1),(-1,0),(1,0)]
    if board[y][x] in (7,-7):
        for e in king_move:
            y_c = y + e[0]
            x_c = x + e[1]
            if y_c >= 0 and y_c <= 7 and x_c >= 0 and x_c <= 7 and (board[y_c][x_c] >= 0 if board[y][x] == -7 else board[y_c][x_c] <= 0):
                list_k_move.append([[y,x],[y_c,x_c]])
    if (castling_p_white if board[y][x] > 0 else castling_p_black) and (rook_m['rook_white_castling'] if board[y][x] > 0 else rook_m['rook_black_castling']) and board[y][x] > 0:
        if board[y][x-1] == 0 and board[y][x-2] == 0:
            new_board = copy.deepcopy(board)
            new_board[y][x-1] = board[y][x]
            new_board[y][x] = 0
            if is_check('white' if board[y][x] > 0 else 'black', new_board) != 'check':
                list_k_move.append([[y,x],[y,x-2]])
    elif (big_castling_p_white if board[y][x] > 0 else big_castling_p_black) and (rook_m['rook_big_white_castling'] if board[y][x] > 0 else rook_m['rook_big_black_castling']) and board[y][x] > 0:
        if board[y][x+1] == 0 and board[y][x+2] == 0 and board[y][x+3] == 0:
            new_board = copy.deepcopy(board)
            new_board[y][x+1] = board[y][x] 
            new_board[y][x] = 0
            if is_check('white' if board[y][x] > 0 else 'black', new_board) != 'check':
                list_k_move.append([[y,x],[y,x+2]])
    return list_k_move

def list_all_legal_move():
    global board
    list_all_move = []
    for y_i in range(0,8):
        for x_i in range(0,8):
            if board[y_i][x_i] != 0:
                n_move = []
                if board[y_i][x_i] in (1,-1):
                    n_move = list_pion_move(y_i,x_i)
                elif board[y_i][x_i] in (7,-7):
                    n_move = list_king_move(y_i,x_i)
                elif board[y_i][x_i] in (9,-9):
                    n_move = list_queen_move(y_i,x_i)
                elif board[y_i][x_i] in (5,-5):
                    n_move = list_rook_move(y_i,x_i)
                elif board[y_i][x_i] in (4,-4):
                    n_move = list_bishop_move(y_i,x_i)
                elif board[y_i][x_i] in (3,-3):
                    n_move = list_knight_move(y_i,x_i)
                if n_move:
                    for m in n_move:
                        new_board = copy.deepcopy(board)
                        new_board[m[0][0]][m[0][1]] = 0
                        new_board[m[1][0]][m[1][1]] = board[y_i][x_i]
                        if is_check('white' if board[y_i][x_i] > 0 else 'black', new_board) != 'check':
                            list_all_move.append(m)
    return list_all_move

def list_all_legal_white_move():
    global board
    list_all_move = []
    for y_i in range(0,8):
        for x_i in range(0,8):
            if board[y_i][x_i] != 0:
                n_move = []
                if board[y_i][x_i] == 1:
                    n_move = list_pion_move(y_i,x_i)
                elif board[y_i][x_i] == 7:
                    n_move = list_king_move(y_i,x_i)
                elif board[y_i][x_i] == 9:
                    n_move = list_queen_move(y_i,x_i)
                elif board[y_i][x_i] == 5:
                    n_move = list_rook_move(y_i,x_i)
                elif board[y_i][x_i] == 4:
                    n_move = list_bishop_move(y_i,x_i)
                elif board[y_i][x_i] == 3:
                    n_move = list_knight_move(y_i,x_i)
                if n_move:
                    for m in n_move:
                        new_board = copy.deepcopy(board)
                        new_board[m[0][0]][m[0][1]] = 0
                        new_board[m[1][0]][m[1][1]] = board[y_i][x_i]
                        if is_check('white', new_board) != 'check':
                            list_all_move.append(m)
    return list_all_move

def list_all_legal_black_move():
    global board
    list_all_move = []
    for y_i in range(0,8):
        for x_i in range(0,8):
            if board[y_i][x_i] != 0:
                n_move = []
                if board[y_i][x_i] == -1:
                    n_move = list_pion_move(y_i,x_i)
                elif board[y_i][x_i] == -7:
                    n_move = list_king_move(y_i,x_i)
                elif board[y_i][x_i] == -9:
                    n_move = list_queen_move(y_i,x_i)
                elif board[y_i][x_i] == -5:
                    n_move = list_rook_move(y_i,x_i)
                elif board[y_i][x_i] == -4:
                    n_move = list_bishop_move(y_i,x_i)
                elif board[y_i][x_i] == -3:
                    n_move = list_knight_move(y_i,x_i)
                if n_move:
                    for m in n_move:
                        new_board = copy.deepcopy(board)
                        new_board[m[0][0]][m[0][1]] = 0
                        new_board[m[1][0]][m[1][1]] = board[y_i][x_i]

                        if is_check('black', new_board) != 'check':
                            list_all_move.append(m)
    return list_all_move

def is_checkmate(color, board_actual):
    if color in ('black','white'):
        if is_check(color, board_actual) == 'check':
            move = list_all_legal_black_move() if color == 'black' else list_all_legal_white_move()
            for m in move:
                if board[m[0][0]][m[0][1]] not in (7,-7) or abs(m[0][1]-m[1][1]) != 2:
                    new_board = copy.deepcopy(board_actual)
                    new_board[m[0][0]][m[0][1]] = 0
                    new_board[m[1][0]][m[1][1]] = board_actual[m[0][0]][m[0][1]]
                    if is_check(color, new_board) != 'check':
                        return False
            return True
    return False

def play_move():
    global board
    global castling_p_white,castling_p_black,big_castling_p_white,big_castling_p_black,list_game_move
    result_valid_king = None
    result_valid_pion = None

    if is_checkmate(color='black',board_actual=board):
        print("✅---checkmate white win---✅")
        return 'checkmate'
    if is_checkmate(color='white',board_actual=board):
        print("✅---checkmate black win---✅")
        return 'checkmate'
    if info_move["start_value"] > 0:
        if is_check('black',board) != 'valid':
            print("🚫---invalide move black is in check---🚫")
            return
    else:
        if is_check('white',board) != 'valid':
            print("🚫---invalide move white is in check---🚫")
            return

    if info_move["start_value"] == 1 or info_move["start_value"] == -1:
        result_valid_pion = valid_pion_move(info_move,False)
        if result_valid_pion != 'valid' and result_valid_pion != 'en passant':
            print("🚫---invalide move---🚫")
            return
        elif result_valid_pion == 'en passant':
            new_board = copy.deepcopy(board)
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
            new_board[info_move["y_end_coordinate"]][info_move["x_end_coordinate"]] = info_move["start_value"]
            new_board[info_move["y_start_coordinate"]][info_move["x_end_coordinate"]] = 0
    elif info_move["start_value"] == 5 or info_move["start_value"] == -5:
        if valid_rook_move(info_move,debug=None) != 'valid':
            print("🚫---invalide move---🚫")
            return 
    elif info_move["start_value"] == 4 or info_move["start_value"] == -4:
        if valid_bishop_move(info_move) != 'valid':
            print("🚫---invalide move---🚫")
            return
    elif info_move["start_value"] == 3 or info_move["start_value"] == -3:
        if valid_knight_move(info_move) != 'valid':
            print("🚫---invalide move---🚫")
            return
    elif info_move["start_value"] == 7 or info_move["start_value"] == -7:
        result_valid_king = valid_king_move(info_move,castling_white=castling_p_white,castling_black=castling_p_black,big_castling_black=big_castling_p_black,big_castling_white=big_castling_p_white)
        if result_valid_king not in ['casting', 'big_casting','valid']:
            print("🚫---invalide move---🚫")
            return 
        elif result_valid_king == 'casting':
            print("casting !")
            new_board = copy.deepcopy(board)
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]-3] = 0
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]-1] = (5 if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else -5)
            new_board[info_move["y_end_coordinate"]][info_move["x_end_coordinate"]] = info_move["start_value"]
        elif result_valid_king == 'big_casting':
            print("big casting !")
            new_board = copy.deepcopy(board)
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]+4] = 0
            new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]+1] = (5 if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0 else -5)
            new_board[info_move["y_end_coordinate"]][info_move["x_end_coordinate"]] = info_move["start_value"]
        else:
            if info_move["start_value"] > 0:
                castling_p_white, big_castling_p_white = (False, False)  
            else:
                castling_p_black, big_castling_p_black = (False, False)   

    elif info_move["start_value"] == 9 or info_move["start_value"] == -9:
        if valid_queen_move(info_move) != 'valid':
            print("🚫---invalide move---🚫")
            return
    
    if result_valid_king not in ['big_casting', 'casting'] and result_valid_pion != 'en passant':
        new_board = copy.deepcopy(board)
        new_board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] = 0
        new_board[info_move["y_end_coordinate"]][info_move["x_end_coordinate"]] = info_move["start_value"]
    elif result_valid_king  != 'big_casting':
        if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0: 
            castling_p_white = False
        else:
            castling_p_black = False
    else:
        if board[info_move["y_start_coordinate"]][info_move["x_start_coordinate"]] > 0: 
            big_castling_p_white = False
        else:
            big_castling_p_black = False


    if info_move["start_value"] < 0:
        if is_check('black',new_board) != 'valid':
            print("🚫---invalide move black is in check---🚫")
            return
    else:
        if is_check('white',new_board) != 'valid':
            print("🚫---invalide move white is in check---🚫")
            return
    
    board = copy.deepcopy(new_board)
    
    if is_checkmate(color='black',board_actual=board):
        print("✅---checkmate white win---✅")
        print()
        list_game_move.append(board)
        list_game_board_move.append([[info_move['y_start_coordinate'],info_move["x_start_coordinate"]],[info_move['y_end_coordinate'], info_move['x_end_coordinate']]])
        board_print(True,'black',board)
        return 'checkmate'
    if is_checkmate(color='white',board_actual=board):
        print("✅---checkmate black win---✅")
        print()
        list_game_move.append(board)
        list_game_board_move.append([[info_move['y_start_coordinate'], info_move['x_start_coordinate']],[info_move['y_end_coordinate'], info_move['x_end_coordinate']]])
        board_print(True,'white',board)
        return 'checkmate'

    print("✅---valide move---✅")
    print()
    list_game_move.append([[info_move['y_start_coordinate'], info_move['x_start_coordinate']],[info_move['y_end_coordinate'], info_move['x_end_coordinate']]])
    list_game_board_move.append(board)
    return 'valid'

def play():
    global castling_p_white,castling_p_black,big_castling_p_white,big_castling_p_black,info_move,rook_m,list_game_move,list_game_board_move
    global board
    castling_p_white = True
    castling_p_black = True 
    big_castling_p_white = True 
    big_castling_p_black = True
    rook_m = {'rook_white_castling' : True, 'rook_black_castling' : True, 'rook_big_white_castling' : True, 'rook_big_black_castling' : True}
    list_game_move =[]
    list_game_board_move =[]

    board = [
        [ 5, 3, 4, 7, 9, 4, 3, 5],
        [ 1, 1, 1, 1, 1, 1, 1, 1],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 0, 0, 0],
        [-1,-1,-1,-1,-1,-1,-1,-1],
        [-5,-3,-4,-7,-9,-4,-3,-5]
    ]

    if board[0][3] != 7:
        castling_p_white = False
        big_castling_p_white = False
    if board[0][0] != 5:
        rook_m['rook_white_castling'] = False
    if board[0][7] != 5:
        rook_m['rook_big_white_castling'] = False
    if board[7][3] != -7:
        castling_p_black = False
        big_castling_p_black = False
    if board[7][0] != -5:
        rook_m['rook_black_castling'] = False
    if board[7][7] != -5:
        rook_m['rook_big_black_castling'] = False

    print(list_all_legal_white_move())
    print(len(list_all_legal_white_move()))
    print("🌟 Game start 🌟")
    print()
    print("⚪---white play---⚪")
    print()
    board_print(True,'white',board)
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
                        print("🚫---invalide move---🚫 => valide move example: ✅--- e2 e4 ---✅")
                
                legal_white_move = list_all_legal_white_move()
                legal_black_move = list_all_legal_black_move()


                if legal_white_move == [] and i == 0:
                    print("⬛---whites are pat---⬛")
                    print()
                    board_print(True,'white',board)
                    list_game_move.append(board)
                    list_game_board_move.append([[info_move['y_start_coordinate'], info_move['x_start_coordinate']],[info_move['y_end_coordinate'], info_move['x_end_coordinate']]])
                    return 'pat'
                if legal_black_move == [] and i == 1:
                    print("⬛---blacks are pat---⬛")
                    print()
                    board_print(True,'black',board)
                    list_game_move.append([[info_move['y_start_coordinate'], info_move['x_start_coordinate']],[info_move['y_end_coordinate'], info_move['x_end_coordinate']]])
                    list_game_board_move.append(board)
                    print()
                    print("Game move:",list_game_move)
                    return 'pat'

                move = random.choice(list_all_legal_white_move()) if i == 0 else random.choice(list_all_legal_black_move())
                all_move = f"{coordinate[move[0][1]+1]}{move[0][0]+1} {coordinate[move[1][1]+1]}{move[1][0]+1}"   
                
                print(all_move,move)
                
                info_move = give_move_info(all_move,debug=None)
                if info_move == 'illegal':
                    print("🚫---invalide move---🚫")
                elif (info_move['start_value'] > 0 and i == 1) or (info_move['start_value'] < 0 and i == 0):
                    print("🚫---It's not your turn ---🚫")
                else:
                    rep = play_move()

                if rep == 'checkmate':
                    return 'checkmate'

            if check_repetition():
                if i == 0:
                    board_print(True,'white',board)
                else:
                    board_print(True,'black',board)
                print("⏸---Draw by repetition---⏸")
                return 'draw'
            
            if len(list_game_move) >= 50:
                no_capture_moves = all(board[move[1][0]][move[1][1]] == 0 for move in list_game_move[-50:])               

                if no_capture_moves:
                    if i == 0:
                        board_print(True,'white',board)
                    else:
                        board_print(True,'black',board)
                    print("⏸---Draw by fifty-move rule---⏸")
                    return 'draw'

            def material_insufficiency(board):
                for row in board:
                    for element in row:
                        if element not in [0, 7, -7]:
                            return False
                return True

            if material_insufficiency(board):
                print("⏸---Draw by insufficient material---⏸")
                print()
                if i == 0:
                    board_print(True,'white',board) 
                else:
                    board_print(True,'black',board)
                return 'draw'
                
            if i == 0:
                print()
                print("⚫---black play---⚫")
                print()
                board_print(True,'black',board)

            elif i == 1:
                print()
                print("⚪---white play---⚪")
                print()
                board_print(True,'white',board)    

play()
                
