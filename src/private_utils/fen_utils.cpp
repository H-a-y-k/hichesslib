#include "internal/fen_utils.h"
#include <stdexcept>
#include <sstream>
#include "public_utils/piece_utils.h"
#include "public_utils/square_utils.h"
#include "public_utils/precomputed.h"

/******************************************************************************
 * fen utilities
 ******************************************************************************/

using namespace chess;

std::vector<std::string> utility::validate_and_split_board_fen(const std::string &_board_fen)
{
    if (_board_fen.empty())
        throw std::invalid_argument("fen is empty");

    if (_board_fen.find(' ') != std::string::npos)
        throw std::invalid_argument(std::string("expected position part, got multiple parts: ") + _board_fen);

    std::istringstream split(_board_fen);
    std::vector<std::string> rows;

    for (std::string row; std::getline(split, row, '/'); rows.push_back(row))
    {
        if (row.empty())
            throw std::invalid_argument("rows in fen cannot be empty: " + _board_fen);

        int empty_cells = 0;
        int occupied_cells = 0;
        bool previous_was_digit = false;

        for (auto symbol_it = row.begin(); symbol_it != row.end(); symbol_it++)
        {
            if (!isdigit(*symbol_it))
            {
                if (piece_type_from_symbol(*symbol_it) == def::no_piece)
                    throw std::invalid_argument("invalid character(s)('" +
                                                 std::string(1, *symbol_it) +
                                                 "') in the fen: " + _board_fen);
                previous_was_digit = false;
                occupied_cells++;
                continue;
            }
            empty_cells += *symbol_it - '0';
            if (previous_was_digit)
                throw std::invalid_argument("a row in the fen shouldn't contain two digits next to each other: " + _board_fen);
            previous_was_digit = true;
        }

        if (empty_cells + occupied_cells != 8)
            throw std::invalid_argument("a fen row has to occupy exactly 8 cells: " + _board_fen);
    }

    if (rows.empty())
        throw std::invalid_argument("rows aren't separated with slashes('/') in the fen: " + _board_fen);
    else if (rows.size() != 8)
        throw std::invalid_argument("the fen has to contain 8 rows and not" + std::to_string(rows.size()) + ": " + _board_fen);

    return rows;
}

std::array<std::array<uint64_t, 7>, 2> utility::parse_board_fen_from_rows(std::vector<std::string> crows, const std::string &_board_fen)
{
    std::array<std::array<uint64_t, 7>, 2> tmp_bb_board {{{0,0,0,0,0,0,0},{0,0,0,0,0,0,0}}};

    for (auto row_it = crows.cbegin(); row_it != crows.cend(); row_it++)
    {
        bool previous_was_digit = false;

        for (auto symbol_it = row_it->cbegin(); symbol_it != row_it->cend(); symbol_it++)
        {
            if (isdigit(*symbol_it))
            {
                previous_was_digit = true;
                continue;
            }
            int rank = 7 - std::abs(std::distance(row_it, crows.cbegin()));
            int file = std::abs(std::distance(symbol_it, row_it->cbegin()));

            if (previous_was_digit)
            {
                file += *(symbol_it-1) - '0' - 1;
                previous_was_digit = false;
            }
            Color color = std::isupper(*symbol_it);
            PieceType piece = piece_type_from_symbol(*symbol_it);

            tmp_bb_board[color][piece] |= precomputed::bb_squares[square_at(rank, file)];
        }
    }
    return tmp_bb_board;
}

std::string utility::bitboard_to_string(uint64_t bb)
{
    std::string strbb;
    for (int i = 0; i < 8; i++)
    {
        for (int j = 7; j >= 0; j--)
            strbb.insert(strbb.begin(), (bb & ((uint64_t(1) << square_at(i, j)))) ? '1' : '0');

        strbb.insert(strbb.begin(), '\n');
    }
    return strbb;
}
