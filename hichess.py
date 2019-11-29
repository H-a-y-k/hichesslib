import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

from typing import Optional

from . import resources


class SquareWidget(QtWidgets.QPushButton):
    def __init__(self, square: int,
                 parent: Optional[QtWidgets.QWidget] = None):
        assert square in chess.SQUARES

        super().__init__(parent)
        self._square = square

    @property
    def square(self):
        return self._square

    @square.setter
    def square(self, square):
        assert square in chess.SQUARES
        self._square = square

class PieceWidget(SquareWidget):
    def __init__(self, piece: chess.Piece, square: int,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)
        self.setAutoExclusive(True)
        self.setCheckable(True)
        self.transformInto(piece)
        self.setIconSize(self.size())

    def transformInto(self, piece: chess.Piece):
        colorName = chess.COLOR_NAMES[piece.color]
        pieceName = chess.PIECE_NAMES[piece.piece_type]
        self.setIcon(QtGui.QIcon(":/images/{}_{}.png".format(colorName, pieceName)))


class HighlightedSquareWidget(SquareWidget):
    def __init__(self, square: int, #callback,
                 parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(square, parent)
        #self.clicked.connect(callback)
        #self.setIcon(QtGui.QIcon(":/images/highlighted_square"))
        #self.setIconSize(self.size() / 4)

class BoardLayout(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget, adjustWidget=lambda w: None):
        super().__init__(parent)
        self._widgets = []
        self._temporaryWidgets = []
        self.adjustWidget = adjustWidget
        parent.installEventFilter(self)

    def getWidgets(self):
        return self._widgets.copy()

    def getTemporaryWidgets(self):
        return self._temporaryWidgets.copy()

    def clearTemporaryWidgets(self):
        for w in self._temporaryWidgets:
            w.deleteLater()
        self._temporaryWidgets.clear()

    def addWidget(self, w: QtWidgets.QWidget):
        w.setParent(self.parent())
        self._widgets.append(w)
        self.adjustWidget(w)

    def addWidgetAt(self, pos: int, w: QtWidgets.QWidget):
        w.setParent(self.parent())
        self._widgets.insert(pos, w)
        self.adjustWidget(w)

    def addTemporaryWidget(self, w: QtWidgets.QWidget):
        w.setParent(self.parent())
        self._temporaryWidgets.append(w)
        self.adjustWidget(w)

    def addTemporaryWidgetAt(self, pos: int, w: QtWidgets.QWidget):
        w.setParent(self.parent())
        self._temporaryWidgets.insert(pos, w)
        self.adjustWidget(w)

    def eventFilter(self, watched: QtCore.QObject, event: QtGui.QResizeEvent) -> bool:
        if watched == self.parent() and event.type() == QtCore.QEvent.Resize:
            watched.heightForWidth(max(watched.width(), watched.height()))
            for w in self._widgets:
                self.adjustWidget(w)
            for tempW in self._temporaryWidgets:
                self.adjustWidget(tempW)
            return True
        return super().eventFilter(watched, event)


class BoardWidget(QtWidgets.QLabel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 flipped: bool = False):
        super().__init__(parent)

        self.board = chess.Board() if not flipped else chess.Board().mirror()
        self.flipped = flipped
        self.boardLayout = BoardLayout(self, self._adjustWidget)
        self.current = None

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        self.loadPiecesFromPieceMap()
        #self.setStyleSheet("QPushButton { background: transparent; }")

    def loadPiecesFromPieceMap(self):
        for square, piece in self.board.piece_map().items():
            self._loadPiece(square, piece)

    def moveWidget(self, toSquare: int, w: QtWidgets.QWidget):
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare)
        y = chess.square_rank(toSquare)
        w.move(x * w.width(), y * w.height())

    def pushPiece(self, toSquare: int, w: PieceWidget):
        assert self.board.is_legal(chess.Move(w.square, toSquare)), \
               "Not legal move: {} -> {}".format(w.square, toSquare)
        self.board.push(chess.Move(w.square, toSquare))
        self.moveWidget(toSquare, w)
        self.boardLayout.clearTemporaryWidgets()
        w.square = toSquare

    def highlightLegalMoves(self, w: PieceWidget):
        def connectWidget(square, w):
            w.clicked.connect(lambda: self.pushPiece(square, self.current))

        for move in self.board.legal_moves:
            if w.square == move.from_square:
                print(move.to_square)
                highlightedSquare = HighlightedSquareWidget(move.to_square, self)
                self.boardLayout.addTemporaryWidget(highlightedSquare)
                highlightedSquare.setText("O")
                connectWidget(move.to_square, highlightedSquare)
                highlightedSquare.show()

    def flip(self):
        self.flipped = not self.flipped
        self._setBoardPixmap()
        self.board = self.board.mirror()

        for piece in self.boardLayout.getWidgets():
            self.moveWidget(chess.square_mirror(piece.square), piece)

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
    def onPieceWidgetToggled(self, toggled: bool, w):
        if toggled:
            self.boardLayout.clearTemporaryWidgets()
            self.current = w
            self.highlightLegalMoves(w)
        else:
            self.current = None

    def _loadPiece(self, square: int, piece: chess.Piece):
        w = PieceWidget(piece, square)
        self.boardLayout.addWidget(w)
        w.toggled.connect(lambda t: self.onPieceWidgetToggled(t, w))
