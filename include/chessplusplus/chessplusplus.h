#ifndef CHESSPLUSPLUS_H
#define CHESSPLUSPLUS_H

#include <array>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <exception>
#include <functional>
#include <utility>
#include <cstdint>
#include "public_utils/definitions.h"
#include "public_utils/precomputed.h"
#include "public_utils/bitboard_utils.h"
#include "public_utils/piece_utils.h"
#include "public_utils/square_utils.h"

namespace chess
{
struct Piece
{
    PieceType piece_type;
    Color color;

    Piece(PieceType _piece_type, Color _color);
    [[nodiscard]]
    static Piece empty_square();

    [[nodiscard]]
    bool operator== (const Piece &other) const;
    [[nodiscard]]
    bool operator!= (const Piece &other) const;
};

struct Move
{
    Square from, to;

    Move(Square from, Square to);
};

class Board
{
    std::array<std::array<Bitboard, 7>, 2> bb_board {{{0,0,0,0,0,0,0},{0,0,0,0,0,0,0}}};
    bool king_under_check = false;
    std::string castling_rights = "KQkq";
public:

//public:
    Board(const std::string &fen = def::starting_fen);

    Board operator=(const Board&);

    // board state
    void reset_board();
    void clear();
    void set_board_fen(const std::string &board_fen);
    void set_fen(const std::string &fen);

    [[nodiscard]]
    std::string board_fen();
    [[nodiscard]]
    std::string fen();

    // board string representation
    [[nodiscard]]
    std::string board_str();
    [[nodiscard]]
    std::string bitboard_str();

    // square related
    [[nodiscard]]
    PieceType piece_type_at(Square square);
    [[nodiscard]]
    Piece piece_at(Square square);
    [[nodiscard]]
    Color color_at(Square square);
    [[nodiscard]]
    Square king(Color side);
    [[nodiscard]]
    bool square_is_empty(Square square);

    // castling
    [[nodiscard]]
    bool can_castle_kingside(Color side);
    [[nodiscard]]
    bool can_castle_queenside(Color side);

    // board manipulation
    [[nodiscard]]
    Board mirror();
    void move_piece(Square from, Square to);

    [[nodiscard]]
    Bitboard pseudo_legal_moves_on_square(Square square,
                                          std::function<bool(Square)> = [](Square) { return true; });
    [[nodiscard]]
    bool move_is_pseudo_legal(Square from, Square to);
    [[nodiscard]]
    bool is_attacking_square(Square from, Square to);
    [[nodiscard]]
    bool is_capture(Square from, Square to);
    [[nodiscard]]
    std::pair<bool, def::error_code> move_is_legal(Square from, Square to);
    void make_move(Square from, Square to);
};

// TODO
// create move system
}

#endif // CHESSPLUSPLUS_H
