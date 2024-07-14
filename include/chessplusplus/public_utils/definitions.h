#ifndef DEF_H
#define DEF_H

#include <array>
#include <cstdint>

namespace chess
{
using Color = bool;
using PieceType = std::size_t;
using Square = uint8_t;
using Bitboard = uint64_t;

namespace def
{
enum directions : std::size_t
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
