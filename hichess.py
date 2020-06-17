# -*- coding: utf-8 -*-
#
# This file is part of the HiChess project.
# Copyright (C) 2019-2020 Haik Sargsian <haiksargsian6@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it In the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
from PySide2.QtGui import QPixmap, QMouseEvent, QDrag

import chess

import logging
from enum import Enum
from functools import partial
from typing import Optional, Mapping, Generator, Callable, Any
from collections import deque


class NotAKingError(Exception):
    pass


class IllegalMove(Exception):
    pass


class CellWidget(QtWidgets.QPushButton):
    """ A `QPushButton` representing a single cell of chess board.
    CellWidget can be either a chess piece or an empty cell of the
    board. It can be marked with different colors.

    `CellWidget` by default represents an empty cell.

    Attributes
    ----------
    """

    designated = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._piece = None
        self._isInCheck = False
        self._isHighlighted = False
        self._isMarked = False
        self._justMoved = False

        self.setObjectName("cell_plain")
        self.setCheckable(False)

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)

    def getPiece(self) -> Optional[chess.Piece]:
        return self._piece

    def isPiece(self) -> bool:
        """ This property indicates the type of the cell.
        It is True if the cell is a chess piece
        and False if it is an empty cell.
        """
        return self._piece is not None

    def setPiece(self, piece: Optional[chess.Piece]) -> None:
        """ Sets the content of the cell.

        Parameters
        ----------
        piece : Optional[chess.Piece]
            The piece that will occupy this cell.

            The cell is emptied if the piece is None otherwise its
            object name is set to ``cell_`` + the name of the piece or ``plain``.
            For example the object name of an empty cell will be ``cell_plain`` and
            the object name of a cell occupied by a white pawn will be ``cell_white_pawn``

            Cells containing a piece are checkable, whereas those empty ones are not.
        """

        self._piece = piece

        if self._piece:
            self.setObjectName(f"cell_{chess.COLOR_NAMES[piece.color]}_{chess.PIECE_NAMES[piece.piece_type]}")
            self.setCheckable(True)
        else:
            self.setObjectName("cell_plain")
            self.setCheckable(False)

        self.style().unpolish(self)
        self.style().polish(self)

    def isPlain(self) -> bool:
        """ A convinience property indicating if the cell is empty or not.
        """
        return not self._piece

    def toPlain(self) -> None:
        """ Empties the cell.
        """
        self.setPiece(None)

    @staticmethod
    def makePiece(piece: chess.Piece) -> "CellWidget":
        """ A static method that creates a `CellWidget` from the given piece.
            Parameters
            ----------
            piece : chess.Piece
                The piece that will occupy the cell. Note that the type of
                the piece cannot be NoneType as in the definition of the
                method `setPiece`, because by default cells are created empty.
         """
        assert isinstance(piece, chess.Piece)

        w = CellWidget()
        w.setPiece(piece)
        return w

    def isInCheck(self) -> bool:
        """ This property indicates if the cell contains a king in check.
            Warnings
            --------
            Cells that aren't occupied by a king cannot be in check.

            Raises
            -------
            NotAKingError
                This exception is raised when the property is set to True for
                a cell not being occupied by a king.
            """
        return self._isInCheck

    def setInCheck(self, ck: bool) -> None:
        if self._piece.piece_type == chess.KING:
            self._isInCheck = ck
            self.style().unpolish(self)
            self.style().polish(self)
        else:
            raise NotAKingError("Trying to (un)check a piece that is not a king.")

    def check(self) -> None:
        """ A convenience method that sets the property `isInCheck` to True.
        """
        self.setInCheck(True)

    def uncheck(self) -> None:
        """ A convenience method that sets the property `isInCheck` to False.
        """
        self.setInCheck(False)

    def isHighlighted(self) -> bool:
        """ This property indicates if the cell is highlighted.
        Highlighted cells are special cells that are used to indicate
        legal moves on the board.
        Highlighted cells are not checkable.
        """
        return self._isHighlighted

    def setHighlighted(self, highlighted: bool) -> None:
        if self._isHighlighted != highlighted:
            self._isHighlighted = highlighted

            if self._isHighlighted:
                self.setCheckable(False)
            else:
                self.setCheckable(bool(self._piece))
            self.style().unpolish(self)
            self.style().polish(self)

    def highlight(self) -> None:
        """ A convenience method that sets the property `highlighted` to True.
        """
        self.setHighlighted(True)

    def unhighlight(self) -> None:
        """ A convenience method that sets the property `highlighted` to False.
        """
        self.setHighlighted(False)

    def isMarked(self) -> bool:
        return self._isMarked

    def setMarked(self, marked: bool) -> None:
        self._isMarked = marked
        self.designated.emit(self._isMarked)
        self.style().unpolish(self)
        self.style().polish(self)

    def mark(self):
        self.setMarked(True)

    def unmark(self):
        self.setMarked(False)

    def justMoveed(self) -> bool:
        """ This property indicates if the piece occupying this cell was just moved from/to this cell.
        """
        return self._justMoved

    def setJustMoved(self, jm: bool):
        self._justMoved = jm
        self.style().unpolish(self)
        self.style().polish(self)

    piece = QtCore.Property(bool, isPiece, setPiece)
    plain = QtCore.Property(bool, isPlain)
    inCheck = QtCore.Property(bool, isInCheck, setInCheck)
    highlighted = QtCore.Property(bool, isHighlighted, setHighlighted)
    marked = QtCore.Property(bool, isMarked, setMarked, notify=designated)
    justMoved = QtCore.Property(bool, justMoveed, setJustMoved)


class AccessibleSides(Enum):
    NONE = 0
    ONLY_WHITE = 1
    ONLY_BLACK = 2
    BOTH = 3


NO_SIDE = AccessibleSides.NONE
ONLY_WHITE_SIDE = AccessibleSides.ONLY_WHITE
ONLY_BLACK_SIDE = AccessibleSides.ONLY_BLACK
BOTH_SIDES = AccessibleSides.BOTH


class _PromotionDialog(QtWidgets.QDialog):
    OptionOrder = bool
    QUEEN_ON_BOTTOM, QUEEN_ON_TOP = [True, False]

    def __init__(self, parent=None, color: bool = chess.WHITE,
                 order: OptionOrder = QUEEN_ON_TOP):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)

        self.chosenPiece = chess.QUEEN

        def makePiece(pieceType):
            w = CellWidget.makePiece(chess.Piece(pieceType, color))
            w.clicked.connect(partial(self.onPieceChosen, pieceType))
            return w

        layout = QtWidgets.QVBoxLayout()
        options = [chess.QUEEN, chess.KNIGHT, chess.ROOK, chess.BISHOP]

        if order == self.QUEEN_ON_TOP:
            [layout.addWidget(makePiece(option))
             for option in options]
        else:
            [layout.addWidget(makePiece(option))
             for option in options[::-1]]

        self.setLayout(layout)

    @QtCore.Slot()
    def onPieceChosen(self, pieceType):
        self.chosenPiece = pieceType
        self.accept()


class BoardWidget(QtWidgets.QLabel):
    """
    A graphical chess board.
    """

    moveMade = QtCore.Signal(str)
    checkmate = QtCore.Signal(bool)
    draw = QtCore.Signal()
    stalemate = QtCore.Signal()
    gameOver = QtCore.Signal()

    def __init__(self, parent=None,
                 fen: Optional[str] = chess.STARTING_FEN,
                 flipped: bool = False,
                 sides: AccessibleSides = NO_SIDE):
        super().__init__(parent=parent)

        self.board = chess.Board(fen)
        self.popStack = deque()

        self._flipped = flipped
        self._accessibleSides = sides

        self.blockBoardOnPop = False

        self.defaultPixmap = self.pixmap()
        self.flippedPixmap = QPixmap(self.pixmap())
        self.lastCheckedCellWidget = None

        self.dragPieces = True
        self._dragWidget = None
        self._dragStartPos = QtCore.QPoint(0, 0)

        self._boardLayout = QtWidgets.QGridLayout()
        self._boardLayout.setContentsMargins(0, 0, 0, 0)
        self._boardLayout.setSpacing(0)

        def newCellWidget():
            cellWidget = CellWidget()
            cellWidget.clicked.connect(partial(self.onCellWidgetClicked, cellWidget))
            cellWidget.toggled.connect(partial(self.onCellWidgetToggled, cellWidget))
            cellWidget.designated.connect(self.onCellWidgetMarked)
            cellWidget.installEventFilter(self)
            return cellWidget

        for i in range(8):
            for j in range(8):
                self._boardLayout.addWidget(newCellWidget(), i, j)
        self.setLayout(self._boardLayout)

        self.setFen(self.board.fen())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)

    def eventFilter(self, watched, event: QMouseEvent) -> bool:
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.RightButton:
                if isinstance(watched, CellWidget):
                    if self.accessibleSides != NO_SIDE:
                        watched.setMarked(not watched.marked)
        return watched.event(event)

    def cellWidgets(self, filter=lambda w: True) -> Generator[CellWidget, None, None]:
        for i in range(self._boardLayout.count()):
            w = self._boardLayout.itemAt(i).widget()
            if filter(w):
                yield w

    def flipSquare(self, square: chess.Square) -> chess.Square:
        if self._flipped:
            return chess.SQUARES[63-square]
        return square

    def cellIndexOfSquare(self, square: chess.Square) -> Optional[chess.Square]:
        if not self._flipped:
            return chess.square_mirror(square)
        return chess.square(7 - chess.square_file(square), chess.square_rank(square))

    def squareOf(self, w: CellWidget) -> chess.Square:
        i = self._boardLayout.indexOf(w)
        if not self.flipped:
            return chess.square_mirror(i)
        return chess.square(7 - chess.square_file(i), chess.square_rank(i))

    def cellWidgetAtSquare(self, square: chess.Square) -> Optional[CellWidget]:
        """
        Returns the cell widget at the given square.
        """

        item = self._boardLayout.itemAt(self.cellIndexOfSquare(square))
        if item is not None:
            return item.widget()
        return None

    def pieceCanBePushedTo(self, w: CellWidget):
        for move in self.board.legal_moves:
            if move.from_square == self.squareOf(w):
                yield move.to_square

    def isPseudoLegalPromotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)

        if piece is not None and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                return chess.A8 <= move.to_square <= chess.H8
            elif piece.color == chess.BLACK:
                return chess.A1 <= move.to_square <= chess.H1
        return False

    def king(self, color: chess.Color) -> CellWidget:
        return self.cellWidgetAtSquare(self.board.king(color))

    def setBoardPixmap(self, defaultPixmap, flippedPixmap) -> None:
        self.defaultPixmap = defaultPixmap
        self.flippedPixmap = flippedPixmap
        self._updatePixmap()

    @QtCore.Slot()
    def onCellWidgetClicked(self, w):
        if w.highlighted:
            self.pushPiece(self.squareOf(w), self.lastCheckedCellWidget)
            self.unmarkCells()
        elif not w.piece:
            self._foreachCells(CellWidget.unhighlight, lambda w: w.setChecked(False), CellWidget.unmark)

    @QtCore.Slot()
    def onCellWidgetToggled(self, w: CellWidget, toggled: bool):
        if chess.COLOR_NAMES[self.board.turn] != w.objectName().split('_')[1] or not self._isCellAccessible(w):
            w.setChecked(False)
            return

        if toggled:
            if self.popStack:
                w.setChecked(False)
                return

            def callback(_w: CellWidget):
                if _w != w:
                    _w.setChecked(False)

            self._foreachCells(CellWidget.unmark, CellWidget.unhighlight, callback)
            if not self.highlightLegalMoveCellsFor(w):
                w.setChecked(False)
            self.lastCheckedCellWidget = w
        else:
            self.unhighlightCells()

    @QtCore.Slot()
    def onCellWidgetMarked(self, marked: bool):
        if marked:
            def callback(w):
                if w.isChecked():
                    w.setChecked(False)
            self._foreachCells(callback, CellWidget.unhighlight)

    def setPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        return self._setPieceAt(square, piece)

    def removePieceAt(self, square: chess.Square) -> CellWidget:
        w = self.cellWidgetAtSquare(square)

        if w.isPlain():
            raise ValueError(f"Cell widget at {square} is not a piece")

        self.board.remove_piece_at(square)
        w.toPlain()

        return w

    def addPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        """
        This function is the safer version of the function
        `setPieceAt` for its ability to raise an error if the given
        square is invalid.
        Raises
        ------
        ValueError
            If the given square is already occupied.
        Returns
        -------
        The created cell widget.
        """

        if self.board.piece_at(square) is not None:
            raise ValueError("Square {} is occupied")
        return self._setPieceAt(square, piece)

    def synchronize(self) -> None:
        def callback(w):
            if not w.isPlain():
                w.toPlain()
            elif self.accessibleSides != NO_SIDE:
                w.accessible = True

        temp = self.board.copy()
        list(map(callback, self.cellWidgets()))
        for square, piece in self.board.piece_map().items():
            self._setPieceAt(square, piece)
        self.board = temp

    def synchronizeAndUpdateStyles(self):
        self.synchronize()

        self._updateJustMovedCells(False)
        self._updateJustMovedCells(True)

        if self.board.is_check():
            self.king(self.board.turn).check()
        else:
            self.king(self.board.turn).uncheck()
            self.king(not self.board.turn).uncheck()

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        self.unhighlightCells()
        self.synchronize()

    def setFen(self, fen: Optional[str]) -> None:
        self.board = chess.Board(fen)
        self.unhighlightCells()
        self.synchronize()

    def clear(self):
        self._updateJustMovedCells(False)

        self.king(chess.WHITE).uncheck()
        self.king(chess.BLACK).uncheck()

        self.board.clear()
        self._foreachCells(CellWidget.unhighlight, CellWidget.unmark, lambda w: w.setChecked(False))
        self.synchronize()

    def reset(self):
        self._setFlipped(False)
        self._updateJustMovedCells(False)
        self.king(chess.WHITE).uncheck()
        self.king(chess.BLACK).uncheck()
        self.board.reset()
        self.popStack.clear()
        self._foreachCells(CellWidget.unhighlight, CellWidget.unmark, lambda w: w.setChecked(False))
        self.synchronize()

    def makeMove(self, move: chess.Move):
        self._updateJustMovedCells(False)
        self.board.push(move)
        self._updateJustMovedCells(True)
        self.synchronizeAndUpdateStyles()

    def pushPiece(self, toSquare: chess.Square, w: CellWidget) -> None:
        self._push(chess.Move(self.squareOf(w), toSquare))

    def push(self, move: chess.Move) -> None:
        self._push(move)

    def pop(self, n=1) -> str:
        self._updateJustMovedCells(False)

        lastMove = None
        for i in range(n):
            lastMove = self.board.pop()
            self.popStack.append(lastMove)

        self._foreachCells(CellWidget.unmark, CellWidget.unhighlight)
        self.synchronizeAndUpdateStyles()

        return lastMove.uci()

    def unpop(self, n=1) -> str:
        self._updateJustMovedCells(False)

        lastMove = None
        for i in range(n):
            lastMove = self.popStack.pop()
            self.board.push(lastMove)

        self._foreachCells(CellWidget.unmark, CellWidget.unhighlight)
        self.synchronizeAndUpdateStyles()

        return lastMove.uci()

    def goToMove(self, id):
        if id >= 0:
            moveStackLen = len(self.board.move_stack)
            if moveStackLen != id:
                if moveStackLen < id:
                    self.unpop(id - moveStackLen)
                elif moveStackLen > id:
                    self.pop(moveStackLen - id)

    def highlightLegalMoveCellsFor(self, w: CellWidget) -> int:
        counter = 0
        for square in self.pieceCanBePushedTo(w):
            self.cellWidgetAtSquare(square).highlight()
            counter += 1
        return counter

    def uncheckCells(self, exceptFor: Optional[CellWidget] = None):
        def callback(w: CellWidget):
            if w != exceptFor:
                w.setChecked(False)

        self._foreachCells(callback)

    def unhighlightCells(self) -> None:
        list(map(CellWidget.unhighlight, self.cellWidgets()))

    def unmarkCells(self) -> None:
        list(map(CellWidget.unmark, self.cellWidgets()))

    @property
    def flipped(self) -> bool:
        return self._flipped

    @flipped.setter
    def flipped(self, flipped: bool) -> None:
        self._setFlipped(flipped)

    def flip(self) -> None:
        self._setFlipped(not self.flipped)

    @property
    def accessibleSides(self) -> AccessibleSides:
        return self._accessibleSides

    @accessibleSides.setter
    def accessibleSides(self, accessibleSides: AccessibleSides) -> None:
        self._accessibleSides = accessibleSides
        self.synchronize()

    def _foreachCells(self, *args: Callable[[CellWidget], Any], predicate: Callable[[CellWidget], bool] = lambda w: True):
        for w in self.cellWidgets():
            if predicate(w):
                for callback in args:
                    callback(w)

    def _isCellAccessible(self, w):
        if self.accessibleSides == NO_SIDE:
            return False
        if self.accessibleSides == BOTH_SIDES:
            return True

        if w.piece:
            color = w.getPiece().color

            if color == chess.WHITE:
                return self.accessibleSides == ONLY_WHITE_SIDE
            if color == chess.BLACK:
                return self.accessibleSides == ONLY_BLACK_SIDE

    def _setPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        self.board.set_piece_at(square, piece)

        w = self.cellWidgetAtSquare(square)
        w.setPiece(piece)

        return w

    def _updatePixmap(self) -> None:
        if not self._flipped:
            self.setPixmap(self.defaultPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio,
                                                     QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(self.flippedPixmap.scaled(self.size(), QtCore.Qt.KeepAspectRatio,
                                                     QtCore.Qt.SmoothTransformation))

    def _updateJustMovedCells(self, justMoved: bool):
        if self.board.move_stack:
            lastMove = self.board.move_stack[-1]
            self.cellWidgetAtSquare(lastMove.from_square).justMoved = justMoved
            self.cellWidgetAtSquare(lastMove.to_square).justMoved = justMoved

    def _push(self, move: chess.Move) -> None:
        self._updateJustMovedCells(False)

        turn = self.board.turn

        if self._isCellAccessible(self.cellWidgetAtSquare(move.from_square)) and move.promotion is None and self.isPseudoLegalPromotion(move):
            w = self.cellWidgetAtSquare(move.to_square)

            promotionDialog = _PromotionDialog(parent=self, color=turn,
                                               order=self._flipped)
            if not self._flipped and turn:
                promotionDialog.move(self.mapToGlobal(w.pos()))
            else:
                promotionDialog.move(self.mapToGlobal(QtCore.QPoint(w.x(), w.y() - 3 * w.height())))
            promotionDialog.setFixedWidth(w.width())
            promotionDialog.setFixedHeight(4 * w.height())

            exitCode = promotionDialog.exec_()
            if exitCode == _PromotionDialog.Accepted:
                move.promotion = promotionDialog.chosenPiece
            elif exitCode == _PromotionDialog.Rejected:
                self._foreachCells(CellWidget.unhighlight, lambda w: w.setChecked(False))
                return

        if not self.board.is_legal(move):
            raise IllegalMove(f"illegal move {move} by ")
        logging.debug(f"\n{self.board.lan(move)} ({move.from_square} -> {move.to_square})")

        if self.board.is_check():
            self.king(turn).uncheck()

        san = self.board.san(move)
        self.board.push(move)
        logging.debug(f"\n{self.board}\n")

        self._updateJustMovedCells(True)
        self.popStack.clear()

        self._foreachCells(CellWidget.unmark, CellWidget.unhighlight)
        self.synchronizeAndUpdateStyles()

        if self.board.is_checkmate():
            self.checkmate.emit(turn)
            self.gameOver.emit()
        elif self.board.is_insufficient_material():
            self.draw.emit()
            self.gameOver.emit()
        elif self.board.is_stalemate():
            self.stalemate.emit()
            self.gameOver.emit()

        self.moveMade.emit(san)

    def _setFlipped(self, flipped: bool):
        if self._flipped != flipped:
            self._updateJustMovedCells(False)

            markedWidgets = list(self.cellWidgets(CellWidget.isMarked))
            for w in markedWidgets:
                w.unmark()
                self.cellWidgetAtSquare(63 - self.squareOf(w)).mark()

            self._flipped = flipped
            self.synchronizeAndUpdateStyles()
            self._updatePixmap()

    def resizeEvent(self, event) -> None:
        s = min(self.width(), self.height())
        self.resize(s, s)
        self._updatePixmap()
