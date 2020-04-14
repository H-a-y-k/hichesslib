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

import chess

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui

import logging
from enum import Enum
from functools import partial
from typing import Optional, Mapping


class IllegalMove(Exception):
    pass


class CellType(Enum):
    PLAIN = 0
    PIECE = 1


CELL_PLAIN = CellType.PLAIN
CELL_PIECE = CellType.PIECE


class CellWidget(QtWidgets.QPushButton):
    """
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.cellType = CELL_PLAIN
        self.setProperty("highlighted", False)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.sizePolicy().setHeightForWidth(True)
        self.setAutoExclusive(True)

    def toPiece(self, piece: chess.Piece) -> "CellWidget":
        self.setCheckable(True)
        self.cellType = CELL_PIECE
        pieceColor = chess.COLOR_NAMES[piece.color]
        pieceName = chess.PIECE_NAMES[piece.piece_type]
        self.setObjectName(f"{pieceColor}_{pieceName}")
        self._updateStyle()
        return self

    def toPlain(self) -> "CellWidget":
        self.cellType = CELL_PLAIN
        self.setCheckable(False)
        self.setObjectName("plain_cell")
        self._updateStyle()
        return self

    def isHighlighted(self) -> bool:
        return self.property("highlighted")

    def highlight(self) -> "CellWidget":
        self.setProperty("highlighted", True)
        self._updateStyle()
        self.setCheckable(False)
        return self

    def unhighlight(self) -> "CellWidget":
        self.setProperty("highlighted", False)
        self._updateStyle()
        self.setCheckable(True)
        return self

    def _updateStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)


class BoardWidget(QtWidgets.QLabel):
    """
    A graphical chess board.
    """
    def __init__(self, parent=None,
                 fen: Optional[str] = chess.STARTING_FEN,
                 flipped: bool = False):
        super().__init__(parent=parent)

        self.board = chess.Board(fen)
        self.flipped = flipped
        self.defaultPixmap = self.pixmap()
        self.flippedPixmap = self.pixmap()
        self.toggled = None

        self._boardLayout = QtWidgets.QGridLayout()
        self._boardLayout.setContentsMargins(0, 0, 0, 0)
        self._boardLayout.setSpacing(0)

        def cn(w):
            w.clicked.connect(lambda: self.onPieceCellWidgetClicked(w))
            w.toggled.connect(lambda toggled: self.onPieceCellWidgetToggled(w, toggled))

        for i in range(8):
            for j in range(8):
                cellWidget = CellWidget()
                cn(cellWidget)
                self._boardLayout.addWidget(cellWidget, i, j)
        self.setLayout(self._boardLayout)

        self.setPieceMap(self.board.piece_map())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                           QtWidgets.QSizePolicy.Ignored)

    def cellIndexOfSquare(self, square: chess.Square):
        if not self.flipped:
            return chess.square_mirror(square)
        else:
            return square

    def squareOf(self, w: CellWidget) -> chess.Square:
        i = self._boardLayout.indexOf(w)
        if not self.flipped:
            return chess.square_mirror(i)
        else:
            return i

    def cellWidgetAtSquare(self, square: chess.Square) -> Optional[CellWidget]:
        """
        Returns the cell widget at the given square.
        """

        item = self._boardLayout.itemAt(self.cellIndexOfSquare(square))
        if item is not None:
            return item.widget()
        return None

    def updatePixmap(self):
        if not self.flipped:
            self.setPixmap(self.defaultPixmap)
        else:
            self.setPixmap(self.flippedPixmap)

    def setBoardPixmap(self, defaultPixmap, flippedPixmap):
        self.defaultPixmap = defaultPixmap
        self.flippedPixmap = flippedPixmap
        self.updatePixmap()

    @QtCore.Slot()
    def onPieceCellWidgetClicked(self, w: CellWidget):
        if w.isHighlighted():
            self.pushPiece(self.squareOf(w), self.toggled)

    @QtCore.Slot()
    def onPieceCellWidgetToggled(self, w: CellWidget, toggled: bool):
        if toggled:
            self.unhighlightCells()
            self.highlightLegalMoveCellsFor(w)
            self.toggled = w

    def setPieceAt(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        self.board.set_piece_at(square, piece)
        w = self.cellWidgetAtSquare(square)
        w.toPiece(piece)
        w.setCheckable(True)
        return w

    def addPiece(self, square: chess.Square, piece: chess.Piece) -> CellWidget:
        """
        Adds `piece` to the board at the given squares. Creates a
        piece widget with the given square and piece and adds it to
        board layout. Connects the created piece widget to the
        `onPieceWidgetToggled` slot.

        Returns
        -------
        The created piece widget.

        Raises
        ------
        ValueError
            If the given square is already occupied.
        """

        if self.board.piece_at(square) is not None:
            raise ValueError("Square {} is occupied")
        return self.setPieceAt(square, piece)

    def synchronizeBoard(self) -> None:
        for i in range(self._boardLayout.count()):
            self._boardLayout.itemAt(i).widget().toPlain()

        for square, piece in self.board.piece_map().items():
            self.setPieceAt(square, piece)

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        self.synchronizeBoard()

    def setFen(self, fen: str) -> None:
        self.board.set_fen(fen)
        self.synchronizeBoard()

    def isPseudoLegalPromotion(self, move: chess.Move) -> bool:
        piece = self.board.piece_at(move.from_square)

        if piece is not None and piece.piece_type == chess.PAWN:
            if piece.color == chess.WHITE:
                return chess.A8 <= move.to_square <= chess.H8
            elif piece.color == chess.BLACK:
                return chess.A1 <= move.to_square <= chess.H1
        return False

    def pushPiece(self, toSquare: chess.Square, w: CellWidget) -> None:
        move = chess.Move(self.squareOf(w), toSquare)
        # TODO
        if self.isPseudoLegalPromotion(move):
            # TODO Create a promotion dialogue
            move.promotion = chess.QUEEN
            w.toPiece(move.promotion)

        if not self.board.is_legal(move):
            raise IllegalMove(f"illegal move {move} with {chess.PIECE_NAMES[self.board.piece_at(move.from_square).piece_type]}")
        logging.debug(f"\n{self.board.lan(move)} ({move.from_square} -> {toSquare})")

        self.board.push(move)
        self.synchronizeBoard()

        logging.debug(f"\n{self.board}\n")

        self.unhighlightCells()

    def push(self, move: chess.Move) -> "BoardWidget":
        self.pushPiece(move.to_square, self.cellWidgetAtSquare(move.from_square))
        return self

    def pop(self) -> "BoardWidget":
        self.board.pop()
        self.synchronizeBoard()
        return self

    def highlightLegalMoveCellsFor(self, w: CellWidget) -> None:
        for move in self.board.legal_moves:
            if move.from_square == self.squareOf(w):
                self.cellWidgetAtSquare(move.to_square).highlight()

    def unhighlightCells(self) -> None:
        for w in self.children():
            if isinstance(w, CellWidget):
                w.unhighlight()

    def flip(self) -> "BoardWidget":
        self.flipped = not self.flipped
        self.updatePixmap()
        self.synchronizeBoard()
        return self

    def resizeEvent(self, event):
        s = min(self.width(), self.height())
        self.resize(s, s)
