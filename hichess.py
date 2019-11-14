import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

from typing import Optional

from . import resources

class PieceWidget(QtWidgets.QPushButton):
    def __init__(self, piece: chess.Piece, square: int,
                 parent: Optional[QtWidgets.QWidget] = None):
        assert square in chess.SQUARES

        super().__init__(parent)
        self.setParent(parent)
        self.square = square

        self._setPieceIcon(piece)
        self.setIconSize(self.size())

    def transformInto(self, piece: chess.Piece):
        self._setPieceIcon(piece)

    def _setPieceIcon(self, piece: chess.Piece):
        colorName = chess.COLOR_NAMES[piece.color]
        pieceName = chess.PIECE_NAMES[piece.piece_type]
        self.setIcon(QtGui.QIcon(":/images/{}_{}.png".format(colorName, pieceName)))

class BoardLayout(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget, adjustWidget):
        super().__init__(parent)
        self._widgets = []
        self.adjustWidget = adjustWidget
        parent.installEventFilter(self)

    def addWidget(self, w: QtWidgets.QWidget):
        self._widgets.append(w)

    def eventFilter(self, watched: QtCore.QObject, event: QtGui.QResizeEvent) -> bool:
        if watched == self.parent() and event.type() ==  QtCore.QEvent.Resize:
            for w in self._widgets:
                self.adjustWidget(w)
            return True
        return QtWidgets.QWidget.eventFilter(self, watched, event)

class BoardWidget(QtWidgets.QLabel):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 flipped: bool = False):
        super().__init__(parent)

        self._board = chess.Board() if not flipped else chess.Board().mirror()
        self.flipped = flipped
        self.boardLayout = BoardLayout(self, self._adjustPiece)

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        self.loadPiecesFromPieceMap()
        self.setStyleSheet("QPushButton { background: transparent; }")

    def loadPiecesFromPieceMap(self):
        for square, piece in self._board.piece_map().items():
            self._loadPiece(piece, square)

    def pushPiece(self, piece: PieceWidget, toSquare: int):
        assert self._board.is_legal(chess.Move(piece.square, toSquare)), \
               "Not legal move: {} -> {}".format(piece.square, toSquare)
        self._moveWidget(piece, toSquare)

    """
    def highlightLegalMoves(self, piece: PieceWidget):
        for move in self._board.legal_moves:
            if piece.square == move.from_square:
                highlightedSquare = QtWidgets.QPushButton(self)
                highlightedSquare.setText("O")
                self._moveWidget(highlightedSquare, move.to_square)
                self.highlightedSquares.append(highlightedSquare)
                highlightedSquare.show()
    """

    def flip(self):
        self.flipped = not self.flipped
        self._setBoardPixmap()

        for piece in self.pieces:
            self._board = self._board.mirror()
            newSquare = chess.square_mirror(piece.square)
            self.movePiece(piece, newSquare)

    def _setBoardPixmap(self):
        if self.flipped:
            boardPix = QtGui.QPixmap(":/images/flipped_chessboard.png")
        else:
            boardPix = QtGui.QPixmap(":/images/chessboard.png")

        self.setPixmap(boardPix.scaled(self.width(), self.height(),
                                       QtCore.Qt.KeepAspectRatioByExpanding,
                                       QtCore.Qt.SmoothTransformation))

    def _moveWidget(self, w: QtWidgets.QWidget, toSquare: int):
        if not self.flipped:
            toSquare = chess.square_mirror(toSquare)
        x = chess.square_file(toSquare)
        y = chess.square_rank(toSquare)
        w.move(x * w.width(), y * w.height())

    def _adjustPiece(self, piece: PieceWidget):
        piece.resize(self.size() / 8)
        piece.setIconSize(piece.size())

        self._moveWidget(piece, piece.square)

    def _loadPiece(self, piece: chess.Piece, square: int):
        widget = PieceWidget(piece, square, parent=self)
        self._adjustPiece(widget)
        self.boardLayout.addWidget(widget)

    def mousePressEvent(self, e):
        for sq in self.highlightedSquares:
            sq.deleteLater()

    def resizeEvent(self, e):
        self.heightForWidth(max(self.width(), self.height()))