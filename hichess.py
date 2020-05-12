# -*- coding: utf-8 -*-
#
# This file is part of the HiChess project.
# Copyright (C) 2019-2020 Haik Sargsian <haiksargsian6@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
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
from PySide2.QtGui import QPixmap, QPalette, QColor

import chess

import logging
from enum import Enum
from functools import partial
from typing import Optional, Mapping, Generator
from collections import deque

import math


class IllegalMove(Exception):
    pass


class CellWidget(QtWidgets.QPushButton):
    """
    """

    designated = QtCore.Signal(bool)

    def __init__(self, parent=None, isAccessible=False):
        super().__init__(parent=parent)

        self.isAccessible = isAccessible
        self._isPiece = False
        self._isCheckedKing = False
        self._isHighlighted = False
        self._isMarked = False
        self._justMoved = False
        self.setObjectName("cell_plain")
        self.setCheckable(self.isAccessible)

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

    def isPiece(self) -> bool:
        return self._isPiece

    def setPiece(self, piece: Optional[chess.Piece]):
        self._isPiece = piece is not None

        if self._isPiece:
            self.setObjectName(f"cell_{chess.COLOR_NAMES[piece.color]}_{chess.PIECE_NAMES[piece.piece_type]}")
            self.setCheckable(self.isAccessible)
        else:
            self.setObjectName("cell_plain")
            self.setCheckable(False)

        self._updateStyle()

    def isPlain(self) -> bool:
        return not self._isPiece

    def toPlain(self) -> None:
        self.setPiece(None)

    @staticmethod
    def makePiece(piece: chess.Piece) -> "CellWidget":
        w = CellWidget()
        w.setPiece(piece)
        return w

    def isCheckedKing(self) -> bool:
        return self._isCheckedKing

    def setIsCheckedKing(self, ck: bool) -> bool:
        identifiers = self.objectName().split('_')
        if identifiers[0] == "cell" and identifiers[-1] == "king":
            self._isCheckedKing = ck
            self._updateStyle()
            return True
        return False

    def check(self) -> bool:
        return self.setIsCheckedKing(True)

    def uncheck(self) -> bool:
        return self.setIsCheckedKing(False)

    def isHighlighted(self) -> bool:
        return self._isHighlighted

    def setHighlighted(self, highlighted: bool) -> None:
        self._isHighlighted = highlighted

        if self._isHighlighted:
            self.setCheckable(False)
        else:
            self.setCheckable(self.isAccessible and self._isPiece)
        self._updateStyle()

    def highlight(self) -> None:
        self.setHighlighted(True)

    def unhighlight(self) -> None:
        self.setHighlighted(False)

    def isMarked(self) -> bool:
        return self._isMarked

    def setMarked(self, marked: bool) -> None:
        if self._isMarked != marked:
            self._isMarked = marked
            self.designated.emit(self._isMarked)
            self._updateStyle()

    def mark(self):
        self.setMarked(True)

    def unmark(self):
        self.setMarked(False)

    def justMoveed(self) -> bool:
        return self._justMoved

    def setJustMoved(self, jm: bool):
        self._justMoved = jm
        self._updateStyle()

    def _updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if self.isAccessible:
            if e.button() == QtCore.Qt.RightButton:
                self.setMarked(True)

    piece = QtCore.Property(bool, isPiece, setPiece)
    plain = QtCore.Property(bool, isPlain)
    checkedKing = QtCore.Property(bool, isCheckedKing, setIsCheckedKing)
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

    def __init__(self, parent=None,
                 fen: Optional[str] = chess.STARTING_FEN,
                 flipped: bool = False,
                 sides: AccessibleSides = NO_SIDE):
        super().__init__(parent=parent)

        self.board = chess.Board(fen)
        self.pop_stack = deque()

        self._flipped = flipped
        self._accessibleSides = sides

        self.defaultPixmap = self.pixmap()
        self.flippedPixmap = QPixmap(self.pixmap())
        self.lastCheckedCellWidget = None

        self._boardLayout = QtWidgets.QGridLayout()
        self._boardLayout.setContentsMargins(0, 0, 0, 0)
        self._boardLayout.setSpacing(0)

        def newCellWidget():
            cellWidget = CellWidget()
            cellWidget.clicked.connect(partial(self.onCellWidgetClicked, cellWidget))
            cellWidget.toggled.connect(partial(self.onCellWidgetToggled, cellWidget))
            cellWidget.designated.connect(self.onCellWidgetMarked)
            return cellWidget

        for i in range(8):
            for j in range(8):
                self._boardLayout.addWidget(newCellWidget(), i, j)
        self.setLayout(self._boardLayout)

        self.setFen(self.board.fen())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                           QtWidgets.QSizePolicy.Ignored)

    def cellWidgets(self) -> Generator[CellWidget, None, None]:
        for i in range(self._boardLayout.count()):
            yield self._boardLayout.itemAt(i).widget()

    def cellIndexOfSquare(self, square: chess.Square) -> Optional[chess.Square]:
        if not self.flipped:
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
        if not w.marked:
            self.unmarkCells()
        if w.highlighted:
            self.pushPiece(self.squareOf(w), self.lastCheckedCellWidget)
        elif not w.piece:
            self.unhighlightCells()
            self.uncheckCells()

    @QtCore.Slot()
    def onCellWidgetToggled(self, w: CellWidget, toggled: bool):
        if chess.COLOR_NAMES[self.board.turn] != w.objectName().split('_')[1]:
            w.setChecked(False)
        else:
            self.unhighlightCells()
            if toggled:
                self.uncheckCells(exceptFor=w)
                self.unmarkCells()
                self.highlightLegalMoveCellsFor(w)
                self.lastCheckedCellWidget = w

    @QtCore.Slot()
    def onCellWidgetMarked(self, marked: bool):
        if marked:
            self.uncheckCells()
            self.unhighlightCells()

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
                w.isAccessible = True

        temp = self.board.copy()
        list(map(callback, self.cellWidgets()))
        for square, piece in self.board.piece_map().items():
            self._setPieceAt(square, piece)
        self.board = temp

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        self.unhighlightCells()
        self.synchronize()

    def setFen(self, fen: Optional[str]) -> None:
        self.board = chess.Board(fen)
        self.unhighlightCells()
        self.synchronize()

    def clear(self):
        self.board.clear()
        self.unhighlightCells()
        self.synchronize()

    def makeMove(self, move: chess.Move):
        self.board.push(move)
        self.synchronize()

    def pushPiece(self, toSquare: chess.Square, w: CellWidget) -> None:
        self._push(chess.Move(self.squareOf(w), toSquare))

    def push(self, move: chess.Move) -> None:
        self._push(move)

    def pop(self) -> chess.Move:
        move = self.board.pop()

        self.pop_stack.append(move)

        self.cellWidgetAtSquare(move.from_square).justMoved = False
        self.cellWidgetAtSquare(move.to_square).justMoved = False

        if self.board.move_stack:
            lastMove = self.board.move_stack[-1]
            self.cellWidgetAtSquare(lastMove.from_square).justMoved = True
            self.cellWidgetAtSquare(lastMove.to_square).justMoved = True

        self.unmarkCells()
        self.unhighlightCells()
        self.synchronize()

        if self.board.is_check():
            self.king(self.board.turn).check()
        else:
            self.king(self.board.turn).uncheck()
            self.king(not self.board.turn).uncheck()

        return move

    def unpop(self):
        move = self.pop_stack.pop()

        if self.board.move_stack:
            lastMove = self.board.move_stack[-1]
            self.cellWidgetAtSquare(lastMove.from_square).justMoved = False
            self.cellWidgetAtSquare(lastMove.to_square).justMoved = False

        self.cellWidgetAtSquare(move.from_square).justMoved = True
        self.cellWidgetAtSquare(move.to_square).justMoved = True

        self.unmarkCells()
        self.unhighlightCells()
        self.makeMove(move)

        if self.board.is_check():
            self.king(self.board.turn).check()
        else:
            self.king(self.board.turn).uncheck()
            self.king(not self.board.turn).uncheck()

    def highlightLegalMoveCellsFor(self, w: CellWidget):
        for square in self.pieceCanBePushedTo(w):
            self.cellWidgetAtSquare(square).highlight()

    def uncheckCells(self, exceptFor: Optional[CellWidget] = None):
        def callback(w):
            if w != exceptFor:
                w.setChecked(False)

        list(map(callback, self.cellWidgets()))

    def unhighlightCells(self) -> None:
        list(map(lambda w: w.unhighlight(), self.cellWidgets()))

    def unmarkCells(self) -> None:
        list(map(lambda w: w.unmark(), self.cellWidgets()))

    @property
    def flipped(self) -> bool:
        return self._flipped

    @flipped.setter
    def flipped(self, flipped: bool) -> None:
        if self._flipped != flipped:
            self._flipped = flipped
            self.unhighlightCells()
            self.synchronize()
            self._updatePixmap()

    def flip(self) -> None:
        self._flipped = not self._flipped
        self.unhighlightCells()
        self.synchronize()
        self._updatePixmap()

    @property
    def accessibleSides(self) -> AccessibleSides:
        return self._accessibleSides

    @accessibleSides.setter
    def accessibleSides(self, accessibleSides: AccessibleSides) -> None:
        self._accessibleSides = accessibleSides
        self.synchronize()

    def _setPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        self.board.set_piece_at(square, piece)

        w = self.cellWidgetAtSquare(square)

        if self.accessibleSides == BOTH_SIDES:
            w.isAccessible = True
        elif self.accessibleSides == ONLY_WHITE_SIDE:
            if piece.color == chess.WHITE:
                w.isAccessible = True
        elif self.accessibleSides == ONLY_BLACK_SIDE:
            if piece.color == chess.BLACK:
                w.isAccessible = True

        w.setPiece(piece)

        return w

    def _updatePixmap(self) -> None:
        if not self._flipped:
            self.setPixmap(self.defaultPixmap)
        else:
            self.setPixmap(self.flippedPixmap)

    def _push(self, move: chess.Move) -> None:
        if self.board.move_stack:
            lastMove = self.board.move_stack[-1]
            self.cellWidgetAtSquare(lastMove.from_square).justMoved = False
            self.cellWidgetAtSquare(lastMove.to_square).justMoved = False

        turn = self.board.turn

        if self.cellWidgetAtSquare(move.from_square).isAccessible and move.promotion is None and self.isPseudoLegalPromotion(move):
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
                self.unhighlightCells()
                self.uncheckCells()
                return

        if not self.board.is_legal(move):
            raise IllegalMove(f"illegal move {move} by ")
        logging.debug(f"\n{self.board.lan(move)} ({move.from_square} -> {move.to_square})")

        self.cellWidgetAtSquare(move.from_square).justMoved = True
        self.cellWidgetAtSquare(move.to_square).justMoved = True

        if self.board.is_check():
            self.king(turn).uncheck()

        self.board.push(move)
        self.pop_stack.clear()

        if self.board.is_check():
            self.king(not turn).check()

        self.moveMade.emit(move.uci())
        logging.debug(f"\n{self.board}\n")
        self.synchronize()

        self.unhighlightCells()
        self.unmarkCells()

    def resizeEvent(self, event) -> None:
        s = min(self.width(), self.height())
        self.resize(s, s)
