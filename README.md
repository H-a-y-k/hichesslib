# hichesslib
[![PyPI version fury.io](https://badge.fury.io/py/ansicolortags.svg)](https://pypi.org/project/hichesslib/) [![Build Status](https://travis-ci.com/H-a-y-k/hichesslib.svg?branch=master)](https://travis-ci.com/H-a-y-k/hichesslib)

## Description
hichesslib is a Python GUI chess library based on [python-chess](https://pypi.org/project/python-chess/) and [PySide2](https://pypi.org/project/PySide2/).
The library comes with a board widget that supports the chess rules and provides a set of interactions with the squares of the board and with the board iteself including drag and drop, cell marking, piece movement, board flipping and more.

## Dependencies
Requires python version >= 3.6. For other dependencies see requirements.txt.

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

### Examples
Minimal examples will be provided in the future.

# Tests
The library is tested with the [unittest](https://docs.python.org/3/library/unittest.html) framework.
Tests are located in [hichesslib/test/](https://github.com/H-a-y-k/hichesslib/tree/master/test).

# License
hichesslib is licensed under GPLv3.0+ license. See [license](https://github.com/H-a-y-k/hichesslib/blob/master/LICENSE) file.
