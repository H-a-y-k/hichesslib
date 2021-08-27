#ifndef CHESSPLUSPLUS_H
#define CHESSPLUSPLUS_H

#include "chessplusplus_global.h"
#include <array>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <exception>


namespace chess
{
using Color = bool;
using PieceType = int;
using Square = int;

struct Piece
{
    PieceType piece_type;
    Color color;

    Piece(PieceType _piece_type, Color _color);
    static Piece empty_square();
    
    bool operator== (const Piece &other) const;
};

uint64_t square_bb(Square square);

Square square_at(int rank, int file);

namespace def
{
constexpr Color white = true;
constexpr Color black = false;

std::array<char, 8> file_names = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
std::array<int, 8> rank_names = {'1', '2', '3', '4', '5', '6', '7', '8'};

enum piece_types: PieceType
{
    no_piece = -1,
    pawn,
    knight,
    bishop,
    rook,
    queen,
    king
};

constexpr std::array<char, 6> piece_symbols = {'p', 'n', 'b', 'r', 'q', 'k'};
constexpr std::array<const char*, 6> piece_names = {"pawn", "knight", "bishop", "rook", "queen", "knight"};

char piece_symbol(PieceType t);
const char* piece_name(PieceType t);

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

constexpr std::array<uint64_t, 8> bb_ranks =
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

constexpr uint64_t bb_empty = 0;
constexpr uint64_t bb_full = 0xffffffffffffffff;
}

class Board
{
    std::array<std::array<uint64_t, 6>, 2> bb_board {};

public:
    Board(const std::string &fen = def::starting_board_fen);

    void reset_board();
    void clear();
    void set_board_fen(const std::string &board_fen);
    PieceType piece_type_at(Square square);
    Piece piece_at(Square square);
    bool square_is_empty(Square square);
    void move_piece(Square from, Square to);
    void make_move(Square from, Square to);
};

// TODO
// create move system
}

#endif // CHESSPLUSPLUS_H
