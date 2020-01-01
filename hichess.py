import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

import logging
from functools import partial
from typing import Optional, Callable
import sys

from . import resources


def _error(msg: str):
    print(msg, file=sys.stderr)


class SquareWidget(QtWidgets.QPushButton):
    def __init__(self, square: chess.Square,
                 parent: Optional[QtWidgets.QWidget] = None):
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
    def __init__(self, square: chess.Square, piece: chess.Piece,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)

        self._piece = piece

        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.transformInto(piece.piece_type)
        self.setIconSize(self.size())

    def __eq__(self, w: "PieceWidget"):
        if isinstance(w, PieceWidget):
            return self._piece == w.piece and self.square == w.square
        return False

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


class HighlightedSquareWidget(SquareWidget):
    def __init__(self, square: chess.Square,  # callback,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)
        # self.clicked.connect(callback)
        # self.setIcon(QtGui.QIcon(":/images/highlighted_square"))
        # self.setIconSize(self.size() / 4)


class BoardLayout(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget,
                 adjustWidget: Callable[[QtWidgets.QWidget], None] = lambda w: None):
        super().__init__(parent)

        if parent.layout() is not None:
            _error("BoardLayout: parent already has a layout")
        else:
            parent.installEventFilter(self)

        self.widgets = []
        self.adjustWidget = adjustWidget

    def addWidget(self, w: QtWidgets.QWidget):
        if self._insideLayout(w):
            _error("BoardLayout: Attempting to add a widget, which already is in a layout")
            return
        w.setParent(self.parent())
        self.widgets.append(w)
        self.adjustWidget(w)
        w.show()

    def deleteWidgets(self, function: Callable[[QtWidgets.QWidget], bool] = lambda w: None):
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
        if (w != None and w.parent() != None and
                w.parent().layout() != self):
            return True
        return False


class BoardWidget(QtWidgets.QLabel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 flipped: bool = False):
        super().__init__(parent)

        logging.basicConfig(filename='myapp.log', level=logging.INFO)

        self.board = chess.Board() if not flipped else chess.Board().mirror()
        self.flipped = flipped
        self._boardLayout = None
        self.currentWidget = None

        self.setLayout(BoardLayout(self, self._adjustWidget))
        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        self.loadPiecesFromPieceMap()
        self.setStyleSheet("QPushButton { background: transparent; }")

    def previousFileSquare(self, square: chess.Square) -> chess.Square:
        return chess.SQUARES[square - 1]

    def nextFileSquare(self, square: chess.Square) -> chess.Square:
        return chess.SQUARES[square + 1]

    def previousRankSquare(self, square: chess.Square) -> chess.Square:
        return chess.SQUARES[square - 8]

    def nextRankSquare(self, square: chess.Square) -> chess.Square:
        return chess.SQUARES[square + 8]

    def pieceWidgetAt(self, square: chess.Square) -> Optional[PieceWidget]:
        piece = self.board.piece_at(square)
        if piece is not None:
            return PieceWidget(square, piece)
        return None

    def loadPiece(self, square: chess.Square, piece: chess.Piece):
        w = PieceWidget(square, piece)
        self._boardLayout.addWidget(w)
        w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def loadPieceWidget(self, w: PieceWidget):
        self._boardLayout.addWidget(w)
        w.toggled.connect(partial(self.onPieceWidgetToggled, w))

    def loadPiecesFromPieceMap(self, map=chess.Board().piece_map()):
        for square, piece in self.board.piece_map().items():
            self.loadPiece(square, piece)

    def moveWidget(self, toSquare: chess.Square, w: QtWidgets.QWidget):
        w.square = toSquare
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare)
        y = chess.square_rank(toSquare)
        w.move(x * w.width(), y * w.height())

    def isLegalPromotion(self, move: chess.Move):
        w = self.pieceWidgetAt(move.from_square)
        if w.piece.piece_type == chess.PAWN:
            rank = chess.square_rank(move.to_square)
            if rank == 0 or rank == 7:
                return True
        return False

    def pushPieceWidget(self, toSquare: chess.Square, w: PieceWidget):
        move = chess.Move(w.square, toSquare)

        if self.isLegalPromotion(move):
            # TODO Create a promotion dialogue
            move.promotion = chess.QUEEN
            w.transformInto(move.promotion)

        if not self.board.is_legal(move):
            _error("BoardWidget: Attempting to do an illegal move: {} -> {}".format(w.square, toSquare))
            return

        print("{} ({} -> {})".format(self.board.lan(move), w.square, toSquare))

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
        logging.info(self.board)

        self.moveWidget(toSquare, w)
        self.deleteHighlightedSquares()

    def highlightLegalMoves(self, w: PieceWidget):
        def connectWidget(square, w):
            w.clicked.connect(partial(self.pushPieceWidget, square, self.currentWidget))

        for move in self.board.legal_moves:
            if w.square == move.from_square:
                highlightedSquare = HighlightedSquareWidget(move.to_square)
                self._boardLayout.addWidget(highlightedSquare)
                highlightedSquare.setText("O")
                connectWidget(move.to_square, highlightedSquare)

    def deleteHighlightedSquares(self):
        self._boardLayout.deleteWidgets(
            lambda w: isinstance(w, HighlightedSquareWidget)
        )

    def flip(self) -> "BoardWidget":
        self.flipped = not self.flipped
        self._setBoardPixmap()
        self.board = self.board.mirror()

        for piece in self._boardLayout.widgets:
            self.moveWidget(chess.square_mirror(piece.square), piece)

        return self

    def layout(self) -> BoardLayout:
        return self._boardLayout

    def setLayout(self, layout: BoardLayout):
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
            self.currentWidget = w
            self.highlightLegalMoves(w)
        else:
            self.currentWidget = None

    def _kingsideCastle(self, color: chess.Color):
        if not self.board.has_kingside_castling_rights(color):
            _error("{} does not have kingside castling rights".format(chess.COLOR_NAMES[color]))
            return

        king = self.pieceWidgetAt(self.board.king(color))
        rook = self.pieceWidgetAt(king.square + 3)
        for w in filter(lambda _w: _w == king or _w == rook, self._boardLayout.widgets):
            if w == king:
                self.moveWidget(king.square + 2, w)
            elif w == rook:
                self.moveWidget(rook.square - 2, w)

    def _queensideCastle(self, color: chess.Color):
        if not self.board.has_queenside_castling_rights(color):
            _error("{} does not have queenside castling rights".format(chess.COLOR_NAMES[color]))
            return

        king = self.pieceWidgetAt(self.board.king(color))
        rook = self.pieceWidgetAt(king.square - 4)
        for w in filter(lambda _w: _w == king or _w == rook, self._boardLayout.widgets):
            if w == king:
                self.moveWidget(king.square - 2, w)
            elif w == rook:
                self.moveWidget(rook.square + 3, w)

    def _captureEnPassant(self, move: chess.Move, w: PieceWidget):
        if self.board.color_at(w.square) == chess.WHITE:
            toCapture = self.pieceWidgetAt(self.previousRankSquare(move.to_square))
        else:
            toCapture = self.pieceWidgetAt(self.nextRankSquare(move.to_square))

        self.moveWidget(move.to_square, w)
        self._boardLayout.deleteWidgets(lambda _w: _w == toCapture)
