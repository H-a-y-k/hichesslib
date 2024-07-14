#include "chessplusplus/chessplusplus.h"
#include <iostream>
#include <cassert>
#include <set>

using namespace std;
using namespace chess;

#include <gtest/gtest.h>

std::string bitboard_to_string(Bitboard bb)
{
    std::string strbb;
    for (int i = 0; i < 8; i++)
    {
        for (int j = 7; j >= 0; j--)
            strbb.insert(strbb.begin(), (bb & ((Bitboard(1) << square_at(i, j)))) ? '1' : '0');

        strbb.insert(strbb.begin(), '\n');
    }
    return strbb;
}

// Bitboard pawn_dirs_on_squaree(Square square, Color color)
// {
//     if (color == def::white)
//     {
//         return shift_bb(square, def::up_left) | shift_bb(square, def::up_right);
//     }
// }

int main()
{
    // for (Square sq = def::A1; sq <= def::H8; sq++)
    // {
    //     if (sq != def::A1 && square_bb(sq) & def::bb_files[0])
    //         std::cout << "\n";
    // std::cout << bitboard_to_string(def::bb_ranks[0] << 8) << "\n";
    // }
    // std::cout << bitboard_to_string(shift_square_bb(def::H2, def::down)) << "\n";
    // for (auto qd : def::bb_queen_dirs)
    // {
    // }
    return 0;
}
