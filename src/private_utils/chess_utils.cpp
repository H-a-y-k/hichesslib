#include "internal/chess_utils.h"
#include "chessplusplus.h"

/******************************************************************************
 * chess utilities
 ******************************************************************************/

char chess::piece_symbol(PieceType type)
{
    return def::piece_symbols[type];
}

char chess::piece_symbol_from_piece(PieceType type, Color color)
{
    return (color == def::white) ? std::toupper(def::piece_symbols[type])
                                 : def::piece_symbols[type];
}

chess::PieceType chess::piece_type_from_symbol(char c)
{
    if (!c) return def::no_piece;

    auto found = std::find(def::piece_symbols.begin(), def::piece_symbols.end(), std::tolower(c));
    if (found == def::piece_symbols.end())
        return def::no_piece;
    return static_cast<PieceType>(std::abs(std::distance(found, def::piece_symbols.begin())));
}

const char* chess::piece_name(PieceType type)
{
    return def::piece_names[type];
}

bool chess::is_valid_square(Square square)
{
    return square < 64;
}

uint64_t chess::square_bb(Square square)
{
    return uint64_t(1) << square;
}

chess::Square chess::square_at(int rank, int file)
{
    return (rank << 3) | file;
}

chess::Square chess::shift_square(Square square, def::directions direction, int step)
{
    static constexpr std::array<int, 8> shift_offsets = {
        8,  // up
        -8, // down
        1,  // right
        -1, // left
        9,  // up_right (up + right)
        7,  // up_left (up + left)
        -7, // down_right (down + right)
        -9  // down_left (down + left)
    };

    return (direction == def::null) ? square
                                    : square + step * shift_offsets[static_cast<std::size_t>(direction)];
}

int chess::square_rank(chess::Square square)
{
    return square >> 3;
}

int chess::square_file(chess::Square square)
{
    return square & 7;
}

uint64_t chess::diagonals_at(Square square)
{
    return def::bb_diagonals[7 + square_rank(square) - square_file(square)]
           | def::bb_antidiagonals[square_rank(square) + square_file(square)];
}
