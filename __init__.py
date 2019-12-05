import chess

def checkSquare(square: chess.Square):
    if square not in chess.SQUARES:
        raise