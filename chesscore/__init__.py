from . import constants as constant
from .constants import *
from .constants import __all__ as _constants_all
from .chess_game import *
from .chess_game import __all__ as _chess_game_all
from .chess_game import __version__, __author__

__all__ = [*dict.fromkeys([*_chess_game_all, *_constants_all, "constant", "__version__", "__author__"])]
