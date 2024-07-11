#ifndef DEF_H
#define DEF_H

#include <array>
#include <map>
#include <cstdint>

namespace chess
{
using Color = bool;
using PieceType = int;
using Square = std::size_t;
using Bitboard = uint64_t;

namespace def
{
enum directions
{
    up,
    down,
    right,
    left,
    up_right,
    up_left,
    down_right,
    down_left,
    null
};

constexpr Color white = true;
constexpr Color black = false;

constexpr std::array<char, 8> file_names = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
constexpr std::array<int, 8> rank_names = {'1', '2', '3', '4', '5', '6', '7', '8'};

enum piece_types: PieceType
{
    pawn,
    knight,
    bishop,
    rook,
    queen,
    king,
    no_piece
};

constexpr std::array<char, 7> piece_symbols = {'p', 'n', 'b', 'r', 'q', 'k', '\0'};
constexpr std::array<const char*, 7> piece_names = {"pawn", "knight", "bishop", "rook", "queen", "king", ""};

constexpr const char* starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
constexpr const char* starting_board_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";

enum squares: Square
{
    A1, B1, C1, D1, E1, F1, G1, H1,
    A2, B2, C2, D2, E2, F2, G2, H2,
    A3, B3, C3, D3, E3, F3, G3, H3,
    A4, B4, C4, D4, E4, F4, G4, H4,
    A5, B5, C5, D5, E5, F5, G5, H5,
    A6, B6, C6, D6, E6, F6, G6, H6,
    A7, B7, C7, D7, E7, F7, G7, H7,
    A8, B8, C8, D8, E8, F8, G8, H8=63
};

constexpr std::array<Bitboard, 64> bb_squares =
{
    Bitboard(1) << A1,
    Bitboard(1) << A2,
    Bitboard(1) << A3,
    Bitboard(1) << A4,
    Bitboard(1) << A5,
    Bitboard(1) << A6,
    Bitboard(1) << A7,
    Bitboard(1) << A8,

    Bitboard(1) << B1,
    Bitboard(1) << B2,
    Bitboard(1) << B3,
    Bitboard(1) << B4,
    Bitboard(1) << B5,
    Bitboard(1) << B6,
    Bitboard(1) << B7,
    Bitboard(1) << B8,

    Bitboard(1) << C1,
    Bitboard(1) << C2,
    Bitboard(1) << C3,
    Bitboard(1) << C4,
    Bitboard(1) << C5,
    Bitboard(1) << C6,
    Bitboard(1) << C7,
    Bitboard(1) << C8,

    Bitboard(1) << D1,
    Bitboard(1) << D2,
    Bitboard(1) << D3,
    Bitboard(1) << D4,
    Bitboard(1) << D5,
    Bitboard(1) << D6,
    Bitboard(1) << D7,
    Bitboard(1) << D8,

    Bitboard(1) << E1,
    Bitboard(1) << E2,
    Bitboard(1) << E3,
    Bitboard(1) << E4,
    Bitboard(1) << E5,
    Bitboard(1) << E6,
    Bitboard(1) << E7,
    Bitboard(1) << E8,

    Bitboard(1) << F1,
    Bitboard(1) << F2,
    Bitboard(1) << F3,
    Bitboard(1) << F4,
    Bitboard(1) << F5,
    Bitboard(1) << F6,
    Bitboard(1) << F7,
    Bitboard(1) << F8,

    Bitboard(1) << G1,
    Bitboard(1) << G2,
    Bitboard(1) << G3,
    Bitboard(1) << G4,
    Bitboard(1) << G5,
    Bitboard(1) << G6,
    Bitboard(1) << G7,
    Bitboard(1) << G8,

    Bitboard(1) << H1,
    Bitboard(1) << H2,
    Bitboard(1) << H3,
    Bitboard(1) << H4,
    Bitboard(1) << H5,
    Bitboard(1) << H6,
    Bitboard(1) << H7,
    Bitboard(1) << H8
};

constexpr Bitboard bb_empty = 0;
constexpr Bitboard bb_full = 0xffffffffffffffff;

constexpr std::array<const char*, 64> square_names =
{
    "A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1",
    "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
    "A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3",
    "A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4",
    "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",
    "A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6",
    "A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7",
    "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8"
};

constexpr std::array<Bitboard, 8> bb_files =
{
    0x101010101010101,
    0x202020202020202,
    0x404040404040404,
    0x808080808080808,
    0x1010101010101010,
    0x2020202020202020,
    0x4040404040404040,
    0x8080808080808080
};

constexpr std::array<Bitboard, 8> bb_ranks =
{
    0x00000000000000ff,
    0x000000000000ff00,
    0x0000000000ff0000,
    0x00000000ff000000,
    0x000000ff00000000,
    0x0000ff0000000000,
    0x00ff000000000000,
    0xff00000000000000
};

// diagonals with default 7+rank-file numbering
constexpr std::array<Bitboard, 15> bb_diagonals =
{
    0x80,
    0x8040,
    0x804020,
    0x80402010,
    0x8040201008,
    0x804020100804,
    0x80402010080402,
    0x8040201008040201,
    0x4020100804020100,
    0x2010080402010000,
    0x1008040201000000,
    0x804020100000000,
    0x402010000000000,
    0x201000000000000,
    0x100000000000000
};

// diagonals with alternative (rank-file)&15 numbering
constexpr std::array<Bitboard, 16> bb_diagonals_alt =
{
    0x80,
    0x4020100804020100,
    0x2010080402010000,
    0x1008040201000000,
    0x804020100000000,
    0x402010000000000,
    0x201000000000000,
    0x100000000000000,
    0x0, // 8 is a nexus thus it's skipped
    0x80,
    0x8040,
    0x804020,
    0x80402010,
    0x8040201008,
    0x804020100804,
    0x80402010080402
};

// antidiagonals with default rank+file ordering
constexpr std::array<Bitboard, 15> bb_antidiagonals =
{
    0x1,
    0x102,
    0x10204,
    0x1020408,
    0x102040810,
    0x10204081020,
    0x1020408102040,
    0x102040810204080,
    0x204081020408000,
    0x408102040800000,
    0x810204080000000,
    0x1020408000000000,
    0x2040800000000000,
    0x4080000000000000,
    0x8000000000000000
};

// antidiagonals with alternative (rank+file)^7 numbering
constexpr std::array<Bitboard, 16> bb_antidiagonals_alt =
{
    0x102040810204080,
    0x1020408102040,
    0x10204081020,
    0x102040810,
    0x1020408,
    0x10204,
    0x102,
    0x1,
    0x0, // 8 is a nexus number
    0x8000000000000000,
    0x4080000000000000,
    0x2040800000000000,
    0x1020408000000000,
    0x810204080000000,
    0x408102040800000,
    0x204081020408000
};

constexpr std::array<Bitboard, 64> bb_white_pawn_pseudolegal_moves =
{
    0x300,
    0x700,
    0xe00,
    0x1c00,
    0x3800,
    0x7000,
    0xe000,
    0xc000,

    0x1030000,
    0x2070000,
    0x40e0000,
    0x81c0000,
    0x10380000,
    0x20700000,
    0x40e00000,
    0x80c00000,

    0x3000000,
    0x7000000,
    0xe000000,
    0x1c000000,
    0x38000000,
    0x70000000,
    0xe0000000,
    0xc0000000,

    0x300000000,
    0x700000000,
    0xe00000000,
    0x1c00000000,
    0x3800000000,
    0x7000000000,
    0xe000000000,
    0xc000000000,

    0x30000000000,
    0x70000000000,
    0xe0000000000,
    0x1c0000000000,
    0x380000000000,
    0x700000000000,
    0xe00000000000,
    0xc00000000000,

    0x3000000000000,
    0x7000000000000,
    0xe000000000000,
    0x1c000000000000,
    0x38000000000000,
    0x70000000000000,
    0xe0000000000000,
    0xc0000000000000,

    0x300000000000000,
    0x700000000000000,
    0xe00000000000000,
    0x1c00000000000000,
    0x3800000000000000,
    0x7000000000000000,
    0xe000000000000000,
    0xc000000000000000,

    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0
};

constexpr std::array<Bitboard, 64> bb_black_pawn_pseudolegal_moves =
{
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,
    0x0,

    0x3,
    0x7,
    0xe,
    0x1c,
    0x38,
    0x70,
    0xe0,
    0xc0,

    0x300,
    0x700,
    0xe00,
    0x1c00,
    0x3800,
    0x7000,
    0xe000,
    0xc000,

    0x30000,
    0x70000,
    0xe0000,
    0x1c0000,
    0x380000,
    0x700000,
    0xe00000,
    0xc00000,

    0x3000000,
    0x7000000,
    0xe000000,
    0x1c000000,
    0x38000000,
    0x70000000,
    0xe0000000,
    0xc0000000,

    0x300000000,
    0x700000000,
    0xe00000000,
    0x1c00000000,
    0x3800000000,
    0x7000000000,
    0xe000000000,
    0xc000000000,

    0x30100000000,
    0x70200000000,
    0xe0400000000,
    0x1c0800000000,
    0x381000000000,
    0x702000000000,
    0xe04000000000,
    0xc08000000000,

    0x3000000000000,
    0x7000000000000,
    0xe000000000000,
    0x1c000000000000,
    0x38000000000000,
    0x70000000000000,
    0xe0000000000000,
    0xc0000000000000
};

constexpr std::array<Bitboard, 64> bb_knight_pseudolegal_moves =
{
    0x442800000028440,
    0x885000000050880,
    0x110a0000000a1100,
    0x2214000000142200,
    0x4428000000284400,
    0x8850000000508800,
    0x10a0000000a11001,
    0x2140000001422002,

    0x4280000002844004,
    0x8500000005088008,
    0xa0000000a110011,
    0x1400000014220022,
    0x2800000028440044,
    0x5000000050880088,
    0xa0000000a1100110,
    0x4000000142200221,

    0x8000000284400442,
    0x508800885,
    0xa1100110a,
    0x1422002214,
    0x2844004428,
    0x5088008850,
    0xa1100110a0,
    0x14220022140,

    0x28440044280,
    0x50880088500,
    0xa1100110a00,
    0x142200221400,
    0x284400442800,
    0x508800885000,
    0xa1100110a000,
    0x1422002214000,

    0x2844004428000,
    0x5088008850000,
    0xa1100110a0000,
    0x14220022140000,
    0x28440044280000,
    0x50880088500000,
    0xa1100110a00000,
    0x142200221400000,

    0x284400442800000,
    0x508800885000000,
    0xa1100110a000000,
    0x1422002214000000,
    0x2844004428000000,
    0x5088008850000000,
    0xa1100110a0000000,
    0x4220022140000001,

    0x8440044280000002,
    0x880088500000005,
    0x1100110a0000000a,
    0x2200221400000014,
    0x4400442800000028,
    0x8800885000000050,
    0x100110a0000000a1,
    0x2002214000000142,

    0x4004428000000284,
    0x8008850000000508,
    0x110a0000000a11,
    0x22140000001422,
    0x44280000002844,
    0x88500000005088,
    0x110a0000000a110,
    0x221400000014220
};

constexpr std::array<Bitboard, 64> bb_bishop_pseudolegal_moves =
{
    0x8040201008040201,
    0x80402010080502,
    0x804020110a04,
    0x8041221408,
    0x182442810,
    0x10204885020,
    0x102040810a040,
    0x102040810204080,

    0x4020100804020102,
    0x8040201008050205,
    0x804020110a040a,
    0x804122140814,
    0x18244281028,
    0x1020488502050,
    0x102040810a040a0,
    0x204081020408040,

    0x2010080402010204,
    0x4020100805020508,
    0x804020110a040a11,
    0x80412214081422,
    0x1824428102844,
    0x102048850205088,
    0x2040810a040a010,
    0x408102040804020,

    0x1008040201020408,
    0x2010080502050810,
    0x4020110a040a1120,
    0x8041221408142241,
    0x182442810284482,
    0x204885020508804,
    0x40810a040a01008,
    0x810204080402010,

    0x804020102040810,
    0x1008050205081020,
    0x20110a040a112040,
    0x4122140814224180,
    0x8244281028448201,
    0x488502050880402,
    0x810a040a0100804,
    0x1020408040201008,

    0x402010204081020,
    0x805020508102040,
    0x110a040a11204080,
    0x2214081422418000,
    0x4428102844820100,
    0x8850205088040201,
    0x10a040a010080402,
    0x2040804020100804,

    0x201020408102040,
    0x502050810204080,
    0xa040a1120408000,
    0x1408142241800000,
    0x2810284482010000,
    0x5020508804020100,
    0xa040a01008040201,
    0x4080402010080402,

    0x102040810204080,
    0x205081020408000,
    0x40a112040800000,
    0x814224180000000,
    0x1028448201000000,
    0x2050880402010000,
    0x40a0100804020100,
    0x8040201008040201
};

constexpr std::array<Bitboard, 64> bb_rook_pseudolegal_moves =
{
    0x1010101010101ff,
    0x2020202020202ff,
    0x4040404040404ff,
    0x8080808080808ff,
    0x10101010101010ff,
    0x20202020202020ff,
    0x40404040404040ff,
    0x80808080808080ff,

    0x10101010101ff01,
    0x20202020202ff02,
    0x40404040404ff04,
    0x80808080808ff08,
    0x101010101010ff10,
    0x202020202020ff20,
    0x404040404040ff40,
    0x808080808080ff80,

    0x101010101ff0101,
    0x202020202ff0202,
    0x404040404ff0404,
    0x808080808ff0808,
    0x1010101010ff1010,
    0x2020202020ff2020,
    0x4040404040ff4040,
    0x8080808080ff8080,

    0x1010101ff010101,
    0x2020202ff020202,
    0x4040404ff040404,
    0x8080808ff080808,
    0x10101010ff101010,
    0x20202020ff202020,
    0x40404040ff404040,
    0x80808080ff808080,

    0x10101ff01010101,
    0x20202ff02020202,
    0x40404ff04040404,
    0x80808ff08080808,
    0x101010ff10101010,
    0x202020ff20202020,
    0x404040ff40404040,
    0x808080ff80808080,

    0x101ff0101010101,
    0x202ff0202020202,
    0x404ff0404040404,
    0x808ff0808080808,
    0x1010ff1010101010,
    0x2020ff2020202020,
    0x4040ff4040404040,
    0x8080ff8080808080,

    0x1ff010101010101,
    0x2ff020202020202,
    0x4ff040404040404,
    0x8ff080808080808,
    0x10ff101010101010,
    0x20ff202020202020,
    0x40ff404040404040,
    0x80ff808080808080,

    0xff01010101010101,
    0xff02020202020202,
    0xff04040404040404,
    0xff08080808080808,
    0xff10101010101010,
    0xff20202020202020,
    0xff40404040404040,
    0xff80808080808080
};

constexpr std::array<Bitboard, 64> bb_queen_pseudolegal_moves =
{
    0x81412111090503ff,
    0x2824222120a07ff,
    0x404844424150eff,
    0x8080888492a1cff,
    0x10101011925438ff,
    0x2020212224a870ff,
    0x404142444850e0ff,
    0x8182848890a0c0ff,

    0x412111090503ff03,
    0x824222120a07ff07,
    0x4844424150eff0e,
    0x80888492a1cff1c,
    0x101011925438ff38,
    0x20212224a870ff70,
    0x4142444850e0ffe0,
    0x82848890a0c0ffc0,

    0x2111090503ff0305,
    0x4222120a07ff070a,
    0x844424150eff0e15,
    0x888492a1cff1c2a,
    0x1011925438ff3854,
    0x212224a870ff70a8,
    0x42444850e0ffe050,
    0x848890a0c0ffc0a0,

    0x11090503ff030509,
    0x22120a07ff070a12,
    0x4424150eff0e1524,
    0x88492a1cff1c2a49,
    0x11925438ff385492,
    0x2224a870ff70a824,
    0x444850e0ffe05048,
    0x8890a0c0ffc0a090,

    0x90503ff03050911,
    0x120a07ff070a1222,
    0x24150eff0e152444,
    0x492a1cff1c2a4988,
    0x925438ff38549211,
    0x24a870ff70a82422,
    0x4850e0ffe0504844,
    0x90a0c0ffc0a09088,

    0x503ff0305091121,
    0xa07ff070a122242,
    0x150eff0e15244484,
    0x2a1cff1c2a498808,
    0x5438ff3854921110,
    0xa870ff70a8242221,
    0x50e0ffe050484442,
    0xa0c0ffc0a0908884,

    0x3ff030509112141,
    0x7ff070a12224282,
    0xeff0e1524448404,
    0x1cff1c2a49880808,
    0x38ff385492111010,
    0x70ff70a824222120,
    0xe0ffe05048444241,
    0xc0ffc0a090888482,

    0xff03050911214181,
    0xff070a1222428202,
    0xff0e152444840404,
    0xff1c2a4988080808,
    0xff38549211101010,
    0xff70a82422212020,
    0xffe0504844424140,
    0xffc0a09088848281
};

constexpr std::array<Bitboard, 64> bb_white_king_pseudolegal_moves =
{
    0x302,
    0x705,
    0xe0a,
    0x1c14,
    0x386c,
    0x7050,
    0xe0a0,
    0xc040,

    0x30203,
    0x70507,
    0xe0a0e,
    0x1c141c,
    0x382838,
    0x705070,
    0xe0a0e0,
    0xc040c0,

    0x3020300,
    0x7050700,
    0xe0a0e00,
    0x1c141c00,
    0x38283800,
    0x70507000,
    0xe0a0e000,
    0xc040c000,

    0x302030000,
    0x705070000,
    0xe0a0e0000,
    0x1c141c0000,
    0x3828380000,
    0x7050700000,
    0xe0a0e00000,
    0xc040c00000,

    0x30203000000,
    0x70507000000,
    0xe0a0e000000,
    0x1c141c000000,
    0x382838000000,
    0x705070000000,
    0xe0a0e0000000,
    0xc040c0000000,

    0x3020300000000,
    0x7050700000000,
    0xe0a0e00000000,
    0x1c141c00000000,
    0x38283800000000,
    0x70507000000000,
    0xe0a0e000000000,
    0xc040c000000000,

    0x302030000000000,
    0x705070000000000,
    0xe0a0e0000000000,
    0x1c141c0000000000,
    0x3828380000000000,
    0x7050700000000000,
    0xe0a0e00000000000,
    0xc040c00000000000,

    0x203000000000000,
    0x507000000000000,
    0xa0e000000000000,
    0x141c000000000000,
    0x2838000000000000,
    0x5070000000000000,
    0xa0e0000000000000,
    0x40c0000000000000
};

constexpr std::array<Bitboard, 64> bb_black_king_pseudolegal_moves =
{
    0x302,
    0x705,
    0xe0a,
    0x1c14,
    0x3828,
    0x7050,
    0xe0a0,
    0xc040,

    0x30203,
    0x70507,
    0xe0a0e,
    0x1c141c,
    0x382838,
    0x705070,
    0xe0a0e0,
    0xc040c0,

    0x3020300,
    0x7050700,
    0xe0a0e00,
    0x1c141c00,
    0x38283800,
    0x70507000,
    0xe0a0e000,
    0xc040c000,

    0x302030000,
    0x705070000,
    0xe0a0e0000,
    0x1c141c0000,
    0x3828380000,
    0x7050700000,
    0xe0a0e00000,
    0xc040c00000,

    0x30203000000,
    0x70507000000,
    0xe0a0e000000,
    0x1c141c000000,
    0x382838000000,
    0x705070000000,
    0xe0a0e0000000,
    0xc040c0000000,

    0x3020300000000,
    0x7050700000000,
    0xe0a0e00000000,
    0x1c141c00000000,
    0x38283800000000,
    0x70507000000000,
    0xe0a0e000000000,
    0xc040c000000000,

    0x302030000000000,
    0x705070000000000,
    0xe0a0e0000000000,
    0x1c141c0000000000,
    0x3828380000000000,
    0x7050700000000000,
    0xe0a0e00000000000,
    0xc040c00000000000,

    0x203000000000000,
    0x507000000000000,
    0xa0e000000000000,
    0x141c000000000000,
    0x6c38000000000000,
    0x5070000000000000,
    0xa0e0000000000000,
    0x40c0000000000000
};

constexpr std::array<std::array<Bitboard, 64>, 7> bb_white_pseudolegal_moves =
{
    bb_white_pawn_pseudolegal_moves,
    bb_knight_pseudolegal_moves,
    bb_bishop_pseudolegal_moves,
    bb_rook_pseudolegal_moves,
    bb_queen_pseudolegal_moves,
    bb_white_king_pseudolegal_moves,
    0x0
};

constexpr std::array<std::array<Bitboard, 64>, 7> bb_black_pseudolegal_moves =
{
    bb_black_pawn_pseudolegal_moves,
    bb_knight_pseudolegal_moves,
    bb_bishop_pseudolegal_moves,
    bb_rook_pseudolegal_moves,
    bb_queen_pseudolegal_moves,
    bb_black_king_pseudolegal_moves,
    0x0
};

constexpr std::array<std::array<std::array<Bitboard, 64>, 7>,2> bb_pseudolegal_moves =
{
    bb_black_pseudolegal_moves,
    bb_white_pseudolegal_moves
};

// constexpr std::array<Bitboard,
enum error_code
{
    ok = 0,
    move_not_pseudo_legal,
    square_not_empty,
    king_capture,
    king_passing_through_check,
    cant_castle,
    pawn_capturing_empty_square
};

} // namespace def
}
#endif // DEF_H
