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
Bitboard rotate_right(Bitboard bb, int s);
Bitboard rotate_left(Bitboard bb, int s);
Bitboard gen_shift(Bitboard bb, int s);

Bitboard bb_flip_vertical(Bitboard bb);
Bitboard bb_flip_horizontal(Bitboard bb);
Bitboard bb_flip_diagonal(Bitboard bb);
Bitboard bb_flip_antidiagonal(Bitboard bb);

Bitboard bb_rotate_180(Bitboard bb);
Bitboard bb_rotate_90_clockwise(Bitboard bb);
Bitboard bb_rotate_90_anti_clockwise(Bitboard bb);
Bitboard bb_pseudo_rotate_45_clockwise(Bitboard bb);
Bitboard bb_pseudo_rotate_45_anti_clockwise(Bitboard bb);

Bitboard bb_shift_up(Bitboard bb);
Bitboard bb_shift_2_up(Bitboard bb);
Bitboard bb_shift_down(Bitboard bb);
Bitboard bb_shift_2_down(Bitboard bb);
Bitboard bb_shift_left(Bitboard bb);
Bitboard bb_shift_2_left(Bitboard bb);
Bitboard bb_shift_right(Bitboard bb);
Bitboard bb_shift_2_right(Bitboard bb);
Bitboard bb_shift_up_left(Bitboard bb);
Bitboard bb_shift_up_right(Bitboard bb);
Bitboard bb_shift_down_left(Bitboard bb);
Bitboard bb_shift_down_right(Bitboard bb);
Bitboard bb_shift(Bitboard bb, def::directions dir);
}

#endif // CONVENIENCE_H
