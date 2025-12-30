# Chess.py

Chess.py is a chess game written in Python. This project allows you to play chess in the command line, with features for move validation and rule management.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Ewazer/chess.git
   ```
2. Accédez au répertoire du projet :
   ```sh
   cd chess.py
   ```

## Utilisation

To start the game, run the [`chess.py`](chess.py) file:
```sh
python 

chess.py

```

## Features

- **Interactive Command-Line Interface**: Play chess with a beautiful Unicode board display
- **Complete Standard chess rules from FIDE (World Chess Federation)**:
  - All standard piece movements (Pawn, Knight, Bishop, Rook, Queen, King)
  - Castling (both kingside and queenside)
  - En passant capture
  - Pawn promotion with choice of piece (Queen, Rook, Bishop, Knight)
  - Check and checkmate detection
  - Stalemate detection
  - Draw by threefold repetition
  - Draw by fifty-move rule
  - Draw by insufficient material
- **Flexible Gameplay Options**:  
  - Choose starting color (white or black)
  - Customizable pawn promotion (automatic or manual selection)
  - Move history tracking
  - Custom board positions - Load any chess position programmatically

## Example Game

Enter moves using algebraic notation:  `[from] [to]`

For examples:
```
> e2 e4        # Move pawn from e2 to e4
> e7 e8q       # Move pawn from e7 to e8 and promote to queen
> e1 g1        # Kingside castling (if conditions are met)
```
## Promotion Pieces

When promoting a pawn, add the piece code at the end: 
- `q` = Queen
- `r` = Rook
- `b` = Bishop
- `n` = Knight

## Advanced Features

### Custom Game Setup

```python
from chess import Chess

# Create a new game
game = Chess()

# Start with black pieces
game.play(color="black")

# Enable automatic queen promotion
game.play(auto_promotion="9")

# Disable auto-promotion (manual choice)
game.play(auto_promotion=False)
```

### Programmatic Play

```python
from chess import Chess

game = Chess()
game.launch_partie(color="white")

# Play a sequence of moves
moves = ["e2 e4", "e7 e5", "g1 f3", "b8 c6"]
for move in moves:
    result = game.play_move(move)
    if result == 'checkmate':
        print("Game Over!")
        break
```

### Custom Board Positions

You can load any chess position using the `load_board()` method.

```python
from chess import Chess

game = Chess()

# Define piece constants
EMPTY = 0
PAWN = 1
KNIGHT = 3
BISHOP = 4
ROOK = 5
KING = 7
QUEEN = 9

# Create a custom position (White's perspective:  rank 1 = row 0, 'a' file = column 0)
# Example: King and Pawn endgame
custom_board = [
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, KING, EMPTY],     # Rank 1
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PAWN, EMPTY],     # Rank 2
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],    # Rank 3
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],    # Rank 4
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],    # Rank 5
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],    # Rank 6
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, -PAWN, EMPTY, EMPTY],    # Rank 7
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, -KING, EMPTY]     # Rank 8
]

# Load the custom position
game.load_board(custom_board)

# Start playing from this position
game.launch_partie(color="white")
```

#### Piece Encoding

When creating custom boards, use these values: 

| Piece | White | Black |
|-------|-------|-------|
| Empty | 0 | 0 |
| Pawn | 1 | -1 |
| Knight | 3 | -3 |
| Bishop | 4 | -4 |
| Rook | 5 | -5 |
| King | 7 | -7 |
| Queen | 9 | -9 |

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss the changes you'd like to make.

## Licence

This project is licensed under the MIT License. See the LICENSE file for more details.
