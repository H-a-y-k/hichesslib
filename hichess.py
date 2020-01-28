import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

import logging
from functools import partial
from typing import Optional, Union, Callable, Mapping
import sys
import copy

from . import resources


class IllegalMoveError(Exception):
    pass

class SquareWidget(QtWidgets.QPushButton):
    def __init__(self, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(parent=parent)

        self._square = None
        self.square = square

    @property
    def square(self):
        return self._square

    @square.setter
    def square(self, square):
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
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(square, parent)

        self._piece = piece

        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.transformInto(piece.piece_type)
        self.setIconSize(self.size())

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, pieceType: chess.PieceType):
        self.transformInto(pieceType)

    def transformInto(self, pieceType: chess.PieceType):
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
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(square, parent)

        # self.setIcon(QtGui.QIcon(":/images/highlighted_square"))
        # self.setIconSize(self.size() / 4)


class BoardLayout(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget,
                 adjustWidget: Callable[[QtWidgets.QWidget], None]=lambda w: None):
        super().__init__(parent=parent)

        if parent is not None:
            if parent.layout() is None:
                parent.installEventFilter(self)
            else:
                print("BoardLayout: parent already has a layout", sys.stderr)

        self.widgets = []
        self.adjustWidget = adjustWidget

    def addWidget(self, w: QtWidgets.QWidget):
        if not self._insideLayout(w):
            w.setParent(self.parent())
            self.widgets.append(w)
            self.adjustWidget(w)
            w.show()
        else:
            logging.log(logging.WARN, "BoardLayout: Attempting to add a widget, which already is in a layout")

    def removeWidget(self, w: QtWidgets.QWidget):
        self.widgets.remove(w)
        w.setParent(None)

    def deleteWidgets(self, function: Callable[[QtWidgets.QWidget], bool]=lambda w: True):
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
    def __init__(self, parent: Optional[QtWidgets.QWidget]=None,
                 fen: Optional[str]=chess.STARTING_FEN,
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

    def pieceWidgetAt(self, square: chess.Square) -> Optional[PieceWidget]:
        piece = self.board.piece_at(square)
        if piece is not None:
            dict = {w.square: w for w in self._boardLayout.widgets}
            return type(PieceWidget).__new__(dict[square].__class__())
        return None

    def moveWidget(self, toSquare: chess.Square, w: QtWidgets.QWidget):
        w.square = toSquare
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare)
        y = chess.square_rank(toSquare)
        w.move(x * w.width(), y * w.height())

    def movePieceWidget(self, toSquare: chess.Square, w: PieceWidget):
        piece = w.piece
        self.board.remove_piece_at(w.square)
        self.board.set_piece_at(toSquare, piece)

        w.square = toSquare
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

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]):
        self.board.set_piece_map(pieces)
        for square, piece in pieces.items():
            w = PieceWidget(square, piece)
            self._boardLayout.addWidget(w)
            w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def setFen(self, fen: str):
        self.board.set_fen(fen)
        self._boardLayout.deleteWidgets()

        for square, piece in self.board.piece_map().items():
            w = PieceWidget(square, piece)
            self._boardLayout.addWidget(w)
            w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def isPseudoLegalPromotion(self, move: chess.Move):
        piece = self.board.piece_at(move.from_square)
        if piece is not None and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                return chess.A7 <= move.from_square <= chess.H7 and chess.A8 <= move.to_square <= chess.H8
            elif piece.color == chess.BLACK:
                return chess.A2 <= move.from_square <= chess.H2 and chess.A1 <= move.to_square <= chess.H1
        return False

    def pushPieceWidget(self, toSquare: chess.Square, w: PieceWidget):
        move = chess.Move(w.square, toSquare)

        if self.isPseudoLegalPromotion(move):
            # TODO Create a promotion dialogue
            move.promotion = chess.QUEEN
            w.transformInto(move.promotion)

        if not self.board.is_legal(move):
            raise IllegalMoveError("illegal move {} with {}".format(move, chess.PIECE_NAMES[w.piece.piece_type]))

        logging.debug("\n{} ({} -> {})".format(self.board.lan(move), w.square, toSquare))

        if self.board.is_kingside_castling(move):
            self._kingsideCastle(w.piece.color)
        elif self.board.is_queenside_castling(move):
            self._queensideCastle(w.piece.color)
        elif self.board.is_en_passant(move):
            self._captureEnPassant(move, w)
        elif self.board.is_capture(move):
            self._boardLayout.deleteWidgets(
                lambda _w: self.pieceWidgetAt(toSquare) == _w
            )
        self.board.push(move)

        logging.debug("\n{}\n".format(self.board))

        self.moveWidget(toSquare, w)
        self.deleteHighlightedSquares()

    def push(self, move: chess.Move):
        for w in self._boardLayout.widgets:
            if w.square == move.from_square:
                self.pushPieceWidget(move.to_square, w)

    def pop(self):
        move = self.board.pop()

        for w in self._boardLayout.widgets:
            if w.square == move.to_square:
                self.movePieceWidget(move.from_square, w)

    def highlightLegalMovesFor(self, w: PieceWidget):
        def connectWidget(square, w):
            w.clicked.connect(partial(self.pushPieceWidget, square, self.toggledWidget))

        for move in self.board.legal_moves:
            if w == self.pieceWidgetAt(move.from_square):
                highlightedSquare = HighlightedSquareWidget(move.to_square)
                self._boardLayout.addWidget(highlightedSquare)
                highlightedSquare.setText("O")
                connectWidget(move.to_square, highlightedSquare)

    def deleteHighlightedSquares(self):
        self._boardLayout.deleteWidgets(
            lambda w: isinstance(w, HighlightedSquareWidget)
        )

    def flip(self):
        self.flipped = not self.flipped
        self._setBoardPixmap()

        for w in self._boardLayout.widgets:
            self.moveWidget(chess.square_mirror(w.square), w)

    def layout(self) -> BoardLayout:
        return self._boardLayout

    def setLayout(self, layout: BoardLayout):
        if self._boardLayout is not None:
            for w in self._boardLayout.widgets:
                w.setParent(None)
        layout.setParent(self)
        for w in layout.widgets:
            w.setParent(self)
        self._boardLayout = layout

    def _setBoardPixmap(self):
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

    def _kingsideCastle(self, color: chess.Color):
        king = self.pieceWidgetAt(self.board.king(color))
        rook = self.pieceWidgetAt(king.square + 3)
        for w in filter(lambda _w: _w == king or _w == rook, self._boardLayout.widgets):
            if w == king:
                self.moveWidget(king.square + 2, w)
            elif w == rook:
                self.moveWidget(rook.square - 2, w)

    def _queensideCastle(self, color: chess.Color):
        king = self.pieceWidgetAt(self.board.king(color))
        rook = self.pieceWidgetAt(king.square - 4)
        for w in filter(lambda _w: _w == king or _w == rook, self._boardLayout.widgets):
            if w == king:
                self.moveWidget(king.square - 2, w)
            elif w == rook:
                self.moveWidget(rook.square + 3, w)

    def _captureEnPassant(self, move: chess.Move, w: PieceWidget):
        if self.board.color_at(w.square) == chess.WHITE:
            captureSquare = move.to_square - 8
        else:
            captureSquare = move.to_square + 8

        self.moveWidget(move.to_square, w)
        self._boardLayout.deleteWidgets(lambda _w: _w.square == captureSquare)
