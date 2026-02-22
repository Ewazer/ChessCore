try:
    from .constants import *
    from .constants import __all__ as _constants_all
except ImportError:
    from constants import *
    from constants import __all__ as _constants_all

__version__ = "3.0.1"
__author__ = "Leroux Lubin"

__all__ = ["ChessCore", "Board", "MoveGen", "GameState", "ChessDisplay", *_constants_all]

class Board:
    __slots__ = (
        'pawn', 'knight', 'bishop', 'rook', 'queen', 'king','board_occupied_squares', 'all_board_occupied_squares', 'king_square',
        'move_history', 'side_to_move', 'counter_halfmove_without_capture','castling_rights', 'position_has_loaded', 'en_passant_square',
        'last_position_hash', 'position_hash_history', 'encoded_move_in_progress','start_coordinate', 'end_coordinate', 'start_value', 'end_value', 'capture_value'
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


    def load_board(self, fen) -> None:
        """
        Load a custom board position.

        Args:
            fen (str): FEN string representing the board state.
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
                print("\033[31mFEN string is invalid (board position).\033[0m")
                return
            
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

                    if type(position[i]) != str:
                        print("\033[31mFEN string is invalid (board position).\033[0m")
                        return
                    
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
                            print("\033[31mFEN string is invalid (board position).\033[0m")
                            return
                        
                    if file != 8:
                        print("\033[31mFEN string is invalid (board position).\033[0m")
                        return

            if fen[1] in ("w", "b"): 
                side = WHITE if fen[1] == "w" else BLACK

            else:
                print("\033[31mFEN string is invalid (side to move).\033[0m")
                return
            
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
                print("\033[31mFEN string is invalid (castling rights).\033[0m")
                return

            if fen[3] == "-":
                en_passant_square = 0
            elif len(fen[3]) == 2 and fen[3][0] in "abcdefgh" and fen[3][1] in "36":
                file_idx = ord(fen[3][0]) - ord('a')
                rank_idx = int(fen[3][1]) - 1
                en_passant_square = rank_idx * 8 + file_idx
            else:
                print("\033[31mFEN string is invalid (en passant square).\033[0m")
                return

            if fen[4].isdigit():
                if int(fen[4]) >= 0:
                    counter_halfmove_without_capture = int(fen[4])
                else:
                    print("\033[31mFEN string is invalid.\033[0m")
                    return 
            else:
                    print("\033[31mFEN string is invalid.\033[0m")
                    return 

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
        else:
            print("\033[31mFEN string is invalid.\033[0m")

        return 
    
    
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

        mask = SQUARE_MASK[square]

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
            mask = SQUARE_MASK[square]
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
                # Promotion: remove pawn, add promoted piece
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

                elif to == en_passant_prev:
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
        

    def move_parser(self, move_str) -> int:
        """
        Parse a move string.

        Args:
            move_str (str): Move string (e.g., "e2 e4").
    
        Returns:
            int: Encoded move value.
        """
    
        all_move = move_str.split(" ")  
        return SQUARES[all_move[0]] | (SQUARES[all_move[1]] << 6)
    
    
    def parse_move_and_validate(self, all_move) -> bool:
        """
        Parse a move string and validate it.

        Args:
            all_move (str): Move string (e.g., "e2 e4").

        Returns:
            bool: True if valid, False otherwise.
        """

        try:
            a, b = all_move.split()
            self.encoded_move_in_progress = SQUARES[a] | (SQUARES[b] << 6)
            return True
        
        except Exception:
            return False


    def give_move_info(self) -> "None | str":
        """
        Extract move information.
    
        Returns:
            None or str: None if the move is valid, or str if the move is invalid.
        """

        self.start_coordinate = self.encoded_move_in_progress & 0x3F
        self.end_coordinate = (self.encoded_move_in_progress >> 6) & 0x3F
        
        self.start_value = self.get_piece_type_and_color(self.start_coordinate)         
        self.end_value = self.get_piece_type_and_color(self.end_coordinate)

        if self.start_value == EMPTY:
            return 'illegal'

        if self.start_value == 0 or (self.start_value > 0) != (self.side_to_move == WHITE):
            return "It's not your turn."

        if self.end_value == EMPTY:
            self.capture_value = EMPTY
        elif (self.end_value < 0 and self.start_value > 0) or (self.end_value > 0 and self.start_value < 0):
            self.capture_value = self.end_value
        else:
            return 'illegal'



class MoveGen:      
    def list_all_pawn_move(board_obj, color) -> list[int]:
        """
        Generate all valid pawn moves for the specified color, including en passant.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_p_move = []
        append = list_p_move.append

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
                en_passant_square_mask = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_square_mask & ~FILE_MASKS[0]) >> 9) | ((en_passant_square_mask & ~FILE_MASKS[7]) >> 7))
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
                en_passant_square_mask = 1 << en_passant_square
                en_passant_square_attackers = pawn_board & (((en_passant_square_mask & ~FILE_MASKS[0]) << 7) | ((en_passant_square_mask & ~FILE_MASKS[7]) << 9))
                while en_passant_square_attackers:
                    least_significant_bit = en_passant_square_attackers & -en_passant_square_attackers
                    from_ = least_significant_bit.bit_length() - 1
                    en_passant_square_attackers ^= least_significant_bit
                    append(from_ | (en_passant_square << 6))

        return list_p_move
    

    def list_all_knight_move(board_obj, color) -> list[int]:
        """
        Generate all valid knight moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_move = []
        append = list_k_move.append

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

        return list_k_move


    @staticmethod
    def list_all_rook_move(board_obj, color) -> list[int]:
        """
        Generate all valid rook moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_r_move = []
        append = list_r_move.append

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
        
        return list_r_move
    

    @staticmethod
    def list_all_bishop_move(board_obj, color) -> list[int]:
        """
        Generate all valid bishop moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_b_move = []
        append = list_b_move.append

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
        
        return list_b_move
    

    @staticmethod
    def list_all_queen_move(board_obj, color) -> list[int]:
        """
        Generate all queen bishop moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_q_move = []
        append = list_q_move.append

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

        return list_q_move


    @staticmethod
    def list_all_king_move(board_obj, color, castling=True) -> list[int]:
        """
        Generate all king moves for the specified color.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (int): Piece color (WHITE=1 or BLACK=-1).
            castling (optional bool): Whether to include castling moves. Defaults to True.

        Returns:
            list: Encoded moves as (from_square | (to_square << 6)).
        """

        list_k_move = []

        own_occupied_squares = board_obj.board_occupied_squares[WHITE_INDEX if color == WHITE else BLACK_INDEX]

        king_board = board_obj.king & own_occupied_squares

        free_squares = (~own_occupied_squares) & U64 

        from_ = king_board.bit_length() - 1

        to_possibilities = KING_TABLE[from_] & free_squares
        while to_possibilities:
            least_significant_bit2 = to_possibilities & -to_possibilities
            to = least_significant_bit2.bit_length() - 1
            to_possibilities &= to_possibilities - 1

            list_k_move.append(from_ | (to << 6))

        if castling:
            list_k_move.extend(MoveGen.list_all_castling_move(board_obj, color))

        return list_k_move
    
    
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

        list_castling_move = []

        rights = board_obj.castling_rights
        all_board_occupied_squares = board_obj.all_board_occupied_squares
        attackers_to = GameState.attackers_to

        if color == WHITE:
            canKingsideCastling = (rights & CR_WK) and (all_board_occupied_squares & WK_EMPTY) == 0
            canQueensideCastling = (rights & CR_WQ) and (all_board_occupied_squares & WQ_EMPTY) == 0
            if not (canKingsideCastling or canQueensideCastling):
                return list_castling_move

            if attackers_to(board_obj, WHITE, 4):
                return list_castling_move

            if canKingsideCastling and (not attackers_to(board_obj, WHITE, 5)):
                list_castling_move.append(4 | (6 << 6))

            if canQueensideCastling and (not attackers_to(board_obj, WHITE, 3)):
                list_castling_move.append(4 | (2 << 6))

        else:
            canKingsideCastling = (rights & CR_BK) and (all_board_occupied_squares & BK_EMPTY) == 0
            canQueensideCastling = (rights & CR_BQ) and (all_board_occupied_squares & BQ_EMPTY) == 0
            if not (canKingsideCastling or canQueensideCastling):
                return list_castling_move

            if attackers_to(board_obj, BLACK, 60):
                return list_castling_move

            if canKingsideCastling and (not attackers_to(board_obj, BLACK, 61)):
                list_castling_move.append(60 | (62 << 6))

            if canQueensideCastling and (not attackers_to(board_obj, BLACK, 59)):
                list_castling_move.append(60 | (58 << 6))

        return list_castling_move


    @staticmethod
    def list_all_legal_move(board_obj, side, castling = True) -> list[int]:
        """
        Generate all legal moves for a side (excluding moves leaving king in check).
        
        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int): Side color (WHITE=1 or BLACK=-1).
            castling (bool, optional): Whether to include castling moves. Defaults to True.
        
        Returns:
            list: Encoded castling moves as (from_square | (to_square << 6)).
        """
        
        list_all_move = []
        append = list_all_move.append

        make = board_obj.make_move
        unmake = board_obj.unmake_move
        attackers_to = GameState.attackers_to
        king_square = board_obj.king_square
        INDEX = WHITE_INDEX if side == WHITE else BLACK_INDEX

        gens = (
            MoveGen.list_all_pawn_move,
            MoveGen.list_all_knight_move,
            MoveGen.list_all_bishop_move,
            MoveGen.list_all_rook_move,
            MoveGen.list_all_queen_move,
            lambda b, s: MoveGen.list_all_king_move(b, s, castling),
        )

        for gen in gens:
            for mv in gen(board_obj, side):
                undo = make(mv, side)
                if not attackers_to(board_obj, side, king_square[INDEX]):
                    append(mv)
                unmake(undo, side)

        return list_all_move


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

        for e in MoveGen.list_all_king_move(board_obj, side, castling):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_queen_move(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_knight_move(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
    
        for e in MoveGen.list_all_bishop_move(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e

        for e in MoveGen.list_all_rook_move(board_obj, side):
            undo = make(e, side)
            legal = not attackers_to(board_obj, side, king_square[INDEX])
            unmake(undo, side)
            if legal:
                yield e
        
        for e in MoveGen.list_all_pawn_move(board_obj, side):
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
            potential_moves = MoveGen.list_all_pawn_move(board_obj, color)
        elif abs(piece_value) == KNIGHT:
            potential_moves = MoveGen.list_all_knight_move(board_obj, color)
        elif abs(piece_value) == BISHOP:
            potential_moves =  MoveGen.list_all_bishop_move(board_obj, color)
        elif abs(piece_value) == ROOK:
            potential_moves =  MoveGen.list_all_rook_move(board_obj, color)
        elif abs(piece_value) == QUEEN:
            potential_moves =  MoveGen.list_all_queen_move(board_obj, color)
        elif abs(piece_value) == KING:
            potential_moves =  MoveGen.list_all_king_move(board_obj, color)
        else:
            potential_moves = []
        
        list_move = []
        for e in potential_moves:
            if (e & 0x3F) == square:
                list_move.append(e)

        return list_move



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
        mask = SQUARE_MASK[from_sq]

        if board_obj.pawn & mask:
            pseudo_moves = MoveGen.list_all_pawn_move(board_obj, side)
        elif board_obj.knight & mask:
            pseudo_moves = MoveGen.list_all_knight_move(board_obj, side)
        elif board_obj.bishop & mask:
            pseudo_moves = MoveGen.list_all_bishop_move(board_obj, side)
        elif board_obj.rook & mask:
            pseudo_moves = MoveGen.list_all_rook_move(board_obj, side)
        elif board_obj.queen & mask:
            pseudo_moves = MoveGen.list_all_queen_move(board_obj, side)
        elif board_obj.king & mask:
            pseudo_moves = MoveGen.list_all_king_move(board_obj, side)
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

        if side == WHITE:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)] for i in range(8)][::-1]
        else:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)][::-1] for i in range(8)]

        for row in board_rendu:
            print(row)
    

    @staticmethod
    @print_disabled
    def print_game_start(board_obj, side=WHITE) -> None:
        """
        Print the game start message and board.

        Args:
            board_obj (object): Board object with bitboard attributes.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        print("╔═════════════ GAME START ═════════════╗")

        print()
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == WHITE else "⚫ ═══════════ Black play ═══════════ ⚫")
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
        print("⚪ ═══════════ White play ═══════════ ⚪" if side == WHITE else "⚫ ═══════════ Black play ═══════════ ⚫")
        print()


    @staticmethod
    def print_game_already_over() -> None:
        """Print a message indicating the game is already over."""

        print("🚫 ════════ The game is over ════════ 🚫")
        return


    @staticmethod
    def print_invalid_move(reason=None) -> None:
        """
        Print an invalid move message.

        Args:
            reason (str, optional): Optional reason for the invalid move.
        """

        print("🚫 ══════════ Invalid move ══════════ 🚫")

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

        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(board_obj, winner if side == None else side)
        print()
        print(f"╚════════ CHECKMATE {'WHITE' if winner == WHITE else 'BLACK'} WIN ═════════╝")


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

        print("════════════════════════════════════════")
        print()
        ChessDisplay.print_board(board_obj, side)
        print()

        if draw_type == 'insufficient_material':
            print("⏸ ══ Draw by insufficient material ═ ⏸")

        elif draw_type == 'fifty_move_rule':
            print("⏸ ═════ Draw by fifty-move rule ════ ⏸")

        elif draw_type == 'threefold_repetition':
            print("⏸ ═══════ Draw by repetition ═══════ ⏸")
        
        elif draw_type == 'stalemate':
            print("⏸ ══════ Draw by stalemate ═══════ ⏸")

        else:
            print("⏸ ══════════════ Draw ══════════════ ⏸")
            

    @staticmethod
    @print_disabled
    def print_move(move) -> None:
        """
        Print a chess move.
        
        Args:
            move (str): Move string (e.g., "e2 e4").
        """

        print(f"> {move}")
        print()

    
    @staticmethod
    @print_disabled
    def print_invalid_format() -> None:
        """Print an invalid format message with example."""

        print("🚫 ═════════ Invalid format ═════════ 🚫")
        print("Valid move example: ✅--- e2 e4 ---✅")


    @staticmethod
    def print_row_as_list(row) -> None:
        """
        Print a board row with empty cells shown as '#'.
        
        Args:
            row (list): Row of piece symbols.
        """

        import re
        
        EMPTY_CHAR = "#"  
        parts = []

        for cell in row:
            raw = re.compile(r"\x1b\[[0-9;]*m").sub("", cell)     
            if raw == " ":
                cell = cell.replace(" ", EMPTY_CHAR)
            parts.append(f"'{cell}'")

        print("[" + ", ".join(parts) + "]")


    @staticmethod
    def color_to_code(color) -> tuple:
        """
        Convert a color name to ANSI codes.

        Args:
            color (str): Color name ("red", "green", "yellow", "blue", "magenta", "cyan").

        Returns:
            tuple: (start_code, end_code) or (None, None) if invalid.
        """

        if color == "red":
            return "\033[31m", "\033[0m"
        elif color == "green": 
            return "\033[32m", "\033[0m"
        elif color == "yellow":
            return "\033[33m", "\033[0m"
        elif color == "blue":
            return "\033[34m", "\033[0m"
        elif color == "magenta":
            return "\033[35m", "\033[0m"
        elif color == "cyan":
            return "\033[36m", "\033[0m"
        else:
            return None, None

    
    @staticmethod
    def print_last_move_highlighted(board_obj, color, side = WHITE) -> None:
        """
        Print the board with the last move highlighted.

        Args:
            board_obj (object): Board object representing the board.
            color (str): Highlight color name.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        if not board_obj.move_history:
            ChessDisplay.print_board(board_obj, side)
            return

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(board_obj, side)
            return

        if side == WHITE:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)] for i in range(8)][::-1]
        else:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)][::-1] for i in range(8)]

        last_encoded = board_obj.move_history[-1]
        from_sq = last_encoded & 0x3F
        to_sq = (last_encoded >> 6) & 0x3F

        last_move = []
        for square in (from_sq, to_sq):
            square_row, square_col = divmod(square, 8)
            last_move.append((square_row, square_col))

        for coord in last_move:
            y, x = coord
            
            if side == WHITE:
                row_idx = 7 - y
                col_idx = x
            else:
                row_idx = y
                col_idx = 7 - x
                
            board_rendu[row_idx][col_idx] = f"{start_highlight}{board_rendu[row_idx][col_idx]}{end_highlight}"
                                                                                    
        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)


    @staticmethod
    def print_highlighted_legal_move(board_obj, color, square, side = WHITE) -> None:
        """
        Print the board with legal moves for a piece highlighted.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (str): Highlight color name.
            square (int or str): Square index (0-63) or algebraic like 'e2'.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """
        
        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(board_obj, side)
            return

        if side == WHITE:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(s)] for s in range(i * 8, (i + 1) * 8)] for i in range(8)][::-1]
        else:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(s)] for s in range(i * 8, (i + 1) * 8)][::-1] for i in range(8)]

        if isinstance(square, int):
            square_idx = square
        else:
            try:
                square_idx = SQUARES[square]
            except Exception:
                print("⚠️ Invalid square argument.")
                ChessDisplay.print_board(board_obj, side)
                return

        piece_val = board_obj.get_piece_type_and_color(square_idx)
        list_move = MoveGen.list_all_piece_move(board_obj, square_idx, piece_val)
        
        for move in list_move:
            from_square = move & 0x3F
            to_square = (move >> 6) & 0x3F
            
            for sq in (from_square, to_square):
                square_row, square_col = divmod(sq, 8)
                
                if side == WHITE:
                    render_row, render_col = 7 - square_row, square_col
                else:
                    render_row, render_col = square_row, 7 - square_col

                if not board_rendu[render_row][render_col].startswith(start_highlight):
                    board_rendu[render_row][render_col] = f"{start_highlight}{board_rendu[render_row][render_col]}{end_highlight}"

        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)


    @staticmethod
    def print_highlighted_all_legal_move(board_obj, color, side = WHITE) -> None:
        """
        Print the board with all legal moves highlighted.

        Args:
            board_obj (object): Board object with bitboard attributes.
            color (str): Highlight color name.
            side (int, optional): Side color (WHITE=1 or BLACK=-1).
        """

        start_highlight, end_highlight = ChessDisplay.color_to_code(color)

        if start_highlight is None or end_highlight is None:
            print("⚠️ Invalid color for highlighting.")
            ChessDisplay.print_board(board_obj, side)
            return

        if side == WHITE:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)] for i in range(8)][::-1]
        else:
            board_rendu = [[piece_note_style[board_obj.get_piece_type_and_color(square)] for square in range(i * 8, (i + 1) * 8)][::-1] for i in range(8)]

        list_move = MoveGen.list_all_legal_move(board_obj, side)
        
        for move in list_move:
            from_square = move & 0x3F
            to_square = (move >> 6) & 0x3F
            
            for square_idx in (from_square, to_square):
                square_row, square_col = divmod(square_idx, 8)
                
                if side == WHITE:
                    render_row, render_col = 7 - square_row, square_col
                else:
                    render_row, render_col = square_row, 7 - square_col
                    
                if not board_rendu[render_row][render_col].startswith(start_highlight):
                    board_rendu[render_row][render_col] = f"{start_highlight}{board_rendu[render_row][render_col]}{end_highlight}"

        for row in board_rendu:
            ChessDisplay.print_row_as_list(row)



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

        self.promotion_value = None

        if len(all_move) == 6:
            if all_move[-1] in ('q','r','b','n'):
                self.promotion_value = {'q':QUEEN,'r':ROOK,'b':BISHOP,'n':KNIGHT}[all_move[-1]]

                if not self.board.parse_move_and_validate(all_move[:-1]):
                    ChessDisplay.print_invalid_format()
                    self.promotion_value = None
                    return 'illegal'
                
            else:
                ChessDisplay.print_invalid_format()
                return 'illegal'
        
        elif not self.board.parse_move_and_validate(all_move):
            ChessDisplay.print_invalid_format()
            return 'illegal'

        self.info_move = self.board.give_move_info()

        if self.info_move:
            if self.info_move != "illegal":
                ChessDisplay.print_invalid_move(self.info_move)
                return 'illegal'
            else:
                ChessDisplay.print_invalid_move("Illegal move coordinates.")
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
        ChessDisplay.print_board(self.board, self.board.side_to_move)
        
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
        
        legal_move = MoveGen.list_all_legal_move(self.board, WHITE if self.board.side_to_move == BLACK else BLACK)      

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

    
    def god_mode(self, move) -> None:
        """
        Apply a move without any checks (for testing or AI purposes).

        Args:
            move (str): Move string (e.g., "e2 e4", or "e7 e8q" for promotion).
        """

        promotion_piece = 0

        if len(move) == 6 and move[-1] in ('q','r','b','n'):
            promotion_piece = {'q':QUEEN,'r':ROOK,'b':BISHOP,'n':KNIGHT}[move[-1]]
            move = move[:-1]

        if not self.board.parse_move_and_validate(move):
            print("Invalid move format for commit.")
            return
        
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

        self.god_mode(move)
        
        outcome = self.is_game_over()

        if outcome:
            self.party_over = True
            return outcome

        return None


if __name__ == "__main__":
    process = ChessCore()
    process.play()

# yes, we are in 2026 :=)
