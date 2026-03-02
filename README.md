# ChessCore

> **Version 3.0.7** by Leroux Lubin

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

Enter your moves in the format `[start_square][target_square]`:

```
> e2e4
> e7e5
> g1f3
> e7e8q    # promotion to queen
> e1g1     # kingside castling
```

### Minimal programmatic usage

```python
from chesscore import ChessCore

game = ChessCore()
game.start_new_game(side="white")

result = game.play_move("e2e4")
result = game.play_move("e7e5")
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
| `mg_score` | `int` | Incremental middlegame evaluation score (for engine use) |
| `eg_score` | `int` | Incremental endgame evaluation score (for engine use) |
| `phase` | `int` | Incremental game phase counter (for engine use) |

#### Methods

| Method | Signature | Description |
|---------|-----------|-------------|
| `init_board()` | `→ None` | Resets the board to the starting position |
| `init_board_for_engine()` | `→ None` | Initializes engine-specific state: `mailbox`, `mg_score`, `eg_score`, `phase` — call after `init_board()` or `load_board()` |
| `load_board(fen)` | `fen: str → None` | Loads a position from a complete FEN string |
| `get_piece_type(square)` | `square: int → int \| None` | Returns the piece type on a square (0-63), or `None` |
| `get_piece_type_with_mask(mask)` | `mask: int → int \| None` | Same but with a bitboard mask |
| `get_piece_type_and_color(square)` | `square: int → int` | Returns the signed type (positive=white, negative=black, 0=empty) |
| `make_move(move, side, promotion_piece)` | `move: int, side: int, promotion_piece: int → tuple` | Applies a move and returns an undo tuple |
| `unmake_move(undo, side)` | `undo: tuple, side: int → None` | Undoes a move using the undo tuple |
| `make_move_search(move, side, promotion_piece)` | `move: int, side: int, promotion_piece: int → tuple` | Like `make_move` but also updates `mg_score`, `eg_score`, `phase` incrementally — optimized for engine search |
| `unmake_move_search(undo, side)` | `undo: tuple, side: int → None` | Like `unmake_move` but also restores `mg_score`, `eg_score`, `phase` from the undo tuple |

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

#### Search Undo Tuple (`undo` — search variant)

Returned by `make_move_search()`, used by `unmake_move_search()`. Contains three additional fields for incremental evaluation:

```python
undo = (move, from_piece, to_piece, castling_rights_prev, halfmove_count, en_passant_prev, promotion_piece, mg_score, eg_score, phase)
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
| 7 | `mg_score` before the move | `int` |
| 8 | `eg_score` before the move | `int` |
| 9 | `phase` before the move | `int` |

---

### Class `MoveGen`

Pseudo-legal and legal move generation. All methods are static.

Several functions follow a simple pattern: they return a flat list of all pseudo‑legal moves of a given type.  To avoid repeating the heavy magic‑bitboard lookup when an engine needs separate capture/quiet/promotion lists, a second family of helpers performs the calculation **one time per piece** and fills user‑supplied lists.  These are the `get_..._categorized` methods and the convenience `get_all_moves_categorized` which returns three lists at once.

| Method | Signature | Description |
|---------|-----------|-------------|
| `list_all_pawn_moves(board_obj, color)` | `→ list[int]` | All pawn moves (advance, double advance, captures, en passant) |
| `list_all_knight_moves(board_obj, color)` | `→ list[int]` | All knight moves |
| `list_all_bishop_moves(board_obj, color)` | `→ list[int]` | All bishop moves (magic bitboards) |
| `list_all_rook_moves(board_obj, color)` | `→ list[int]` | All rook moves (magic bitboards) |
| `list_all_queen_moves(board_obj, color)` | `→ list[int]` | All queen moves (rook + bishop combination) |
| `list_all_king_moves(board_obj, color, castling=True)` | `→ list[int]` | All king moves + castling |
| `list_all_castling_move(board_obj, color)` | `→ list[int]` | Castling moves only |
| `list_all_legal_moves(board_obj, side, castling=True)` | `→ list[int]` | All legal moves (filters moves leaving the king in check) |
| `generate_all_moves(board_obj, side, castling=True)` | `→ generator` | Legal move generator (yield) |
| `list_all_pawn_captures(board_obj, color)` | `→ list[int]` | Pawn capture moves only (captures + en passant, excludes promotion moves) |
| `list_all_pawn_promotions(board_obj, color)` | `→ list[int]` | Pawn moves that result in a promotion (push and capture promotions) |
| `list_all_knight_captures(board_obj, color)` | `→ list[int]` | Knight capture moves only |
| `list_all_bishop_captures(board_obj, color)` | `→ list[int]` | Bishop capture moves only (magic bitboards) |
| `list_all_rook_captures(board_obj, color)` | `→ list[int]` | Rook capture moves only (magic bitboards) |
| `list_all_queen_captures(board_obj, color)` | `→ list[int]` | Queen capture moves only |
| `list_all_king_captures(board_obj, color)` | `→ list[int]` | King capture moves only |
| `list_all_legal_captures(board_obj, side)` | `→ list[int]` | All legal captures (filters moves leaving the king in check) |
| `generate_all_captures(board_obj, side)` | `→ generator` | Legal capture generator (yield) |
| `list_all_pawn_quiets(board_obj, color)` | `→ list[int]` | Pawn quiet moves only (advances, no captures, no en passant, excluding promotions) |
| `list_all_knight_quiets(board_obj, color)` | `→ list[int]` | Knight quiet moves only (non-captures) |
| `list_all_bishop_quiets(board_obj, color)` | `→ list[int]` | Bishop quiet moves only (magic bitboards) |
| `list_all_rook_quiets(board_obj, color)` | `→ list[int]` | Rook quiet moves only (magic bitboards) |
| `list_all_queen_quiets(board_obj, color)` | `→ list[int]` | Queen quiet moves only |
| `list_all_king_quiets(board_obj, color, castling=True)` | `→ list[int]` | King quiet moves only + castling |
| `list_all_legal_quiets(board_obj, side, castling=True)` | `→ list[int]` | All legal quiet moves (filters moves leaving the king in check) |
| `generate_all_quiets(board_obj, side, castling=True)` | `→ generator` | Legal quiet move generator (yield) |
| `list_all_piece_move(board_obj, square, piece_value)` | `→ list[int]` | Moves of a specific piece from a square (only used by `print_highlighted_legal_move` in ChessDisplay) |
| `get_pawn_moves_categorized(board_obj, color, captures, quiets, promotions)` | `→ None` | Fill three lists with pawn moves; heavy bitboard calc done once. |
| `get_knight_moves_categorized(board_obj, color, captures, quiets)` | `→ None` | Fill captures/quiets for knights. |
| `get_bishop_moves_categorized(board_obj, color, captures, quiets)` | `→ None` | Fill captures/quiets for bishops. |
| `get_rook_moves_categorized(board_obj, color, captures, quiets)` | `→ None` | Fill captures/quiets for rooks. |
| `get_queen_moves_categorized(board_obj, color, captures, quiets)` | `→ None` | Fill captures/quiets for queens. |
| `get_king_moves_categorized(board_obj, color, captures, quiets, castling=True)` | `→ None` | Fill captures/quiets for king; castling appended to quiets. |
| `get_all_moves_categorized(board_obj, color, captures, quiets, promotions, castling=True)` | `→ tuple` | Convenience wrapper that returns the three lists. |
| `get_captures_and_promotions(board_obj, color, captures, promotions)` | `→ None` | Fill only captures and promotions (no quiet moves). Optimized for quiescence search, skips all quiet move generation entirely. |

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
| `get_all_attackers(board_obj, square, occupied=None)` | `→ int` | Returns a bitboard of all attackers on a square (used for SEE or detailed attack lists) |
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
| `print_game_start(board_obj, side=WHITE)` | Game start message + board |
| `print_turn(side)` | Indicates whose turn it is |
| `print_game_already_over()` | Message indicating the game is already over |
| `print_game_over(board_obj, winner, side=None)` | Checkmate message |
| `print_draw(board_obj, side=WHITE, draw_type=None)` | Draw message (`insufficient_material`, `fifty_move_rule`, `threefold_repetition`, `stalemate`) |
| `print_invalid_move(reason=None)` | Invalid move message (with optional reason) |
| `print_invalid_format()` | Invalid format message with example |
| `print_move(move)` | Prints the played move |
| `print_last_move_highlighted(board_obj, side=WHITE)` | Board with last move highlighted |
| `print_highlighted_legal_move(board_obj, square, side=WHITE)` | Board with legal moves of a piece highlighted (`square` can be an index or algebraic string like `'e2'`) |

Note: `print_invalid_move` and `print_game_already_over` are **not** affected by `@print_disabled` — they always print. All other display methods are silenced when `ChessDisplay.enable_print = False`.

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
| `force_move(move)` | `move: str → None` | Applies a move **without any legality check** |
| `commit(move)` | `move: str → str \| None` | Applies a move without check + verifies if game is over |
| `is_game_over()` | `→ bool \| str` | Queries the game state |
| `move_parser(move_str)` | `move_str: str → tuple[int, int]` | Parses a LAN or SAN move string → `(encoded_move, promotion_piece)` |
| `parse_move_and_validate(move_str)` | `move_str: str → bool` | Parses, detects promotion, validates. Sets `board.encoded_move_in_progress` and `promotion_value` |
| `lan_to_encoded_move(lan_move)` | *(static)* `lan_move: str → tuple[int, int]` | Parses LAN (`"e2e4"`, `"e7e8q"`) → `(encoded_move, promotion_piece)`. Raises `ValueError` on invalid |
| `lan_to_encoded_move_and_validate(lan_move)` | `lan_move: str → tuple[int, int] \| None` | Parses LAN, sets board state, validates. Returns `None` on failure |
| `sen_to_encoded_move(board_obj, sen_move, side)` | *(static)* `→ tuple[int, int]` | Converts SAN (e.g., `"Nf3"`, `"O-O"`, `"e8=Q"`) → `(encoded_move, promotion_piece)` |
| `give_move_info(board_obj, encoded_move)` | *(static)* `→ None \| str` | Validates move source/target coherence. `None` = valid, `str` = reason |

The last 3 game methods (`force_move`, `commit`, `is_game_over`) are designed for use by an AI engine.

The parser methods (`move_parser`, `lan_to_encoded_move`, `sen_to_encoded_move`) all return a consistent `(encoded_move, promotion_piece)` tuple, where `promotion_piece` is `0` when no promotion occurs.

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
| `KNIGHT` | `2` | Knight |
| `BISHOP` | `3` | Bishop |
| `ROOK` | `4` | Rook |
| `QUEEN` | `5` | Queen |
| `KING` | `6` | King |

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

### Engine Constants

| Constant | Value | Description |
|-----------|--------|-------------|
| `MG_INDEX` | `0` | Index for middlegame phase in PST and piece-value tuples |
| `EG_INDEX` | `1` | Index for endgame phase in PST and piece-value tuples |
| `PAWN_VALUE` | `(128, 213)` | Pawn material value `(mg, eg)` |
| `KNIGHT_VALUE` | `(781, 854)` | Knight material value `(mg, eg)` |
| `BISHOP_VALUE` | `(825, 915)` | Bishop material value `(mg, eg)` |
| `ROOK_VALUE` | `(1276, 1380)` | Rook material value `(mg, eg)` |
| `QUEEN_VALUE` | `(2538, 2682)` | Queen material value `(mg, eg)` |
| `pst` | `tuple` | Piece-Square Tables indexed by `pst[piece_type][MG_INDEX\|EG_INDEX][square]`. Material values are already included. |

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

Text format: `[start_square][target_square][promotion]`

| Example | Description |
|---------|-------------|
| `e2e4` | Pawn e2 to e4 |
| `g1f3` | Knight g1 to f3 |
| `e1g1` | White kingside castling |
| `e1c1` | White queenside castling |
| `e7e8q` | Promotion to queen |
| `e7e8r` | Promotion to rook |
| `e7e8b` | Promotion to bishop |
| `e7e8n` | Promotion to knight |
| `e5d6` | En passant capture (if legal) |

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

moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]
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

result = game.play_move("f1b5")
```

### Silent Mode

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

result = engine.play_move("e2e4", print_move=False)
result = engine.play_move("e7e5", print_move=False)
```

### Fast Moves without verification (`commit`), useful for an AI engine as it uses moves generated by `MoveGen` without validation.

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

# commit() does not verify move legality, but returns the game state after the move.
outcome = engine.commit("e2e4")    # → None 
outcome = engine.commit("e7e5")    # → None
outcome = engine.commit("d1h5")    # → None
outcome = engine.commit("b8c6")    # → None
outcome = engine.commit("f1c4")    # → None
outcome = engine.commit("g8f6")    # → None
outcome = engine.commit("h5f7")    # → 'checkmate'
```

### `force_move()`

```python
from chesscore import ChessCore

engine = ChessCore()
engine.start_new_game(side="white", enable_print=False)

# Applies a move without any return
engine.force_move("e2e4")
engine.force_move("e7e5")

# Check game state afterwards
print(engine.is_game_over())  # → False
```

### Generate and Explore Legal Moves

```python
from chesscore import Board, MoveGen, ChessDisplay
from chesscore.constants import *

board = Board()

# All legal moves for white
legal_moves = MoveGen.list_all_legal_moves(board, WHITE)
print(f"{len(legal_moves)} legal moves")  # → 20

# Decode moves
for move in legal_moves:
    from_sq = INVERSE_SQUARES[move & 0x3F]
    to_sq = INVERSE_SQUARES[(move >> 6) & 0x3F]
    print(f"{from_sq} → {to_sq}")

# An alternative fast path: generate categorized lists once
captures, quiets, promotions = [], [], []
MoveGen.get_all_moves_categorized(board, WHITE, captures, quiets, promotions)
print(f"categorized  captures={len(captures)}, quiets={len(quiets)}, promos={len(promotions)}")
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

# detailed attacker bitboard
attackers_bb = GameState.get_all_attackers(board, 60)
print(f"attackers bitboard: {attackers_bb:064b}")
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

### Make / Unmake Search (incremental evaluation)

`make_move_search` / `unmake_move_search` maintain `mg_score`, `eg_score`, and `phase` incrementally, no need to recompute the full evaluation at each node. Must be initialized before use (e.g., by computing scores from scratch once at the root).

### Mailbox and `init_board_for_engine`

The **mailbox** is a flat 64-element list (`board.mailbox[0..63]`) that mirrors the bitboard state: each cell holds the signed piece type at that square (positive = white, negative = black, `0` = empty).

It is designed for fast **O(1) piece-type lookup** without iterating over bitboards, which is especially useful in evaluation and search code.

```python
from chess_game import Board, MoveGen, WHITE, BLACK
from chess_game import PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING, EMPTY

board = Board()
board.init_board_for_engine()  # sets mailbox + engine scores to initial values

# Read piece at a square 
print(board.mailbox[0])   # → 4  (white ROOK on a1)
print(board.mailbox[63])  # → -4 (black ROOK on h8)
print(board.mailbox[28])  # → 0  (empty square)

# Use make_move_search / unmake_move_search to keep mailbox in sync
moves = MoveGen.list_all_legal_moves(board, WHITE)
for move in moves:
    undo = board.make_move_search(move, WHITE)
    # board.mailbox, mg_score, eg_score and phase are all up to date here
    board.unmake_move_search(undo, WHITE)
```

> The mailbox is **not** automatically initialized by `Board()`. You must call `init_board_for_engine()` (or manually set it) before using `make_move_search` / `unmake_move_search`.

---

## Benchmarks

100K iterations/function, executed on Github Codespaces (2 cores), **PyPy3**, Linux (Ubuntu 24.04):

### Micro-benchmarks

| Function | Average time | Ops/s |
|----------|------------|-------|
| `Board.__init__()` | 157.63 ns | 6.34M |
| `Board.material_insufficiency()` | 59.80 ns | 16.72M |
| `GameState.attackers_to()` (is_check) | 456.12 ns | 2.19M |
| `GameState.is_checkmate()` | 448.84 ns | 2.23M |
| `MoveGen.list_all_pawn_moves()` | 1.41 µs | 710.88K |
| `MoveGen.list_all_knight_moves()` | 416.64 ns | 2.40M |
| `MoveGen.list_all_bishop_moves()` | 336.63 ns | 2.97M |
| `MoveGen.list_all_rook_moves()` | 502.84 ns | 1.99M |
| `MoveGen.list_all_queen_moves()` | 309.48 ns | 3.23M |
| `MoveGen.list_all_king_moves()` | 128.02 ns | 7.81M |
| `MoveGen.list_all_legal_moves()` | 12.88 µs | 77.62K |

### PERFT (move generation validation)

| Depth | Nodes | Time | NPS |
|-----------|-------|-------|-----|
| 1 | 20 | 34.10 µs | 586.51K |
| 2 | 400 | 10.80 ms | 37.04K |
| 3 | 8 902 | 31.61 ms | 281.59K |
| 4 | 197 281 | 424.91 ms | 464.29K |
| 5 | 4.87M | 5.50 s | 884.64K |
| 6 | 119.06M | 116.28 s | 1.02M |

---

## Contributing

Contributions are welcome! Open a PR or an issue to discuss your changes.

---

## License

This project is licensed under the license. See the LICENSE file for details.
