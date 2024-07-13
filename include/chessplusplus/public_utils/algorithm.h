#ifndef CONVENIENCE_H
#define CONVENIENCE_H

#include "definitions.h"
#include <cctype>
#include <functional>
#include <string>
#include <exception>
#include <stdexcept>
#include <iostream>
#include <sstream>

namespace chess
{
[[nodiscard]]
char piece_symbol(PieceType t);
[[nodiscard]]
char piece_symbol_from_piece(PieceType t, Color c);
[[nodiscard]]
PieceType piece_type_from_symbol(char c);
[[nodiscard]]
const char* piece_name(PieceType t);
[[nodiscard]]
bool is_valid_square(Square square);
[[nodiscard]]
Square square_at(int rank, int file);
[[nodiscard]] inline
Bitboard shift_square(Square square, def::directions direction, int step = 1) {}
[[nodiscard]]
Bitboard shift_square_bb(Square square, def::directions direction, int step = 1);
// [[nodiscard]]
// Bitboard shift_square_bb(Bitboard bb, def::directions direction, int step = 1);
[[nodiscard]]
int square_rank(Square square);
[[nodiscard]]
int square_file(Square square);
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
#endif // CONVENIENCE_H
