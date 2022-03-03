<a name=".hichess"></a>
# hichess
Cross-platform Python chess GUI library based on PySide2 and python_chess.

<a name=".hichess.hichess.CellWidget"></a>
## CellWidget Objects

```python
class CellWidget(QtWidgets.QPushButton):
    CellWidget(parent=None)
```

A `QPushButton` representing a single cell of chess board.
CellWidget can be either a chess piece or an empty cell of the
board. It can be marked with different colors.

`CellWidget` by default represents an empty cell.

<a name=".hichess.hichess.CellWidget.designated"></a>
## designated

Indicates that the setter of `marked` property has been called.

<a name=".hichess.hichess.CellWidget.isPiece"></a>
## isPiece

```python
   isPiece() -> bool
```

Indicates the type of the cell.
It is True if the cell is a chess piece
and False if it is an empty cell.

<a name=".hichess.hichess.CellWidget.setPiece"></a>
## setPiece

```python
   setPiece(piece: Optional[chess.Piece]) -> None
```

Sets the content of the cell.

Parameters
----------
piece : Optional[chess.Piece]
    The piece that will occupy this cell.

    The cell is emptied if the piece is None otherwise its
    object name is set to ``cell_`` + the name of the piece or ``plain``.
    For example the object name of an empty cell will be ``cell_plain`` and
    the object name of a cell occupied by a white pawn will be ``cell_white_pawn``

    Cells containing a piece are checkable, whereas those empty ones are not.

<a name=".hichess.hichess.CellWidget.isPlain"></a>
## isPlain

```python
   isPlain() -> bool
```

A convenience property indicating if the cell is empty or not.

<a name=".hichess.hichess.CellWidget.toPlain"></a>
## toPlain

```python
   toPlain() -> None
```

Empties the cell.

<a name=".hichess.hichess.CellWidget.makePiece"></a>
## makePiece

```python
   @staticmethod
   makePiece(piece: chess.Piece) -> "CellWidget"
```

A static method that creates a `CellWidget` from the given piece.

Parameters
----------
piece : chess.Piece
    The piece that will occupy the cell. Note that the type of
    the piece cannot be NoneType as in the definition of the
    method `setPiece`, because by default cells are created empty.

<a name=".hichess.hichess.CellWidget.isInCheck"></a>
## isInCheck

```python
   isInCheck() -> bool
```

Indicates if the cell contains a king in check.

Warnings
--------
Cells that aren't occupied by a king cannot be in check.

Raises
-------
NotAKingError
    It is raised when the property is set to True for
    a cell not being occupied by a king.

<a name=".hichess.hichess.CellWidget.check"></a>
## check

```python
   check() -> None
```

A convenience method that sets the property `isInCheck` to True.

<a name=".hichess.hichess.CellWidget.uncheck"></a>
## uncheck

```python
   uncheck() -> None
```

A convenience method that sets the property `isInCheck` to False.

<a name=".hichess.hichess.CellWidget.isHighlighted"></a>
## isHighlighted

```python
   isHighlighted() -> bool
```

Indicates if the cell is highlighted.
Highlighted cells are special cells that are used to indicate
legal moves on the board.
Highlighted cells are not checkable.

<a name=".hichess.hichess.CellWidget.highlight"></a>
## highlight

```python
   highlight() -> None
```

A convenience method that sets the property `highlighted` to True.

<a name=".hichess.hichess.CellWidget.unhighlight"></a>
## unhighlight

```python
   unhighlight() -> None
```

A convenience method that sets the property `highlighted` to False.

<a name=".hichess.hichess.CellWidget.isMarked"></a>
## isMarked

```python
   isMarked() -> bool
```

Indicates if a cell is marked.
Marked cells can have a different stylesheet which will visually distinguish
them from other cells.
The `designated` signal is emitted when this property's setter is called.

<a name=".hichess.hichess.CellWidget.mark"></a>
## mark

```python
   mark()
```

A convenience method that sets the property `marked` to True.

<a name=".hichess.hichess.CellWidget.unmark"></a>
## unmark

```python
   unmark()
```

A convenience method that sets the property `marked` to False.

<a name=".hichess.hichess.BoardWidget"></a>
## BoardWidget Objects

```python
class BoardWidget(QtWidgets.QLabel):
    BoardWidget(parent=None, fen: Optional[str] = chess.STARTING_FEN, flipped: bool = False, sides: AccessibleSides = NO_SIDE, dnd: bool = False)
```

Represents a customizable graphical chess board.
It inherits `QtWidgets.QLabel` and has a `QtWidgets.QGridLayout` with 64
`CellWidget` instances that can be moved. It also supports all the
chess rules and allows drag and drop.

Attributes
----------
board : chess.Board
    Represents the actual board. Moves and their validation are
    conducted through this object.

popStack : Deque[chess.Move]
    The moves that are popped from the `board.move_stack` through the functions
    `goToMove`, `pop` are stored in this deque.

blockBoardOnPop : bool
    If this attribute is True, the board can't be interacted with unless `popStack`
    is empty.

defaultPixmap : QPixmap
    The pixmap that the board will have when the property `flipped` is False.

flippedPixmap : QPixmap
    The pixmap that the board will have when the property `flipped` is True.

lastCheckedCellWidget : Optional[CellWidget]
    Holds the last CellWidget that was checked through
    `QtWidgets.QPushButton.setChecked(True)`.
    Its value is None in case no CellWidget has been checked.

dragAndDrop : bool
    This is used to enable or disable drag and drop.
    When it is True, cell widgets can be dragged, by pressing on them
    with the mouse left button and moving the mouse cursor. They
    can be dropped by releasing the mouse left button during the drag. Whereever
    the cell is dropped, the board acts as if the same point were clicked with
    the mouse.

<a name=".hichess.hichess.BoardWidget.moveMade"></a>
## moveMade

Indicates that a move on the board has been made either with `BoardWidget.makeMove`
or any other function that calls makes a move on `board` (e.g `chess.Board.push`). The signal accepts the move in
form of `str` as a parameter. Particularly, the library always emits the signal with the move in form of san as a
parameter. If it is a `checkmate`, a `draw` or a `stalemate` the respective signal is emitted together with `gameOver`.

<a name=".hichess.hichess.BoardWidget.movePushed"></a>
## movePushed

This is nearly the same as `moveMade`, with the exception that it's emit only by those functions that
contain the word 'push' in the name.

<a name=".hichess.hichess.BoardWidget.checkmate"></a>
## checkmate

This is emitted when it is checkmate on the board. It accepts the color of the winning side as a parameter.

<a name=".hichess.hichess.BoardWidget.draw"></a>
## draw

This is emitted when it is drag on the board.

<a name=".hichess.hichess.BoardWidget.stalemate"></a>
## stalemate

This is emitted when it is stalemate on the board.

<a name=".hichess.hichess.BoardWidget.gameOver"></a>
## gameOver

This is emitted when the game is over.

<a name=".hichess.hichess.BoardWidget.cellWidgets"></a>
## cellWidgets

```python
   cellWidgets(predicate: Callable[[CellWidget], bool] = _DefaultPredicate) -> Generator[CellWidget, None, None]
```

Yields Generator[CellWidget, None, None]
    All the cell widgets in the board's layout
    that fulfill the predicate's condition.

<a name=".hichess.hichess.BoardWidget.foreachCells"></a>
## foreachCells

```python
   foreachCells(*args: Callable[[CellWidget], Any], predicate: Callable[[CellWidget], bool] = _DefaultPredicate)
```

Iterates over all the cell widgets that fulfill the condition of `predicate`
and calls the callbacks passed through *args one by one in the given order.

Parameters
----------
*args : Callable[[CellWidget], Any]
    The callbacks that will be called on the cell widgets.
predicate : Callable[[CellWidget], bool]

<a name=".hichess.hichess.BoardWidget.cellIndexOfSquare"></a>
## cellIndexOfSquare

```python
   cellIndexOfSquare(square: chess.Square) -> Optional[chess.Square]
```

Returns
-------
Optional[chess.Square]
    The index of the widget at the given square number if we started counting from the top left
    corner of the board.

<a name=".hichess.hichess.BoardWidget.squareOf"></a>
## squareOf

```python
   squareOf(w: CellWidget) -> chess.Square
```

Returns
-------
chess.Square
    The square number corresponding to the given cell widget.

<a name=".hichess.hichess.BoardWidget.cellWidgetAtSquare"></a>
## cellWidgetAtSquare

```python
   cellWidgetAtSquare(square: chess.Square) -> Optional[CellWidget]
```

Returns
-------
Optional[CellWidget]
    The cell widget at the given square if there is one, otherwise
    it returns None.

<a name=".hichess.hichess.BoardWidget.pieceCanBePushedTo"></a>
## pieceCanBePushedTo

```python
   pieceCanBePushedTo(w: CellWidget)
```

Yields the numbers of squares that the piece on the cell widget can be legally pushed
to.

<a name=".hichess.hichess.BoardWidget.isPseudoLegalPromotion"></a>
## isPseudoLegalPromotion

```python
   isPseudoLegalPromotion(move: chess.Move) -> bool
```

This method indicates if the given move can be a promotion. So would be if the piece
being moved were a pawn, and if it were being moved to the corresponding end of the board.

Warnings
--------
The result of this method is pseudo-true, as it doesn't do any move validation. It is the
caller's responsibility to validate the move.

<a name=".hichess.hichess.BoardWidget.king"></a>
## king

```python
   king(color: chess.Color) -> Optional[CellWidget]
```

Returns
-------
Optional[CellWidget]
    The cell widget that holds the king of the given color or None if there is no
    king.

<a name=".hichess.hichess.BoardWidget.setBoardPixmap"></a>
## setBoardPixmap

```python
   setBoardPixmap(defaultPixmap, flippedPixmap) -> None
```

Sets the default and flipped pixmaps and updates the board's pixmap
according to them.

<a name=".hichess.hichess.BoardWidget.setPieceAt"></a>
## setPieceAt

```python
   setPieceAt(square: chess.Square, piece: chess.Piece) -> CellWidget
```

Sets the given piece at the given square of the board.

Returns
-------
CellWidget
    The cell widget where the piece was set.

<a name=".hichess.hichess.BoardWidget.removePieceAt"></a>
## removePieceAt

```python
   removePieceAt(square: chess.Square) -> CellWidget
```

Removes the piece from the given square of the board.
The cell at the given square is turned into a plain cell.

Raises
------
ValueError
    If the cell at the given square does not hold a chess piece.

Returns
-------
CellWidget
    The cell widget at the given square.

<a name=".hichess.hichess.BoardWidget.addPieceAt"></a>
## addPieceAt

```python
   addPieceAt(square: chess.Square, piece: chess.Piece) -> CellWidget
```

This method is the safer version of `setPieceAt`.

Raises
------
ValueError
    If the given square is already occupied.

Returns
-------
CellWidget
    The created cell widget.

<a name=".hichess.hichess.BoardWidget.synchronize"></a>
## synchronize

```python
   synchronize() -> None
```

Synchronizes the widget with the contents of `board`.
This method makes all the cells plain and then sets their pieces on by one.

<a name=".hichess.hichess.BoardWidget.synchronizeAndUpdateStyles"></a>
## synchronizeAndUpdateStyles

```python
   synchronizeAndUpdateStyles() -> None
```

Synchronizes the widget with the contents of `board` and updates
the just moved cells and the king in check.

<a name=".hichess.hichess.BoardWidget.setPieceMap"></a>
## setPieceMap

```python
   setPieceMap(pieces: Mapping[int, chess.Piece]) -> None
```

Sets the board's piece map and synchronizes the board widget.
The highlighted cells are also unhighlighted, because the positions of
the pieces change after the change of piece map.

<a name=".hichess.hichess.BoardWidget.setFen"></a>
## setFen

```python
   setFen(fen: Optional[str]) -> None
```

Sets the board's fen and synchronizes the board widget.
The highlighted cells are also unhighlighted, because the positions of
the pieces change after the fen.

<a name=".hichess.hichess.BoardWidget.clear"></a>
## clear

```python
   clear() -> None
```

Clears the board widget and resets the properties of the cells.

<a name=".hichess.hichess.BoardWidget.reset"></a>
## reset

```python
   reset() -> None
```

Resets the pieces to their standard positions and resets the
properties of the board widget and all the pieces inside of its layout.

<a name=".hichess.hichess.BoardWidget.makeMove"></a>
## makeMove

```python
   makeMove(move: chess.Move) -> None
```

Makes a move without move validation.
The move, though, should be pseudo-legal. Otherwise `chess.Board.push`
will raise an exception. Can be useful when you don't need a promotion dialog
or notifications about the game state. Emits moveMade signal, with move's san as
parameter.

<a name=".hichess.hichess.BoardWidget.pushPiece"></a>
## pushPiece

```python
   pushPiece(toSquare: chess.Square, w: CellWidget) -> None
```

Pushes the piece on the given cell widget to the given square.
If there is a promotion a dialog will appear with 4 pieces to choose.
Emits moveMade and movePushed signals, with move's san as parameter.
If the it is a draw/stalemate/checkmate the corresponding signal will be
emitted.

Raises
------
IllegalMove
    If the move is illegal.

<a name=".hichess.hichess.BoardWidget.push"></a>
## push

```python
   push(move: chess.Move) -> None
```

Pushes the given move.
For further reference see `pushPiece`.

Raises
------
IllegalMove
    If the move is illegal or null.

<a name=".hichess.hichess.BoardWidget.pop"></a>
## pop

```python
   pop(n=1) -> str
```

Pops the move `n` times.
Removes `marked` and `highlighted` properties from cells.
Updates just moved properties.

Returns
--------
str
    Last poped move in form of uci.

<a name=".hichess.hichess.BoardWidget.unpop"></a>
## unpop

```python
   unpop(n=1) -> str
```

Unpops moves `n` times.
This method works in the same way as `pop`.
For further reference see the latter's documentation.

<a name=".hichess.hichess.BoardWidget.goToMove"></a>
## goToMove

```python
   goToMove(id: int) -> bool
```

Goes to the move with the given `id`.

Returns
-------
bool
    True if a move with the given `id` exists. Otherwise returns False.

<a name=".hichess.hichess.BoardWidget.highlightLegalMoveCellsFor"></a>
## highlightLegalMoveCellsFor

```python
   highlightLegalMoveCellsFor(w: CellWidget) -> int
```

Highlights the legal moves for the given cell widget.

Returns
-------
int
    The number of highlighted cells as a result of this method's call.

<a name=".hichess.hichess.BoardWidget.uncheckCells"></a>
## uncheckCells

```python
   uncheckCells(exceptFor: Optional[CellWidget] = None) -> None
```

Calls QtWidgets.QPushButton.setChecked(False) for all the cells except for the
specified one. If you want to set checked to False for all the cells, then pass None as
an argument to this method instead.

<a name=".hichess.hichess.BoardWidget.unhighlightCells"></a>
## unhighlightCells

```python
   unhighlightCells() -> None
```

Calls `CellWidget.unhighlight` for each cell.

<a name=".hichess.hichess.BoardWidget.unmarkCells"></a>
## unmarkCells

```python
   unmarkCells() -> None
```

Calls `CellWidget.unmark` for each cell.

<a name=".hichess.hichess.BoardWidget.flip"></a>
## flip

```python
   flip() -> None
```

A convenience method that sets the property `flipped` to True.
