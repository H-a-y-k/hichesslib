# hichesslib
[![PyPI version fury.io](https://badge.fury.io/py/ansicolortags.svg)](https://pypi.org/project/hichesslib/) [![Build Status](https://app.travis-ci.com/H-a-y-k/hichesslib.svg?token=nP5fyR4hXGDypLNHLdGX&branch=master)](https://app.travis-ci.com/H-a-y-k/hichesslib) [![Coverage Status](https://coveralls.io/repos/github/H-a-y-k/hichesslib/badge.svg?branch=master)](https://coveralls.io/github/H-a-y-k/hichesslib?branch=master)

## Description
hichesslib is a cross-platform Python GUI chess library based on [python-chess](https://pypi.org/project/python-chess/) and [PySide2](https://pypi.org/project/PySide2/).
The library comes with a board widget that supports the chess rules and provides a set of interactions with the cells of the board and with the board itself including drag and drop, cell marking, piece movement, board flipping and more.

## Dependencies
Requires python version >= 3.6. For other dependencies see [requirements file](https://github.com/H-a-y-k/hichesslib/blob/master/requirements.txt).

## Usage
### Installation
> python3 -m pip install hichesslib

### Initialization
To start using the library you need to create a PySide2 application. The library's widgets can be used like any Qt widget.
``` python
>>> import hichess
>>> from PySide2.QtWidgets import QApplication
>>> import sys
>>>
>>> if __name__ == "__main__":
...     app = QApplication(sys.argv)
...     boardWidget = hichess.BoardWidget()
...     boardWidget.show()
...     sys.exit(app.exec_())
```
### Features
#### CellWidget
  * CellWidget can contain any chess piece.
  * Can be marked. Marked cell widgets are easily customizable.
  * Can be highlighted to display the legal moves on the board.

#### BoardWidget
  * BoardWidget supports all the chess rules.
  * Is easily customizable.
  * Supports rotation.
  * Supports drag and drop.
  * Games are easily traversable.
  * Interactions can be limited to only one side or for all sides (the latter is for read only boards).
  * Notifies about the game status (draw/stalemate/checkmate).

### Documentation
The the documentation is located in [docs](https://github.com/H-a-y-k/hichesslib/tree/master/docs).

### Problems and limitations
  * In order to make CellWidget graphically customizable, after each property change, the methods [unpolish](https://doc.qt.io/qt-5/qstyle.html#unpolish) and [polish](https://doc.qt.io/qt-5/qstyle.html#polish) are called, which significantly slows down the interactions with CellWidget.

### Examples
See [examples folder](https://github.com/H-a-y-k/hichesslib/tree/master/examples).

## Status
The library has been tested on Windows7, Windows10, Fedora 31.

## Tests
Unittests are done with the [unittest](https://docs.python.org/3/library/unittest.html) framework.
Tests are located in [hichesslib/test/](https://github.com/H-a-y-k/hichesslib/tree/master/test).

## License
hichesslib is licensed under GPLv3.0+ license. See [license](https://github.com/H-a-y-k/hichesslib/blob/master/LICENSE) file.
