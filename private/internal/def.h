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

constexpr uint64_t bb_empty = 0;
constexpr uint64_t bb_full = 0xffffffffffffffff;

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

constexpr std::array<uint64_t, 8> bb_files =
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

constexpr std::array<uint64_t, 8> bb_ranks =
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
constexpr std::array<uint64_t, 15> bb_diagonals =
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
constexpr std::array<uint64_t, 16> bb_diagonals_alt =
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
constexpr std::array<uint64_t, 15> bb_antidiagonals =
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
constexpr std::array<uint64_t, 16> bb_antidiagonals_alt =
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

// constexpr std::array<uint64_t,
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
