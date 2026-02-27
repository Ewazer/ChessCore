#Project constant
__all__ = [
    "EMPTY",
    "PAWN",
    "KNIGHT",
    "BISHOP",
    "ROOK",
    "QUEEN",
    "KING",
    "WHITE",
    "BLACK",
    "WHITE_INDEX",
    "BLACK_INDEX",
    "piece_note_style",
    "SQUARES",
    "INVERSE_SQUARES",
    "SQUARE_MASK",
    "U64",
    "ROOK_MASK",
    "ROOK_MAGIC",
    "ROOK_SHIFT",
    "ROOK_NBITS",
    "BISHOP_MASK",
    "BISHOP_MAGIC",
    "BISHOP_SHIFT",
    "BISHOP_NBITS",
    "ROOK_TABLE",
    "BISHOP_TABLE",
    "KNIGHT_TABLE",
    "KING_TABLE",
    "PAWN_TABLE",
    "INVERTED_PAWN_TABLE",
    "RANK_MASKS",
    "FILE_MASKS",
    "WK_EMPTY",
    "WQ_EMPTY",
    "BK_EMPTY",
    "BQ_EMPTY",
    "WK_SAFE",
    "WQ_SAFE",
    "BK_SAFE",
    "BQ_SAFE",
    "CR_WK",
    "CR_WQ",
    "CR_BK",
    "CR_BQ",
    #for engine
    "MG_INDEX",
    "EG_INDEX",
    "pst",
    "PAWN_VALUE",
    "KNIGHT_VALUE",
    "BISHOP_VALUE",
    "ROOK_VALUE",
    "QUEEN_VALUE",
    "PIECE_VALUES",
    "MVV_LVA",
]


EMPTY  = 0


PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6


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


import os
import json

with open(os.path.join(os.path.dirname(__file__), 'data', 'magic_bitboards.json'), "r") as f:
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


#For engine

MG_INDEX = 0
EG_INDEX = 1

# The PST tables are placed in the tuple so that the values of the pieces used in Chesscore can serve as indexes.

pst = (
    # EMPTY
    (),

    # PAWN
    (
        # MG
        (
            0,   0,   0,   0,   0,   0,   0,   0,
            3,   3,  10,  19,  16,  19,   7,  -5,
            -9, -15,  11,  15,  32,  22,   5, -22,
            -8, -23,   6,  20,  40,  17,   4, -12,
            13,   0, -13,   1,  11,  -2, -13,   5,
            -5, -12,  -7,  22,  -8,  -5, -15, -18,
            -7,   7,  -3, -13,   5, -16,  10,  -8,
            0,   0,   0,   0,   0,   0,   0,   0
        ),
        # EG
        (
            0,   0,   0,   0,   0,   0,   0,   0,
            -10,  -6,  10,   0,  14,   7,  -5, -19,
            -10, -10, -10,   4,   4,   3,  -6,  -4,
            6,  -2,  -8,  -4, -13, -12, -10,  -9,
            9,   4,   3, -12, -12,  -6,  13,   8,
            28,  20,  21,  28,  30,   7,   6,  13,
            0, -11,  12,  21,  25,  19,   4,   7,
            0,   0,   0,   0,   0,   0,   0,   0
        ),
    ),

    # KNIGHT
    (
        # MG
        (
            -175, -92, -74, -73, -73, -74, -92,-175,
            -77, -41, -27, -15, -15, -27, -41, -77,
            -61, -17,   6,  12,  12,   6, -17, -61,
            -35,   8,  40,  49,  49,  40,   8, -35,
            -34,  13,  44,  51,  51,  44,  13, -34,
            -9,  22,  58,  53,  53,  58,  22,  -9,
            -67, -27,   4,  37,  37,   4, -27, -67,
            -201, -83, -56, -26, -26, -56, -83,-201
        ),
        # EG
        (
            -96, -65, -49, -21, -21, -49, -65, -96,
            -67, -54, -18,   8,   8, -18, -54, -67,
            -40, -27,  -8,  29,  29,  -8, -27, -40,
            -35,  -2,  13,  28,  28,  13,  -2, -35,
            -45, -16,   9,  39,  39,   9, -16, -45,
            -51, -44, -16,  17,  17, -16, -44, -51,
            -69, -50, -51,  12,  12, -51, -50, -69,
            -100, -88, -56, -17, -17, -56, -88,-100
        )
    ),

    # BISHOP
    (
        # MG
        (
            -53,  -5,  -8, -23, -23,  -8,  -5, -53,
            -15,   8,  19,   4,   4,  19,   8, -15,
            -7,  21,  -5,  17,  17,  -5,  21,  -7,
            -5,  11,  25,  39,  39,  25,  11,  -5,
            -12,  29,  22,  31,  31,  22,  29, -12,
            -16,   6,   1,  11,  11,   1,   6, -16,
            -17, -14,   5,   0,   0,   5, -14, -17,
            -48,   1, -14, -23, -23, -14,   1, -48
        ),
        # EG
        (
            -57, -30, -37, -12, -12, -37, -30, -57,
            -37, -13, -17,   1,   1, -17, -13, -37,
            -16,  -1,  -2,  10,  10,  -2,  -1, -16,
            -20,  -6,   0,  17,  17,   0,  -6, -20,
            -17,  -1, -14,  15,  15, -14,  -1, -17,
            -30,   6,   4,   6,   6,   4,   6, -30,
            -31, -20,  -1,   1,   1,  -1, -20, -31,
            -46, -42, -37, -24, -24, -37, -42, -46
        )
    ),

    # ROOK
    (
        # MG
        (
            -31, -20, -14,  -5,  -5, -14, -20, -31,
            -21, -13,  -8,   6,   6,  -8, -13, -21,
            -25, -11,  -1,   3,   3,  -1, -11, -25,
            -13,  -5,  -4,  -6,  -6,  -4,  -5, -13,
            -27, -15,  -4,   3,   3,  -4, -15, -27,
            -22,  -2,   6,  12,  12,   6,  -2, -22,
            -2,  12,  16,  18,  18,  16,  12,  -2,
            -17, -19,  -1,   9,   9,  -1, -19, -17
        ),
        # EG
        (
            -9, -13, -10,  -9,  -9, -10, -13,  -9,
            -12,  -9,  -1,  -2,  -2,  -1,  -9, -12,
            6,  -8,  -2,  -6,  -6,  -2,  -8,   6,
            -6,   1,  -9,   7,   7,  -9,   1,  -6,
            -5,   8,   7,  -6,  -6,   7,   8,  -5,
            6,   1,  -7,  10,  10,  -7,   1,   6,
            4,   5,  20,  -5,  -5,  20,   5,   4,
            18,   0,  19,  13,  13,  19,   0,  18
        )
    ),

    # QUEEN
    (
        # MG
        (
            3,  -5,  -5,   4,   4,  -5,  -5,   3,
            -3,   5,   8,  12,  12,   8,   5,  -3,
            -3,   6,  13,   7,   7,  13,   6,  -3,
            4,   5,   9,   8,   8,   9,   5,   4,
            0,  14,  12,   5,   5,  12,  14,   0,
            -4,  10,   6,   8,   8,   6,  10,  -4,
            -5,   6,  10,   8,   8,  10,   6,  -5,
            -2,  -2,   1,  -2,  -2,   1,  -2,  -2
        ),
        # EG
        (
            -69, -57, -47, -26, -26, -47, -57, -69,
            -55, -31, -22,  -4,  -4, -22, -31, -55,
            -39, -18,  -9,   3,   3,  -9, -18, -39,
            -23,  -3,  13,  24,  24,  13,  -3, -23,
            -29,  -6,   9,  21,  21,   9,  -6, -29,
            -38, -18, -12,   1,   1, -12, -18, -38,
            -50, -27, -24,  -8,  -8, -24, -27, -50,
            -75, -52, -43, -36, -36, -43, -52, -75
        )
    ),

    # KING
    (
        # MG
        (
            271, 327, 271, 198, 198, 271, 327, 271,
            278, 303, 234, 179, 179, 234, 303, 278,
            195, 258, 169, 120, 120, 169, 258, 195,
            164, 190, 138,  98,  98, 138, 190, 164,
            154, 179, 105,  70,  70, 105, 179, 154,
            123, 145,  81,  31,  31,  81, 145, 123,
            88, 120,  65,  33,  33,  65, 120,  88,
            59,  89,  45,  -1,  -1,  45,  89,  59
        ),
        # EG
        (
            1,  45,  85,  76,  76,  85,  45,   1,
            53, 100, 133, 135, 135, 133, 100,  53,
            88, 130, 169, 175, 175, 169, 130,  88,
            103, 156, 172, 172, 172, 172, 156, 103,
            96, 166, 199, 199, 199, 199, 166,  96,
            92, 172, 184, 191, 191, 184, 172,  92,
            47, 121, 116, 131, 131, 116, 121,  47,
            11,  59,  73,  78,  78,  73,  59,  11
        )
    ),
)

PAWN_VALUE = (128, 213)
KNIGHT_VALUE = (781, 854)
BISHOP_VALUE = (825, 915)
ROOK_VALUE = (1276, 1380)
QUEEN_VALUE = (2538, 2682)


MVV_LVA = [[[0] for i in range(6)]for i in range(7)]

PIECE_VALUES = [0, PAWN_VALUE[0], KNIGHT_VALUE[0], BISHOP_VALUE[0], ROOK_VALUE[0], QUEEN_VALUE[0], 3000]

for att in range(1, 7):
    for targ in range(1, 6):
        MVV_LVA[att][targ] = PIECE_VALUES[targ] - att + 10000


pst = (
    (
        (),

        # PAWN
        (
            # MG
            tuple(pst_value + PAWN_VALUE[MG_INDEX] for pst_value in pst[PAWN][MG_INDEX]),
            
            # EG
            tuple(pst_value + PAWN_VALUE[EG_INDEX] for pst_value in pst[PAWN][EG_INDEX]),
        ),

        # KNIGHT
        (
            # MG
            tuple(pst_value + KNIGHT_VALUE[MG_INDEX] for pst_value in pst[KNIGHT][MG_INDEX]),
            
            # EG
            tuple(pst_value + KNIGHT_VALUE[EG_INDEX] for pst_value in pst[KNIGHT][EG_INDEX]),
        ),

        # BISHOP
        (
            # MG
            tuple(pst_value + BISHOP_VALUE[MG_INDEX] for pst_value in pst[BISHOP][MG_INDEX]),

            # EG
            tuple(pst_value + BISHOP_VALUE[EG_INDEX] for pst_value in pst[BISHOP][EG_INDEX]),
        ),

        # ROOK
        (
            # MG
            tuple(pst_value + ROOK_VALUE[MG_INDEX] for pst_value in pst[ROOK][MG_INDEX]),
            
            # EG
            tuple(pst_value + ROOK_VALUE[EG_INDEX] for pst_value in pst[ROOK][EG_INDEX]),
        ),

        # QUEEN
        (
            # MG
            tuple(pst_value + QUEEN_VALUE[MG_INDEX] for pst_value in pst[QUEEN][MG_INDEX]),
            
            # EG
            tuple(pst_value + QUEEN_VALUE[EG_INDEX] for pst_value in pst[QUEEN][EG_INDEX]),
        ),

        # KING
        (
            # MG
            tuple(pst_value for pst_value in pst[KING][MG_INDEX]),

            # EG
            tuple(pst_value for pst_value in pst[KING][EG_INDEX]),
        )
     )
)

