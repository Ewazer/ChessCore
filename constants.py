#Project constant
EMPTY  = 0
PAWN   = 1
KNIGHT = 3
BISHOP = 4
ROOK   = 5
KING   = 7
QUEEN  = 9

WHITE = 1
BLACK = -1

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

piece = {
    EMPTY: "empty",
    PAWN: "white_pawn",
    ROOK: "white_rook",
    BISHOP: "white_bishop",
    KNIGHT: "white_knight",
    QUEEN: "white_queen",
    KING: "white_king",
    -PAWN: "black_pawn",
    -ROOK: "black_rook",
    -BISHOP: "black_bishop",
    -KNIGHT: "black_knight",
    -QUEEN: "black_queen",
    -KING: "black_king"
}

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
