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

import unittest
from unittest.mock import patch

from context import hichess
import chess
import chess.pgn

from PySide2.QtWidgets import QApplication, QSizePolicy

import itertools
import os
import sys


class CellWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.cellWidget = hichess.CellWidget(parent=None)

    def testInit(self):
        self.assertTrue(self.cellWidget.isPlain())
        self.assertFalse(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

    def testGetPiece(self):
        self.assertIsNone(self.cellWidget.getPiece())
        piece = chess.Piece(chess.PAWN, chess.BLACK)
        self.cellWidget.setPiece(piece)
        self.assertEqual(self.cellWidget.getPiece(), piece)

    def testPieceProperty(self):
        for pieceType, color in itertools.product(chess.PIECE_TYPES, chess.COLORS):
            piece = chess.Piece(pieceType, color)
            self.cellWidget.setPiece(piece)
            self.assertEqual(self.cellWidget.getPiece(), piece)
            self.assertTrue(self.cellWidget.isPiece())
            self.assertTrue(self.cellWidget.isCheckable())
            self.assertEqual(self.cellWidget.objectName(), f"cell_{chess.COLOR_NAMES[color]}_{chess.PIECE_NAMES[pieceType]}")

        self.assertTrue(self.cellWidget.isPiece())
        self.cellWidget.setPiece(None)
        self.assertFalse(self.cellWidget.isPiece())
        self.assertEqual(self.cellWidget.objectName(), "cell_plain")
        self.assertFalse(self.cellWidget.isCheckable())

    def testIsPlain(self):
        self.assertTrue(self.cellWidget.isPlain())
        self.cellWidget.setPiece(chess.Piece(chess.PAWN, chess.BLACK))
        self.assertFalse(self.cellWidget.isPlain())
        self.cellWidget.setPiece(None)
        self.assertTrue(self.cellWidget.isPlain())

    @patch("hichess.hichess.CellWidget.setPiece")
    def testToPlain(self, mockSetPiece):
        self.cellWidget.toPlain()
        mockSetPiece.assert_called_with(None)

    def testMakePiece(self):
        piece = chess.Piece(chess.PAWN, chess.WHITE)
        w = hichess.CellWidget.makePiece(piece)
        self.assertEqual(w.getPiece(), piece)

        with self.assertRaises(AssertionError):
            hichess.CellWidget.makePiece(None)

    def testInCheckProperty(self):
        self.assertFalse(self.cellWidget.isInCheck())

        with self.assertRaises(hichess.NotAKingError):
            self.cellWidget.setInCheck(True)

        self.cellWidget.setPiece(chess.Piece(chess.KING, chess.WHITE))
        self.assertFalse(self.cellWidget.isInCheck())
        self.cellWidget.setInCheck(True)
        self.assertTrue(self.cellWidget.isInCheck())
        self.cellWidget.setInCheck(False)
        self.assertFalse(self.cellWidget.isInCheck())

    @patch("hichess.hichess.CellWidget.setInCheck")
    def testCheck(self, mockSetIsCheckedKing):
        self.cellWidget.check()
        mockSetIsCheckedKing.assert_called_once_with(True)

    @patch("hichess.hichess.CellWidget.setInCheck")
    def testUncheck(self, mockSetIsCheckedKing):
        self.cellWidget.uncheck()
        mockSetIsCheckedKing.assert_called_once_with(False)

    def testSetHighlighted(self):
        self.assertFalse(self.cellWidget.isHighlighted())
        self.cellWidget.setHighlighted(True)
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.setHighlighted(False)
        self.assertFalse(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

        self.cellWidget.setPiece(chess.Piece(chess.PAWN, chess.WHITE))
        self.cellWidget.setHighlighted(True)
        self.assertTrue(self.cellWidget.isHighlighted())
        self.assertFalse(self.cellWidget.isCheckable())

    @patch("hichess.hichess.CellWidget.setHighlighted")
    def testHighlight(self, mockSetHighlighted):
        self.cellWidget.highlight()
        mockSetHighlighted.assert_called_once_with(True)

    @patch("hichess.hichess.CellWidget.setHighlighted")
    def testUnhighlight(self, mockSetHighlighted):
        self.cellWidget.unhighlight()
        mockSetHighlighted.assert_called_once_with(False)

    def testMarkedProperty(self):
        self.cellWidget = hichess.CellWidget()

        self.assertFalse(self.cellWidget.isMarked())
        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

        self.cellWidget.mark()
        self.assertTrue(self.cellWidget.isMarked())

        self.cellWidget.unmark()
        self.assertFalse(self.cellWidget.isMarked())

    @patch("hichess.hichess.CellWidget.setMarked")
    def testMark(self, mockSetMarked):
        self.cellWidget.mark()
        mockSetMarked.assert_called_once_with(True)

    @patch("hichess.hichess.CellWidget.setMarked")
    def testUnmark(self, mockSetMarked):
        self.cellWidget.unmark()
        mockSetMarked.assert_called_once_with(False)


class BoardWidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN, flipped=False, sides=hichess.NO_SIDE)

    def testInit(self):
        boardWidgetCopy = self.boardWidget

        self.assertEqual(self.boardWidget.board.fen(), chess.STARTING_FEN)
        self.assertFalse(self.boardWidget.flipped)
        self.assertEqual(self.boardWidget.accessibleSides, hichess.NO_SIDE)
        self.assertDictEqual(self.boardWidget.board.piece_map(), chess.Board().piece_map())
        self.assertEqual(len(list(filter(hichess.CellWidget.isPiece, self.boardWidget.cellWidgets()))), 32)
        self.assertEqual(len(list(filter(hichess.CellWidget.isPlain, self.boardWidget.cellWidgets()))), 32)

        self.boardWidget = hichess.BoardWidget(fen=None, flipped=False, sides=hichess.NO_SIDE)
        self.assertEqual(self.boardWidget.board.fen(), chess.Board(None).fen())
        self.assertFalse(self.boardWidget.flipped)
        self.assertEqual(self.boardWidget.accessibleSides, hichess.NO_SIDE)
        self.assertFalse(list(filter(hichess.CellWidget.isPiece, self.boardWidget.cellWidgets())))
        self.assertEqual(len(list(filter(hichess.CellWidget.isPlain, self.boardWidget.cellWidgets()))), 64)

        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN, flipped=True, sides=hichess.BOTH_SIDES)
        self.assertEqual(self.boardWidget.board.fen(), chess.STARTING_FEN)
        self.assertTrue(self.boardWidget.flipped)
        self.assertEqual(self.boardWidget.accessibleSides, hichess.BOTH_SIDES)

        for i in range(64):
            w1 = self.boardWidget.cellWidgetAtSquare(i)
            w2 = boardWidgetCopy.cellWidgetAtSquare(i)

            self.assertEqual(w1.isPlain(), w2.isPlain())
            self.assertEqual(w1.isPiece(), w2.isPiece())
            self.assertEqual(w1.isHighlighted(), w2.isHighlighted())
            self.assertEqual(w1.isMarked(), w2.isMarked())
            self.assertEqual(w1.objectName(), w2.objectName())

    def testGetCellWidgets(self):
        lyt = self.boardWidget.layout()
        lytWidgets = list([lyt.itemAt(i).widget() for i in range(lyt.count())])
        self.assertListEqual(lytWidgets, list(self.boardWidget.cellWidgets()))

    def testForeachCells(self):
        pass

    def testCellIndexOfSquare(self):
        for i in range(64):
            self.assertEqual(self.boardWidget.cellIndexOfSquare(i), chess.square_mirror(i))

        self.boardWidget.flipped = True
        for i in range(64):
            self.assertEqual(self.boardWidget.cellIndexOfSquare(i),
                             chess.square(7 - chess.square_file(i), chess.square_rank(i)))

    def testSquareOf(self):
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertEqual(self.boardWidget.squareOf(w), chess.square_mirror(i))

        self.boardWidget.flip()
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertEqual(self.boardWidget.squareOf(w),
                             chess.square(7 - chess.square_file(i), chess.square_rank(i)))

    def testCellWidgetAtSquare(self):
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertIs(w, self.boardWidget.cellWidgetAtSquare(chess.square_mirror(i)))

        self.boardWidget.flip()
        for i, w in enumerate(self.boardWidget.cellWidgets()):
            self.assertIs(w, self.boardWidget.cellWidgetAtSquare(
                          chess.square(7 - chess.square_file(i), chess.square_rank(i))))

    def testCanBePushedTo(self):
        for w in self.boardWidget.cellWidgets():
            squares = list(self.boardWidget.pieceCanBePushedTo(w))
            self.assertListEqual(squares,
                                 [move.to_square
                                  for move in self.boardWidget.board.legal_moves
                                  if move.from_square == self.boardWidget.squareOf(w)])

    def testIsPseudoLegalPromotion(self):
        self.boardWidget.setFen(None)

        a = chess.Move(chess.A7, chess.A8)
        b = chess.Move(chess.A2, chess.A1)
        c = chess.Move(chess.A3, chess.A4)
        d = chess.Move(chess.B7, chess.B8)
        e = chess.Move(chess.C7, chess.C8)

        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(a))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(b))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(c))

        self.boardWidget.addPieceAt(chess.A2, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPieceAt(chess.A7, chess.Piece(chess.PAWN, chess.WHITE))
        self.boardWidget.addPieceAt(chess.B7, chess.Piece(chess.PAWN, chess.BLACK))
        self.boardWidget.addPieceAt(chess.C7, chess.Piece(chess.ROOK, chess.WHITE))

        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(a))
        self.assertTrue(self.boardWidget.isPseudoLegalPromotion(b))

        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(c))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(d))
        self.assertFalse(self.boardWidget.isPseudoLegalPromotion(e))

    def testKing(self):
        self.assertEqual(self.boardWidget.squareOf(self.boardWidget.king(chess.WHITE)),
                         self.boardWidget.board.king(chess.WHITE))
        self.assertEqual(self.boardWidget.squareOf(self.boardWidget.king(chess.BLACK)),
                         self.boardWidget.board.king(chess.BLACK))

    def testSetPieceAt(self):
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)
        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.ONLY_WHITE_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)

        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN,
                                               sides=hichess.ONLY_BLACK_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.WHITE))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)

        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.ONLY_BLACK_SIDE)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.BLACK))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)

        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertTrue(w.isCheckable())
        self.assertEqual(w.objectName(), "cell_black_pawn")

        self.boardWidget = hichess.BoardWidget(sides=hichess.BOTH_SIDES)
        self.boardWidget.setPieceAt(chess.A4, chess.Piece(chess.PAWN, chess.BLACK))
        w = self.boardWidget.cellWidgetAtSquare(chess.A4)

        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertEqual(w.objectName(), "cell_black_pawn")

    def testRemovePieceAt(self):
        self.boardWidget.removePieceAt(chess.A2)
        w = self.boardWidget.cellWidgetAtSquare(chess.A2)
        self.assertTrue(w.isPlain())
        self.assertFalse(w.isPiece())
        self.assertFalse(w.isCheckable())
        self.assertIsNone(self.boardWidget.board.piece_at(chess.A2))

        with self.assertRaises(ValueError):
            self.boardWidget.removePieceAt(chess.A2)

        for square in range(chess.A3, chess.H5):
            with self.assertRaises(ValueError):
                self.boardWidget.removePieceAt(square)

    def testAddPieceAt(self):
        square = chess.A5
        piece = chess.Piece(chess.PAWN, chess.WHITE)

        w = self.boardWidget.addPieceAt(square, piece)

        self.assertTrue(w.isPiece())
        self.assertFalse(w.isHighlighted())
        self.assertFalse(w.isMarked())
        self.assertEqual(w.objectName(), "cell_white_pawn")

        with self.assertRaises(ValueError):
            self.boardWidget.addPieceAt(square, piece)

    def testSynchronize(self):
        self.boardWidget = hichess.BoardWidget(fen=None)
        self.assertFalse(list(filter(hichess.CellWidget.isPiece, self.boardWidget.cellWidgets())))

        self.boardWidget.board.set_fen(chess.STARTING_FEN)
        self.boardWidget.synchronize()

        self.assertEqual(self.boardWidget.board.fen(), chess.Board.starting_fen)
        self.assertDictEqual(self.boardWidget.board.piece_map(), chess.Board().piece_map())

    @patch("hichess.hichess.BoardWidget.synchronize")
    def testSetPieceMap(self, mockSynchronize):
        self.boardWidget = hichess.BoardWidget(fen=None)
        mockSynchronize.assert_called_once()

        newPieceMap = chess.Board().piece_map()
        self.boardWidget.setPieceMap(newPieceMap)
        self.assertEqual(mockSynchronize.call_count, 2)
        self.assertDictEqual(self.boardWidget.board.piece_map(), newPieceMap)

    def testSetFen(self):
        self.assertEqual(self.boardWidget.board.fen(), chess.STARTING_FEN)

        self.boardWidget.setFen(None)

        self.assertEqual(self.boardWidget.board.fen(), chess.Board(None).fen())
        self.assertFalse(self.boardWidget.board.piece_map())
        self.assertFalse(list(filter(hichess.CellWidget.isPiece, self.boardWidget.cellWidgets())))

    @patch("hichess.hichess.BoardWidget.synchronize")
    def testClear(self, mockSynchronize):
        boardWidget = self.boardWidget
        boardWidget.clear()
        self.assertTrue(self.boardWidget.board, chess.Board(None))
        self.assertFalse(self.boardWidget.popStack)
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isInCheck)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isHighlighted)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isMarked)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isChecked)))

        mockSynchronize.assert_called_once()

    @patch("hichess.hichess.BoardWidget.synchronize")
    def testReset(self, mockSynchronize):
        self.boardWidget.push(chess.Move.from_uci("a2a4"))
        self.boardWidget.flipped = True
        self.boardWidget.king(chess.WHITE).check()

        self.boardWidget.reset()
        self.assertFalse(self.boardWidget.flipped)
        self.assertEqual(self.boardWidget.board, chess.Board())
        self.assertFalse(self.boardWidget.popStack)
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isInCheck)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isHighlighted)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isMarked)))
        self.assertFalse(list(self.boardWidget.cellWidgets(hichess.CellWidget.isChecked)))

        mockSynchronize.assert_called_once()

    def testMakeMove(self):
        for gameName in os.listdir("games"):
            with open(f"games/{gameName}") as pgn:
                game = chess.pgn.read_game(pgn)
                self.boardWidget = hichess.BoardWidget(fen=game.board().fen(),
                                                       flipped=False, sides=hichess.NO_SIDE)
                for move in game.mainline_moves():
                    self.boardWidget.makeMove(move)
                    w = self.boardWidget.cellWidgetAtSquare(move.to_square)

                    self.assertTrue(w.isPiece())
                    colorName, pieceName = w.objectName().split('_')[1:]
                    pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                    self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(w)),
                                     chess.Piece(pieceType, colorName == 'white'))

    def testPush(self):
        for gameName in os.listdir("games"):
            with open(f"games/{gameName}") as pgn:
                game = chess.pgn.read_game(pgn)
                self.boardWidget = hichess.BoardWidget(fen=game.board().fen(),
                                                       flipped=False, sides=hichess.NO_SIDE)
                for move in game.mainline_moves():
                    self.boardWidget.push(move)
                    w = self.boardWidget.cellWidgetAtSquare(move.to_square)

                    self.assertTrue(w.isPiece())
                    colorName, pieceName = w.objectName().split('_')[1:]
                    pieceType = chess.PIECE_TYPES[chess.PIECE_NAMES.index(pieceName) - 1]
                    self.assertEqual(self.boardWidget.board.piece_at(self.boardWidget.squareOf(w)),
                                     chess.Piece(pieceType, colorName == 'white'))

    def testPushForRaises(self):
        boardWidget = hichess.BoardWidget()

        illegalMoves = ["a1d6", "b2b6", "c2d5", "a7a6", "e1g1"]
        for uci in illegalMoves:
            with self.assertRaises(hichess.IllegalMove):
                boardWidget.push(chess.Move.from_uci(uci))

    def testPopAndUnpop(self):
        self.boardWidget.setFen(chess.STARTING_FEN)
        boardCopy = self.boardWidget.board.copy()

        self.boardWidget.push(chess.Move(chess.A2, chess.A4))
        self.boardWidget.pop()
        self.assertEqual(self.boardWidget.board, boardCopy)
        self.boardWidget.reset()

        moves = [chess.Move(chess.A2, chess.A4), chess.Move(chess.A4, chess.A6), chess.Move(chess.A6, chess.A8)]
        self.boardWidget.makeMove(moves[0])
        self.boardWidget.makeMove(moves[1])
        self.boardWidget.makeMove(moves[2])
        moveStack = self.boardWidget.board.move_stack.copy()
        boardCopy2 = self.boardWidget.board.copy()

        self.boardWidget.pop(3)
        self.assertEqual(self.boardWidget.board, boardCopy)
        self.assertListEqual(list(self.boardWidget.popStack), moveStack[::-1])

        self.boardWidget.unpop(3)
        self.assertEqual(self.boardWidget.board, boardCopy2)
        self.assertFalse(self.boardWidget.popStack)
        self.assertListEqual(list(self.boardWidget.board.move_stack), moves)

    @patch("hichess.hichess.BoardWidget.unpop")
    @patch("hichess.hichess.BoardWidget.pop")
    def testGoToMove(self, mockPop, mockUnpop):
        self.assertFalse(self.boardWidget.goToMove(-1))
        self.assertFalse(self.boardWidget.goToMove(1))

        self.boardWidget.makeMove(chess.Move.from_uci("a2a4"))
        self.boardWidget.makeMove(chess.Move.from_uci("a4a6"))
        self.assertTrue(self.boardWidget.goToMove(0))
        mockPop.assert_called_with(2)

        self.boardWidget.popStack.append(chess.Move.from_uci("a4a6"))
        self.boardWidget.popStack.append(chess.Move.from_uci("a2a4"))
        self.boardWidget.board.clear_stack()
        self.assertTrue(self.boardWidget.goToMove(2))
        mockUnpop.assert_called_with(2)

    def testHighlightLegalMoveCellsFor(self):
        self.boardWidget.setFen("R6R/3Q4/1Q4Q1/4Q3/2Q4Q/Q4Q2/pp1Q4/kBNN1KB1 w - - 0 1")

        for w in self.boardWidget.cellWidgets():
            canBePushedTo = self.boardWidget.pieceCanBePushedTo(w)
            self.boardWidget.highlightLegalMoveCellsFor(w)
            for square in canBePushedTo:
                self.assertTrue(self.boardWidget.cellWidgetAtSquare(square).isHighlighted())
            self.boardWidget.unhighlightCells()

    def testUncheckCells(self):
        self.boardWidget.accessibleSides = hichess.BOTH_SIDES

        def callback(w):
            if w.isCheckable():
                w.setChecked(True)

        list(map(callback, self.boardWidget.cellWidgets()))
        self.boardWidget.uncheckCells(None)
        self.assertFalse(list(filter(hichess.CellWidget.isChecked, self.boardWidget.cellWidgets())))

        list(map(callback, self.boardWidget.cellWidgets()))
        for w in self.boardWidget.cellWidgets():
            if w.isChecked():
                self.boardWidget.uncheckCells(exceptFor=w)
                checkedWidgets = list(filter(hichess.CellWidget.isChecked, self.boardWidget.cellWidgets()))
                self.assertEqual(len(checkedWidgets), 1)
                self.assertIs(checkedWidgets[0], w)
                break

    def testUnhighlightCells(self):
        self.boardWidget.accessibleSides = hichess.BOTH_SIDES

        list(map(hichess.CellWidget.highlight, self.boardWidget.cellWidgets()))
        self.boardWidget.unhighlightCells()
        self.assertFalse(list(filter(hichess.CellWidget.isHighlighted, self.boardWidget.cellWidgets())))

    def testUnmarkCells(self):
        list(map(hichess.CellWidget.mark, self.boardWidget.cellWidgets()))
        self.boardWidget.unmarkCells()
        self.assertFalse(list(filter(hichess.CellWidget.isMarked, self.boardWidget.cellWidgets())))

    def testFlip(self):
        boardWidgetCopy = self.boardWidget

        self.boardWidget = hichess.BoardWidget(fen=chess.STARTING_FEN, flipped=False, sides=hichess.BOTH_SIDES)

        for i in range(64):
            w1 = self.boardWidget.cellWidgetAtSquare(i)
            w2 = boardWidgetCopy.cellWidgetAtSquare(i)

            self.assertEqual(w1.isPlain(), w2.isPlain())
            self.assertEqual(w1.isPiece(), w2.isPiece())
            self.assertEqual(w1.isHighlighted(), w2.isHighlighted())
            self.assertEqual(w1.isMarked(), w2.isMarked())
            self.assertEqual(w1.objectName(), w2.objectName())

        self.boardWidget.flip()

        for i in range(64):
            w1 = self.boardWidget.cellWidgetAtSquare(i)
            w2 = boardWidgetCopy.cellWidgetAtSquare(i)

            self.assertEqual(w1.isPlain(), w2.isPlain())
            self.assertEqual(w1.isPiece(), w2.isPiece())
            self.assertEqual(w1.isHighlighted(), w2.isHighlighted())
            self.assertEqual(w1.isMarked(), w2.isMarked())
            self.assertEqual(w1.objectName(), w2.objectName())

    @patch("hichess.hichess.BoardWidget.synchronize")
    def testSetAccessibleSides(self, mockSynchronize):
        self.boardWidget.accessibleSides = hichess.BOTH_SIDES
        self.assertEqual(self.boardWidget.accessibleSides, hichess.BOTH_SIDES)
        mockSynchronize.assert_called_once()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    unittest.main()
    sys.exit(app.exec_())
