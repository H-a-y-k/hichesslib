#include "../include/chessplusplus/chessplusplus.h"
#include <iostream>
#include <cassert>

using namespace std;
using namespace chess;

int main()
{
    chess::Board board;
    std::string fen = "rnbqkbnr/pppppppp/8/8/P1Q5/8/PPPPP2P/RNBQ3R";
    board.set_board_fen(def::starting_board_fen);
//    auto str = board.bitboard_str();
//    for (int i = 0; i < 64; i++)
//    {
//        if (i > 0 && i % 8 == 0)
//            std::cout << '\n';
//        std::cout << str[i];
//    }

//    std::cout << board.board_fen() << '\n' << '\n';

    board.make_move(def::F2, def::F3);
    std::cout << board.board_fen() << std::endl;
    std::cout << board.bitboard_str();


    return 0;
}
