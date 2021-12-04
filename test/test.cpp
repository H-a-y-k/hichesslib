#include "../include/chessplusplus/chessplusplus.h"
#include <iostream>

using namespace std;
using namespace chess;

int main()
{
    chess::Board board;
    board.set_board_fen(def::starting_board_fen);
    std::cout << board.board() << '\n' << '\n';

    board.move_piece(def::A2, def::A4);
    std::cout << board.board();

    return 0;
}
