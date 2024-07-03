#include <gtest/gtest.h>
#include "chessplusplus/chessplusplus.h"

TEST(FenTest, StartingFenTest)
{
    // check if board is correctly default initialized
    chess::Board board;
    ASSERT_EQ(board.board_fen(), chess::def::starting_board_fen) << "board_fen() is different from staring board fen";
}

TEST(FenTest, RandomBoardFenTest)
{
    // feed random board fens and check if board_fen() is correct

    // std::vector<std::string> board_fens = {

    // }
}
