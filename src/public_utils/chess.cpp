#include "public_utils/chess.h"
#include "internal/other_utils.h"
#include "chessplusplus.h"

/******************************************************************************
 * chess utilities
 ******************************************************************************/

using namespace chess;

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

chess::Square chess::square_at(int rank, int file)
{
    return (rank << 3) | file;
}

Bitboard chess::shift_square_bb(Square square, def::directions direction, int step)
{
    static constexpr std::array<int, 9> shift_offsets = {
        8,  // up
        -8, // down
        1,  // right
        -1, // left
        9,  // up_right (up + right)
        7,  // up_left (up + left)
        -7, // down_right (down + right)
        -9, // down_left (down + left)
        0   // null
    };

    static constexpr std::array<Bitboard, 9> invalid_shifts =
    {
        def::bb_ranks[7],
        def::bb_ranks[0],
        def::bb_files[7],
        def::bb_files[0],
        def::bb_ranks[7] | def::bb_files[7],
        def::bb_ranks[7] | def::bb_files[0],
        def::bb_ranks[0] | def::bb_files[7],
        def::bb_ranks[0] | def::bb_files[0],
        0x0
    };

    size_t dir = static_cast<std::size_t>(direction);
    auto bb_square = def::bb_squares[square];

    for (int i = 0; i < step; i++)
    {
        if (bb_square & invalid_shifts[dir])
            return 0x0;
        if (shift_offsets[dir] < 0)
        {
            bb_square >>= -shift_offsets[dir];
            continue;
        }
        bb_square <<= shift_offsets[dir];
    }
    return bb_square;
}

int chess::square_rank(chess::Square square)
{
    return square >> 3;
}

int chess::square_file(chess::Square square)
{
    return square & 7;
}

Bitboard chess::rank_at(Square square)
{
    return def::bb_ranks[square_rank(square)];
}

Bitboard chess::file_at(Square square)
{
    return def::bb_files[square_file(square)];
}

Bitboard chess::diagonal_at(Square square)
{
    return def::bb_diagonals[7 + square_rank(square) - square_file(square)];
}

Bitboard chess::antidiagonal_at(Square square)
{
    return def::bb_antidiagonals[square_rank(square) + square_file(square)];
}
