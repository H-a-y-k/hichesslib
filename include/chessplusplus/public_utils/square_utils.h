#include "definitions.h"
#include <cstddef>

namespace chess
{
[[nodiscard]]
bool is_valid_square(Square square) noexcept;
[[nodiscard]]
Square square_at(std::size_t rank, std::size_t file) noexcept ;
[[nodiscard]]
size_t square_distance(Square square1, Square square2) noexcept;
[[nodiscard]]
size_t square_manhattan_distance(Square square1, Square square2) noexcept;

[[nodiscard]]
int square_rank(Square square) noexcept;
[[nodiscard]]
int square_file(Square square) noexcept;
[[nodiscard]]
Bitboard rank_at(Square square);
[[nodiscard]]
Bitboard file_at(Square square);
[[nodiscard]]
Bitboard diagonal_at(Square square);
[[nodiscard]]
Bitboard antidiagonal_at(Square square);

[[nodiscard]]
int square_mirror(Square square);
}
