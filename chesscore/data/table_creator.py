"""
This file isn't really optimized, but it doesn't matter.
"""

import json

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from constants import *


def get_bit(bb, i):
    return (bb >> i) & 1


def all_combinations(obj):
    return [[]] if len(obj) == 0 else [[x] + e for x in (0, 1) for e in all_combinations(obj[1:])]


def rook_attacks_table(square, occ_real):
    attacks = 0

    for i_sq in range(square + 8, 64, 8):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break
    
    for i_sq in range(square - 8, -1, -8):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break
    
    for i_sq in range(square + 1, square + 8 - (square % 8), 1):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break
    
    for i_sq in range(square - 1, square - (square % 8) - 1, -1):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break

    return attacks


def bishop_attacks_table(square, occ_real):
    attacks = 0

    for i_sq in range(square + 9, square + 9 * (min(7 - (square // 8), 7 - (square % 8)) + 1), 9):
    
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break

    for i_sq in range(square + 7, square + 7 * (min(7 - square // 8, square % 8) + 1), 7):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break
    
    for i_sq in range(square - 7, square - 7 * (min(square // 8, 7 - square % 8) + 1), -7):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break
    
    for i_sq in range(square - 9, square - 9 * (min(square // 8, square % 8) + 1), -9):
        attacks = attacks | 1 << i_sq
        if (occ_real >> i_sq) & 1:
            break

    return attacks


with open("data/magic_bitboards.json", "r") as f:
    magic_data = json.load(f)

ROOK_MASK = [int(magic_data["rook_magics"][i]["mask"], 16) for i in range(64)]
ROOK_MAGIC = [int(magic_data["rook_magics"][i]["magic"], 16) for i in range(64)]
ROOK_SHIFT = [magic_data["rook_magics"][i]["shift"] for i in range(64)]
ROOK_NBITS = [magic_data["rook_magics"][i]["n_bits"] for i in range(64)]

BISHOP_MASK = [int(magic_data["bishop_magics"][i]["mask"], 16) for i in range(64)]
BISHOP_MAGIC = [int(magic_data["bishop_magics"][i]["magic"], 16) for i in range(64)]
BISHOP_SHIFT = [magic_data["bishop_magics"][i]["shift"] for i in range(64)]
BISHOP_NBITS = [magic_data["bishop_magics"][i]["n_bits"] for i in range(64)]


ROOK_TABLE = []

for square in range(64):
    ROOK_TABLE.append([0] * 2**ROOK_NBITS[square])

    rank = square // 8
    file = square % 8

    top_len = 7 - rank
    top = all_combinations([0] * top_len)
    
    list_top_square = []
    for top_e in top:
        mask = 0
        for i in range(len(top_e)):
            if top_e[i]:
                mask |= (1 << ((rank + 1 + i) * 8 + file))
        list_top_square.append(mask)

    bottom_len = rank
    bottom = all_combinations([0] * bottom_len)

    list_bottom_square = []
    for bottom_e in bottom:
        mask = 0
        for i in range(len(bottom_e)):
            if bottom_e[i]:
                mask |= (1 << ((rank - 1 - i) * 8 + file))
        list_bottom_square.append(mask)

    left_len = file
    left = all_combinations([0] * left_len)

    list_left_square = []
    for left_e in left:
        mask = 0
        for i in range(len(left_e)):
            if left_e[i]:
                mask |= (1 << (rank * 8 + (file - 1 - i)))
        list_left_square.append(mask)
    
    right_len = 7 - file
    right = all_combinations([0] * right_len)

    list_right_square = []
    for right_e in right:
        mask = 0
        for i in range(len(right_e)):
            if right_e[i]:
                mask |= (1 << (rank * 8 + (file + 1 + i)))
        list_right_square.append(mask)

    blocker_combinations = []

    for top_e in list_top_square:
        for bottom_e in list_bottom_square:
            for left_e in list_left_square:
                for right_e in list_right_square:
                    blocker_combinations.append(top_e | bottom_e | left_e | right_e) 

    for occ_rel in blocker_combinations:
        idx = (((occ_rel & ROOK_MASK[square]) * ROOK_MAGIC[square]) & U64) >> ROOK_SHIFT[square]
        ROOK_TABLE[square][idx] = rook_attacks_table(square, occ_rel)
        

BISHOP_TABLE = [] 

for square in range(64):
    BISHOP_TABLE.append([0] * 2**BISHOP_NBITS[square])

    rank = square // 8
    file = square % 8

    top_len = 7 - rank
    bottom_len = rank
    left_len = file
    right_len = 7 - file

    top_right_len = min(top_len, right_len)
    top_right = all_combinations([0] * top_right_len)
    
    list_top_right_square = []
    for top_right_e in top_right:
        mask = 0
        for i in range(len(top_right_e)):
            if top_right_e[i]:
                mask |= (1 << ((rank + 1 + i) * 8 + file + i + 1))

        list_top_right_square.append(mask)

    top_left_len = min(top_len, left_len)
    top_left = all_combinations([0] * top_left_len)
    
    list_top_left_square = []
    for top_left_e in top_left:
        mask = 0
        for i in range(len(top_left_e)):
            if top_left_e[i]:
                mask |= (1 << ((rank + 1 + i) * 8 + file - i - 1))

        list_top_left_square.append(mask)

    bottom_right_len = min(bottom_len, right_len)
    bottom_right = all_combinations([0] * bottom_right_len)
    
    list_bottom_right_square = []
    for bottom_right_e in bottom_right:
        mask = 0
        for i in range(len(bottom_right_e)):
            if bottom_right_e[i]:
                mask |= (1 << ((rank - 1 - i) * 8 + file + i + 1))

        list_bottom_right_square.append(mask)

    bottom_left_len = min(bottom_len, left_len)
    bottom_left = all_combinations([0] * bottom_left_len)
    
    list_bottom_left_square = []
    for bottom_left_e in bottom_left:
        mask = 0
        for i in range(len(bottom_left_e)):
            if bottom_left_e[i]:
                mask |= (1 << ((rank - 1 - i) * 8 + file - i - 1))

        list_bottom_left_square.append(mask)


    blocker_combinations = []

    for tr in list_top_right_square:
        for tl in list_top_left_square:
            for br in list_bottom_right_square:
                for bl in list_bottom_left_square:
                    blocker_combinations.append(tr | tl | br | bl)

    for occ_rel in blocker_combinations:
        idx = (((occ_rel & BISHOP_MASK[square]) * BISHOP_MAGIC[square]) & U64) >> BISHOP_SHIFT[square]
        BISHOP_TABLE[square][idx] = bishop_attacks_table(square, occ_rel)


KNIGHT_TABLE = []

for square in range(64):
    rank = square // 8
    file = square % 8

    attacks = 0
     
    knight_moves = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]
    
    for move in knight_moves:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]


    KNIGHT_TABLE.append(attacks)


KING_TABLE = []

for square in range(64):
    rank = square // 8
    file = square % 8

    attacks = 0
    
    king_move = ((1, 1), (-1, 1), (-1, -1), (1, -1),
                 (0, 1), (0, -1), (-1, 0), (1, 0))
    
    for move in king_move:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]

    KING_TABLE.append(attacks)


PAWN_TABLE = [[],[]]

for square in range(0, 64): #Normally 8 ≤ sq ≤ 55, but it doesn't matter.
    rank = square // 8
    file = square % 8

    attacks = 0

    white_pawn_move = ((1, 1), (-1, 1))

    for move in white_pawn_move:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]

    PAWN_TABLE[WHITE_INDEX].append(attacks)

    attacks = 0

    black_pawn_move = ((1, -1), (-1, -1))

    for move in black_pawn_move:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]

    PAWN_TABLE[BLACK_INDEX].append(attacks)

INVERTED_PAWN_TABLE = [[],[]]

for square in range(0, 64):
    rank = square // 8
    file = square % 8

    attacks = 0

    white_pawn_move = ((1, -1), (-1, -1))

    for move in white_pawn_move:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]

    INVERTED_PAWN_TABLE[WHITE_INDEX].append(attacks)

    attacks = 0

    black_pawn_move = ((1, 1), (-1, 1))

    for move in black_pawn_move:
        if (0 <= rank + move[1] <= 7) and (0 <= file + move[0] <= 7):
            attacks |= 1 << (rank + move[1])*8 + file + move[0]

    INVERTED_PAWN_TABLE[BLACK_INDEX].append(attacks)


magic_data["rook_table"] = ROOK_TABLE
magic_data["bishop_table"] = BISHOP_TABLE
magic_data["knight_table"] = KNIGHT_TABLE
magic_data["king_table"] = KING_TABLE
magic_data["pawn_table"] = PAWN_TABLE
magic_data["inverted_pawn_table"] = INVERTED_PAWN_TABLE

with open("data/magic_bitboards.json", "w") as f:
    json.dump(magic_data, f)


# Test

import chess_game

b = chess_game.Board()
b.load_board("6k1/p4r1p/3nQ3/6p1/2P1PR1P/1Pb1B3/N2q2P1/6K1 b - - 0 31")

chess_game.ChessDisplay.print_board(WHITE, b)
print()

#rook

rook_square = 29

occ_rel = ROOK_MASK[rook_square] & b.all_board_occupied_squares

idx = ((occ_rel * ROOK_MAGIC[rook_square]) & U64) >> ROOK_SHIFT[rook_square]

print(f"Test result (rook): {ROOK_TABLE[rook_square][idx] == rook_attacks_table(rook_square, occ_rel)}")


#bishop

bishop_square = 20

occ_rel = BISHOP_MASK[bishop_square] & b.all_board_occupied_squares

idx = ((occ_rel * BISHOP_MAGIC[bishop_square]) & U64) >> BISHOP_SHIFT[bishop_square]

print(f"Test result (bishop): {BISHOP_TABLE[bishop_square][idx] == bishop_attacks_table(bishop_square, occ_rel)}")


#queen

queen_square = 44

rook_occ_rel = ROOK_MASK[queen_square] & b.all_board_occupied_squares

bishop_occ_rel = BISHOP_MASK[queen_square] & b.all_board_occupied_squares

rook_idx = ((rook_occ_rel * ROOK_MAGIC[queen_square]) & U64) >> ROOK_SHIFT[queen_square]

bishop_idx = ((bishop_occ_rel * BISHOP_MAGIC[queen_square]) & U64) >> BISHOP_SHIFT[queen_square]

print(f"Test result (queen): {(BISHOP_TABLE[queen_square][bishop_idx]|ROOK_TABLE[queen_square][rook_idx]) == (bishop_attacks_table(queen_square, bishop_occ_rel)|rook_attacks_table(queen_square, rook_occ_rel))}")


#knight

knight_square = 8

print(f'Test result (knight): {b.bitboard_to_fen(KNIGHT_TABLE[knight_square]) == "8/8/8/8/1p6/2p5/8/2p5"}')


#king

king_square = 62

print(f'Test result (king): {b.bitboard_to_fen(KING_TABLE[king_square]) == "5p1p/5ppp/8/8/8/8/8/8"}')


#pawn

black_pawn_square = 38

print(f'Test result (black pawn): {b.bitboard_to_fen(PAWN_TABLE[BLACK_INDEX][black_pawn_square]) == "8/8/8/8/5p1p/8/8/8"}')

white_pawn_square = 31

print(f'Test result (black pawn): {b.bitboard_to_fen(PAWN_TABLE[WHITE_INDEX][white_pawn_square]) == "8/8/8/6p1/8/8/8/8"}')


#inverted pawn

white_inverted_pawn_square = 62

print(f'Test result (white inverted pawn): {b.bitboard_to_fen(INVERTED_PAWN_TABLE[WHITE_INDEX][white_inverted_pawn_square]) == "8/5p1p/8/8/8/8/8/8"}')

black_inverted_pawn_square = 11

print(f'Test result (black inverted pawn): {b.bitboard_to_fen(INVERTED_PAWN_TABLE[BLACK_INDEX][black_inverted_pawn_square]) == "8/8/8/8/8/2p1p3/8/8"}')
