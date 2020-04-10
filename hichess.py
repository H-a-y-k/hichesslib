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

from . import resources


class IllegalMove(Exception):
    pass


class CellType(Enum):
    PLAIN = 0
    PIECE = 1


class CellWidget(QtWidgets.QPushButton):
    """
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.cellType = CellType.PLAIN
        self.isHighlighted = False
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)
        self.sizePolicy().setHeightForWidth(True)

    def toPiece(self, piece: chess.Piece):
        self.cellType = CellType.PIECE
        colorName = chess.COLOR_NAMES[piece.color]
        pieceName = chess.PIECE_NAMES[piece.piece_type]
        self.setStyleSheet(f"border-image: url(:/images/{colorName}_{pieceName}.png) 2 2 2 2 stretch stretch;")

    def highlight(self):
        pass

    def unhighlight(self):
        pass


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
        self.toggledWidget = None

        self._boardLayout = QtWidgets.QGridLayout()
        self._boardLayout.setContentsMargins(0, 0, 0, 0)
        self._boardLayout.setSpacing(0)

        for i in range(8):
            for j in range(8):
                cellWidget = CellWidget()
                self._boardLayout.addWidget(cellWidget, i, j)
        self.setLayout(self._boardLayout)

        self.setPieceMap(self.board.piece_map())

        self.setAutoFillBackground(True)
        self.setScaledContents(True)
        self._setBoardPixmap()
        #self.setStyleSheet("QPushButton { background: transparent; }")

    def cellWidgetAt(self, square: chess.Square) -> Optional[CellWidget]:
        """
        Returns the cell widget at the given square.
        """

        item = self._boardLayout.itemAtPosition(chess.square_rank(square),
                                                chess.square_file(square))
        if item is not None:
            return item.widget()
        return None

    @QtCore.Slot()
    def onPieceCellWidgetToggled(self, w: CellWidget, toggled: bool):
        self.unhighlightCells()

        if toggled:
            self.toggledWidget = w
            self.highlightLegalMovesFor(w)
        else:
            self.toggledWidget = None

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
            raise ValueError("Square {} is already occupied")

        self.board.set_piece_at(square, piece)
        w = self.cellWidgetAt(square)
        w.toPiece(piece)
        return w

    def synchronizeBoard(self) -> None:
        for i in range(self._boardLayout.count()):
            self._boardLayout.itemAt(i).widget().toPlain()

        for square, piece in self.board.piece_map().items():
            self.cellWidgetAt(square).toPiece(piece)

    def setPieceMap(self, pieces: Mapping[int, chess.Piece]) -> None:
        self.board.set_piece_map(pieces)
        for square, piece in pieces.items():
            self.cellWidgetAt(square).toPiece(piece)

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
        move = chess.Move(w.square, toSquare)

        # TODO
        if self.isPseudoLegalPromotion(move):
            # TODO Create a promotion dialogue
            move.promotion = chess.QUEEN
            w.toPiece(move.promotion)

        if not self.board.is_legal(move):
            raise IllegalMove(f"illegal move {move} with {chess.PIECE_NAMES[w.piece.piece_type]}")

        logging.debug(f"\n{self.board.lan(move)} ({w.square} -> {toSquare})")

        self.board.push(move)
        self.synchronizeBoard()

        logging.debug(f"\n{self.board}\n")

        self.unhighlightCells()

    def push(self, move: chess.Move) -> "BoardWidget":
        self.pushPiece(move.to_square, self.pieceCellWidgetAt(move.from_square))
        return self

    def pop(self) -> "BoardWidget":
        self.board.pop()
        self.synchronizeBoard()
        return self

    def highlightLegalMoveCellsFor(self, w: CellWidget) -> None:
        pass

    def unhighlightCells(self) -> None:
        pass

    def flip(self) -> "BoardWidget":
        self.flipped = not self.flipped
        self._setBoardPixmap()

        # TODO
        return self

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.heightForWidth(min(self.width(), self.height()))

    def _setBoardPixmap(self):
        if self.flipped:
            self.setPixmap(QtGui.QPixmap(":/images/flipped_chessboard.png"))
        else:
            self.setPixmap(QtGui.QPixmap(":/images/chessboard.png"))
