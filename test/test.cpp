#include "../include/chessplusplus/chessplusplus.h"
#include <iostream>
#include <cassert>

using namespace std;
using namespace chess;

int main()
{
    assert(("faga",1>2));
    chess::Board board;
    std::string fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R";
    board.set_board_fen(fen);
    std::cout << board.board() << '\n' << '\n';

//    board.make_move(def::F1, def::H1);
//    std::cout << board.board();


    return 0;
}
