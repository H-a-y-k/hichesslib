#include "public_utils/bitboard_utils.h"
#include "public_utils/precomputed.h"
#include <cstddef>

using namespace chess;

#define rotl64(bb, s) (bb << s) | (bb >> (64-s))
#define rotr64(bb, s) (bb >> s) | (bb << (64-s))
#define gen_shift64(bb, s) (s > 0) ? (bb << s) : (bb >> -s)

Bitboard chess::rotate_left(Bitboard bb, int s)
{
    return rotl64(bb,s);
}

Bitboard chess::rotate_right(Bitboard bb, int s)
{
    return rotr64(bb,s);
}

Bitboard chess::gen_shift(Bitboard bb, int s)
{
    return gen_shift64(bb, s);
}

Bitboard chess::bb_flip_vertical(Bitboard bb)
{
    static constexpr Bitboard mask1 = 0x00FF'00FF'00FF'00FF;
    static constexpr Bitboard mask2 = 0x0000'FFFF'0000'FFFF;

    bb = ((bb >>  8) & mask1) | ((bb & mask1) <<  8);
    bb = ((bb >> 16) & mask2) | ((bb & mask2) << 16);
    bb =  (bb >> 32) | (bb << 32);

    return bb;
}

Bitboard chess::bb_flip_horizontal(Bitboard bb)
{
    static constexpr Bitboard mask1 = 0x5555'5555'5555'5555;
    static constexpr Bitboard mask2 = 0x3333'3333'3333'3333;
    static constexpr Bitboard mask4 = 0x0f0f'0f0f'0f0f'0f0f;

    bb = ((bb >> 1) & mask1) | ((bb & mask1) << 1);
    bb = ((bb >> 2) & mask2) | ((bb & mask2) << 2);
    bb = ((bb >> 4) & mask4) | ((bb & mask4) << 4);

    return bb;
}

Bitboard chess::bb_flip_diagonal(Bitboard bb)
{
    Bitboard temp_bb;
    static constexpr Bitboard mask1 = 0x5500'5500'5500'5500;
    static constexpr Bitboard mask2 = 0x3333'0000'3333'0000;
    static constexpr Bitboard mask4 = 0x0f0f'0f0f'0000'0000;

    temp_bb = mask4 & (bb ^ (bb << 28));
    bb ^= temp_bb ^ (temp_bb >> 28);
    temp_bb = mask2 & (bb ^ (bb << 14));
    bb ^= temp_bb ^ (temp_bb >> 14);
    temp_bb = mask1 & (bb ^ (bb <<  7));
    bb ^= temp_bb ^ (temp_bb >> 7);

    return bb;
}

Bitboard chess::bb_flip_antidiagonal(Bitboard bb)
{
    Bitboard temp_bb;

    static constexpr Bitboard mask1 = 0xaa00'aa00'aa00'aa00;
    static constexpr Bitboard mask2 = 0xcccc'0000'cccc'0000;
    static constexpr Bitboard mask4 = 0xf0f0'f0f0'0f0f0f0f;

    temp_bb = bb ^ (bb << 36);
    bb ^= mask4 & (temp_bb ^ (bb >> 36));
    temp_bb = mask2 & (bb ^ (bb << 18));
    bb ^= temp_bb ^ (temp_bb >> 18);
    temp_bb = mask1 & (bb ^ (bb << 9));
    bb ^= temp_bb ^ (temp_bb >>  9);

    return bb;
}

Bitboard chess::bb_rotate_180(Bitboard bb)
{
    static constexpr Bitboard mask_h1 = 0x5555555555555555;
    static constexpr Bitboard mask_h2 = 0x3333333333333333;
    static constexpr Bitboard mask_h4 = 0x0F0F0F0F0F0F0F0F;
    static constexpr Bitboard mask_v1 = 0x00FF00FF00FF00FF;
    static constexpr Bitboard mask_v2 = 0x0000FFFF0000FFFF;

    bb = ((bb >>  1) & mask_h1) | ((bb & mask_h1) <<  1);
    bb = ((bb >>  2) & mask_h2) | ((bb & mask_h2) <<  2);
    bb = ((bb >>  4) & mask_h4) | ((bb & mask_h4) <<  4);
    bb = ((bb >>  8) & mask_v1) | ((bb & mask_v1) <<  8);
    bb = ((bb >> 16) & mask_v2) | ((bb & mask_v2) << 16);
    bb = (bb >> 32) | (bb << 32);

    return bb;
}

Bitboard chess::bb_rotate_90_clockwise(Bitboard bb)
{
    // return bb_flip_vertical(bb_flip_diagonal(bb));

    static constexpr Bitboard mask_v1 = 0x00FF'00FF'00FF'00FF;
    static constexpr Bitboard mask_v2 = 0x0000'FFFF'0000'FFFF;
    static constexpr Bitboard mask_h1 = 0x5555'5555'5555'5555;
    static constexpr Bitboard mask_h2 = 0x3333'3333'3333'3333;
    static constexpr Bitboard mask_h4 = 0x0f0f'0f0f'0f0f'0f0f;

    bb = ((bb >>  8) & mask_v1) | ((bb & mask_v1) <<  8);
    bb = ((bb >> 16) & mask_v2) | ((bb & mask_v2) << 16);
    bb =  (bb >> 32) | (bb << 32);

    bb = ((bb >> 1) & mask_h1) | ((bb & mask_h1) << 1);
    bb = ((bb >> 2) & mask_h2) | ((bb & mask_h2) << 2);
    bb = ((bb >> 4) & mask_h4) | ((bb & mask_h4) << 4);

    return bb;
}

Bitboard chess::bb_rotate_90_anti_clockwise(Bitboard bb)
{
    // return bb_flip_diagonal(bb_flip_vertical(bb));

    Bitboard temp_bb;

    static constexpr Bitboard mask_d1 = 0xaa00'aa00'aa00'aa00;
    static constexpr Bitboard mask_d2 = 0xcccc'0000'cccc'0000;
    static constexpr Bitboard mask_d4 = 0xf0f0'f0f0'0f0f0f0f;
    static constexpr Bitboard mask_v1 = 0x00FF'00FF'00FF'00FF;
    static constexpr Bitboard mask_v2 = 0x0000'FFFF'0000'FFFF;

    temp_bb = bb ^ (bb << 36);
    bb ^= mask_d4 & (temp_bb ^ (bb >> 36));
    temp_bb = mask_d2 & (bb ^ (bb << 18));
    bb ^= temp_bb ^ (temp_bb >> 18);
    temp_bb = mask_d1 & (bb ^ (bb << 9));
    bb ^= temp_bb ^ (temp_bb >> 9);

    bb = ((bb >>  8) & mask_v1) | ((bb & mask_v1) <<  8);
    bb = ((bb >> 16) & mask_v2) | ((bb & mask_v2) << 16);
    bb =  (bb >> 32) | (bb << 32);

    return bb;
}

Bitboard chess::bb_pseudo_rotate_45_clockwise(Bitboard bb)
{
    static constexpr Bitboard mask1 = 0xAAAA'AAAA'AAAA'AAAA;
    static constexpr Bitboard mask2 = 0xCCCC'CCCC'CCCC'CCCC;
    static constexpr Bitboard mask4 = 0xF0F0'F0F0'F0F0'F0F0;

    bb ^= mask1 & (bb ^ rotr64(bb,  8));
    bb ^= mask2 & (bb ^ rotr64(bb, 16));
    bb ^= mask4 & (bb ^ rotr64(bb, 32));

    return bb;
}

Bitboard chess::bb_pseudo_rotate_45_anti_clockwise(Bitboard bb)
{
    static constexpr Bitboard mask1 = 0x5555'5555'5555'5555;
    static constexpr Bitboard mask2 = 0x3333'3333'3333'3333;
    static constexpr Bitboard mask4 = 0x0F0F'0F0F'0F0F'0F0F;

    bb ^= mask1 & (bb ^ rotr64(bb,  8));
    bb ^= mask2 & (bb ^ rotr64(bb, 16));
    bb ^= mask4 & (bb ^ rotr64(bb, 32));

    return bb;
}
Bitboard chess::bb_shift_up(Bitboard bb)
{
    return bb << 8;
}

Bitboard chess::bb_shift_2_up(Bitboard bb)
{
    return bb << 16;
}

Bitboard chess::bb_shift_down(Bitboard bb)
{
    return bb >> 8;
}

Bitboard chess::bb_shift_2_down(Bitboard bb)
{
    return bb >> 16;
}

Bitboard chess::bb_shift_right(Bitboard bb)
{
    return (bb << 1) & ~precomputed::bb_files[0];
}

Bitboard chess::bb_shift_2_right(Bitboard bb)
{
    return (bb << 2) & ~precomputed::bb_files[0] & ~precomputed::bb_files[1];
}

Bitboard chess::bb_shift_left(Bitboard bb)
{
    return (bb >> 1) & ~precomputed::bb_files[7];
}

Bitboard chess::bb_shift_2_left(Bitboard bb)
{
    return (bb >> 2) & ~precomputed::bb_files[7] & ~precomputed::bb_files[6];
}

Bitboard chess::bb_shift_up_right(Bitboard bb)
{
    return (bb<<9) & ~precomputed::bb_files[0];
}

Bitboard chess::bb_shift_up_left(Bitboard bb)
{
    return (bb<<7) & ~precomputed::bb_files[7];
}

Bitboard chess::bb_shift_down_right(Bitboard bb)
{
    return (bb>>7) & ~precomputed::bb_files[7];
}

Bitboard chess::bb_shift_down_left(Bitboard bb)
{
    return (bb>>9) & ~precomputed::bb_files[0];
}

Bitboard chess::bb_shift(Bitboard bb, def::directions dir)
{
    using namespace precomputed;
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

    static constexpr std::array<Bitboard, 9> masks =
    {
        bb_full,
        bb_full,
        bb_files[0],
        bb_files[7],
        bb_files[0],
        bb_files[7],
        bb_files[0],
        bb_files[7],
        bb_full
    };

    return gen_shift(bb, shift_offsets[dir]) & masks[dir];
}

#undef rotl64
#undef rotr64
#undef gen_shift64

