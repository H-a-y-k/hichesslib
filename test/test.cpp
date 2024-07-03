#include "chessplusplus/chessplusplus.h"
#include <iostream>
#include <cassert>
#include <set>

using namespace std;
using namespace chess;

#include <gtest/gtest.h>

// std::array<uint64_t, 2> ddiagonals_at(Square square)
// {
//     uint64_t result1 = 0;
//     uint64_t result2 = 0;
//     result1 |= square_bb(square);
//     result2 |= square_bb(square);

//     if (square_rank(square) != 7 && square_file(square) != 0)
//     {
//     for (Square i = shift_square(square, def::up_left); is_valid_square(i); i = shift_square(i, def::up_left))
//     {
//         // std::cout << def::square_names[square];
//         // std::cout << def::square_names[i];
//         result1 |= square_bb(i);
//         if (square_rank(i) == 7 || square_file(i) == 0)
//         {
//             break;
//         }
//     }
//     }
//     if (square_rank(square) != 0 && square_file(square) != 7)
//     {
//     for (Square i = shift_square(square, def::down_right); is_valid_square(i); i = shift_square(i, def::down_right))
//     {
//         // std::cout << def::square_names[i];
//         result1 |= square_bb(i);
//         if (square_rank(i) == 0 || square_file(i) == 7)
//         {
//             break;
//         }
//     }
//     }

//     // std::cout << "\n";
//     if (square_rank(square) != 7 && square_file(square) != 7)
//     {
//     for (Square i = shift_square(square, def::up_right); is_valid_square(i); i = shift_square(i, def::up_right))
//     {
//         // std::cout << def::square_names[i];
//         result2 |= square_bb(i);
//         if (square_rank(i) == 7 || square_file(i) == 7)
//         {
//             break;
//         }
//     }
//     }
//     if (square_rank(square) != 0 && square_file(square) != 0)
//     {
//     for (Square i = shift_square(square, def::down_left); is_valid_square(i); i = shift_square(i, def::down_left))
//     {
//         // std::cout << def::square_names[i];
//         result2 |= square_bb(i);
//         if (square_rank(i) == 0 || square_file(i) == 0)
//         {
//             break;
//         }
//     }
//     }
//     // std::cout << "\n";

//     return {result1, result2};
// }

std::string bitboard_to_string(uint64_t bb, int k)
{
    std::string strbb;
    for (int i = 0; i < 8; i++)
    {
        for (int j = 7; j >= 0; j--)
            strbb = (bb & ((uint64_t(1) << square_at(i, j))) ? std::to_string(k).append(strbb) : std::string("0").append(strbb));

        strbb.insert(strbb.begin(), '\n');
    }
    return strbb;
}

int main()
{
    chess::square_at(1,1);
    return 0;
}
