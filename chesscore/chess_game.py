try:
    from .constants import *
    from .constants import __all__ as _constants_all
except ImportError:
    from constants import *
    from constants import __all__ as _constants_all

__version__ = "3.0.7"
__author__ = "Leroux Lubin"

__all__ = ["ChessCore", "Board", "MoveGen", "GameState", "ChessDisplay", *_constants_all]

class Board:
    __slots__ = (
        'pawn', 'knight', 'bishop', 'rook', 'queen', 'king','board_occupied_squares', 'all_board_occupied_squares', 'king_square',
        'move_history', 'side_to_move', 'counter_halfmove_without_capture','castling_rights', 'position_has_loaded', 'en_passant_square','start_value',
        'last_position_hash', 'position_hash_history', 'encoded_move_in_progress','mg_score', 'eg_score', 'phase', 'mailbox','end_coordinate'
    )

    def __init__(self):
        """Initialize the board with the standard starting position and game state."""

        self.init_board()
        
        self.move_history = []
        self.side_to_move = WHITE
        self.counter_halfmove_without_capture = 0
        self.castling_rights = CR_WK | CR_WQ | CR_BK | CR_BQ
        self.position_has_loaded = False
        self.en_passant_square = 0
        self.last_position_hash = self.get_position_hash()
        self.position_hash_history = {self.last_position_hash: 1}
        self.encoded_move_in_progress = None
    

    def init_board(self) -> None:
        """
        Set up/reset the board state to the standard starting position.

        Returns:
            None
        """

        self.pawn =   0b00000000_11111111_00000000_00000000_00000000_00000000_11111111_00000000
        self.knight = 0b01000010_00000000_00000000_00000000_00000000_00000000_00000000_01000010
        self.bishop = 0b00100100_00000000_00000000_00000000_00000000_00000000_00000000_00100100
        self.rook =   0b10000001_00000000_00000000_00000000_00000000_00000000_00000000_10000001
        self.queen =  0b00001000_00000000_00000000_00000000_00000000_00000000_00000000_00001000
        self.king =   0b00010000_00000000_00000000_00000000_00000000_00000000_00000000_00010000

        self.board_occupied_squares = [
            0b00000000_00000000_00000000_00000000_00000000_00000000_11111111_11111111,
            0b11111111_11111111_00000000_00000000_00000000_00000000_00000000_00000000
        ]

        self.all_board_occupied_squares = self.pawn | self.knight | self.bishop | self.rook | self.queen | self.king

        self.king_square = [4, 60]


    def init_board_for_engine(self) -> None:
        """Initialize the board for engine use, including setting up the mailbox and evaluation scores."""

        self.mg_score = 0
        self.eg_score = 0
        self.phase = 0
        self.mailbox = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK] + [PAWN] * 8 + [EMPTY] * 32 + [-PAWN] * 8 + [-ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP, -KNIGHT, -ROOK]


    def load_board(self, fen) -> None:
        """
        Load a custom board position.

        Args:
            fen (str): FEN string representing the board state.

        Raises:
            ValueError: If the FEN string is invalid.
        """
        
        fen_dict = {
            "P": PAWN,
            "N": KNIGHT,
            "B": BISHOP,
            "R": ROOK,
            "Q": QUEEN,
            "K": KING,
            "p": -PAWN,
            "n": -KNIGHT,
            "b": -BISHOP,
            "r": -ROOK,
            "q": -QUEEN,
            "k": -KING,
        }

        fen = fen.split(" ")
        if len(fen) == 6:
            position = fen[0].split("/")

            if len(position) != 8:
                raise ValueError("FEN string is invalid (board position).")
            
            else:
                pawn = 0
                knight = 0
                bishop = 0
                rook = 0
                queen = 0
                king = 0
                board_occupied_squares = [0,0]

                for i in range(8):
                    file = 0

                    if not isinstance(position[i], str):
                        raise ValueError("FEN string is invalid (board position).")
                    
                    for c in position[i]:
                        if c.isdigit():
                            file += int(c)

                        elif c in fen_dict:
                            piece_bit = 1 << (((7 - i) * 8) + file)
                            file += 1
                            if fen_dict[c] == PAWN:
                                pawn |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -PAWN:
                                pawn |= piece_bit
                                board_occupied_squares[1] |= piece_bit
                            elif fen_dict[c] == KNIGHT:
                                knight |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -KNIGHT:
                                knight |= piece_bit
                                board_occupied_squares[1] |= piece_bit
                            elif fen_dict[c] == BISHOP:
                                bishop |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -BISHOP:
                                bishop |= piece_bit
                                board_occupied_squares[1] |= piece_bit
                            elif fen_dict[c] == ROOK:
                                rook |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -ROOK:
                                rook |= piece_bit
                                board_occupied_squares[1] |= piece_bit
                            elif fen_dict[c] == QUEEN:
                                queen |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -QUEEN:
                                queen |= piece_bit
                                board_occupied_squares[1] |= piece_bit
                            elif fen_dict[c] == KING:
                                king |= piece_bit
                                board_occupied_squares[0] |= piece_bit
                            elif fen_dict[c] == -KING:
                                king |= piece_bit
                                board_occupied_squares[1] |= piece_bit

                        if file > 8:
                            raise ValueError("FEN string is invalid (board position).")
                        
                    if file != 8:
                        raise ValueError("FEN string is invalid (board position).")

            if fen[1] in ("w", "b"): 
                side = WHITE if fen[1] == "w" else BLACK

            else:
                raise ValueError("FEN string is invalid (side to move).")
            
            if fen[2] == "-":
                castling_rights = 0

            elif all(c in "KQkq" for c in fen[2]):
                castling_rights = 0
                if "K" in fen[2]:
                    castling_rights |= CR_WK
                if "Q" in fen[2]:
                    castling_rights |= CR_WQ
                if "k" in fen[2]:
                    castling_rights |= CR_BK
                if "q" in fen[2]:
                    castling_rights |= CR_BQ

            else:
                raise ValueError("FEN string is invalid (castling rights).")

            if fen[3] == "-":
                en_passant_square = 0
            elif len(fen[3]) == 2 and fen[3][0] in "abcdefgh" and fen[3][1] in "36":
                file_idx = ord(fen[3][0]) - ord('a')
                rank_idx = int(fen[3][1]) - 1
                en_passant_square = rank_idx * 8 + file_idx
            else:
                raise ValueError("FEN string is invalid (en passant square).")

            if fen[4].isdigit():
                if int(fen[4]) >= 0:
                    counter_halfmove_without_capture = int(fen[4])
                else:
                    raise ValueError("FEN string is invalid (halfmove clock).")
            else:
                raise ValueError("FEN string is invalid (halfmove clock).")

            self.pawn = pawn
            self.knight = knight
            self.bishop = bishop
            self.rook = rook
            self.queen = queen
            self.king = king

            self.board_occupied_squares = board_occupied_squares

            self.all_board_occupied_squares = self.pawn | self.knight | self.bishop | self.rook | self.queen | self.king

            self.king_square = [(self.king & board_occupied_squares[0]).bit_length() - 1, (self.king & board_occupied_squares[1]).bit_length() - 1]

            self.move_history = []
            self.counter_halfmove_without_capture = counter_halfmove_without_capture
            self.side_to_move = side
            self.castling_rights = castling_rights
            self.en_passant_square = en_passant_square
            self.position_has_loaded = True 

            if getattr(self, 'mailbox', None):
                for square in range(64):
                    piece_type = self.get_piece_type_and_color(square)
                    self.mailbox[square] = piece_type if piece_type else EMPTY
        else:
            raise ValueError("FEN string is invalid (expected 6 fields).")
    
    
    def add_to_history(self) -> None:
        """
        Add a move to history and save the current board state.
        """

        self.move_history.append(self.encoded_move_in_progress)
        self.last_position_hash = self.get_position_hash()
        self.position_hash_history[self.last_position_hash] = self.position_hash_history.get(self.last_position_hash, 0) + 1
    
     
    def get_position_hash(self) -> tuple:
        """Generate a hash of the current position for repetition detection."""

        return (
            self.pawn, self.knight, self.bishop, self.rook, self.queen, self.king, self.en_passant_square,
            self.side_to_move, self.castling_rights, self.board_occupied_squares[WHITE_INDEX], self.board_occupied_squares[BLACK_INDEX]
        )


    def change_side(self) -> None:
        """Change the side to move."""

        self.side_to_move *= -1


    @staticmethod
    def has_single_piece(bitboard) -> bool:
        """
        Check if a bitboard has exactly one piece.
        
        Args:
            bitboard (int): A 64-bit integer representing the bitboard position,

        Returns:
            bool: True if exactly one piece is present, False otherwise.
        """

        return bitboard != 0 and (bitboard & (bitboard - 1)) == 0


    def material_insufficiency(self) -> bool:
        """
        Check if only kings remain on the board.

        Returns:
            bool: True if insufficient material, False otherwise.
        """
        
        if self.pawn or self.rook or self.queen:
            return False

        white_minors = (self.knight | self.bishop) & self.board_occupied_squares[WHITE_INDEX]
        black_minors = (self.knight | self.bishop) & self.board_occupied_squares[BLACK_INDEX]

        if not white_minors and not black_minors:
            return True

        if (Board.has_single_piece(white_minors) and not black_minors) or (Board.has_single_piece(black_minors) and not white_minors):
            return True

        return False
        

    def get_piece_type(self, square) -> "int | None":
        """
        Get the piece type on a given square.

        Args:
            square (int): Square index (0-63).

        Returns:
            int | None: The piece type (PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING) if a piece is present on the square, otherwise None.
        """

        mask = SQUARE_MASKS[square]

        if not self.all_board_occupied_squares & mask:
            return None 
        elif self.pawn & mask:
            return PAWN
        elif self.knight & mask:
            return KNIGHT
        elif self.bishop & mask:
            return BISHOP
        elif self.rook & mask:
            return ROOK
        elif self.queen & mask:
            return QUEEN
        else:
            return KING
        

    def get_piece_type_with_mask(self, mask) -> "int | None":
        """
        Get the piece type using a bitboard mask.

        Args:
            mask (int): A bitboard mask with a single bit set corresponding to the square of interest.

        Returns:
            int | None: The piece type (PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING) if a piece is present on the square corresponding to the mask, otherwise None.
        """

        if not (self.all_board_occupied_squares & mask):
            return None 
        elif self.pawn & mask:
            return PAWN
        elif self.knight & mask:
            return KNIGHT
        elif self.bishop & mask:
            return BISHOP
        elif self.rook & mask:
            return ROOK
        elif self.queen & mask:
            return QUEEN
        else:
            return KING
            
        
    def get_piece_type_and_color(self, square) -> int:
        """
        Get the piece type and color on a given square.

        Args:
            square (int): Square index (0-63).

        Returns:
            int: The piece type with color (positive for white, negative for black, 0 for empty).
        """

        piece_type = self.get_piece_type(square)
        if piece_type:
            mask = SQUARE_MASKS[square]
            color = bool(self.board_occupied_squares[WHITE_INDEX] & mask)
            return piece_type if color else -piece_type
        else:
            return EMPTY
        

    def make_move(self, move, side_to_move, promotion_piece=0) -> tuple:
        """
        Apply a move to the board and return an undo tuple.

        Args:
            move (int): Encoded move value.
            side_to_move (int): Side color (WHITE=1 or BLACK=-1).
            promotion_piece (int, optional): Piece type to promote to (QUEEN, ROOK, BISHOP, KNIGHT), or 0 for no promotion.

        Returns:
            undo (tuple): Undo information for the move.
        """

        from_ = move & 0x3F
        to = (move >> 6) & 0x3F

        from_bitboard = 1 << from_
        to_bitboard = 1 << to

        from_piece = self.get_piece_type_with_mask(from_bitboard)
        to_piece = self.get_piece_type_with_mask(to_bitboard)

        INDEX = WHITE_INDEX if side_to_move == WHITE else BLACK_INDEX
        ATT_INDEX = 1 - INDEX

        if not promotion_piece and from_piece == PAWN:
            if (side_to_move == WHITE and to >= 56) or (side_to_move == BLACK and to <= 7):
                promotion_piece = QUEEN

        en_passant_prev = self.en_passant_square
        castling_rights_prev = self.castling_rights

        undo = (move, from_piece, to_piece, castling_rights_prev, self.counter_halfmove_without_capture, en_passant_prev, promotion_piece)

        self.en_passant_square = 0

        if to_piece:
            if to_piece == PAWN:
                self.pawn &= ~to_bitboard
            elif to_piece == BISHOP:
                self.bishop &= ~to_bitboard
            elif to_piece == KNIGHT:
                self.knight &= ~to_bitboard
            elif to_piece == ROOK:
                self.rook &= ~to_bitboard
                if to == 7: 
                    self.castling_rights &= ~CR_WK
                if to == 0: 
                    self.castling_rights &= ~CR_WQ
                if to == 63: 
                    self.castling_rights &= ~CR_BK
                if to == 56: 
                    self.castling_rights &= ~CR_BQ
            else:
                self.queen &= ~to_bitboard   

            self.counter_halfmove_without_capture = 0
            self.board_occupied_squares[ATT_INDEX] &= ~to_bitboard   
        else:
            self.counter_halfmove_without_capture += 1

        if from_piece == PAWN:
            self.counter_halfmove_without_capture = 0

            if promotion_piece:
                self.pawn &= ~from_bitboard
                if promotion_piece == QUEEN:
                    self.queen |= to_bitboard
                elif promotion_piece == ROOK:
                    self.rook |= to_bitboard
                elif promotion_piece == BISHOP:
                    self.bishop |= to_bitboard
                elif promotion_piece == KNIGHT:
                    self.knight |= to_bitboard
            else:
                self.pawn = (self.pawn & ~from_bitboard) | to_bitboard

                if (to - from_) == 16 or (to - from_) == -16: # Note: abs() is slower
                    self.en_passant_square = (from_ + to) // 2

                elif en_passant_prev != 0 and to == en_passant_prev:
                    if side_to_move == WHITE:
                        captured_pawn_square = to - 8
                    else:
                        captured_pawn_square = to + 8

                    captured_pawn_bitboard = 1 << captured_pawn_square
                    self.pawn &= ~captured_pawn_bitboard
                    self.board_occupied_squares[ATT_INDEX] &= ~captured_pawn_bitboard

        elif from_piece == BISHOP:
            self.bishop = (self.bishop & ~from_bitboard) | to_bitboard

        elif from_piece == KNIGHT:
            self.knight = (self.knight & ~from_bitboard) | to_bitboard

        elif from_piece == ROOK:
            self.rook = (self.rook & ~from_bitboard) | to_bitboard
            if from_ == 7: 
                self.castling_rights &= ~CR_WK
            if from_ == 0: 
                self.castling_rights &= ~CR_WQ
            if from_ == 63: 
                self.castling_rights &= ~CR_BK
            if from_ == 56: 
                self.castling_rights &= ~CR_BQ

        elif from_piece == QUEEN:
            self.queen = (self.queen & ~from_bitboard) | to_bitboard

        else:
            self.king = (self.king & ~from_bitboard) | to_bitboard

            self.king_square[INDEX] = to

            if side_to_move == WHITE:
                self.castling_rights &= ~CR_WK
                self.castling_rights &= ~CR_WQ
            else:
                self.castling_rights &= ~CR_BK
                self.castling_rights &= ~CR_BQ

        if from_piece == KING:
            d = to - from_
            if d == 2:  
                rook_from_mask = 1 << (7 if side_to_move == WHITE else 63)
                rook_to_mask = 1 << (5 if side_to_move == WHITE else 61)

                self.rook = (self.rook & ~rook_from_mask) | rook_to_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_from_mask) | rook_to_mask

            elif d == -2:  
                rook_from_mask = 1 << (0 if side_to_move == WHITE else 56)
                rook_to_mask = 1 << (3 if side_to_move == WHITE else 59)
                
                self.rook = (self.rook & ~rook_from_mask) | rook_to_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_from_mask) | rook_to_mask

        self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~from_bitboard) | to_bitboard
        self.all_board_occupied_squares = self.board_occupied_squares[WHITE_INDEX] | self.board_occupied_squares[BLACK_INDEX]

        return undo
    

    def make_move_search(self, move, side_to_move, promotion_piece=0) -> tuple:
        """
        Apply a move to the board and return an undo tuple.
        This version is primarily used by engines as it also updates the
        game phase and the middlegame/endgame evaluation scores.

        Before calling this function, the variables: mailbox, phase, eg_score and mg score must be defined.
            Ex: board_obj.mailbox = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK] + [PAWN] * 8 + [EMPTY] * 32 + [-PAWN] * 8 + [-ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP, -KNIGHT, -ROOK]

        Args:
            move (int): Encoded move value.
            side_to_move (int): Side color (WHITE=1 or BLACK=-1).
            promotion_piece (int, optional): Piece type to promote to (QUEEN, ROOK, BISHOP, KNIGHT), or 0 for no promotion.
        
        Returns:
            undo (tuple): Undo information for the move.
        """

        from_ = move & 0x3F
        to = (move >> 6) & 0x3F

        from_bitboard = 1 << from_
        to_bitboard = 1 << to

        from_piece = abs(self.mailbox[from_])
        to_piece = abs(self.mailbox[to])

        INDEX = WHITE_INDEX if side_to_move == WHITE else BLACK_INDEX
        ATT_INDEX = 1 - INDEX

        if not promotion_piece and from_piece == PAWN:
            if (side_to_move == WHITE and to >= 56) or (side_to_move == BLACK and to <= 7):
                promotion_piece = QUEEN

        en_passant_prev = self.en_passant_square
        castling_rights_prev = self.castling_rights

        undo = (move, from_piece, to_piece, castling_rights_prev, self.counter_halfmove_without_capture, en_passant_prev, promotion_piece, self.mg_score, self.eg_score, self.phase)

        self.en_passant_square = 0

        if to_piece:
            if to_piece == PAWN:
                self.pawn &= ~to_bitboard
            elif to_piece == BISHOP:
                self.phase -= 1
                self.bishop &= ~to_bitboard
            elif to_piece == KNIGHT:
                self.phase -= 1
                self.knight &= ~to_bitboard
            elif to_piece == ROOK:
                self.rook &= ~to_bitboard
                self.phase -= 2
                if to == 7: 
                    self.castling_rights &= ~CR_WK
                if to == 0: 
                    self.castling_rights &= ~CR_WQ
                if to == 63: 
                    self.castling_rights &= ~CR_BK
                if to == 56: 
                    self.castling_rights &= ~CR_BQ
            else:
                self.queen &= ~to_bitboard   
                self.phase -= 4

            self.counter_halfmove_without_capture = 0
            self.board_occupied_squares[ATT_INDEX] &= ~to_bitboard

            if side_to_move == WHITE:
                self.mg_score += pst[to_piece][MG_INDEX][to ^ 56]
                self.eg_score += pst[to_piece][EG_INDEX][to ^ 56]
            else:
                self.mg_score -= pst[to_piece][MG_INDEX][to]
                self.eg_score -= pst[to_piece][EG_INDEX][to]

        else:
            self.counter_halfmove_without_capture += 1

        if from_piece == PAWN:
            self.counter_halfmove_without_capture = 0

            if promotion_piece:
                self.pawn &= ~from_bitboard
                if promotion_piece == QUEEN:
                    self.queen |= to_bitboard
                elif promotion_piece == ROOK:
                    self.rook |= to_bitboard
                elif promotion_piece == BISHOP:
                    self.bishop |= to_bitboard
                elif promotion_piece == KNIGHT:
                    self.knight |= to_bitboard
                
                if side_to_move == WHITE:
                    self.mg_score -= pst[PAWN][MG_INDEX][from_]
                    self.eg_score -= pst[PAWN][EG_INDEX][from_]
                    self.mg_score += pst[promotion_piece][MG_INDEX][to]
                    self.eg_score += pst[promotion_piece][EG_INDEX][to]
                else:
                    self.mg_score += pst[PAWN][MG_INDEX][from_ ^ 56]
                    self.eg_score += pst[PAWN][EG_INDEX][from_ ^ 56]
                    self.mg_score -= pst[promotion_piece][MG_INDEX][to ^ 56]
                    self.eg_score -= pst[promotion_piece][EG_INDEX][to ^ 56]
            else:
                self.pawn = (self.pawn & ~from_bitboard) | to_bitboard

                if side_to_move == WHITE:
                    self.mg_score -= pst[PAWN][MG_INDEX][from_]
                    self.eg_score -= pst[PAWN][EG_INDEX][from_]
                    self.mg_score += pst[PAWN][MG_INDEX][to]
                    self.eg_score += pst[PAWN][EG_INDEX][to]
                else:
                    self.mg_score += pst[PAWN][MG_INDEX][from_ ^ 56]
                    self.eg_score += pst[PAWN][EG_INDEX][from_ ^ 56]
                    self.mg_score -= pst[PAWN][MG_INDEX][to ^ 56]
                    self.eg_score -= pst[PAWN][EG_INDEX][to ^ 56]

                if (to - from_) == 16 or (to - from_) == -16: # Note abs() is slower than direct comparison
                    self.en_passant_square = (from_ + to) // 2

                elif en_passant_prev != 0 and to == en_passant_prev:
                    if side_to_move == WHITE:
                        captured_pawn_square = to - 8
                    else:
                        captured_pawn_square = to + 8

                    captured_pawn_bitboard = 1 << captured_pawn_square
                    self.pawn &= ~captured_pawn_bitboard
                    self.board_occupied_squares[ATT_INDEX] &= ~captured_pawn_bitboard
                    
                    if side_to_move == WHITE:
                        self.mg_score += pst[PAWN][MG_INDEX][captured_pawn_square ^ 56]
                        self.eg_score += pst[PAWN][EG_INDEX][captured_pawn_square ^ 56]
                    else:
                        self.mg_score -= pst[PAWN][MG_INDEX][captured_pawn_square]
                        self.eg_score -= pst[PAWN][EG_INDEX][captured_pawn_square]

        elif from_piece == BISHOP:
            self.bishop = (self.bishop & ~from_bitboard) | to_bitboard
            if side_to_move == WHITE:
                self.mg_score -= pst[BISHOP][MG_INDEX][from_]
                self.eg_score -= pst[BISHOP][EG_INDEX][from_]
                self.mg_score += pst[BISHOP][MG_INDEX][to]
                self.eg_score += pst[BISHOP][EG_INDEX][to]
            else:
                self.mg_score += pst[BISHOP][MG_INDEX][from_ ^ 56]
                self.eg_score += pst[BISHOP][EG_INDEX][from_ ^ 56]
                self.mg_score -= pst[BISHOP][MG_INDEX][to ^ 56]
                self.eg_score -= pst[BISHOP][EG_INDEX][to ^ 56]

        elif from_piece == KNIGHT:
            self.knight = (self.knight & ~from_bitboard) | to_bitboard
            if side_to_move == WHITE:
                self.mg_score -= pst[KNIGHT][MG_INDEX][from_]
                self.eg_score -= pst[KNIGHT][EG_INDEX][from_]
                self.mg_score += pst[KNIGHT][MG_INDEX][to]
                self.eg_score += pst[KNIGHT][EG_INDEX][to]
            else:
                self.mg_score += pst[KNIGHT][MG_INDEX][from_ ^ 56]
                self.eg_score += pst[KNIGHT][EG_INDEX][from_ ^ 56]
                self.mg_score -= pst[KNIGHT][MG_INDEX][to ^ 56]
                self.eg_score -= pst[KNIGHT][EG_INDEX][to ^ 56]

        elif from_piece == ROOK:
            self.rook = (self.rook & ~from_bitboard) | to_bitboard
            if side_to_move == WHITE:
                self.mg_score -= pst[ROOK][MG_INDEX][from_]
                self.eg_score -= pst[ROOK][EG_INDEX][from_]
                self.mg_score += pst[ROOK][MG_INDEX][to]
                self.eg_score += pst[ROOK][EG_INDEX][to]
            else:
                self.mg_score += pst[ROOK][MG_INDEX][from_ ^ 56]
                self.eg_score += pst[ROOK][EG_INDEX][from_ ^ 56]
                self.mg_score -= pst[ROOK][MG_INDEX][to ^ 56]
                self.eg_score -= pst[ROOK][EG_INDEX][to ^ 56]
            
            if from_ == 7: 
                self.castling_rights &= ~CR_WK
            if from_ == 0: 
                self.castling_rights &= ~CR_WQ
            if from_ == 63: 
                self.castling_rights &= ~CR_BK
            if from_ == 56: 
                self.castling_rights &= ~CR_BQ

        elif from_piece == QUEEN:
            self.queen = (self.queen & ~from_bitboard) | to_bitboard
            if side_to_move == WHITE:
                self.mg_score -= pst[QUEEN][MG_INDEX][from_]
                self.eg_score -= pst[QUEEN][EG_INDEX][from_]
                self.mg_score += pst[QUEEN][MG_INDEX][to]
                self.eg_score += pst[QUEEN][EG_INDEX][to]
            else:
                self.mg_score += pst[QUEEN][MG_INDEX][from_ ^ 56]
                self.eg_score += pst[QUEEN][EG_INDEX][from_ ^ 56]
                self.mg_score -= pst[QUEEN][MG_INDEX][to ^ 56]
                self.eg_score -= pst[QUEEN][EG_INDEX][to ^ 56]

        else:
            self.king = (self.king & ~from_bitboard) | to_bitboard

            self.king_square[INDEX] = to
            
            if side_to_move == WHITE:
                self.mg_score -= pst[KING][MG_INDEX][from_]
                self.eg_score -= pst[KING][EG_INDEX][from_]
                self.mg_score += pst[KING][MG_INDEX][to]
                self.eg_score += pst[KING][EG_INDEX][to]
            else:
                self.mg_score += pst[KING][MG_INDEX][from_ ^ 56]
                self.eg_score += pst[KING][EG_INDEX][from_ ^ 56]
                self.mg_score -= pst[KING][MG_INDEX][to ^ 56]
                self.eg_score -= pst[KING][EG_INDEX][to ^ 56]

            if side_to_move == WHITE:
                self.castling_rights &= ~CR_WK
                self.castling_rights &= ~CR_WQ
            else:
                self.castling_rights &= ~CR_BK
                self.castling_rights &= ~CR_BQ

        if from_piece == KING:
            d = to - from_
            if d == 2:  
                rook_from_mask = 1 << (7 if side_to_move == WHITE else 63)
                rook_to_mask = 1 << (5 if side_to_move == WHITE else 61)

                self.rook = (self.rook & ~rook_from_mask) | rook_to_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_from_mask) | rook_to_mask
                
                if side_to_move == WHITE:
                    self.mg_score -= pst[ROOK][MG_INDEX][7]
                    self.eg_score -= pst[ROOK][EG_INDEX][7]
                    self.mg_score += pst[ROOK][MG_INDEX][5]
                    self.eg_score += pst[ROOK][EG_INDEX][5]
                else:
                    self.mg_score += pst[ROOK][MG_INDEX][63 ^ 56]
                    self.eg_score += pst[ROOK][EG_INDEX][63 ^ 56]
                    self.mg_score -= pst[ROOK][MG_INDEX][61 ^ 56]
                    self.eg_score -= pst[ROOK][EG_INDEX][61 ^ 56]

            elif d == -2:  
                rook_from_mask = 1 << (0 if side_to_move == WHITE else 56)
                rook_to_mask = 1 << (3 if side_to_move == WHITE else 59)
                
                self.rook = (self.rook & ~rook_from_mask) | rook_to_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_from_mask) | rook_to_mask
                
                if side_to_move == WHITE:
                    self.mg_score -= pst[ROOK][MG_INDEX][0]
                    self.eg_score -= pst[ROOK][EG_INDEX][0]
                    self.mg_score += pst[ROOK][MG_INDEX][3]
                    self.eg_score += pst[ROOK][EG_INDEX][3]
                else:
                    self.mg_score += pst[ROOK][MG_INDEX][56 ^ 56]
                    self.eg_score += pst[ROOK][EG_INDEX][56 ^ 56]
                    self.mg_score -= pst[ROOK][MG_INDEX][59 ^ 56]
                    self.eg_score -= pst[ROOK][EG_INDEX][59 ^ 56]

        self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~from_bitboard) | to_bitboard
        self.all_board_occupied_squares = self.board_occupied_squares[WHITE_INDEX] | self.board_occupied_squares[BLACK_INDEX]

        if promotion_piece:
            self.mailbox[to] = promotion_piece if side_to_move == WHITE else -promotion_piece
        else:
            self.mailbox[to] = self.mailbox[from_]
        
        self.mailbox[from_] = EMPTY

        if from_piece == PAWN and not promotion_piece and en_passant_prev != 0 and to == en_passant_prev:
            self.mailbox[to - 8 if side_to_move == WHITE else to + 8] = EMPTY
        elif from_piece == KING:
            d = to - from_
            if d == 2:
                self.mailbox[5 if side_to_move == WHITE else 61] = self.mailbox[7 if side_to_move == WHITE else 63]
                self.mailbox[7 if side_to_move == WHITE else 63] = EMPTY
            elif d == -2:
                self.mailbox[3 if side_to_move == WHITE else 59] = self.mailbox[0 if side_to_move == WHITE else 56]
                self.mailbox[0 if side_to_move == WHITE else 56] = EMPTY

        return undo
    

    def unmake_move(self, undo, side_to_move) -> None:
        """
        Revert a move using the provided undo information.

        Args:
            undo (tuple): Undo information for the move.
            side_to_move (int): Side color (WHITE=1 or BLACK=-1).

        Returns:
            None
        """

        move, from_piece, to_piece, castling_rights_prev, counter_halfmove_without_capture, en_passant_prev, promotion_piece = undo

        from_ = move & 0x3F
        to = (move >> 6) & 0x3F

        from_bitboard = 1 << from_
        to_bitboard = 1 << to

        INDEX = WHITE_INDEX if side_to_move == WHITE else BLACK_INDEX
        ATT_INDEX = 1 - INDEX

        self.castling_rights = castling_rights_prev

        if from_piece == KING:
            d = to - from_
            if d == 2:
                rook_from_mask = 1 << (7 if side_to_move == WHITE else 63)
                rook_to_mask = 1 << (5 if side_to_move == WHITE else 61)

                self.rook = (self.rook & ~rook_to_mask) | rook_from_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_to_mask) | rook_from_mask

            elif d == -2:
                rook_from_mask = 1 << (0 if side_to_move == WHITE else 56)
                rook_to_mask = 1 << (3 if side_to_move == WHITE else 59)

                self.rook = (self.rook & ~rook_to_mask) | rook_from_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_to_mask) | rook_from_mask

        if from_piece == PAWN:
            if promotion_piece:
                if promotion_piece == QUEEN:
                    self.queen &= ~to_bitboard
                elif promotion_piece == ROOK:
                    self.rook &= ~to_bitboard
                elif promotion_piece == BISHOP:
                    self.bishop &= ~to_bitboard
                elif promotion_piece == KNIGHT:
                    self.knight &= ~to_bitboard
                self.pawn |= from_bitboard
            else:
                self.pawn = (self.pawn & ~to_bitboard) | from_bitboard
                
                if to == en_passant_prev and en_passant_prev != 0:
                    if side_to_move == WHITE:
                        captured_pawn_square = to - 8
                    else:
                        captured_pawn_square = to + 8

                    captured_pawn_bitboard = 1 << captured_pawn_square
                    self.pawn |= captured_pawn_bitboard
                    self.board_occupied_squares[ATT_INDEX] |= captured_pawn_bitboard

        elif from_piece == BISHOP:
            self.bishop = (self.bishop & ~to_bitboard) | from_bitboard
        elif from_piece == KNIGHT:
            self.knight = (self.knight & ~to_bitboard) | from_bitboard
        elif from_piece == ROOK:
            self.rook = (self.rook & ~to_bitboard) | from_bitboard
        elif from_piece == QUEEN:
            self.queen = (self.queen & ~to_bitboard) | from_bitboard
        else:
            self.king = (self.king & ~to_bitboard) | from_bitboard
            self.king_square[INDEX] = from_

        if to_piece:
            if to_piece == PAWN:
                self.pawn |= to_bitboard
            elif to_piece == BISHOP:
                self.bishop |= to_bitboard
            elif to_piece == KNIGHT: 
                self.knight |= to_bitboard
            elif to_piece == ROOK: 
                self.rook |= to_bitboard
            elif to_piece == QUEEN: 
                self.queen |= to_bitboard
            else:
                self.king |= to_bitboard

            self.board_occupied_squares[ATT_INDEX] |= to_bitboard
        
        self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~to_bitboard) | from_bitboard
        self.all_board_occupied_squares = self.board_occupied_squares[WHITE_INDEX] | self.board_occupied_squares[BLACK_INDEX]
        self.counter_halfmove_without_capture = counter_halfmove_without_capture
        self.en_passant_square = en_passant_prev


    def unmake_move_search(self, undo, side_to_move) -> None:
        """
        Revert a move using the provided undo information.
        This version is primarily used by engines as it also updates the
        game phase and the middlegame/endgame evaluation scores.

        Before calling this function, the variables: mailbox, phase, eg_score and mg score must be defined.
            Ex: board_obj.mailbox = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK] + [PAWN] * 8 + [EMPTY] * 32 + [-PAWN] * 8 + [-ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP, -KNIGHT, -ROOK]

        Args:
            undo (tuple): Undo information for the move.
            side_to_move (int): Side color (WHITE=1 or BLACK=-1).

        Returns:
            None
        """

        move, from_piece, to_piece, castling_rights_prev, counter_halfmove_without_capture, en_passant_prev, promotion_piece, old_mg_score, old_eg_score, old_phase = undo

        self.mg_score = old_mg_score
        self.eg_score = old_eg_score
        self.phase = old_phase

        from_ = move & 0x3F
        to = (move >> 6) & 0x3F

        from_bitboard = 1 << from_
        to_bitboard = 1 << to

        INDEX = WHITE_INDEX if side_to_move == WHITE else BLACK_INDEX
        ATT_INDEX = 1 - INDEX

        color_sign = 1 if side_to_move == WHITE else -1
        self.mailbox[from_] = from_piece * color_sign

        if to_piece == 0:
            self.mailbox[to] = EMPTY
        else:
            self.mailbox[to] = to_piece * (-color_sign)

        self.castling_rights = castling_rights_prev

        if from_piece == KING:
            d = to - from_
            if d == 2:
                rook_from_mask = 1 << (7 if side_to_move == WHITE else 63)
                rook_to_mask = 1 << (5 if side_to_move == WHITE else 61)

                self.rook = (self.rook & ~rook_to_mask) | rook_from_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_to_mask) | rook_from_mask
                
                self.mailbox[7 if side_to_move == WHITE else 63] = self.mailbox[5 if side_to_move == WHITE else 61]
                self.mailbox[5 if side_to_move == WHITE else 61] = EMPTY

            elif d == -2:
                rook_from_mask = 1 << (0 if side_to_move == WHITE else 56)
                rook_to_mask = 1 << (3 if side_to_move == WHITE else 59)

                self.rook = (self.rook & ~rook_to_mask) | rook_from_mask
                self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~rook_to_mask) | rook_from_mask
                
                self.mailbox[0 if side_to_move == WHITE else 56] = self.mailbox[3 if side_to_move == WHITE else 59]
                self.mailbox[3 if side_to_move == WHITE else 59] = EMPTY

        if from_piece == PAWN:
            if promotion_piece:
                if promotion_piece == QUEEN:
                    self.queen &= ~to_bitboard
                elif promotion_piece == ROOK:
                    self.rook &= ~to_bitboard
                elif promotion_piece == BISHOP:
                    self.bishop &= ~to_bitboard
                elif promotion_piece == KNIGHT:
                    self.knight &= ~to_bitboard
                self.pawn |= from_bitboard
            else:
                self.pawn = (self.pawn & ~to_bitboard) | from_bitboard
                
                if to == en_passant_prev and en_passant_prev != 0:
                    if side_to_move == WHITE:
                        captured_pawn_square = to - 8
                    else:
                        captured_pawn_square = to + 8

                    captured_pawn_bitboard = 1 << captured_pawn_square
                    self.pawn |= captured_pawn_bitboard
                    self.board_occupied_squares[ATT_INDEX] |= captured_pawn_bitboard
                    
                    self.mailbox[captured_pawn_square] = PAWN * (-color_sign)
                    self.mailbox[to] = EMPTY

        elif from_piece == BISHOP:
            self.bishop = (self.bishop & ~to_bitboard) | from_bitboard
        elif from_piece == KNIGHT:
            self.knight = (self.knight & ~to_bitboard) | from_bitboard
        elif from_piece == ROOK:
            self.rook = (self.rook & ~to_bitboard) | from_bitboard
        elif from_piece == QUEEN:
            self.queen = (self.queen & ~to_bitboard) | from_bitboard
        else:
            self.king = (self.king & ~to_bitboard) | from_bitboard
            self.king_square[INDEX] = from_

        if to_piece:
            if to_piece == PAWN:
                self.pawn |= to_bitboard
            elif to_piece == BISHOP:
                self.bishop |= to_bitboard
            elif to_piece == KNIGHT: 
                self.knight |= to_bitboard
            elif to_piece == ROOK: 
                self.rook |= to_bitboard
            elif to_piece == QUEEN: 
                self.queen |= to_bitboard
            else:
                self.king |= to_bitboard

            self.board_occupied_squares[ATT_INDEX] |= to_bitboard
        
        self.board_occupied_squares[INDEX] = (self.board_occupied_squares[INDEX] & ~to_bitboard) | from_bitboard
        self.all_board_occupied_squares = self.board_occupied_squares[WHITE_INDEX] | self.board_occupied_squares[BLACK_INDEX]
        self.counter_halfmove_without_capture = counter_halfmove_without_capture
        self.en_passant_square = en_passant_prev



class MoveGen:    
    @staticmethod  
    def list_all_pawn_moves(board_obj, color) -> list[int]:
        """
        Generate all valid pawn moves for the specified color, including en passant.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_p_moves = []
        append = list_p_moves.append

        all_occ = board_obj.all_board_occupied_squares
        en_passant_square = board_obj.en_passant_square

        if color == WHITE:
            empty_board = (~all_occ) & U64
            enemy_board = board_obj.board_occupied_squares[BLACK_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[WHITE_INDEX]

            move1 = (pawn_board << 8) & empty_board
            move2 = ((move1 & RANK_MASKS[2]) << 8) & empty_board

            capt1 = (pawn_board << 7) & enemy_board & ~FILE_MASKS[7]
            capt2 = (pawn_board << 9) & enemy_board & ~FILE_MASKS[0]

            while move1:
                least_significant_bit = move1 & -move1
                to = least_significant_bit.bit_length() - 1
                move1 ^= least_significant_bit
                append(to * 65 - 8)

            while move2:
                least_significant_bit = move2 & -move2
                to = least_significant_bit.bit_length() - 1
                move2 ^= least_significant_bit
                append(to * 65 - 16)

            while capt1:
                least_significant_bit = capt1 & -capt1
                to = least_significant_bit.bit_length() - 1
                capt1 ^= least_significant_bit
                append(to * 65 - 7)

            while capt2:
                least_significant_bit = capt2 & -capt2
                to = least_significant_bit.bit_length() - 1
                capt2 ^= least_significant_bit
                append(to * 65 - 9)

            if en_passant_square:
                en_passant_SQUARE_MASKS = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_SQUARE_MASKS & ~FILE_MASKS[0]) >> 9) | ((en_passant_SQUARE_MASKS & ~FILE_MASKS[7]) >> 7))
                while en_passant_square_attackers:
                    least_significant_bit = en_passant_square_attackers & -en_passant_square_attackers
                    from_ = least_significant_bit.bit_length() - 1
                    en_passant_square_attackers ^= least_significant_bit
                    append(from_ | (en_passant_square << 6))

        else:
            empty_board = (~all_occ) & U64
            enemy_board = board_obj.board_occupied_squares[WHITE_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[BLACK_INDEX]

            move1 = (pawn_board >> 8) & empty_board
            move2 = ((move1 & RANK_MASKS[5]) >> 8) & empty_board

            capt1 = (pawn_board >> 7) & enemy_board & ~FILE_MASKS[0]
            capt2 = (pawn_board >> 9) & enemy_board & ~FILE_MASKS[7]

            while move1:
                least_significant_bit = move1 & -move1
                to = least_significant_bit.bit_length() - 1
                move1 ^= least_significant_bit
                append(to * 65 + 8)

            while move2:
                least_significant_bit = move2 & -move2
                to = least_significant_bit.bit_length() - 1
                move2 ^= least_significant_bit
                append(to * 65 + 16)

            while capt1:
                least_significant_bit = capt1 & -capt1
                to = least_significant_bit.bit_length() - 1
                capt1 ^= least_significant_bit
                append(to * 65 + 7)

            while capt2:
                least_significant_bit = capt2 & -capt2
                to = least_significant_bit.bit_length() - 1
                capt2 ^= least_significant_bit
                append(to * 65 + 9)

            if en_passant_square:
                en_passant_SQUARE_MASKS = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_SQUARE_MASKS & ~FILE_MASKS[0]) << 7) | ((en_passant_SQUARE_MASKS & ~FILE_MASKS[7]) << 9))
                while en_passant_square_attackers:
                    least_significant_bit = en_passant_square_attackers & -en_passant_square_attackers
                    from_ = least_significant_bit.bit_length() - 1
                    en_passant_square_attackers ^= least_significant_bit
                    append(from_ | (en_passant_square << 6))

        return list_p_moves

    
    @staticmethod
    def list_all_pawn_captures(board_obj, color) -> list[int]:
        """
        Generate all valid pawn capture moves (excluding promotion captures) for the specified color, including en passant.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
        """

        list_p_captures = []
        append = list_p_captures.append

        en_passant_square = board_obj.en_passant_square

        if color == WHITE:
            enemy_board = board_obj.board_occupied_squares[BLACK_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[WHITE_INDEX]

            capt1 = (pawn_board << 7) & enemy_board & ~FILE_MASKS[7] & ~RANK_MASKS[7]
            capt2 = (pawn_board << 9) & enemy_board & ~FILE_MASKS[0] & ~RANK_MASKS[7]

            while capt1:
                least_significant_bit = capt1 & -capt1
                to = least_significant_bit.bit_length() - 1
                capt1 ^= least_significant_bit
                append(to * 65 - 7)

            while capt2:
                least_significant_bit = capt2 & -capt2
                to = least_significant_bit.bit_length() - 1
                capt2 ^= least_significant_bit
                append(to * 65 - 9)

            if en_passant_square:
                en_passant_SQUARE_MASKS = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_SQUARE_MASKS & ~FILE_MASKS[0]) >> 9) | ((en_passant_SQUARE_MASKS & ~FILE_MASKS[7]) >> 7))
                while en_passant_square_attackers:
                    least_significant_bit = en_passant_square_attackers & -en_passant_square_attackers
                    from_ = least_significant_bit.bit_length() - 1
                    en_passant_square_attackers ^= least_significant_bit
                    append(from_ | (en_passant_square << 6))

        else: 
            enemy_board = board_obj.board_occupied_squares[WHITE_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[BLACK_INDEX]

            capt1 = (pawn_board >> 7) & enemy_board & ~FILE_MASKS[0] & ~RANK_MASKS[0]
            capt2 = (pawn_board >> 9) & enemy_board & ~FILE_MASKS[7] & ~RANK_MASKS[0]

            while capt1:
                least_significant_bit = capt1 & -capt1
                to = least_significant_bit.bit_length() - 1
                capt1 ^= least_significant_bit
                append(to * 65 + 7)

            while capt2:
                least_significant_bit = capt2 & -capt2
                to = least_significant_bit.bit_length() - 1
                capt2 ^= least_significant_bit
                append(to * 65 + 9)

            if en_passant_square:
                en_passant_SQUARE_MASKS = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_SQUARE_MASKS & ~FILE_MASKS[0]) << 7) | ((en_passant_SQUARE_MASKS & ~FILE_MASKS[7]) << 9))
                while en_passant_square_attackers:
                    least_significant_bit = en_passant_square_attackers & -en_passant_square_attackers
                    from_ = least_significant_bit.bit_length() - 1
                    en_passant_square_attackers ^= least_significant_bit
                    append(from_ | (en_passant_square << 6))

        return list_p_captures


    @staticmethod
    def list_all_pawn_promotions(board_obj, color) -> list[int]:
        """
        Generate all pawn promotion moves (push and capture promotions) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_p_promotions = []
        append = list_p_promotions.append

        if color == WHITE:
            empty_board = (~board_obj.all_board_occupied_squares) & U64
            enemy_board = board_obj.board_occupied_squares[BLACK_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[WHITE_INDEX]

            promo_push = (pawn_board << 8) & empty_board & RANK_MASKS[7]
            promo_capt1 = (pawn_board << 7) & enemy_board & ~FILE_MASKS[7] & RANK_MASKS[7]
            promo_capt2 = (pawn_board << 9) & enemy_board & ~FILE_MASKS[0] & RANK_MASKS[7]

            while promo_push:
                least_significant_bit = promo_push & -promo_push
                to = least_significant_bit.bit_length() - 1
                promo_push ^= least_significant_bit
                append(to * 65 - 8)

            while promo_capt1:
                least_significant_bit = promo_capt1 & -promo_capt1
                to = least_significant_bit.bit_length() - 1
                promo_capt1 ^= least_significant_bit
                append(to * 65 - 7)

            while promo_capt2:
                least_significant_bit = promo_capt2 & -promo_capt2
                to = least_significant_bit.bit_length() - 1
                promo_capt2 ^= least_significant_bit
                append(to * 65 - 9)

        else:
            empty_board = (~board_obj.all_board_occupied_squares) & U64
            enemy_board = board_obj.board_occupied_squares[WHITE_INDEX]
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[BLACK_INDEX]

            promo_push = (pawn_board >> 8) & empty_board & RANK_MASKS[0]
            promo_capt1 = (pawn_board >> 7) & enemy_board & ~FILE_MASKS[0] & RANK_MASKS[0]
            promo_capt2 = (pawn_board >> 9) & enemy_board & ~FILE_MASKS[7] & RANK_MASKS[0]

            while promo_push:
                least_significant_bit = promo_push & -promo_push
                to = least_significant_bit.bit_length() - 1
                promo_push ^= least_significant_bit
                append(to * 65 + 8)

            while promo_capt1:
                least_significant_bit = promo_capt1 & -promo_capt1
                to = least_significant_bit.bit_length() - 1
                promo_capt1 ^= least_significant_bit
                append(to * 65 + 7)

            while promo_capt2:
                least_significant_bit = promo_capt2 & -promo_capt2
                to = least_significant_bit.bit_length() - 1
                promo_capt2 ^= least_significant_bit
                append(to * 65 + 9)

        return list_p_promotions
    

    @staticmethod
    def list_all_knight_moves(board_obj, color) -> list[int]:
        """
        Generate all valid knight moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_moves = []
        append = list_k_moves.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        
        knight_board = board_obj.knight & own_occupied_squares
        
        free_squares = (~own_occupied_squares) & U64 

        while knight_board:
            least_significant_bit = knight_board & -knight_board
            from_ = least_significant_bit.bit_length() - 1
            knight_board &= knight_board - 1

            to_possibilities = KNIGHT_TABLE[from_] & free_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_k_moves
    

    @staticmethod
    def list_all_knight_captures(board_obj, color) -> list[int]:
        """
        Generate all valid knight captures for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_captures = []
        append = list_k_captures.append

        knight_board = board_obj.knight & board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        while knight_board:
            least_significant_bit = knight_board & -knight_board
            from_ = least_significant_bit.bit_length() - 1
            knight_board &= knight_board - 1

            to_possibilities = KNIGHT_TABLE[from_] & board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_k_captures


    @staticmethod
    def list_all_rook_moves(board_obj, color) -> list[int]:
        """
        Generate all valid rook moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_r_moves = []
        append = list_r_moves.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        rook = board_obj.rook & own_occupied_squares
        free_squares = (~own_occupied_squares) & U64 

        occ = board_obj.all_board_occupied_squares

        while rook:
            least_significant_bit = rook & -rook
            from_ = least_significant_bit.bit_length() - 1

            rook &= rook - 1
            
            occ_rel = occ & ROOK_MASK[from_]
            idx = ((occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]
            
            to_possibilities = ROOK_TABLE[from_][idx] & free_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))
        
        return list_r_moves
    

    @staticmethod
    def list_all_rook_captures(board_obj, color) -> list[int]:
        """
        Generate all valid rook captures for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_r_captures = []
        append = list_r_captures.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        rook = board_obj.rook & own_occupied_squares

        occ = board_obj.all_board_occupied_squares

        while rook:
            least_significant_bit = rook & -rook
            from_ = least_significant_bit.bit_length() - 1

            rook &= rook - 1
            
            occ_rel = occ & ROOK_MASK[from_]
            idx = ((occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]
            
            to_possibilities = ROOK_TABLE[from_][idx] & board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))
        
        return list_r_captures
    

    @staticmethod
    def list_all_bishop_moves(board_obj, color) -> list[int]:
        """
        Generate all valid bishop moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_b_moves = []
        append = list_b_moves.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        bishop = board_obj.bishop & own_occupied_squares
        free_squares = (~own_occupied_squares) & U64 

        occ = board_obj.all_board_occupied_squares

        while bishop:
            least_significant_bit = bishop & -bishop
            from_ = least_significant_bit.bit_length() - 1

            bishop &= bishop - 1
            
            occ_rel = occ & BISHOP_MASK[from_]
            idx = ((occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            
            to_possibilities = BISHOP_TABLE[from_][idx] & free_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))
        
        return list_b_moves
    

    @staticmethod
    def list_all_bishop_captures(board_obj, color) -> list[int]:
        """
        Generate all valid bishop captures for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_b_captures = []
        append = list_b_captures.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        bishop = board_obj.bishop & own_occupied_squares

        occ = board_obj.all_board_occupied_squares

        while bishop:
            least_significant_bit = bishop & -bishop
            from_ = least_significant_bit.bit_length() - 1

            bishop &= bishop - 1
            
            occ_rel = occ & BISHOP_MASK[from_]
            idx = ((occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            
            to_possibilities = BISHOP_TABLE[from_][idx] & board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))
        
        return list_b_captures
    

    @staticmethod
    def list_all_queen_moves(board_obj, color) -> list[int]:
        """
        Generate all queen moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_q_moves = []
        append = list_q_moves.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        queen = board_obj.queen & own_occupied_squares
        free_squares = (~own_occupied_squares) & U64 

        occ = board_obj.all_board_occupied_squares

        while queen:
            least_significant_bit = queen & -queen
            from_ = least_significant_bit.bit_length() - 1

            queen &= queen - 1
            
            bishop_occ_rel = occ & BISHOP_MASK[from_]
            bishop_idx = ((bishop_occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            
            rook_occ_rel = occ & ROOK_MASK[from_]
            rook_idx = ((rook_occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]

            to_possibilities = (ROOK_TABLE[from_][rook_idx] | BISHOP_TABLE[from_][bishop_idx]) & free_squares

            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_q_moves


    @staticmethod
    def list_all_queen_captures(board_obj, color) -> list[int]:
        """
        Generate all queen captures for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_q_captures = []
        append = list_q_captures.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        queen = board_obj.queen & own_occupied_squares

        occ = board_obj.all_board_occupied_squares

        while queen:
            least_significant_bit = queen & -queen
            from_ = least_significant_bit.bit_length() - 1

            queen &= queen - 1
            
            bishop_occ_rel = occ & BISHOP_MASK[from_]
            bishop_idx = ((bishop_occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            
            rook_occ_rel = occ & ROOK_MASK[from_]
            rook_idx = ((rook_occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]

            to_possibilities = (ROOK_TABLE[from_][rook_idx] | BISHOP_TABLE[from_][bishop_idx]) & board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]

            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_q_captures


    @staticmethod
    def list_all_king_moves(board_obj, color, castling=True) -> list[int]:
        """
        Generate all king moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            castling (optional bool): Whether to include castling moves. Defaults to True.

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_moves = []

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        king_board = board_obj.king & own_occupied_squares

        free_squares = (~own_occupied_squares) & U64 

        from_ = king_board.bit_length() - 1

        append = list_k_moves.append

        to_possibilities = KING_TABLE[from_] & free_squares
        while to_possibilities:
            least_significant_bit2 = to_possibilities & -to_possibilities
            to = least_significant_bit2.bit_length() - 1
            to_possibilities &= to_possibilities - 1

            append(from_ | (to << 6))

        if castling:
            list_k_moves.extend(MoveGen.list_all_castling_move(board_obj, color))

        return list_k_moves
    

    @staticmethod
    def list_all_king_captures(board_obj, color, castling=True) -> list[int]:
        """
        Generate all king captures for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            castling (optional bool): Whether to include castling moves. Defaults to True.

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_captures = []

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        king_board = board_obj.king & own_occupied_squares

        from_ = king_board.bit_length() - 1

        append = list_k_captures.append

        to_possibilities = KING_TABLE[from_] & board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        while to_possibilities:
            least_significant_bit2 = to_possibilities & -to_possibilities
            to = least_significant_bit2.bit_length() - 1
            to_possibilities &= to_possibilities - 1

            append(from_ | (to << 6))

        return list_k_captures
    
    
    @staticmethod
    def list_all_castling_move(board_obj, color) -> list[int]:
        """
        Generate all castling moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
        
        Returns:
            list: Encoded castling moves as (from_square | (to_square << 6)).
        """

        list_castling_moves = []

        rights = board_obj.castling_rights
        all_board_occupied_squares = board_obj.all_board_occupied_squares
        attackers_to = GameState.attackers_to
        append = list_castling_moves.append

        if color == WHITE:
            canKingsideCastling = (rights & CR_WK) and (all_board_occupied_squares & WK_EMPTY) == 0
            canQueensideCastling = (rights & CR_WQ) and (all_board_occupied_squares & WQ_EMPTY) == 0
            if not (canKingsideCastling or canQueensideCastling):
                return list_castling_moves

            if attackers_to(board_obj, WHITE, 4):
                return list_castling_moves

            if canKingsideCastling and (not attackers_to(board_obj, WHITE, 5)):
                append(4 | (6 << 6))

            if canQueensideCastling and (not attackers_to(board_obj, WHITE, 3)):
                append(4 | (2 << 6))

        else:
            canKingsideCastling = (rights & CR_BK) and (all_board_occupied_squares & BK_EMPTY) == 0
            canQueensideCastling = (rights & CR_BQ) and (all_board_occupied_squares & BQ_EMPTY) == 0
            if not (canKingsideCastling or canQueensideCastling):
                return list_castling_moves

            if attackers_to(board_obj, BLACK, 60):
                return list_castling_moves

            if canKingsideCastling and (not attackers_to(board_obj, BLACK, 61)):
                append(60 | (62 << 6))

            if canQueensideCastling and (not attackers_to(board_obj, BLACK, 59)):
                append(60 | (58 << 6))

        return list_castling_moves
    

    @staticmethod
    def list_all_legal_moves(board_obj, side, castling = True) -> list[int]:
        """
        Generate all legal moves for a side (excluding moves leaving king in check).
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.
        
        Returns:
            list: Encoded legal moves as (from_square | (to_square << 6)).
        """
        
        list_all_moves = []
        append = list_all_moves.append

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        gens = (
            MoveGen.list_all_pawn_moves,
            MoveGen.list_all_knight_moves,
            MoveGen.list_all_bishop_moves,
            MoveGen.list_all_rook_moves,
            MoveGen.list_all_queen_moves,
            lambda b, s: MoveGen.list_all_king_moves(b, s, castling),
        )

        for gen in gens:
            for mv in gen(board_obj, side):
                undo = make(mv, side)
                if not attackers_to(board_obj, side, king_square[INDEX]):
                    append(mv)
                unmake(undo, side)

        return list_all_moves


    @staticmethod
    def generate_all_moves(board_obj, side, castling = True):
        """
        Generate all legal moves for a side (excluding moves leaving king in check).
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.
        
        Yields:
            generator: Yields encoded moves as (from_square | (to_square << 6)).
        """

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        for e in MoveGen.list_all_king_moves(board_obj, side, castling):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_queen_moves(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_knight_moves(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
    
        for e in MoveGen.list_all_bishop_moves(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_rook_moves(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_pawn_moves(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e


    @staticmethod
    def list_all_legal_captures(board_obj, side) -> list[int]:
        """
        Generate all legal captures for a side (excluding moves leaving king in check).
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """
        
        list_all_captures = []
        append = list_all_captures.append

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        gens = (
            MoveGen.list_all_pawn_captures,
            MoveGen.list_all_knight_captures,
            MoveGen.list_all_bishop_captures,
            MoveGen.list_all_rook_captures,
            MoveGen.list_all_queen_captures,
            lambda b, s: MoveGen.list_all_king_captures(b, s, False),
        )

        for gen in gens:
            for mv in gen(board_obj, side):
                undo = make(mv, side)
                if not attackers_to(board_obj, side, king_square[INDEX]):
                    append(mv)
                unmake(undo, side)

        return list_all_captures
    

    @staticmethod
    def generate_all_captures(board_obj, side):
        """
        Generate all legal captures for a side (excluding moves leaving king in check).
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
        
        Yields:
            generator: Yields encoded moves as (from_square | (to_square << 6)).
        """

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        for e in MoveGen.list_all_king_captures(board_obj, side, castling = False):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_queen_captures(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_knight_captures(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
    
        for e in MoveGen.list_all_bishop_captures(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_rook_captures(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_pawn_captures(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e


    @staticmethod
    def list_all_piece_move(board_obj, square, piece_value) -> list[int]:
        """
        Generate all moves for a specific piece.

        Args:
            square (int): Square index (0-63).
            board_obj (object): Board object with bitboard attributes.
            piece_value (int): Piece type and color value.

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        color = WHITE if piece_value > 0 else BLACK

        if abs(piece_value) == PAWN:
            potential_moves = MoveGen.list_all_pawn_moves(board_obj, color)
        elif abs(piece_value) == KNIGHT:
            potential_moves = MoveGen.list_all_knight_moves(board_obj, color)
        elif abs(piece_value) == BISHOP:
            potential_moves =  MoveGen.list_all_bishop_moves(board_obj, color)
        elif abs(piece_value) == ROOK:
            potential_moves =  MoveGen.list_all_rook_moves(board_obj, color)
        elif abs(piece_value) == QUEEN:
            potential_moves =  MoveGen.list_all_queen_moves(board_obj, color)
        elif abs(piece_value) == KING:
            potential_moves =  MoveGen.list_all_king_moves(board_obj, color)
        else:
            potential_moves = []
        
        list_move = []
        for e in potential_moves:
            if (e & 0x3F) == square:
                list_move.append(e)

        return list_move


    @staticmethod
    def list_all_pawn_quiets(board_obj, color) -> list[int]:
        """
        Generate all quiet pawn moves (non-captures, excluding promotions) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_p_quiets = []
        append = list_p_quiets.append

        all_occ = board_obj.all_board_occupied_squares

        if color == WHITE:
            empty_board = (~all_occ) & U64
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[WHITE_INDEX]

            move1 = (pawn_board << 8) & empty_board & ~RANK_MASKS[7]
            move2 = ((move1 & RANK_MASKS[2]) << 8) & empty_board

            while move1:
                least_significant_bit = move1 & -move1
                to = least_significant_bit.bit_length() - 1
                move1 ^= least_significant_bit
                append(to * 65 - 8)

            while move2:
                least_significant_bit = move2 & -move2
                to = least_significant_bit.bit_length() - 1
                move2 ^= least_significant_bit
                append(to * 65 - 16)

        else:
            empty_board = (~all_occ) & U64
            pawn_board = board_obj.pawn & board_obj.board_occupied_squares[BLACK_INDEX]

            move1 = (pawn_board >> 8) & empty_board & ~RANK_MASKS[0]
            move2 = ((move1 & RANK_MASKS[5]) >> 8) & empty_board

            while move1:
                least_significant_bit = move1 & -move1
                to = least_significant_bit.bit_length() - 1
                move1 ^= least_significant_bit
                append(to * 65 + 8)

            while move2:
                least_significant_bit = move2 & -move2
                to = least_significant_bit.bit_length() - 1
                move2 ^= least_significant_bit
                append(to * 65 + 16)

        return list_p_quiets


    @staticmethod
    def list_all_knight_quiets(board_obj, color) -> list[int]:
        """
        Generate all quiet knight moves (non-captures) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_quiets = []
        append = list_k_quiets.append

        knight_board = board_obj.knight & board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        empty_squares = (~board_obj.all_board_occupied_squares) & U64

        while knight_board:
            least_significant_bit = knight_board & -knight_board
            from_ = least_significant_bit.bit_length() - 1
            knight_board &= knight_board - 1

            to_possibilities = KNIGHT_TABLE[from_] & empty_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_k_quiets


    @staticmethod
    def list_all_rook_quiets(board_obj, color) -> list[int]:
        """
        Generate all quiet rook moves (non-captures) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_r_quiets = []
        append = list_r_quiets.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        rook = board_obj.rook & own_occupied_squares

        occ = board_obj.all_board_occupied_squares
        empty_squares = (~occ) & U64

        while rook:
            least_significant_bit = rook & -rook
            from_ = least_significant_bit.bit_length() - 1

            rook &= rook - 1

            occ_rel = occ & ROOK_MASK[from_]
            idx = ((occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]

            to_possibilities = ROOK_TABLE[from_][idx] & empty_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_r_quiets


    @staticmethod
    def list_all_bishop_quiets(board_obj, color) -> list[int]:
        """
        Generate all quiet bishop moves (non-captures) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_b_quiets = []
        append = list_b_quiets.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        bishop = board_obj.bishop & own_occupied_squares

        occ = board_obj.all_board_occupied_squares
        empty_squares = (~occ) & U64

        while bishop:
            least_significant_bit = bishop & -bishop
            from_ = least_significant_bit.bit_length() - 1

            bishop &= bishop - 1

            occ_rel = occ & BISHOP_MASK[from_]
            idx = ((occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]

            to_possibilities = BISHOP_TABLE[from_][idx] & empty_squares
            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_b_quiets


    @staticmethod
    def list_all_queen_quiets(board_obj, color) -> list[int]:
        """
        Generate all quiet queen moves (non-captures) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_q_quiets = []
        append = list_q_quiets.append

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        queen = board_obj.queen & own_occupied_squares

        occ = board_obj.all_board_occupied_squares
        empty_squares = (~occ) & U64

        while queen:
            least_significant_bit = queen & -queen
            from_ = least_significant_bit.bit_length() - 1

            queen &= queen - 1

            bishop_occ_rel = occ & BISHOP_MASK[from_]
            bishop_idx = ((bishop_occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]

            rook_occ_rel = occ & ROOK_MASK[from_]
            rook_idx = ((rook_occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]

            to_possibilities = (ROOK_TABLE[from_][rook_idx] | BISHOP_TABLE[from_][bishop_idx]) & empty_squares

            while to_possibilities:
                least_significant_bit2 = to_possibilities & -to_possibilities
                to = least_significant_bit2.bit_length() - 1
                to_possibilities &= to_possibilities - 1

                append(from_ | (to << 6))

        return list_q_quiets


    @staticmethod
    def list_all_king_quiets(board_obj, color, castling=True) -> list[int]:
        """
        Generate all quiet king moves (non-captures) for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            castling (optional bool): Whether to include castling moves. Defaults to True.

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_quiets = []

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        king_board = board_obj.king & own_occupied_squares

        empty_squares = (~board_obj.all_board_occupied_squares) & U64

        from_ = king_board.bit_length() - 1

        append = list_k_quiets.append

        to_possibilities = KING_TABLE[from_] & empty_squares
        while to_possibilities:
            least_significant_bit2 = to_possibilities & -to_possibilities
            to = least_significant_bit2.bit_length() - 1
            to_possibilities &= to_possibilities - 1

            append(from_ | (to << 6))

        if castling:
            list_k_quiets.extend(MoveGen.list_all_castling_move(board_obj, color))

        return list_k_quiets


    @staticmethod
    def list_all_legal_quiets(board_obj, side, castling=True) -> list[int]:
        """
        Generate all legal quiet moves (non-captures) for a side (excluding moves leaving king in check).

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.

        Returns:
            list: Encoded legal quiet moves as (from_square | (to_square << 6)).
        """

        list_all_quiets = []
        append = list_all_quiets.append

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        gens = (
            MoveGen.list_all_pawn_quiets,
            MoveGen.list_all_knight_quiets,
            MoveGen.list_all_bishop_quiets,
            MoveGen.list_all_rook_quiets,
            MoveGen.list_all_queen_quiets,
            lambda b, s: MoveGen.list_all_king_quiets(b, s, castling),
        )

        for gen in gens:
            for mv in gen(board_obj, side):
                undo = make(mv, side)
                if not attackers_to(board_obj, side, king_square[INDEX]):
                    append(mv)
                unmake(undo, side)

        return list_all_quiets


    @staticmethod
    def generate_all_quiets(board_obj, side, castling=True):
        """
        Generate all legal quiet moves (non-captures) for a side (excluding moves leaving king in check).

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.

        Yields:
            generator: Yields encoded quiet moves as (from_square | (to_square << 6)).
        """

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        for e in MoveGen.list_all_king_quiets(board_obj, side, castling):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_queen_quiets(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_knight_quiets(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_bishop_quiets(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_rook_quiets(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_pawn_quiets(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e


    @staticmethod
    def get_pawn_moves_categorized(board_obj, color, captures_list, quiets_list, promotions_list):
        """
        Generate all pseudo-legal pawn moves, categorized into captures, quiets and promotions.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
            promotions_list (list): List to append promotion moves to.
        """

        all_occ = board_obj.all_board_occupied_squares
        empty = ~all_occ & U64
        en_passant_square = board_obj.en_passant_square

        if color == WHITE:
            own_occ = board_obj.board_occupied_squares[WHITE_INDEX]
            enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX]
            pawn = board_obj.pawn & own_occ

            push1 = (pawn << 8) & empty
            push2 = ((push1 & RANK_MASKS[2]) << 8) & empty
            capt_left = (pawn << 7) & enemy_occ & ~FILE_MASKS[7]
            capt_right = (pawn << 9) & enemy_occ & ~FILE_MASKS[0]

            promo_mask = RANK_MASKS[7]
            push1_quiet = push1 & ~promo_mask
            push1_promo = push1 & promo_mask
            capt_left_nopromo = capt_left & ~promo_mask
            capt_left_promo = capt_left & promo_mask
            capt_right_nopromo = capt_right & ~promo_mask
            capt_right_promo = capt_right & promo_mask

            while push1_quiet:
                least_significant_bit = push1_quiet & -push1_quiet
                to = least_significant_bit.bit_length() - 1
                push1_quiet &= push1_quiet - 1
                quiets_list.append((to - 8) | (to << 6))

            while push2:
                least_significant_bit = push2 & -push2
                to = least_significant_bit.bit_length() - 1
                push2 &= push2 - 1
                quiets_list.append((to - 16) | (to << 6))

            while capt_left_nopromo:
                least_significant_bit = capt_left_nopromo & -capt_left_nopromo
                to = least_significant_bit.bit_length() - 1
                capt_left_nopromo &= capt_left_nopromo - 1
                captures_list.append((to - 7) | (to << 6))

            while capt_right_nopromo:
                least_significant_bit = capt_right_nopromo & -capt_right_nopromo
                to = least_significant_bit.bit_length() - 1
                capt_right_nopromo &= capt_right_nopromo - 1
                captures_list.append((to - 9) | (to << 6))

            while push1_promo:
                least_significant_bit = push1_promo & -push1_promo
                to = least_significant_bit.bit_length() - 1
                push1_promo &= push1_promo - 1
                promotions_list.append((to - 8) | (to << 6))

            while capt_left_promo:
                least_significant_bit = capt_left_promo & -capt_left_promo
                to = least_significant_bit.bit_length() - 1
                capt_left_promo &= capt_left_promo - 1
                promotions_list.append((to - 7) | (to << 6))

            while capt_right_promo:
                least_significant_bit = capt_right_promo & -capt_right_promo
                to = least_significant_bit.bit_length() - 1
                capt_right_promo &= capt_right_promo - 1
                promotions_list.append((to - 9) | (to << 6))

            if en_passant_square:
                ep_mask = 1 << en_passant_square
                attackers = pawn & (((ep_mask & ~FILE_MASKS[0]) >> 9) | ((ep_mask & ~FILE_MASKS[7]) >> 7))
                while attackers:
                    least_significant_bit = attackers & -attackers
                    from_ = least_significant_bit.bit_length() - 1
                    attackers &= attackers - 1
                    captures_list.append(from_ | (en_passant_square << 6))

        else:
            own_occ = board_obj.board_occupied_squares[BLACK_INDEX]
            enemy_occ = board_obj.board_occupied_squares[WHITE_INDEX]
            pawn = board_obj.pawn & own_occ

            push1 = (pawn >> 8) & empty
            push2 = ((push1 & RANK_MASKS[5]) >> 8) & empty
            capt_left = (pawn >> 7) & enemy_occ & ~FILE_MASKS[0]
            capt_right = (pawn >> 9) & enemy_occ & ~FILE_MASKS[7]

            promo_mask = RANK_MASKS[0]
            push1_quiet = push1 & ~promo_mask
            push1_promo = push1 & promo_mask
            capt_left_nopromo = capt_left & ~promo_mask
            capt_left_promo = capt_left & promo_mask
            capt_right_nopromo = capt_right & ~promo_mask
            capt_right_promo = capt_right & promo_mask

            while push1_quiet:
                least_significant_bit = push1_quiet & -push1_quiet
                to = least_significant_bit.bit_length() - 1
                push1_quiet &= push1_quiet - 1
                quiets_list.append((to + 8) | (to << 6))

            while push2:
                least_significant_bit = push2 & -push2
                to = least_significant_bit.bit_length() - 1
                push2 &= push2 - 1
                quiets_list.append((to + 16) | (to << 6))

            while capt_left_nopromo:
                least_significant_bit = capt_left_nopromo & -capt_left_nopromo
                to = least_significant_bit.bit_length() - 1
                capt_left_nopromo &= capt_left_nopromo - 1
                captures_list.append((to + 7) | (to << 6))

            while capt_right_nopromo:
                least_significant_bit = capt_right_nopromo & -capt_right_nopromo
                to = least_significant_bit.bit_length() - 1
                capt_right_nopromo &= capt_right_nopromo - 1
                captures_list.append((to + 9) | (to << 6))

            while push1_promo:
                least_significant_bit = push1_promo & -push1_promo
                to = least_significant_bit.bit_length() - 1
                push1_promo &= push1_promo - 1
                promotions_list.append((to + 8) | (to << 6))

            while capt_left_promo:
                least_significant_bit = capt_left_promo & -capt_left_promo
                to = least_significant_bit.bit_length() - 1
                capt_left_promo &= capt_left_promo - 1
                promotions_list.append((to + 7) | (to << 6))

            while capt_right_promo:
                least_significant_bit = capt_right_promo & -capt_right_promo
                to = least_significant_bit.bit_length() - 1
                capt_right_promo &= capt_right_promo - 1
                promotions_list.append((to + 9) | (to << 6))

            if en_passant_square:
                ep_mask = 1 << en_passant_square
                attackers = pawn & (((ep_mask & ~FILE_MASKS[0]) << 7) | ((ep_mask & ~FILE_MASKS[7]) << 9))
                while attackers:
                    least_significant_bit = attackers & -attackers
                    from_ = least_significant_bit.bit_length() - 1
                    attackers &= attackers - 1
                    captures_list.append(from_ | (en_passant_square << 6))


    @staticmethod
    def get_knight_moves_categorized(board_obj, color, captures_list, quiets_list):
        """
        Generate all pseudo-legal knight moves, categorized into captures and quiets.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
        """

        own_occ = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        empty_squares = ~board_obj.all_board_occupied_squares & U64

        knight = board_obj.knight & own_occ

        while knight:
            least_significant_bit = knight & -knight
            from_ = least_significant_bit.bit_length() - 1
            knight &= knight - 1

            attacks = KNIGHT_TABLE[from_]

            capts = attacks & enemy_occ
            while capts:
                least_significant_bit2 = capts & -capts
                to = least_significant_bit2.bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

            qts = attacks & empty_squares
            while qts:
                least_significant_bit2 = qts & -qts
                to = least_significant_bit2.bit_length() - 1
                qts &= qts - 1
                quiets_list.append(from_ | (to << 6))


    @staticmethod
    def get_bishop_moves_categorized(board_obj, color, captures_list, quiets_list):
        """
        Generate all pseudo-legal bishop moves, categorized into captures and quiets.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
        """

        own_occ = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        all_occ = board_obj.all_board_occupied_squares
        empty_squares = ~all_occ & U64

        bishop = board_obj.bishop & own_occ

        while bishop:
            least_significant_bit = bishop & -bishop
            from_ = least_significant_bit.bit_length() - 1
            bishop &= bishop - 1

            occ_rel = all_occ & BISHOP_MASK[from_]
            idx = ((occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            attacks = BISHOP_TABLE[from_][idx]

            capts = attacks & enemy_occ
            while capts:
                least_significant_bit2 = capts & -capts
                to = least_significant_bit2.bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

            qts = attacks & empty_squares
            while qts:
                least_significant_bit2 = qts & -qts
                to = least_significant_bit2.bit_length() - 1
                qts &= qts - 1
                quiets_list.append(from_ | (to << 6))


    @staticmethod
    def get_rook_moves_categorized(board_obj, color, captures_list, quiets_list):
        """
        Generate all pseudo-legal rook moves, categorized into captures and quiets.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
        """

        own_occ = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        all_occ = board_obj.all_board_occupied_squares
        empty_squares = ~all_occ & U64

        rook = board_obj.rook & own_occ

        while rook:
            least_significant_bit = rook & -rook
            from_ = least_significant_bit.bit_length() - 1
            rook &= rook - 1

            occ_rel = all_occ & ROOK_MASK[from_]
            idx = ((occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]
            attacks = ROOK_TABLE[from_][idx]

            capts = attacks & enemy_occ
            while capts:
                least_significant_bit2 = capts & -capts
                to = least_significant_bit2.bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

            qts = attacks & empty_squares
            while qts:
                least_significant_bit2 = qts & -qts
                to = least_significant_bit2.bit_length() - 1
                qts &= qts - 1
                quiets_list.append(from_ | (to << 6))


    @staticmethod
    def get_queen_moves_categorized(board_obj, color, captures_list, quiets_list):
        """
        Generate all pseudo-legal queen moves, categorized into captures and quiets.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
        """

        own_occ = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        all_occ = board_obj.all_board_occupied_squares
        empty_squares = ~all_occ & U64

        queen = board_obj.queen & own_occ

        while queen:
            least_significant_bit = queen & -queen
            from_ = least_significant_bit.bit_length() - 1
            queen &= queen - 1

            bishop_occ_rel = all_occ & BISHOP_MASK[from_]
            bishop_idx = ((bishop_occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]

            rook_occ_rel = all_occ & ROOK_MASK[from_]
            rook_idx = ((rook_occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]

            attacks = ROOK_TABLE[from_][rook_idx] | BISHOP_TABLE[from_][bishop_idx]

            capts = attacks & enemy_occ
            while capts:
                least_significant_bit2 = capts & -capts
                to = least_significant_bit2.bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

            qts = attacks & empty_squares
            while qts:
                least_significant_bit2 = qts & -qts
                to = least_significant_bit2.bit_length() - 1
                qts &= qts - 1
                quiets_list.append(from_ | (to << 6))


    @staticmethod
    def get_king_moves_categorized(board_obj, color, captures_list, quiets_list, castling=True):
        """
        Generate all pseudo-legal king moves, categorized into captures and quiets.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            quiets_list (list): List to append quiet moves to.
            castling (bool, optional): Whether to include castling moves. Defaults to True.
        """

        own_occ = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]
        enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX if color == WHITE else WHITE_INDEX]
        empty_squares = ~board_obj.all_board_occupied_squares & U64

        king = board_obj.king & own_occ
        from_ = king.bit_length() - 1

        attacks = KING_TABLE[from_]

        capts = attacks & enemy_occ
        while capts:
            least_significant_bit2 = capts & -capts
            to = least_significant_bit2.bit_length() - 1
            capts &= capts - 1
            captures_list.append(from_ | (to << 6))

        qts = attacks & empty_squares
        while qts:
            least_significant_bit2 = qts & -qts
            to = least_significant_bit2.bit_length() - 1
            qts &= qts - 1
            quiets_list.append(from_ | (to << 6))

        if castling:
            for mv in MoveGen.list_all_castling_move(board_obj, color):
                quiets_list.append(mv)


    @staticmethod
    def get_all_moves_categorized(board_obj, color, captures_list, quiets_list, promotions_list, castling=True):
        """
        Generate all pseudo-legal moves for a side, categorized into 3 lists.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.

        Returns:
            tuple: (captures_list, quiets_list, promotions_list)
        """

        MoveGen.get_pawn_moves_categorized(board_obj, color, captures_list, quiets_list, promotions_list)
        MoveGen.get_knight_moves_categorized(board_obj, color, captures_list, quiets_list)
        MoveGen.get_bishop_moves_categorized(board_obj, color, captures_list, quiets_list)
        MoveGen.get_rook_moves_categorized(board_obj, color, captures_list, quiets_list)
        MoveGen.get_queen_moves_categorized(board_obj, color, captures_list, quiets_list)
        MoveGen.get_king_moves_categorized(board_obj, color, captures_list, quiets_list, castling)

        return captures_list, quiets_list, promotions_list


    @staticmethod
    def get_captures_and_promotions(board_obj, color, captures_list, promotions_list):
        """
        Generate only captures and promotions (no quiet moves).
        Optimized for quiescence search.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Side color (WHITE=1 or BLACK=-1).
            captures_list (list): List to append capture moves to.
            promotions_list (list): List to append promotion moves to.
        """

        all_board_occupied_squares = board_obj.all_board_occupied_squares
        en_passant_square = board_obj.en_passant_square

        if color == WHITE:
            own_occ = board_obj.board_occupied_squares[WHITE_INDEX]
            enemy_occ = board_obj.board_occupied_squares[BLACK_INDEX]
            pawn = board_obj.pawn & own_occ

            push1 = (pawn << 8) & ~all_board_occupied_squares & U64
            capt_left = (pawn << 7) & enemy_occ & ~FILE_MASKS[7]
            capt_right = (pawn << 9) & enemy_occ & ~FILE_MASKS[0]

            promo_mask = RANK_MASKS[7]
            push1_promo = push1 & promo_mask
            capt_left_nopromo = capt_left & ~promo_mask
            capt_left_promo = capt_left & promo_mask
            capt_right_nopromo = capt_right & ~promo_mask
            capt_right_promo = capt_right & promo_mask

            while capt_left_nopromo:
                to = (capt_left_nopromo & -capt_left_nopromo).bit_length() - 1
                capt_left_nopromo &= capt_left_nopromo - 1
                captures_list.append((to - 7) | (to << 6))

            while capt_right_nopromo:
                to = (capt_right_nopromo & -capt_right_nopromo).bit_length() - 1
                capt_right_nopromo &= capt_right_nopromo - 1
                captures_list.append((to - 9) | (to << 6))

            while push1_promo:
                to = (push1_promo & -push1_promo).bit_length() - 1
                push1_promo &= push1_promo - 1
                promotions_list.append((to - 8) | (to << 6))

            while capt_left_promo:
                to = (capt_left_promo & -capt_left_promo).bit_length() - 1
                capt_left_promo &= capt_left_promo - 1
                promotions_list.append((to - 7) | (to << 6))

            while capt_right_promo:
                to = (capt_right_promo & -capt_right_promo).bit_length() - 1
                capt_right_promo &= capt_right_promo - 1
                promotions_list.append((to - 9) | (to << 6))

            if en_passant_square:
                ep_mask = 1 << en_passant_square
                attackers = pawn & (((ep_mask & ~FILE_MASKS[0]) >> 9) | ((ep_mask & ~FILE_MASKS[7]) >> 7))
                while attackers:
                    from_ = (attackers & -attackers).bit_length() - 1
                    attackers &= attackers - 1
                    captures_list.append(from_ | (en_passant_square << 6))
        else:
            own_occ = board_obj.board_occupied_squares[BLACK_INDEX]
            enemy_occ = board_obj.board_occupied_squares[WHITE_INDEX]
            pawn = board_obj.pawn & own_occ

            push1 = (pawn >> 8) & ~all_board_occupied_squares & U64
            capt_left = (pawn >> 7) & enemy_occ & ~FILE_MASKS[0]
            capt_right = (pawn >> 9) & enemy_occ & ~FILE_MASKS[7]

            promo_mask = RANK_MASKS[0]
            push1_promo = push1 & promo_mask
            capt_left_nopromo = capt_left & ~promo_mask
            capt_left_promo = capt_left & promo_mask
            capt_right_nopromo = capt_right & ~promo_mask
            capt_right_promo = capt_right & promo_mask

            while capt_left_nopromo:
                to = (capt_left_nopromo & -capt_left_nopromo).bit_length() - 1
                capt_left_nopromo &= capt_left_nopromo - 1
                captures_list.append((to + 7) | (to << 6))

            while capt_right_nopromo:
                to = (capt_right_nopromo & -capt_right_nopromo).bit_length() - 1
                capt_right_nopromo &= capt_right_nopromo - 1
                captures_list.append((to + 9) | (to << 6))

            while push1_promo:
                to = (push1_promo & -push1_promo).bit_length() - 1
                push1_promo &= push1_promo - 1
                promotions_list.append((to + 8) | (to << 6))

            while capt_left_promo:
                to = (capt_left_promo & -capt_left_promo).bit_length() - 1
                capt_left_promo &= capt_left_promo - 1
                promotions_list.append((to + 7) | (to << 6))

            while capt_right_promo:
                to = (capt_right_promo & -capt_right_promo).bit_length() - 1
                capt_right_promo &= capt_right_promo - 1
                promotions_list.append((to + 9) | (to << 6))

            if en_passant_square:
                ep_mask = 1 << en_passant_square
                attackers = pawn & (((ep_mask & ~FILE_MASKS[0]) << 7) | ((ep_mask & ~FILE_MASKS[7]) << 9))
                while attackers:
                    from_ = (attackers & -attackers).bit_length() - 1
                    attackers &= attackers - 1
                    captures_list.append(from_ | (en_passant_square << 6))

        knight = board_obj.knight & own_occ
        while knight:
            from_ = (knight & -knight).bit_length() - 1
            knight &= knight - 1
            capts = KNIGHT_TABLE[from_] & enemy_occ
            while capts:
                to = (capts & -capts).bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

        bishop = board_obj.bishop & own_occ
        while bishop:
            from_ = (bishop & -bishop).bit_length() - 1
            bishop &= bishop - 1
            occ_rel = all_board_occupied_squares & BISHOP_MASK[from_]
            idx = ((occ_rel * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            capts = BISHOP_TABLE[from_][idx] & enemy_occ
            while capts:
                to = (capts & -capts).bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

        rook = board_obj.rook & own_occ
        while rook:
            from_ = (rook & -rook).bit_length() - 1
            rook &= rook - 1
            occ_rel = all_board_occupied_squares & ROOK_MASK[from_]
            idx = ((occ_rel * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]
            capts = ROOK_TABLE[from_][idx] & enemy_occ
            while capts:
                to = (capts & -capts).bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

        queen = board_obj.queen & own_occ
        while queen:
            from_ = (queen & -queen).bit_length() - 1
            queen &= queen - 1
            b_occ = all_board_occupied_squares & BISHOP_MASK[from_]
            b_idx = ((b_occ * BISHOP_MAGIC[from_]) & U64) >> BISHOP_SHIFT[from_]
            r_occ = all_board_occupied_squares & ROOK_MASK[from_]
            r_idx = ((r_occ * ROOK_MAGIC[from_]) & U64) >> ROOK_SHIFT[from_]
            capts = (ROOK_TABLE[from_][r_idx] | BISHOP_TABLE[from_][b_idx]) & enemy_occ
            while capts:
                to = (capts & -capts).bit_length() - 1
                capts &= capts - 1
                captures_list.append(from_ | (to << 6))

        king = board_obj.king & own_occ
        from_ = king.bit_length() - 1
        capts = KING_TABLE[from_] & enemy_occ
        while capts:
            to = (capts & -capts).bit_length() - 1
            capts &= capts - 1
            captures_list.append(from_ | (to << 6))



class GameState:
    @staticmethod
    def attackers_to(board_obj, side, square) -> bool:
        """
        Check if a square is attacked by the enemy.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            square (int): Square index (0-63).

        Returns:
            True if in check, False if not, "error" if king not found.
        """

        ATT_INDEX = BLACK_INDEX if side == WHITE else WHITE_INDEX

        occ_sides = board_obj.board_occupied_squares
        enemy_occ = occ_sides[ATT_INDEX]

        if INVERTED_PAWN_TABLE[ATT_INDEX][square] & enemy_occ & board_obj.pawn:
            return True

        if KNIGHT_TABLE[square] & enemy_occ & board_obj.knight:
            return True

        if KING_TABLE[square] & enemy_occ & board_obj.king:
            return True

        all_board_occupied_squares = board_obj.all_board_occupied_squares
        queens = enemy_occ & board_obj.queen

        rook_like = (enemy_occ & board_obj.rook) | queens
        occ_rel = ROOK_MASK[square] & all_board_occupied_squares
        idx = ((occ_rel * ROOK_MAGIC[square]) & U64) >> ROOK_SHIFT[square]
        if ROOK_TABLE[square][idx] & rook_like:
            return True

        bishop_like = (enemy_occ & board_obj.bishop) | queens
        occ_rel = BISHOP_MASK[square] & all_board_occupied_squares
        idx = ((occ_rel * BISHOP_MAGIC[square]) & U64) >> BISHOP_SHIFT[square]
        if BISHOP_TABLE[square][idx] & bishop_like:
            return True

        return False
    

    @staticmethod
    def get_all_attackers(board_obj, square, occupied = None) -> int:
        """
        Get all attackers of a square.

        Args:
            board_obj (object): Board object with bitboard attributes.
            square (int): Square index (0-63).
            occupied (int, optional): Bitboard of occupied squares to consider for sliding pieces. If None, uses board_obj.all_board_occupied_squares. Defaults to None.

        Returns:
            int: Bitboard of all attackers to the square.
        """

        #for SEE 
        if occupied is None:
            occupied = board_obj.all_board_occupied_squares

        bb_attackers = 0
        occ_sides = board_obj.board_occupied_squares

        bb_attackers |= INVERTED_PAWN_TABLE[WHITE_INDEX][square] & occ_sides[WHITE_INDEX] & board_obj.pawn
        bb_attackers |= INVERTED_PAWN_TABLE[BLACK_INDEX][square] & occ_sides[BLACK_INDEX] & board_obj.pawn

        bb_attackers |= KNIGHT_TABLE[square] & board_obj.knight
        bb_attackers |= KING_TABLE[square] & board_obj.king

        rook_like = board_obj.rook | board_obj.queen
        occ_rel = ROOK_MASK[square] & occupied
        idx = ((occ_rel * ROOK_MAGIC[square]) & U64) >> ROOK_SHIFT[square]
        bb_attackers |= ROOK_TABLE[square][idx] & rook_like

        bishop_like = board_obj.bishop | board_obj.queen
        occ_rel = BISHOP_MASK[square] & occupied
        idx = ((occ_rel * BISHOP_MAGIC[square]) & U64) >> BISHOP_SHIFT[square]
        bb_attackers |= BISHOP_TABLE[square][idx] & bishop_like

        return bb_attackers


    @staticmethod
    def is_checkmate(board_obj, side) -> bool:
        """
        Check if a side is in checkmate.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).

        Returns:
            bool: True if checkmate, False otherwise.
        """
        
        king_square = (board_obj.king & board_obj.board_occupied_squares[WHITE_INDEX if side == WHITE else BLACK_INDEX]).bit_length() - 1
        
        if GameState.attackers_to(board_obj, side, king_square):
            return not any(MoveGen.generate_all_moves(board_obj, side, castling=False))

        return False
    
    
    @staticmethod
    def check_repetition(board_obj) -> bool:
        """
        Check for threefold repetition.

        Args:
            board_obj (object): Board object with bitboard attributes.
            
        Returns:
            bool: True if position occurred 3+ times, False otherwise.
        """

        return board_obj.position_hash_history.get(board_obj.last_position_hash, 0) >= 3


    @staticmethod
    def is_move_legal(board_obj, encoded_move) -> bool:
        """
        Check if a move is legal for the current board state.
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            encoded_move (int): Encoded move value as (from_square | (to_square << 6)).

        Returns:
            bool: True if the move is legal, False otherwise.
        """

        side = board_obj.side_to_move
        from_sq = encoded_move & 0x3F
        mask = SQUARE_MASKS[from_sq]

        if board_obj.pawn & mask:
            pseudo_moves = MoveGen.list_all_pawn_moves(board_obj, side)
        elif board_obj.knight & mask:
            pseudo_moves = MoveGen.list_all_knight_moves(board_obj, side)
        elif board_obj.bishop & mask:
            pseudo_moves = MoveGen.list_all_bishop_moves(board_obj, side)
        elif board_obj.rook & mask:
            pseudo_moves = MoveGen.list_all_rook_moves(board_obj, side)
        elif board_obj.queen & mask:
            pseudo_moves = MoveGen.list_all_queen_moves(board_obj, side)
        elif board_obj.king & mask:
            pseudo_moves = MoveGen.list_all_king_moves(board_obj, side)
        else:
            return False

        if encoded_move not in pseudo_moves:
            return False

        undo = board_obj.make_move(encoded_move, side)
        king_square = board_obj.king_square[WHITE_INDEX if side == WHITE else BLACK_INDEX]
        in_check = GameState.attackers_to(board_obj, side, king_square)
        board_obj.unmake_move(undo, side)
        return not in_check



class ChessDisplay:
    enable_print = True

    def print_disabled(f):
        """
        Decorator to disable printing for a function if enable_print is False.

        ChessDisplay.enable_print can be set to False to suppress output from decorated functions.
        """
        
        def wrapper(*args, **kwargs):
            if not ChessDisplay.enable_print:
                return None
            return f(*args, **kwargs)
        
        wrapper.__doc__ = getattr(f, "__doc__", None)
        return wrapper


    @staticmethod
    @print_disabled
    def print_board(board_obj, side=WHITE) -> None:
        """
        Print the chess board.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """
        board_rendu = [piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(64)]

        if side == WHITE:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 8 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(56, 64))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(48, 56))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(40, 48))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(32, 40))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(24, 32))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(16, 24))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(8, 16))} {BG} {END_COLOR}",
                f"   \u200A {BG} 1 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(0, 8))} {BG} {END_COLOR}",
                f"   \u200A {BG}   a b c d e f g h  {BG}{END_COLOR}"
            )

        else:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 1 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(7, -1, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(15, 7, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(23, 15, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(31, 23, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(39, 31, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(47, 39, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] for i in range(55, 47, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 8 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] for i in range(63, 55, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG}   h g f e d c b a  {BG}{END_COLOR}"
            )

        print("\n".join(board_rendu))

    

    @staticmethod
    @print_disabled
    def print_game_start(board_obj, side=WHITE) -> None:
        """
        Print the game start message and board.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        print("╔════════ GAME START ════════╗")

        print()
        print("⚪ ══════ White play ═════ ⚪" if side == WHITE else "⚫ ═════ Black play ══════ ⚫")
        print()

        ChessDisplay.print_board(board_obj, side)


    @staticmethod
    @print_disabled
    def print_turn(side) -> None:
        """
        Print which side's turn it is.

        Args:
            side (int): Side color (WHITE=1 or BLACK=-1).
        """

        print()
        print("⚪ ══════ White play ═════ ⚪" if side == WHITE else "⚫ ═════ Black play ══════ ⚫")
        print()


    @staticmethod
    def print_game_already_over() -> None:
        """Print a message indicating the game is already over."""

        print("🚫 ══ The game is over ═══ 🚫")
        return


    @staticmethod
    def print_invalid_move(reason=None) -> None:
        """
        Print an invalid move message.

        Args:
            reason (str, optional): Optional reason for the invalid move.
        """

        print("🚫 ════ Invalid move ═════ 🚫")

        if reason:
            print(f"Reason: {reason}")
    

    @staticmethod
    @print_disabled
    def print_game_over(board_obj, winner, side=None) -> None: 
        """
        Print the checkmate message.

        Args:
            board_obj (object): Board object with bitboard attributes.
            winner (int): Winning side (WHITE=1 or BLACK=-1).
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        print("══════════════════════════════")
        print()
        ChessDisplay.print_board(board_obj, winner if side == None else side)
        print()
        print(f"╚═══ CHECKMATE {'WHITE' if winner == WHITE else 'BLACK'} WIN ═══╝")


    @staticmethod
    @print_disabled
    def print_draw(board_obj, side = WHITE, draw_type=None) -> None:   
        """
        Print a draw message.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
            draw_type (str | None, optional): Draw type ('insufficient_material', 'fifty_move_rule', 'threefold_repetition').
        """   

        print("══════════════════════════════")
        print()
        ChessDisplay.print_board(board_obj, side)
        print()

        if draw_type == 'insufficient_material':
            print("⏸ Draw by insufficient material ⏸")

        elif draw_type == 'fifty_move_rule':
            print("⏸ Draw by fifty-move rule ═ ⏸")

        elif draw_type == 'threefold_repetition':
            print("⏸ ══ Draw by repetition ══ ⏸")
        
        elif draw_type == 'stalemate':
            print("⏸ ═══ Draw by stalemate ═══ ⏸")

        else:
            print("⏸ ═════════ Draw ═════════ ⏸")
            

    @staticmethod
    @print_disabled
    def print_move(move) -> None:
        """
        Print a chess move.
        
        Args:
            move (str): Move string (e.g., "e2e4").
        """

        print(f"> {move}")
        print()

    
    @staticmethod
    @print_disabled
    def print_invalid_format() -> None:
        """Print an invalid format message with example."""

        print("🚫 ═════════ Invalid format ═════════ 🚫")
        print("Valid move example: ✅--- e2e4 ---✅")

    
    @staticmethod
    def print_last_move_highlighted(board_obj, side = WHITE) -> None:
        """
        Print the board with the last move highlighted.

        Args:
            board_obj (object): Board object representing the board.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        HIGHLIGHT_WHITE_BG = "\033[48;5;195m"
        HIGHLIGHT_BLACK_BG = "\033[48;5;109m"

        if not board_obj.move_history:
            ChessDisplay.print_board(board_obj, side)
            return


        last_encoded = board_obj.move_history[-1]
        from_sq = last_encoded & 0x3F
        to_sq = (last_encoded >> 6) & 0x3F

        board_rendu = [piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(64)]
        
        if side == WHITE:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 8 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(56, 64))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(48, 56))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(40, 48))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(32, 40))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(24, 32))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(16, 24))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(8, 16))} {BG} {END_COLOR}",
                f"   \u200A {BG} 1 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(0, 8))} {BG} {END_COLOR}",
                f"   \u200A {BG}   a b c d e f g h  {BG}{END_COLOR}"
            )

        else:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 1 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(7, -1, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(15, 7, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(23, 15, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(31, 23, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(39, 31, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(47, 39, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(55, 47, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 8 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in (from_sq, to_sq) else f'{HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG}{board_rendu[i]}' for i in range(63, 55, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG}   h g f e d c b a  {BG}{END_COLOR}"
            )

        print("\n".join(board_rendu))



    @staticmethod
    def print_highlighted_legal_move(board_obj, square, side = WHITE) -> None:
        """
        Print the board with legal moves for a piece highlighted.

        Args:
            board_obj (object): Board object with bitboard attributes.
            square (int or str): Square index (0-63) or algebraic like 'e2'.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        FROM_HIGHLIGHT_WHITE_BG = "\033[48;5;224m"
        FROM_HIGHLIGHT_BLACK_BG = "\033[48;5;181m"

        HIGHLIGHT_WHITE_BG = "\033[48;5;195m"
        HIGHLIGHT_BLACK_BG = "\033[48;5;109m"
        
        if isinstance(square, str):
            square = SQUARES[square]

        piece_val = board_obj.get_piece_type_and_color(square)
        list_move = MoveGen.list_all_piece_move(board_obj, square, piece_val)

        highlight_squares = [square]

        for move in list_move:
            to_sq = (move >> 6) & 0x3F
            highlight_squares.append(to_sq)

        board_rendu = [piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(64)]
        
        if side == WHITE:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 8 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(56, 64))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(48, 56))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(40, 48))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(32, 40))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(24, 32))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(16, 24))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(8, 16))} {BG} {END_COLOR}",
                f"   \u200A {BG} 1 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(0, 8))} {BG} {END_COLOR}",
                f"   \u200A {BG}   a b c d e f g h  {BG}{END_COLOR}"
            )

        else:
            board_rendu = (
                f"   \u200A {BG}                    {END_COLOR}",
                f"   \u200A \x1b[30m{BG} 1 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(7, -1, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 2 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(15, 7, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 3 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(23, 15, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 4 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(31, 23, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 5 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(39, 31, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 6 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(47, 39, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 7 {' '.join((WHITE_BG if i % 2 == 0 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 0 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 0 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(55, 47, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG} 8 {' '.join((WHITE_BG if i % 2 == 1 else BLACK_BG) + board_rendu[i] if i not in highlight_squares else f'{(FROM_HIGHLIGHT_WHITE_BG if i % 2 == 1 else FROM_HIGHLIGHT_BLACK_BG) if i == square else (HIGHLIGHT_WHITE_BG if i % 2 == 1 else HIGHLIGHT_BLACK_BG)}{board_rendu[i]}' for i in range(63, 55, -1))} {BG} {END_COLOR}",
                f"   \u200A {BG}   h g f e d c b a  {BG}{END_COLOR}"
            )

        print("\n".join(board_rendu))



class ChessCore:
    def __init__(self):
        self.board = Board()
        self.party_over = False
    

    def start_new_game(self, side="white", enable_print = True) -> None:
        """
        Start a new chess game.

        Args:
            side (str, optional): Starting side ('white' or 'black'). Defaults to 'white'.
            enable_print (bool, optional): Whether to enable printing. Defaults to True.
        """
        
        if side == "black":
            self.board.change_side()

        ChessDisplay.enable_print = enable_print

        if enable_print:
            ChessDisplay.print_game_start(self.board, self.board.side_to_move)
    

    def reset_game(self) -> None:
        """Reset the game to its initial state."""

        self.board = Board()
        self.party_over = False


    def load_board(self, fen_string) -> None:
        """
        Load a custom board state.

        Args:
            fen (str): FEN string representing the board state.
        """

        self.board.load_board(fen_string)
    

    def play_move(self, all_move, print_move=True) -> str:
        """
        Play a move and handle game logic.

        Args:
            all_move (str): Move string (e.g., "e2 e4").
            print_move (bool): Print the move. Defaults to True.

        Returns:
            str: 'valid', 'illegal', 'checkmate', or 'draw'.
        """

        if self.party_over:
            ChessDisplay.print_game_already_over()
            return 'illegal'
        
        if print_move:
            ChessDisplay.print_move(all_move)

        if not self.parse_move_and_validate(all_move):
            ChessDisplay.print_invalid_format()
            return 'illegal'

        else:
            if self.board.position_has_loaded:
                if not self.board.move_history:
                    rep = self.check_loaded_position()
                    if rep:
                        return rep
                
            rep = self.validate_and_apply_move()

        if not rep:
            ChessDisplay.print_invalid_move()
            return 'illegal'

        # Note: side_to_move has changed after a valid move

        self.board.add_to_history()
        
        if not any(MoveGen.generate_all_moves(self.board, self.board.side_to_move)):
            if GameState.attackers_to(self.board, self.board.side_to_move, self.board.king_square[WHITE_INDEX if self.board.side_to_move == WHITE else BLACK_INDEX]):
                ChessDisplay.print_game_over(self.board, self.board.side_to_move * -1)
                self.party_over = True
                return 'checkmate'
            
            ChessDisplay.print_draw(self.board,  self.board.side_to_move*-1, 'stalemate')
            self.party_over = True
            return 'draw'

        if GameState.check_repetition(self.board):
            ChessDisplay.print_draw(self.board,  self.board.side_to_move*-1, 'threefold_repetition')
            self.party_over = True
            return 'draw'
        
        if self.board.counter_halfmove_without_capture >= 100:
            ChessDisplay.print_draw(self.board, self.board.side_to_move*-1, 'fifty_move_rule')
            self.party_over = True
            return 'draw'

        if self.board.material_insufficiency():
            ChessDisplay.print_draw(self.board, self.board.side_to_move*-1, "insufficient_material")
            self.party_over = True
            return 'draw'
        

        ChessDisplay.print_turn(self.board.side_to_move)
        ChessDisplay.print_last_move_highlighted(self.board, self.board.side_to_move)
        
        return 'valid'
    

    def check_loaded_position(self) -> "str | None":
        """
        Check if a loaded position is checkmate or stalemate.
        
        Returns:
            str or None: 'checkmate', 'stalemate', or None if game continues.
        """

        if GameState.is_checkmate(self.board, BLACK):
            ChessDisplay.print_game_over(self.board, WHITE)
            return 'checkmate'
        
        if GameState.is_checkmate(self.board, WHITE):
            ChessDisplay.print_game_over(self.board, BLACK)
            return 'checkmate'
        
        legal_move = MoveGen.list_all_legal_moves(self.board, WHITE if self.board.side_to_move == BLACK else BLACK)      

        if not legal_move:
            ChessDisplay.print_draw(self.board,  self.board.side_to_move*-1, 'stalemate')
            return 'draw'
        
        return None
        

    def validate_and_apply_move(self) -> bool:
        """
        Validate and apply the current move to the board.

        Returns:
            bool: True if the move is valid and applied, False otherwise.
        """
        
        side = self.board.side_to_move

        if not GameState.is_move_legal(self.board, self.board.encoded_move_in_progress):
            return False
        
        promotion_piece = 0

        if abs(self.board.start_value) == PAWN:
            if (self.board.start_value == PAWN and self.board.end_coordinate >= 56) or \
               (self.board.start_value == -PAWN and self.board.end_coordinate <= 7):
                promotion_piece = self.promotion_value if self.promotion_value else QUEEN
        
        self.board.make_move(self.board.encoded_move_in_progress, side, promotion_piece)
        self.board.change_side()

        return True
    

    @staticmethod
    def bitboard_to_fen(bitboard) -> str:
        """
        Convert a bitboard representation to FEN?

        Args:
            bitboard (int): A 64-bit integer representing the bitboard position,

        Returns:
            str: A FEN rank string representation of the bitboard.
        """


        bitboard_str = f"{bitboard:064b}"
        r = []

        for i in range(8):
            r_b = bitboard_str[i*8:(i+1)*8][::-1]
            
            fen_rank = ""
            empty = 0

            for bit in r_b:
                if bit == "1":
                    if empty:
                        fen_rank += str(empty)
                        empty = 0
                    fen_rank += "p"
                else:
                    empty += 1

            if empty:
                fen_rank += str(empty)

            r.append(fen_rank)

        return "/".join(r)



    @staticmethod
    def give_move_info(board_obj, encoded_move) -> "str | None":
        """
        Validate the move in progress and populate move metadata.

        Args:
            board_obj (object): Board object with bitboard attributes.
            encoded_move (int): Encoded move value.

        Returns:
            None: If the move source/target are coherent (does not guarantee full legality).
            str: An error message if the move is obviously illegal ('illegal', or a descriptive reason).
        """

        start_coordinate = encoded_move & 0x3F
        board_obj.end_coordinate = (encoded_move >> 6) & 0x3F
        
        board_obj.start_value = board_obj.get_piece_type_and_color(start_coordinate)         
        end_value = board_obj.get_piece_type_and_color(board_obj.end_coordinate)

        if board_obj.start_value == EMPTY:
            return 'illegal'

        if board_obj.start_value == 0 or (board_obj.start_value > 0) != (board_obj.side_to_move == WHITE):
            return "It's not your turn."

        if end_value != EMPTY and not (end_value < 0 and board_obj.start_value > 0) and not (end_value > 0 and board_obj.start_value < 0):
            return 'illegal'
        

    @staticmethod
    def move_parser(board_obj, move_str) -> "tuple[int, int]":
        """
        Parse a move string (LAN or SAN) and return encoded move with promotion piece.

        Args:
            board_obj (object): Board object with bitboard attributes.
            move_str (str): Move in LAN (e.g., "e2e4", "e7e8q") or SAN (e.g., "Nf3", "e8=Q").
    
        Returns:
            tuple[int, int]: (encoded_move, promotion_piece) where promotion_piece is 0 if none.
        """
    
        move_str = move_str.replace(" ", "")
        
        lower = move_str.lower()
        if len(lower) >= 4 and lower[0] in 'abcdefgh' and lower[1].isdigit():
            return ChessCore.lan_to_encoded_move(lower)
        
        if board_obj is not None:
            result = ChessCore.sen_to_encoded_move(board_obj, move_str)
            return result if isinstance(result, tuple) else (result, 0)
            
        raise ValueError("SAN moves require a board instance for context.")


    
    def parse_move_and_validate(self, move_str) -> bool:
        """
        Parse a move string, detect promotion, and validate it.
        Sets self.board.encoded_move_in_progress and self.promotion_value on success.

        Args:
            move_str (str): Move string in LAN (e.g., "e2e4", "e7e8q") or SAN (e.g., "Nf3").

        Returns:
            bool: True if the move is structurally valid, False otherwise.
        """

        self.promotion_value = None

        try:
            encoded_move, promotion_piece = ChessCore.move_parser(self.board, move_str)
        except Exception:
            return False

        self.board.encoded_move_in_progress = encoded_move
        if promotion_piece:
            self.promotion_value = promotion_piece

        info = ChessCore.give_move_info(self.board, encoded_move)
        return info is None


    @staticmethod
    def lan_to_encoded_move(lan_move) -> "tuple[int, int]":
        """
        Parse a LAN move string into an encoded move and promotion piece.

        Args:
            lan_move (str): Move string in LAN format (e.g., "e2e4", "e7e8q").
    
        Returns:
            tuple[int, int]: (encoded_move, promotion_piece) where promotion_piece is 0 if none.

        Raises:
            ValueError: If the move string is invalid.
        """
    
        s = lan_move.replace(" ", "").lower()
        promotion_piece = 0

        if len(s) == 5:
            if s[4] in ('q', 'r', 'b', 'n'):
                promotion_piece = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}[s[4]]
                s = s[:4]
            else:
                raise ValueError(f"Invalid promotion piece: {s[4]!r}")
        elif len(s) < 4:
            raise ValueError("Invalid move string")

        return SQUARES[s[0:2]] | (SQUARES[s[2:4]] << 6), promotion_piece
    

    def lan_to_encoded_move_and_validate(self, lan_move) -> "tuple[int, int] | None":
        """
        Parse a LAN move string, set board state, and validate it.
        Sets self.board.encoded_move_in_progress and self.promotion_value on success.

        Args:
            lan_move (str): Move string in LAN format (e.g., "e2e4", "e7e8q").

        Returns:
            tuple[int, int] | None: (encoded_move, promotion_piece) if valid, None otherwise.
        """

        try:
            encoded_move, promotion_piece = ChessCore.lan_to_encoded_move(lan_move)
        except Exception:
            return None

        self.board.encoded_move_in_progress = encoded_move
        self.promotion_value = promotion_piece if promotion_piece else None

        info = ChessCore.give_move_info(self.board, encoded_move)
        if info is not None:
            return None

        return encoded_move, promotion_piece


    @staticmethod
    def sen_to_encoded_move(board_obj, sen_move, side=None) -> int:
        """
        Convert a move in Standard Algebraic Notation (SAN) to an encoded move format.

        Args:
            sen_move (str): Move in SAN format (e.g., "e4", "Nf3", "e8=Q").
            side (int, optional): Side color (WHITE=1 or BLACK=-1). If None, uses the current side to move (default).
        
        Returns:
            int: Encoded move as an integer.
        """
        
        capture = False
        piece_type = PAWN
        promotion_piece = 0

        if side is None:
            side = board_obj.side_to_move

        if sen_move in ["O-O", "O-O-O"]:
            if side == WHITE:
                if sen_move == "O-O":
                    return SQUARES["e1"] | (SQUARES["g1"] << 6)
                else:
                    return SQUARES["e1"] | (SQUARES["c1"] << 6)
            else:
                if sen_move == "O-O":
                    return SQUARES["e8"] | (SQUARES["g8"] << 6)
                else:
                    return SQUARES["e8"] | (SQUARES["c8"] << 6)
                
        if not sen_move[-1].isdigit():       
            if sen_move[-1] in ('Q', 'R', 'B', 'N') and '=' in sen_move:
                promotion_piece = {'Q': QUEEN, 'R': ROOK, 'B': BISHOP, 'N': KNIGHT}[sen_move[-1]]
                sen_move = sen_move[:-2]
            
            elif sen_move[-1] in ('q', 'r', 'b', 'n') and '=' in sen_move:
                promotion_piece = {'q': QUEEN, 'r': ROOK, 'b': BISHOP, 'n': KNIGHT}[sen_move[-1]]
                sen_move = sen_move[:-2]

            elif sen_move[-1] in ('+', '#'):
                sen_move = sen_move[:-1]

            else:
                raise ValueError("Invalid SAN move: unrecognized promotion or check/mate symbol.")


        to_square = SQUARES[sen_move[-2:]] 

        if 'x' in sen_move:
            sen_move = sen_move.replace('x', '')
            capture = True

        if sen_move[0] in ('K', 'Q', 'R', 'B', 'N'):
            piece_type = {'K': KING, 'Q': QUEEN, 'R': ROOK, 'B': BISHOP, 'N': KNIGHT}[sen_move[0]]
            sen_move = sen_move[1:]

        if sen_move[:-2] in 'abcdefgh':
            column = sen_move[:-2]

        if piece_type == KING:
            if side == WHITE:
                from_square = (KING_TABLE[to_square] & board_obj.king & board_obj.board_occupied_squares[WHITE_INDEX]).bit_length() - 1
            else:
                from_square = (KING_TABLE[to_square] & board_obj.king & board_obj.board_occupied_squares[BLACK_INDEX]).bit_length() - 1

            return from_square | (to_square << 6)
        
        elif piece_type == ROOK:
            occ_rel = ROOK_MASK[to_square] & board_obj.all_board_occupied_squares
            idx = ((occ_rel * ROOK_MAGIC[to_square]) & U64) >> ROOK_SHIFT[to_square]

            own_occ = board_obj.board_occupied_squares[WHITE_INDEX if side == WHITE else BLACK_INDEX]
            candidates = ROOK_TABLE[to_square][idx] & board_obj.rook & own_occ

            if column and candidates & ~FILE_MASKS[FILE_INDEXES[column]]:
                candidates &= FILE_MASKS[FILE_INDEXES[column]]
            from_square = candidates.bit_length() - 1

        elif piece_type == BISHOP:
            occ_rel = BISHOP_MASK[to_square] & board_obj.all_board_occupied_squares
            idx = ((occ_rel * BISHOP_MAGIC[to_square]) & U64) >> BISHOP_SHIFT[to_square]

            own_occ = board_obj.board_occupied_squares[WHITE_INDEX if side == WHITE else BLACK_INDEX]
            candidates = BISHOP_TABLE[to_square][idx] & board_obj.bishop & own_occ

            if column and candidates & ~FILE_MASKS[FILE_INDEXES[column]]:
                candidates &= FILE_MASKS[FILE_INDEXES[column]]
            from_square = candidates.bit_length() - 1

        elif piece_type == QUEEN:
            occ_rel_rook = ROOK_MASK[to_square] & board_obj.all_board_occupied_squares
            occ_rel_bishop = BISHOP_MASK[to_square] & board_obj.all_board_occupied_squares

            idx_rook = ((occ_rel_rook * ROOK_MAGIC[to_square]) & U64) >> ROOK_SHIFT[to_square]
            idx_bishop = ((occ_rel_bishop * BISHOP_MAGIC[to_square]) & U64) >> BISHOP_SHIFT[to_square]

            own_occ = board_obj.board_occupied_squares[WHITE_INDEX if side == WHITE else BLACK_INDEX]
            candidates = (ROOK_TABLE[to_square][idx_rook] | BISHOP_TABLE[to_square][idx_bishop]) & board_obj.queen & own_occ

            if column and candidates & ~FILE_MASKS[FILE_INDEXES[column]]:
                candidates &= FILE_MASKS[FILE_INDEXES[column]]
            from_square = candidates.bit_length() - 1

        elif piece_type == KNIGHT:
            own_occ = board_obj.board_occupied_squares[WHITE_INDEX if side == WHITE else BLACK_INDEX]
            candidates = KNIGHT_TABLE[to_square] & board_obj.knight & own_occ

            if column and candidates & ~FILE_MASKS[FILE_INDEXES[column]]:
                candidates &= FILE_MASKS[FILE_INDEXES[column]]
            from_square = candidates.bit_length() - 1

        elif piece_type == PAWN:
            if not capture:
                if side == WHITE:
                    if board_obj.get_piece_type_and_color(to_square - 8) == PAWN:
                        from_square = to_square - 8
                    elif board_obj.get_piece_type_and_color(to_square - 16) == PAWN:
                        from_square = to_square - 16
                else:
                    if board_obj.get_piece_type_and_color(to_square + 8) == -PAWN:
                        from_square = to_square + 8
                    elif board_obj.get_piece_type_and_color(to_square + 16) == -PAWN:
                        from_square = to_square + 16
            else:
                possible_from_squares = []
                if side == WHITE:
                    if board_obj.get_piece_type_and_color(to_square - 7) == PAWN and (to_square + 1) % 8 != 0:
                        possible_from_squares.append(to_square - 7)
                    if board_obj.get_piece_type_and_color(to_square - 9) == PAWN and (to_square % 8) != 0:
                        possible_from_squares.append(to_square - 9)
                else:
                    if board_obj.get_piece_type_and_color(to_square + 7) == -PAWN and (to_square + 1) % 8 != 0:
                        possible_from_squares.append(to_square + 7)
                    if board_obj.get_piece_type_and_color(to_square + 9) == -PAWN and (to_square % 8) != 0:
                        possible_from_squares.append(to_square + 9)

                if len(possible_from_squares) == 1:
                    from_square = possible_from_squares[0]
                elif column:
                    for sq in possible_from_squares:
                        if sq // 8 == FILE_INDEXES[column]:
                            from_square = sq
                            break
                else:
                    from_square = -1

        if from_square == -1:
            raise ValueError("Invalid SAN move.")

        return from_square | (to_square << 6), promotion_piece
    

    def san_to_encoded_move_and_validate(board_obj, san_move, side=None) -> "int | str":
        """
        Convert a move in Standard Algebraic Notation (SAN) to an encoded move format and validate it.

        Args:
            board_obj (object): Board object with bitboard attributes.
            san_move (str): Move in SAN format (e.g., "e4", "Nf3", "e8=Q").
            side (int, optional): Side color (WHITE=1 or BLACK=-1). If None, uses the current side to move (default).
        """

        try:
            encoded_move = board_obj.sen_to_encoded_move(san_move, side)
            board_obj.encoded_move_in_progress = encoded_move
            validation_result = ChessCore.give_move_info()
        
            if validation_result is not None:
                return validation_result
        
            return encoded_move
        
        except Exception as e:
            return f"Invalid SAN move: {str(e)}"


    def play(self, side="white") -> str:
        """
        Run an interactive chess game loop.
        
        Args:
            side (str, optional): Starting side ('white' or 'black'). Defaults to 'white'.

        Returns:
            str: 'checkmate' or 'draw' when game ends.
        """

        self.start_new_game(side=side)
        
        while True:
            all_move = input("> ")
            result = self.play_move(all_move, print_move=False)
            if result == 'checkmate':
                return 'checkmate' 
            
            elif result == 'draw':
                return 'draw'

    
    def force_move(self, move) -> None:
        """
        Apply a move without legality checks (for engine or testing use).

        Args:
            move (str): Move string (e.g., "e2 e4", or "e7 e8q" for promotion).

        Raises:
            ValueError: If the move string format is invalid.
        """

        promotion_piece = 0

        if not self.parse_move_and_validate(move):
            raise ValueError(f"Invalid move format: {move!r}")
        
        promotion_piece = self.promotion_value or 0

        if not promotion_piece:
            from_sq = self.board.encoded_move_in_progress & 0x3F
            to_sq = (self.board.encoded_move_in_progress >> 6) & 0x3F
            piece = self.board.get_piece_type_and_color(from_sq)
            if (piece == PAWN and to_sq >= 56) or (piece == -PAWN and to_sq <= 7):
                promotion_piece = QUEEN

        self.board.make_move(self.board.encoded_move_in_progress, self.board.side_to_move, promotion_piece)

        self.board.change_side()
        self.board.add_to_history()
            
    
    def is_game_over(self) -> "bool | str":
        """
        Check if the game is over due to checkmate, stalemate, threefold repetition, fifty-move rule, or insufficient material.

        Returns:
            bool or str: 'checkmate', 'draw', or False if the game is not over.
        """

        is_in_check = GameState.attackers_to(self.board, self.board.side_to_move, self.board.king_square[WHITE_INDEX if self.board.side_to_move == WHITE else BLACK_INDEX])

        has_moves = any(MoveGen.generate_all_moves(self.board, self.board.side_to_move))

        if not has_moves:
            return 'checkmate' if is_in_check else 'draw'

        if GameState.check_repetition(self.board):
            return 'draw'
        
        if self.board.counter_halfmove_without_capture >= 100:
            return 'draw'

        if self.board.material_insufficiency():
            return 'draw'

        return False
    

    def commit(self, move) -> "str":
        """
        Commit a move without legality checks (for AI or testing purposes).
        Returns the game outcome if the game is finished.

        Args:
            move (str): Move string (e.g., "e2 e4", or "e7 e8q" for promotion).

        Returns:
            str or None: 'checkmate', 'draw' if game ends, or None if game continues.
        """

        self.force_move(move)
        
        outcome = self.is_game_over()

        if outcome:
            self.party_over = True
            return outcome

        return None



if __name__ == "__main__":
    process = ChessCore()
    process.play()
