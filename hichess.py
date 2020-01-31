import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

import logging
from functools import partial
from typing import Optional, Callable, Mapping

from . import resources


class IllegalMoveError(Exception):
    pass


class SquareWidget(QtWidgets.QPushButton):
    def __init__(self, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        self._square = None
        self.square = square

    @property
    def square(self) -> Optional[chess.Square]:
        return self._square

    @square.setter
    def square(self, square) -> None:
        if square not in chess.SQUARES:
            raise ValueError("Square {} does not exist".format(square))
        self._square = square

    def __eq__(self, other):
        if isinstance(other, SquareWidget):
            return self._square == other.square
        return NotImplemented

    def __ne__(self, other):
        return not self == other

class PieceWidget(SquareWidget):
    def __init__(self, square: chess.Square, piece: chess.Piece,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)

        self._piece = piece

        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.transformInto(piece.piece_type)
        self.setIconSize(self.size())

    @property
    def piece(self) -> chess.Piece:
        return self._piece

    @piece.setter
    def piece(self, pieceType: chess.PieceType) -> None:
        self.transformInto(pieceType)

    def transformInto(self, pieceType: chess.PieceType) -> None:
        self._piece.piece_type = pieceType
        colorName = chess.COLOR_NAMES[self._piece.color]
        pieceName = chess.PIECE_NAMES[pieceType]
        self.setIcon(QtGui.QIcon(":/images/{}_{}.png".format(colorName, pieceName)))

    def __eq__(self, other):
        if isinstance(other, PieceWidget):
            return self._square == other.square and self._piece == other.piece
        return NotImplemented


class HighlightedSquareWidget(SquareWidget):
    def __init__(self, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)

        self.setIcon(QtGui.QIcon(":/images/highlighted_square"))
        self.setIconSize(self.size() / 4)


class BoardLayout(QtCore.QObject):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 adjustWidget: Callable[[QtWidgets.QWidget], None] = lambda w: None):
        super().__init__(parent=parent)

        self.widgets = []
        self.adjustWidget = adjustWidget

    def addWidget(self, w: QtWidgets.QWidget) -> None:
        if not self._insideLayout(w):
            w.setParent(self.parent())
            self.widgets.append(w)
            self.adjustWidget(w)
            w.show()
        else:
            logging.warning("BoardLayout: Attempting to add a widget, which already is in a layout")

    def removeWidget(self, w: QtWidgets.QWidget) -> None:
        self.widgets.remove(w)
        w.setParent(None)

    def deleteWidgets(self, function: Callable[[QtWidgets.QWidget], bool] = lambda w: True) -> None:
        list(map(QtWidgets.QWidget.deleteLater, filter(function, self.widgets)))
        self.widgets = list(filter(lambda w: not function(w), self.widgets))

    def eventFilter(self, watched: QtCore.QObject, event: QtGui.QResizeEvent) -> bool:
        if watched == self.parent() and event.type() == QtCore.QEvent.Resize:
            watched.heightForWidth(max(watched.width(), watched.height()))
            for w in self.widgets:
                self.adjustWidget(w)
            return True
        return super().eventFilter(watched, event)

    def _insideLayout(self, w: QtWidgets.QWidget):
        return w is not None and w.parent() is not None and w.parent().layout() is not self


class BoardWidget(QtWidgets.QLabel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 fen: Optional[str] = chess.STARTING_FEN,
                 flipped: bool = False):
        super().__init__(parent=parent)

        self.board = chess.Board(fen)
        self.flipped = flipped
        self._boardLayout = None
        self.toggledWidget = None

        self.setLayout(BoardLayout(self, self._adjustWidget))
        self.setPieceMap(self.board.piece_map())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        self.setStyleSheet("QPushButton { background: transparent; }")

    def widgetAt(self, square: chess.Square) -> Optional[SquareWidget]:
        dict = {w.square: w for w in self._boardLayout.widgets}
        return dict[square]

    def pieceWidgetAt(self, square: chess.Square) -> Optional[PieceWidget]:
        piece = self.board.piece_at(square)
        if piece is not None:
            dict = {w.square: w for w in self._boardLayout.widgets}
            if isinstance(dict[square], PieceWidget):
                return dict[square]
        return None

    def moveWidget(self, toSquare: chess.Square, w: QtWidgets.QWidget) -> None:
        w.square = toSquare

        # Window coordinates start at top left while board coordinates start at
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare) * w.width()
        y = chess.square_rank(toSquare) * w.height()
        w.move(x, y)

    def movePieceWidget(self, toSquare: chess.Square, w: PieceWidget) -> None:
        piece = w.piece
        self.board.remove_piece_at(w.square)
        self.board.set_piece_at(toSquare, piece)

        w.square = toSquare
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare) * w.width()
        y = chess.square_rank(toSquare) * w.height()
        w.move(x, y)

    def addPiece(self, square: chess.Square, piece: chess.Piece) -> PieceWidget:
        if self.board.piece_at(square) is not None:
            raise ValueError("Square {} is already occupied")

        self.board.set_piece_at(square, piece)
        w = PieceWidget(square, piece)
        self._boardLayout.addWidget(w)
        w.toggled.connect(partial(self.onPieceWidgetToggled, w))

        return w

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        for square, piece in pieces.items():
            w = PieceWidget(square, piece)
            self._boardLayout.addWidget(w)
            w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def setFen(self, fen: str) -> None:
        self.board.set_fen(fen)
        self._boardLayout.deleteWidgets()

        for square, piece in self.board.piece_map().items():
            w = PieceWidget(square, piece)
            self._boardLayout.addWidget(w)
            w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def isPseudoLegalPromotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)
        if piece is not None and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                return chess.A7 <= move.from_square <= chess.H7 and chess.A8 <= move.to_square <= chess.H8
            elif piece.color == chess.BLACK:
                return chess.A2 <= move.from_square <= chess.H2 and chess.A1 <= move.to_square <= chess.H1
        return False

    def pushPieceWidget(self, toSquare: chess.Square, w: PieceWidget) -> None:
        move = chess.Move(w.square, toSquare)

        if self.isPseudoLegalPromotion(move):
            # TODO Create a promotion dialogue
            move.promotion = chess.QUEEN

            if not self.board.is_legal(move):
                raise IllegalMoveError("illegal move {} with {}".format(move, chess.PIECE_NAMES[w.piece.piece_type]))

            w.transformInto(move.promotion)

        logging.debug("\n{} ({} -> {})".format(self.board.lan(move), w.square, toSquare))

        self.board.push(move)
        self.setFen(self.board.fen())

        logging.debug("\n{}\n".format(self.board))

        self.deleteHighlightedSquares()

    def push(self, move: chess.Move) -> "BoardWidget":
        for w in self._boardLayout.widgets:
            if w.square == move.from_square:
                self.pushPieceWidget(move.to_square, w)
        return self

    def pop(self) -> "BoardWidget":
        move = self.board.pop()

        for w in self._boardLayout.widgets:
            if w.square == move.to_square:
                self.movePieceWidget(move.from_square, w)

        return self

    def highlightLegalMovesFor(self, w: PieceWidget) -> None:
        def connectWidget(square, w):
            w.clicked.connect(partial(self.pushPieceWidget, square, self.toggledWidget))

        for move in self.board.legal_moves:
            if w == self.pieceWidgetAt(move.from_square):
                highlightedSquare = HighlightedSquareWidget(move.to_square)
                self._boardLayout.addWidget(highlightedSquare)
                connectWidget(move.to_square, highlightedSquare)

    def deleteHighlightedSquares(self) -> None:
        self._boardLayout.deleteWidgets(
            lambda w: isinstance(w, HighlightedSquareWidget)
        )

    def flip(self) -> "BoardWidget":
        self.flipped = not self.flipped
        self._setBoardPixmap()

        for w in self._boardLayout.widgets:
            self.moveWidget(w.square, w)

        return self

    def layout(self) -> BoardLayout:
        return self._boardLayout

    def setLayout(self, layout: BoardLayout) -> None:
        self.removeEventFilter(self._boardLayout)
        if self._boardLayout is not None:
            for w in self._boardLayout.widgets:
                w.setParent(None)
        layout.setParent(self)
        for w in layout.widgets:
            w.setParent(self)
        self._boardLayout = layout
        self.installEventFilter(self._boardLayout)

    def _setBoardPixmap(self):
        print(QtCore.QFile.exists(":images/chessboard.png"))
        if self.flipped:
            boardPix = QtGui.QPixmap(":/images/flipped_chessboard.png")
        else:
            boardPix = QtGui.QPixmap(":/images/chessboard.png")

        self.setPixmap(boardPix.scaled(self.width(), self.height(),
                                       QtCore.Qt.KeepAspectRatioByExpanding,
                                       QtCore.Qt.SmoothTransformation))

    def _adjustWidget(self, w: SquareWidget):
        w.resize(self.size() / 8)
        w.setIconSize(w.size())
        self.moveWidget(w.square, w)

    @QtCore.Slot()
    def onPieceWidgetToggled(self, w: PieceWidget, toggled: bool):
        self.deleteHighlightedSquares()
        if toggled:
            self.toggledWidget = w
            self.highlightLegalMovesFor(w)
        else:
            self.toggledWidget = None
