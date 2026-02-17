#Project constant
EMPTY  = 0


PAWN = 1
KNIGHT = 3
BISHOP = 4
ROOK = 5
QUEEN = 9
KING = 7


WHITE = 1
BLACK = -1


WHITE_INDEX = 0
BLACK_INDEX = 1


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


SQUARES = {
    "a1": 0, "b1": 1, "c1": 2, "d1": 3, "e1": 4, "f1": 5, "g1": 6, "h1": 7,
    "a2": 8, "b2": 9, "c2": 10, "d2": 11, "e2": 12, "f2": 13, "g2": 14, "h2": 15,
    "a3": 16, "b3": 17, "c3": 18, "d3": 19, "e3": 20, "f3": 21, "g3": 22, "h3": 23,
    "a4": 24, "b4": 25, "c4": 26, "d4": 27, "e4": 28, "f4": 29, "g4": 30, "h4": 31,
    "a5": 32, "b5": 33, "c5": 34, "d5": 35, "e5": 36, "f5": 37, "g5": 38, "h5": 39,
    "a6": 40, "b6": 41, "c6": 42, "d6": 43, "e6": 44, "f6": 45, "g6": 46, "h6": 47,
    "a7": 48, "b7": 49, "c7": 50, "d7": 51, "e7": 52, "f7": 53, "g7": 54, "h7": 55,
    "a8": 56, "b8": 57, "c8": 58, "d8": 59, "e8": 60, "f8": 61, "g8": 62, "h8": 63
}

INVERSE_SQUARES = {v: k for k, v in SQUARES.items()}


SQUARE_MASK = [1 << square for square in range(64)]


U64 = (1 << 64) - 1


import json

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


ROOK_TABLE = magic_data["rook_table"]
BISHOP_TABLE = magic_data["bishop_table"]
KNIGHT_TABLE = magic_data["knight_table"]
KING_TABLE = magic_data["king_table"]
PAWN_TABLE = magic_data["pawn_table"] 
INVERTED_PAWN_TABLE = magic_data["inverted_pawn_table"]


RANK_MASKS = [0xFF << (8 * i) for i in range(8)]
FILE_MASKS = [0x0101010101010101 << i for i in range(8)]


WK_EMPTY = (1<<5) | (1<<6)                   # f1 g1
WQ_EMPTY = (1<<1) | (1<<2) | (1<<3)          # b1 c1 d1
BK_EMPTY = (1<<61) | (1<<62)                # f8 g8
BQ_EMPTY = (1<<57) | (1<<58) | (1<<59)      # b8 c8 d8
    
WK_SAFE = (1<<4) | (1<<5) | (1<<6)         # e1 f1 g1
WQ_SAFE = (1<<4) | (1<<3) | (1<<2)         # e1 d1 c1
BK_SAFE = (1<<60) | (1<<61) | (1<<62)       # e8 f8 g8
BQ_SAFE = (1<<60) | (1<<59) | (1<<58)       # e8 d8 c8

CR_WK = 1
CR_WQ = 2
CR_BK = 4
CR_BQ = 8
