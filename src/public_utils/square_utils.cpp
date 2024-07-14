#include "public_utils/square_utils.h"
#include "public_utils/definitions.h"
#include "public_utils/precomputed.h"
#include <cstddef>
#include <cmath>

using namespace chess;
using namespace chess::precomputed;

bool chess::is_valid_square(Square square) noexcept
{
    return square < 64;
}

Square chess::square_at(std::size_t rank, std::size_t file) noexcept
{
    return (rank << 3) | file;
}

int chess::square_rank(Square square) noexcept
{
    return square >> 3;
}

int chess::square_file(Square square) noexcept
{
    return square & 7;
}

size_t chess::square_distance(Square square1, Square square2) noexcept
{
    return std::max(abs(square_file(square1) - square_file(square2)), abs(square_rank(square1) - square_rank(square2)));
}

size_t chess::square_manhattan_distance(Square square1, Square square2) noexcept
{
    return abs(square_file(square1) - square_file(square2)) + abs(square_rank(square2) - square_rank(square1));
}

Bitboard chess::rank_at(Square square)
{
    return bb_ranks[square_rank(square)];
}

Bitboard chess::file_at(Square square)
{
    return bb_files[square_file(square)];
}

Bitboard chess::diagonal_at(Square square)
{
    return bb_diagonals[7 + square_rank(square) - square_file(square)];
}

Bitboard chess::antidiagonal_at(Square square)
{
    return bb_antidiagonals[square_rank(square) + square_file(square)];
}
