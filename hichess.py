import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

import logging
from typing import Optional, Callable
from itertools import zip_longest
import sys

from . import resources


def _error(msg: str):
    print(msg, file=sys.stderr)

class SquareWidget(QtWidgets.QPushButton):
    def __init__(self, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget]=None):
        if square not in chess.SQUARES:
            raise ValueError("Square {} does not exist".format(square))

        super().__init__(parent)
        self._square = square

    @property
    def square(self):
        return self._square

    @square.setter
    def square(self, square):
        if square not in chess.SQUARES:
            raise ValueError("Square {} does not exist".format(square))
        self._square = square

class PieceWidget(SquareWidget):
    def __init__(self, piece: chess.Piece, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(square, parent)

        self._piece = piece

        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.transformInto(piece)
        self.setIconSize(self.size())

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, piece: chess.Piece):
        self.transformInto(piece)

    def transformInto(self, piece: chess.Piece):
        self.piece = piece
        colorName = chess.COLOR_NAMES[piece.color]
        pieceName = chess.PIECE_NAMES[piece.piece_type]
        self.setIcon(QtGui.QIcon(":/images/{}_{}.png".format(colorName, pieceName)))


class HighlightedSquareWidget(SquareWidget):
    def __init__(self, square: chess.Square, #callback,
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(square, parent)
        #self.clicked.connect(callback)
        #self.setIcon(QtGui.QIcon(":/images/highlighted_square"))
        #self.setIconSize(self.size() / 4)

class BoardLayout(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget,
                 adjustWidget: Callable[[QtWidgets.QWidget], None]=lambda w: None):
        super().__init__(parent)
        self._widgets = []
        self._temporaryWidgets = []
        self.adjustWidget = adjustWidget
        parent.installEventFilter(self)

    def getWidgets(self):
        return self._widgets.copy()

    def addWidget(self, w: QtWidgets.QWidget):
        if self._hasLayout(w):
            _error("BoardLayout: Trying to add a widget, which already is in a layout")
            return
        w.setParent(self.parent())
        self._widgets.append(w)
        self.adjustWidget(w)

    def getTemporaryWidgets(self):
        return self._temporaryWidgets.copy()

    def addTemporaryWidget(self, w: QtWidgets.QWidget):
        if self._hasLayout(w):
            _error("BoardLayout: Trying to add a widget, which already is in a layout")
            return
        w.setParent(self.parent())
        self._temporaryWidgets.append(w)
        self.adjustWidget(w)

    def clearTemporaryWidgets(self):
        for w in self._temporaryWidgets:
            w.deleteLater()
        self._temporaryWidgets.clear()

    def update(self):
        for w, tw in zip_longest(self._widgets, self._temporaryWidgets):
            w.setParent(self.parent())
            self.adjustWidget(w)
            tw.setParent(self.parent())
            self.adjustWidget(tw)

    def eventFilter(self, watched: QtCore.QObject, event: QtGui.QResizeEvent) -> bool:
        if watched == self.parent() and event.type() == QtCore.QEvent.Resize:
            watched.heightForWidth(max(watched.width(), watched.height()))
            for w, tw in zip_longest(self._widgets, self._temporaryWidgets):
                self.adjustWidget(w)
                self.adjustWidget(tw)
            return True
        return super().eventFilter(watched, event)

    def _hasLayout(self, w: QtWidgets.QWidget):
        if (w != None and w.parent() != None and
                isinstance(w.parent().layout(), BoardLayout)):
            return True
        return False


class BoardWidget(QtWidgets.QLabel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 flipped: bool = False):
        super().__init__(parent)

        logging.basicConfig(filename='myapp.log', level=logging.INFO)

        self.board = chess.Board() if not flipped else chess.Board().mirror()
        self.flipped = flipped
        self._boardLayout = BoardLayout(self, self._adjustWidget)
        self.current = None

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        self.loadPiecesFromPieceMap()
        self.setStyleSheet("QPushButton { background: transparent; }")

    def loadPiecesFromPieceMap(self):
        for square, piece in self.board.piece_map().items():
            self._loadPiece(square, piece)

    def pieceWidgetAt(self, square: chess.Square):
        piece = self.board.piece_at(square)
        if piece is not None:
            return PieceWidget(piece, square)

    def moveWidget(self, toSquare: chess.Square, w: QtWidgets.QWidget):
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare)
        y = chess.square_rank(toSquare)
        w.move(x * w.width(), y * w.height())

    def pushPiece(self, toSquare: chess.Square, w: PieceWidget):
        if not self.board.is_legal(chess.Move(w.square, toSquare)):
            _error("BoardWidget: Attempting to do an illegal move: {} -> {}")

        move = chess.Move(w.square, toSquare)
        if self.board.is_en_passant(move):
            self._captureEnPassant(move, w)
        elif self.board.is_capture(move):
            for _w in self._boardLayout.getWidgets():
                if _w.square == toSquare:
                    _w.deleteLater()

        #if self.board.is_kingside_castling(s
        self.board.push(chess.Move(w.square, toSquare))
        logging.info(self.board)
        self.moveWidget(toSquare, w)
        self._boardLayout.clearTemporaryWidgets()
        w.square = toSquare

    def highlightLegalMoves(self, w: PieceWidget):
        def connectWidget(square, w):
            w.clicked.connect(lambda: self.pushPiece(square, self.current))

        for move in self.board.legal_moves:
            if w.square == move.from_square:
                highlightedSquare = HighlightedSquareWidget(move.to_square, self)
                self._boardLayout.addTemporaryWidget(highlightedSquare)
                highlightedSquare.setText("O")
                connectWidget(move.to_square, highlightedSquare)
                highlightedSquare.show()

    def flip(self):
        self.flipped = not self.flipped
        self._setBoardPixmap()
        self.board = self.board.mirror()

        for piece in self._boardLayout.getWidgets():
            self.moveWidget(chess.square_mirror(piece.square), piece)

    def layout(self) -> BoardLayout:
        return self._boardLayout

    def setLayout(self, layout: BoardLayout):
        self._boardLayout = layout
        self._boardLayout.update()

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
    def onPieceWidgetToggled(self, toggled: bool, w: PieceWidget):
        if toggled:
            self._boardLayout.clearTemporaryWidgets()
            self.current = w
            self.highlightLegalMoves(w)
        else:
            self.current = None

    def _loadPiece(self, square: chess.Square, piece: chess.Piece):
        w = PieceWidget(piece, square)
        self._boardLayout.addWidget(w)
        w.toggled.connect(lambda toggled: self.onPieceWidgetToggled(toggled, w))

    def _captureEnPassant(self, move: chess.Move, w: PieceWidget):
        color = self.board.color_at(w.square)
        self.moveWidget(move.to_square, w)
        for _w in self._boardLayout.getWidgets():
            if color:
                sq = move.to_square - 8
            else:
                sq = move.to_square + 8
            if _w.square == sq:
                _w.deleteLater()