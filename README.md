# ChessCore

> **Version 3.0.2** by Leroux Lubin

ChessCore is an optimized chess core, written entirely in **native Python** (no external dependencies required).

It uses a **bitboard** representation of the chess board coupled with **magic bitboards** for piece move generation, achieving near-maximum performance for native Python.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Internal Representation](#internal-representation)
- [API Reference](#api-reference)
  - [Class `Board`](#class-board)
  - [Class `MoveGen`](#class-movegen)
  - [Class `GameState`](#class-gamestate)
  - [Class `ChessDisplay`](#class-chessdisplay)
  - [Class `ChessCore`](#class-chesscore)
- [Constants](#constants)
- [Move Format](#move-format)
- [Move Encoding](#move-encoding)
- [Implemented Rules](#implemented-rules)
- [Usage Examples](#usage-examples)
- [Benchmarks](#benchmarks)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/ewazer/chesscore.git
   ```
2. Access the project directory:
   ```sh
   cd ChessCore
   ```

No dependencies to install. Python 3.10+ required (for `int | None` syntax).

---

## Quick Start

### Play in the terminal

```sh
python chesscore/chess_game.py
```

Enter your moves in the format `[start_square] [target_square]`:

```
> e2 e4
> e7 e5
> g1 f3
> e7 e8q    # promotion to queen
> e1 g1     # kingside castling
```

### Minimal programmatic usage

```python
from chesscore import ChessCore

game = ChessCore()
game.start_new_game(side="white")

result = game.play_move("e2 e4")
result = game.play_move("e7 e5")
```

---

## Architecture

The project is organized into a package structure:

```
chesscore/
├── __init__.py

├── chess_game.py
  ├── Board          → Board state
  ├── MoveGen        → Move generation
  ├── GameState      → Game state detection
  ├── ChessDisplay   → Display management
  └── ChessCore      → Game controller

├── constants.py   → Global constants, pre-calculated tables, magic bitboards loading
└── data/
    ├── table_creator.py  → Attack table generation script
    └── magic_bitboards.json  → Pre-calculated magic bitboards tables
```


## Internal Representation

### Bitboards

Each piece type is stored in a 64-bit integer (one bit per square):

| Attribute    | Description                              |
|-------------|------------------------------------------|
| `board.pawn`    | All pawns                                |
| `board.knight`  | All knights                              |
| `board.bishop`  | All bishops                              |
| `board.rook`    | All rooks                                |
| `board.queen`   | All queens                               |
| `board.king`    | Both kings                               |


Color is determined by two occupancy bitboards:

| Index | Attribute                              | Description        |
|-------|---------------------------------------|--------------------|
| `0`   | `board.board_occupied_squares[0]`     | Squares occupied by white |
| `1`   | `board.board_occupied_squares[1]`     | Squares occupied by black  |

For code readability, the constants `WHITE_INDEX` and `BLACK_INDEX` (0 and 1) can be used to access these bitboards.

### Square Indexing

Squares are numbered from 0 (a1) to 63 (h8), rank by rank:

```
56 57 58 59 60 61 62 63   ← rank 8
48 49 50 51 52 53 54 55   ← rank 7
40 41 42 43 44 45 46 47   ← rank 6
32 33 34 35 36 37 38 39   ← rank 5
24 25 26 27 28 29 30 31   ← rank 4
16 17 18 19 20 21 22 23   ← rank 3
 8  9 10 11 12 13 14 15   ← rank 2
 0  1  2  3  4  5  6  7   ← rank 1
```

### Magic Bitboards

Sliding pieces (rook, bishop, queen) use **magic bitboards** to obtain possible moves in **O(1)**:

```python
# Example: generating a rook move from a square `square` (0-63)
occ_rel = occupation & ROOK_MASK[square]
idx = ((occ_rel * ROOK_MAGIC[square]) & U64) >> ROOK_SHIFT[square]
moves = ROOK_TABLE[square][idx]
```

The tables have been pre-calculated and stored in `data/magic_bitboards.json`.

The generation of these tables is done by `data/table-creator.py`.

---

## API Reference

### Class `Board`

Manages the board state.

#### Constructor

```python
board = Board()
```

Initializes the board in the starting position.

**Main attributes:**

| Attribute | Type | Description |
|----------|------|-------------|
| `pawn`, `knight`, `bishop`, `rook`, `queen`, `king` | `int` | Bitboards per piece type |
| `board_occupied_squares` | `list[int]` | `[white, black]` — occupancy bitboards by color |
| `all_board_occupied_squares` | `int` | Union of all pieces |
| `king_square` | `list[int]` | `[white_king_square, black_king_square]` |
| `side_to_move` | `int` | `WHITE` (1) or `BLACK` (-1) |
| `castling_rights` | `int` | Binary mask of castling rights |
| `en_passant_square` | `int` | En passant square (0 if none) |
| `counter_halfmove_without_capture` | `int` | Half-move counter without capture (50-move rule) |
| `move_history` | `list[int]` | Encoded move history (see [Move Encoding](#move-encoding)) |
| `position_hash_history` | `dict` | Occurrence counter for each position |

#### Methods

| Method | Signature | Description |
|---------|-----------|-------------|
| `init_board()` | `→ None` | Resets the board to the starting position |
| `load_board(fen)` | `fen: str → None` | Loads a position from a complete FEN string |
| `get_piece_type(square)` | `square: int → int \| None` | Returns the piece type on a square (0-63), or `None` |
| `get_piece_type_with_mask(mask)` | `mask: int → int \| None` | Same but with a bitboard mask |
| `get_piece_type_and_color(square)` | `square: int → int` | Returns the signed type (positive=white, negative=black, 0=empty) |
| `make_move(move, side, promo)` | `move: int, side: int, promo: int → tuple` | Applies a move and returns an undo tuple |
| `unmake_move(undo, side)` | `undo: tuple, side: int → None` | Undoes a move using the undo tuple |
| `move_parser(move_str)` | `move_str: str → int` | Parses `"e2 e4"` into an encoded move |
| `parse_move_and_validate(all_move)` | `all_move: str → bool` | Parses and validates a move, stores in `encoded_move_in_progress` |
| `give_move_info()` | `→ None \| str` | Extracts info from the current move. `None` = valid, `str` = invalidity reason |
| `change_side()` | `→ None` | Inverts the turn (`side_to_move *= -1`) |
| `add_to_history()` | `→ None` | Adds the current move to history and updates the hash |
| `get_position_hash()` | `→ tuple` | Hash of the current position (for repetition detection) |
| `has_single_piece(bitboard)` | `bitboard: int → bool` | *(static)* Checks if a bitboard contains exactly one piece |
| `material_insufficiency()` | `→ bool` | Detects material insufficiency (K vs K, K+N vs K, K+B vs K) |
| `bitboard_to_fen(bitboard)` | `bitboard: int → str` | *(static)* Converts a bitboard to a partial FEN string |

#### Undo Tuple (`undo`)

Returned by `make_move()`, used by `unmake_move()`:

```python
undo = (move, from_piece, to_piece, castling_rights_prev, halfmove_count, en_passant_prev, promotion_piece)
```

| Index | Content | Type |
|-------|---------|------|
| 0 | Encoded move | `int` |
| 1 | Moving piece type | `int` |
| 2 | Captured piece type (or `None`) | `int \| None` |
| 3 | Castling rights before the move | `int` |
| 4 | Half-move counter before the move | `int` |
| 5 | En passant square before the move | `int` |
| 6 | Promotion piece (or `0`) | `int` |

---

### Class `MoveGen`

Pseudo-legal and legal move generation. All methods are static.

| Method | Signature | Description |
|---------|-----------|-------------|
| `list_all_pawn_move(board_obj, color)` | `→ list[int]` | All pawn moves (advance, double advance, captures, en passant) |
| `list_all_knight_move(board_obj, color)` | `→ list[int]` | All knight moves |
| `list_all_bishop_move(board_obj, color)` | `→ list[int]` | All bishop moves (magic bitboards) |
| `list_all_rook_move(board_obj, color)` | `→ list[int]` | All rook moves (magic bitboards) |
| `list_all_queen_move(board_obj, color)` | `→ list[int]` | All queen moves (rook + bishop combination) |
| `list_all_king_move(board_obj, color, castling=True)` | `→ list[int]` | All king moves + castling |
| `list_all_castling_move(board_obj, color)` | `→ list[int]` | Castling moves only |
| `list_all_legal_move(board_obj, side, castling=True)` | `→ list[int]` | All legal moves (filters moves leaving the king in check) |
| `generate_all_moves(board_obj, side, castling=True)` | `→ generator` | Legal move generator (yield) |
| `list_all_piece_move(board_obj, square, piece_value)` | `→ list[int]` | Moves of a specific piece from a square (only used by `print_highlighted_legal_move` in ChessDisplay) |

**Common parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `board_obj` | `Board` | Board instance |
| `color` / `side` | `int` | `WHITE` (1) or `BLACK` (-1) |

---

### Class `GameState`

Game state detection. All methods are static.

| Method | Signature | Description |
|---------|-----------|-------------|
| `attackers_to(board_obj, side, square)` | `→ bool` | Checks if a square is attacked by `side`'s enemy |
| `is_checkmate(board_obj, side)` | `→ bool` | Checks if `side` is checkmated |
| `check_repetition(board_obj)` | `→ bool` | Checks for threefold repetition |
| `is_move_legal(board_obj, encoded_move)` | `→ bool` | Checks if an encoded move is legal |

`attackers_to` uses pre-calculated attack tables and magic bitboards for fast attack verification.
This method is used to detect checks, checkmates, and filter legal moves.
It can hardly be optimized further without sacrificing code clarity.

---

### Class `ChessDisplay`

Terminal display with Unicode symbols and ANSI codes. Contains a `@print_disabled` decorator that disables printing when `ChessDisplay.enable_print = False`.

| Method | Description |
|---------|-------------|
| `print_board(board_obj, side=WHITE)` | Prints the board (oriented according to side) |
| `print_game_start(board_obj, side)` | Game start message + board |
| `print_turn(side)` | Indicates whose turn it is |
| `print_game_over(board_obj, winner, side)` | Checkmate message |
| `print_draw(board_obj, side, draw_type)` | Draw message (`insufficient_material`, `fifty_move_rule`, `threefold_repetition`) |
| `print_invalid_move(reason)` | Invalid move message |
| `print_invalid_format()` | Invalid format message |
| `print_move(move)` | Prints the played move |
| `print_last_move_highlighted(board_obj, color, side)` | Board with last move highlighted |
| `print_highlighted_legal_move(board_obj, color, square, side)` | Board with legal moves of a piece highlighted |
| `print_highlighted_all_legal_move(board_obj, color, side)` | Board with all legal moves highlighted |
| `color_to_code(color)` | Converts a color name to ANSI codes |

**Available colors for highlighting:** `"red"`, `"green"`, `"yellow"`, `"blue"`, `"magenta"`, `"cyan"`

Note: Methods returning an error message (`print_invalid_move`, `print_invalid_format`) are not disabled by the `@print_disabled` decorator.

---

### Class `ChessCore`

Main game controller.

#### Constructor

```python
game = ChessCore()
```

**Attributes:**

| Attribute | Type | Description |
|----------|------|-------------|
| `board` | `Board` | Board instance |
| `party_over` | `bool` | `True` if the game is over |

#### Methods

| Method | Signature | Description |
|---------|-----------|-------------|
| `start_new_game(side, enable_print)` | `side: str, enable_print: bool → None` | Initializes a game (`"white"` or `"black"`, display on/off) |
| `reset_game()` | `→ None` | Completely resets the game |
| `load_board(fen_string)` | `fen_string: str → None` | Loads a FEN position |
| `play_move(all_move, print_move)` | `all_move: str, print_move: bool → str` | Plays a move with full validation |
| `validate_and_apply_move()` | `→ bool` | Validates and applies the current move |
| `check_loaded_position()` | `→ str \| None` | Checks if a loaded position is checkmate/stalemate |
| `play(side)` | `side: str → str` | Interactive game loop (console input) |
| `god_mode(move)` | `move: str → None` | Applies a move **without any legality check** |
| `commit(move)` | `move: str → str \| None` | Applies a move without check + verifies if game is over |
| `is_game_over()` | `→ bool \| str` | Queries the game state |

The last 3 methods (`god_mode`, `commit`, `is_game_over`) are designed for use by an AI engine.

#### Return values of `play_move()`

| Return | Meaning |
|--------|---------------|
| `'valid'` | Valid move, game continues |
| `'illegal'` | Illegal move |
| `'checkmate'` | Checkmate |
| `'draw'` | Draw (stalemate, threefold repetition, 50 moves, insufficient material) |

#### Return values of `is_game_over()`

| Return | Meaning |
|--------|---------------|
| `False` | Game continues |
| `'checkmate'` | Checkmate |
| `'draw'` | Draw |

---

## Constants

Defined in `constants.py`:

### Importing constants

You can import constants in two ways:

```python
from chesscore import constant

print(constant.PAWN)
print(constant.CR_WK)
```

```python
from chesscore import *

print(PAWN)
print(CR_WK)
```

### Pieces

| Constant | Value | Description |
|-----------|--------|-------------|
| `EMPTY` | `0` | Empty square |
| `PAWN` | `1` | Pawn |
| `KNIGHT` | `3` | Knight |
| `BISHOP` | `4` | Bishop |
| `ROOK` | `5` | Rook |
| `KING` | `6` | King |
| `QUEEN` | `7` | Queen |

> Black pieces are represented by the negative value.

### Colors

| Constant | Value |
|-----------|--------|
| `WHITE` | `1` |
| `BLACK` | `-1` |
| `WHITE_INDEX` | `0` |
| `BLACK_INDEX` | `1` |

### Castling Rights

| Constant | Value | Description |
|-----------|--------|-------------|
| `CR_WK` | `1` | White kingside castling |
| `CR_WQ` | `2` | White queenside castling |
| `CR_BK` | `4` | Black kingside castling |
| `CR_BQ` | `8` | Black queenside castling |

### Pre-calculated Tables

| Table | Description |
|-------|-------------|
| `SQUARE_MASK[64]` | Bit mask for each square (`1 << i`) |
| `KNIGHT_TABLE[64]` | Knight moves from each square |
| `KING_TABLE[64]` | King moves from each square |
| `PAWN_TABLE[2][64]` | Pawn attacks by color |
| `INVERTED_PAWN_TABLE[2][64]` | Inverted pawn attacks (for check detection) |
| `ROOK_TABLE[64][...]` | Magic bitboards tables for rooks |
| `BISHOP_TABLE[64][...]` | Magic bitboards tables for bishops |
| `ROOK_MASK/MAGIC/SHIFT[64]` | Magic parameters for rooks |
| `BISHOP_MASK/MAGIC/SHIFT[64]` | Magic parameters for bishops |
| `RANK_MASKS[8]` | Rank masks |
| `FILE_MASKS[8]` | File masks |
| `SQUARES` | Dictionary `{"a1": 0, ..., "h8": 63}` |
| `INVERSE_SQUARES` | Inverse dictionary `{0: "a1", ..., 63: "h8"}` |
| `U64` | `(1 << 64) - 1` — 64-bit mask |

---

## Move Format

Text format: `[start_square] [target_square][promotion]`

| Example | Description |
|---------|-------------|
| `e2 e4` | Pawn e2 to e4 |
| `g1 f3` | Knight g1 to f3 |
| `e1 g1` | White kingside castling |
| `e1 c1` | White queenside castling |
| `e7 e8q` | Promotion to queen |
| `e7 e8r` | Promotion to rook |
| `e7 e8b` | Promotion to bishop |
| `e7 e8n` | Promotion to knight |
| `e5 d6` | En passant capture (if legal) |

> Without promotion suffix, promotion defaults to **queen**.

---

## Move Encoding

Internally, each move is encoded in a **12-bit integer**:

```
Bits 0-5  : start square (0–63)
Bits 6-11 : target square (0–63)
```

```python
encoded_move = from_square | (to_square << 6)

# Decode:
from_square = encoded_move & 0x3F
to_square   = (encoded_move >> 6) & 0x3F
```

---

## Implemented Rules

Compliant with FIDE rules:

- **Moves**: all standard moves for each piece
- **Captures**: normal captures and en passant
- **Castling**: kingside and queenside
- **Promotion**: piece choice (queen, rook, bishop, knight) or automatic promotion to queen
- **Check**: detection via `attackers_to()` on the king's square
- **Checkmate**: king in check + no legal moves
- **Stalemate**: king not in check + no legal moves
- **Threefold repetition draw**: same position (pieces, turn, castling rights, en passant) seen 3 times
- **50-move rule draw**: 100 half-moves without capture or pawn advance
- **Insufficient material draw**:
  - King vs King
  - King + Knight vs King
  - King + Bishop vs King

---

## Usage Examples

### Interactive Game

```python
from chesscore import ChessCore

game = ChessCore()
game.play()   # Interactive game loop
```

### Play with Black

```python
from chesscore import ChessCore

game = ChessCore()
game.play(side="black")
```

### Programmatic Game

```python
from chesscore import ChessCore

game = ChessCore()
game.start_new_game(side="white")

moves = ["e2 e4", "e7 e5", "g1 f3", "b8 c6", "f1 b5"]
for move in moves:
    result = game.play_move(move)
    if result in ('checkmate', 'draw'):
        print(result)
        break
```

### Load FEN Position

```python
from chesscore import ChessCore

game = ChessCore()
game.load_board("rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq e6 0 3")
game.start_new_game(side="white")

result = game.play_move("f1 b5")
```

### Silent Mode

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

result = engine.play_move("e2 e4", print_move=False)
result = engine.play_move("e7 e5", print_move=False)
```

### Fast Moves without verification (`commit`), useful for an AI engine as it uses moves generated by `MoveGen` without validation.

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

# commit() does not verify move legality, but returns the game state after the move.
outcome = engine.commit("e2 e4")    # → None 
outcome = engine.commit("e7 e5")    # → None
outcome = engine.commit("d1 h5")    # → None
outcome = engine.commit("b8 c6")    # → None
outcome = engine.commit("f1 c4")    # → None
outcome = engine.commit("g8 f6")    # → None
outcome = engine.commit("h5 f7")    # → 'checkmate'
```

### `god_mode()`

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

# Applies a move without any return
engine.god_mode("e2 e4")
engine.god_mode("e7 e5")

# Check game state afterwards
print(engine.is_game_over())  # → False
```

### Generate and Explore Legal Moves

```python
from chesscore import Board, MoveGen, ChessDisplay
from chesscore.constants import *

board = Board()

# All legal moves for white
legal_moves = MoveGen.list_all_legal_move(board, WHITE)
print(f"{len(legal_moves)} legal moves")  # → 20

# Decode moves
for move in legal_moves:
    from_sq = INVERSE_SQUARES[move & 0x3F]
    to_sq = INVERSE_SQUARES[(move >> 6) & 0x3F]
    print(f"{from_sq} → {to_sq}")
```

### Check and Checkmate Detection

```python
from chesscore import Board, GameState, MoveGen
from chesscore.constants import *

board = Board()
board.load_board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")

# Scholar's Mate, black is checkmated
print(GameState.is_checkmate(board, BLACK))  # → True

# Check if a square is attacked
print(GameState.attackers_to(board, BLACK, 60))  # → True (black king is attacked)
```

### Make / Unmake for Search

```python
from chesscore import Board, MoveGen, GameState
from chesscore.constants import *

board = Board()

for move in MoveGen.generate_all_moves(board, WHITE):
    undo = board.make_move(move, WHITE)
    
    # Evaluate position here...
    in_check = GameState.attackers_to(board, BLACK, board.king_square[BLACK_INDEX])
    
    board.unmake_move(undo, WHITE)  # Restoration of exact state
```

---

## Benchmarks

100K iterations/function, executed on Github Codespaces (2 cores), Python 3.12, Linux (Ubuntu 24.04):

### Micro-benchmarks

| Function | Average time | Ops/s |
|----------|------------|-------|
| `Board.__init__()` | 1.16 µs | 865K |
| `Board.material_insufficiency()` | 348 ns | 2.87M |
| `GameState.attackers_to()` (is_check) | 1.05 µs | 950K |
| `GameState.is_checkmate()` | 1.59 µs | 628K |
| `MoveGen.list_all_pawn_move()` | 4.14 µs | 241K |
| `MoveGen.list_all_knight_move()` | 1.25 µs | 800K |
| `MoveGen.list_all_bishop_move()` | 987 ns | 1.01M |
| `MoveGen.list_all_rook_move()` | 971 ns | 1.03M |
| `MoveGen.list_all_queen_move()` | 903 ns | 1.11M |
| `MoveGen.list_all_king_move()` | 1.43 µs | 700K |
| `MoveGen.list_all_legal_move()` | 57.3 µs | 17.4K |

### PERFT (move generation validation)

| Depth | Nodes | Time | NPS |
|-----------|-------|-------|-----|
| 1 | 20 | 104 µs | 190K |
| 2 | 400 | 1.16 ms | 344K |
| 3 | 8 902 | 32 ms | 277K |
| 4 | 197 281 | 651 ms | 302K |


---

## Contributing

Contributions are welcome! Open a PR or an issue to discuss your changes.

---

## License

This project is licensed under the license. See the LICENSE file for details.
