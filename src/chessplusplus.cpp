#include <iostream>
#include <cassert>
#include <algorithm>
#include <numeric>
#include "chessplusplus/chessplusplus.h"
#include "internal/fen_utils.h"
#include "internal/other_utils.h"

using namespace chess;
using namespace chess::def;

/******************************************************************************
 * chess::Piece
 ******************************************************************************/

Piece::Piece(PieceType _piece_type, Color _color)
    : piece_type(_piece_type)
    , color(_color)
{  }

Piece Piece::empty_square()
{
    return Piece(def::no_piece, def::white);
}

bool Piece::operator==(const Piece &other) const
{
    return piece_type == other.piece_type && color == other.color;
}

bool Piece::operator!=(const Piece &other) const
{
    return piece_type != other.piece_type || color != other.color;
}


/******************************************************************************
 * chess::Move
 ******************************************************************************/

Move::Move(Square from, Square to)
    : from(from)
    , to(to)
{ }


/******************************************************************************
 * chess::Board
 ******************************************************************************/
Board::Board(const std::string &fen)
{
    if (fen.empty())
        clear();
    else if (fen == def::starting_fen)
        reset_board();
    else
        set_fen(fen);
}

void Board::reset_board()
{
    using namespace def;
    using namespace precomputed;

    bb_board[white][pawn] = bb_ranks[1];
    bb_board[white][knight] = bb_squares[B1] | bb_squares[G1];
    bb_board[white][bishop] = bb_squares[C1] | bb_squares[F1];
    bb_board[white][rook] = bb_squares[A1] | bb_squares[H1];
    bb_board[white][queen] = bb_squares[D1];
    bb_board[white][def::king] = bb_squares[E1];

    bb_board[black][pawn] = bb_ranks[6];
    bb_board[black][knight] = bb_squares[B8] | bb_squares[G8];
    bb_board[black][bishop] = bb_squares[C8] | bb_squares[F8];
    bb_board[black][rook] = bb_squares[A8] | bb_squares[H8];
    bb_board[black][queen] = bb_squares[D8];
    bb_board[black][def::king] = bb_squares[E8];
}

void Board::clear()
{
    bb_board[def::white] = {0,0,0,0,0,0,0};
    bb_board[def::black] = {0,0,0,0,0,0,0};
}

// *************
// fen related
// *************

void Board::set_board_fen(const std::string &_board_fen)
{
    const auto crows = utility::validate_and_split_board_fen(_board_fen);
    clear();
    bb_board = utility::parse_board_fen_from_rows(crows, _board_fen);
}

void Board::set_fen(const std::string &fen)
{
    std::istringstream split(fen);
    std::string position;
    std::string turn;
    std::string _castling_rights;
    std::string en_passant;
    std::string halfmove_clock;
    std::string fullmove_num;
    std::string rest;

    std::getline(split, position, ' ');
    std::getline(split, turn, ' '); // TODO
    std::getline(split, _castling_rights, ' ');
    std::getline(split, en_passant, ' '); // TODO
    std::getline(split, halfmove_clock, ' '); // TODO
    std::getline(split, fullmove_num, ' '); // TODO
    std::getline(split, rest, ' ');

    if (!rest.empty())
        throw std::invalid_argument("the fen contains more sections than expected: " + fen);

    set_board_fen(position);
    if (turn == "w")
        turn = def::white;
    else if (turn == "b")
        turn = def::black;
    else
        throw std::invalid_argument("the color section in the fen should contain either w or b: " + fen);

    if (_castling_rights == "-"
        || _castling_rights == "K" || _castling_rights == "Q" || _castling_rights == "KQ"
        || _castling_rights == "k" || castling_rights == "q" || castling_rights == "kq"
        || _castling_rights == "KQkq")
    {
        castling_rights = _castling_rights;
    }
    else throw std::invalid_argument("the castling rights part of the fen is invalid: " + fen);
}

std::string Board::board_fen()
{
    std::string board_fen;

    constexpr int max_fen_length = 90;
    board_fen.reserve(max_fen_length);

    // iterate over each line

    for (int file_i = 7; file_i >= 0; file_i--)
    {
        int empty_square_counter = 0;
        for (Square square = file_i<<3; square - (file_i<<3) < 8; square++)
        {
            Piece piece = piece_at(square);

            if (piece == Piece::empty_square())
            {
                empty_square_counter++;
                continue;
            }
            if (empty_square_counter != 0)
            {
                board_fen.push_back(empty_square_counter + '0');
                empty_square_counter = 0;
            }

            board_fen.push_back(piece_symbol_from_piece(piece.piece_type, piece.color));
        }
        if (empty_square_counter != 0)
            board_fen.push_back(empty_square_counter + '0');

        if (file_i != 0)
            board_fen.push_back('/');
    }

    return board_fen;
}

std::string Board::fen()
{
    // TODO
    std::string fen = board_fen();

    return fen;
}

// ************************************
// string representation of the board
// ************************************

std::string Board::board_str()
{
    std::string board;
    std::string b_fen = board_fen();

    std::istringstream split(b_fen);

    std::vector<std::string> rows;
    for (std::string row; std::getline(split, row, '/'); rows.push_back(row)) { }

    for (const auto &row : rows)
    {
        for (auto symbol : row)
        {
            if (std::isalpha(symbol))
                board += symbol;
            else if (std::isdigit(symbol))
                board.append(symbol - '0', '.');
        }
        board += '\n';
    }
    return board;
}

std::string Board::bitboard_str()
{
    Bitboard bb = 0;

    // accumulate over the white pieces
    bb = std::accumulate(bb_board[def::white].begin(), bb_board[def::white].end(), bb,
                              [](Bitboard acc, auto piece_bb) { return acc | piece_bb; });

    // accumulate over the black pieces
    bb = std::accumulate(bb_board[def::white].begin(), bb_board[def::black].end(), bb,
                         [](Bitboard acc, auto piece_bb) { return acc | piece_bb; });

    return utility::bitboard_to_string(bb);
}

// ****************************
// square related information
// ****************************

PieceType Board::piece_type_at(Square square)
{
    auto pred = [square](const auto piece_bb) {
        return piece_bb & precomputed::bb_squares[square];
    };

    const auto white_begin = bb_board[def::white].begin();
    const auto white_end = bb_board[def::white].end();
    const auto black_begin = bb_board[def::black].begin();
    const auto black_end = bb_board[def::black].end();

    if (auto it = std::find_if(white_begin, white_end, pred); it != white_end)
        return static_cast<PieceType>(std::distance(white_begin, it));

    if (auto it = std::find_if(black_begin, black_end, pred); it != black_end)
        return static_cast<PieceType>(std::distance(black_begin, it));

    return def::no_piece;
}

Piece Board::piece_at(Square square)
{
    PieceType piece_type = piece_type_at(square);

    if (bb_board[def::white][piece_type] & precomputed::bb_squares[square])
        return Piece(piece_type, def::white);
    else if (bb_board[def::black][piece_type] & precomputed::bb_squares[square])
        return Piece(piece_type, def::black);

    return Piece::empty_square();
}

Color Board::color_at(Square square)
{
    return bb_board[def::white][piece_type_at(square)] & precomputed::bb_squares[square];
}

bool Board::square_is_empty(Square square)
{
    return (piece_type_at(square) == def::no_piece);
}

Square Board::king(Color side)
{
    Bitboard bb_king = bb_board[side][def::king];
    Square square_i = 0;
    for (; bb_king != 1; bb_king >>= 2)
        square_i++;

    return square_i;
}

// *************
// castling
// *************

bool Board::can_castle_kingside(Color side)
{
    if (castling_rights.find(side ? "K" : "k") != std::string::npos)
    {
        if (side == def::white)
            return (piece_at(def::E1) == Piece(def::king, def::white)
                    && piece_at(def::H1) == Piece(def::rook, def::white)
                    && square_is_empty(def::G1) && square_is_empty(def::H1));
        else
            return (piece_at(def::E8) == Piece(def::king, def::black)
                    && piece_at(def::H8) == Piece(def::rook, def::black)
                    && square_is_empty(def::G8) && square_is_empty(def::H8));
    }

    return false;
}

bool Board::can_castle_queenside(Color side)
{
    if (castling_rights.find(side ? "Q" : "q") != std::string::npos)
    {
        if (side == def::white)
            return (piece_at(def::E1) == Piece(def::king, def::white)
                    && piece_at(def::A1) == Piece(def::rook, def::black)
                    && square_is_empty(def::B1)
                    && square_is_empty(def::C1)
                    && square_is_empty(def::D1));
        else
            return (piece_at(def::E8) == Piece(def::king, def::black)
                    && piece_at(def::A8) == Piece(def::rook, def::black)
                    && square_is_empty(def::B8)
                    && square_is_empty(def::C8)
                    && square_is_empty(def::D8));
    }

    return false;
}

void Board::move_piece(Square from, Square to)
{
    Piece piece_from = piece_at(from);
    Piece piece_to = piece_at(to);

    if (piece_from == Piece::empty_square())
        throw std::invalid_argument("square " + std::to_string(from) +
                                    " is empty, there is no piece to move.");

    bb_board[piece_from.color][piece_from.piece_type] &= ~precomputed::bb_squares[from];
    if (piece_to != Piece::empty_square())
        bb_board[piece_to.color][piece_to.piece_type] &= ~precomputed::bb_squares[to];

    bb_board[piece_from.color][piece_from.piece_type] |= precomputed::bb_squares[to];
}

Bitboard Board::pseudo_legal_moves_on_square(Square square, std::function<bool(Square)> callback)
{
    Piece piece = piece_at(square);
    return precomputed::bb_pseudolegal_moves[piece.color][piece.piece_type][square];
}

bool Board::move_is_pseudo_legal(Square from, Square to)
{
    return precomputed::bb_squares[to] & pseudo_legal_moves_on_square(from);
}

bool Board::is_attacking_square(Square from, Square to)
{
    // TODO

    // if (move_is_pseudo_legal(from, to))
    // {
    //     if (piece_type_at(from) == def::pawn)
    //         if (square_file(from) != square_file(to))
    //             return true;
    //     return true;
    // }

    // return false;
}

bool Board::is_capture(Square from, Square to)
{
    // TODO

    // if (is_attacking_square(from, to))
    //     if (piece_type_at(to) != def::no_piece && piece_type_at(to) != def::king)
    //         return true;

    // return false;
}

std::pair<bool, def::error_code> Board::move_is_legal(Square from, Square to)
{
    std::pair<bool, def::error_code> _true = {true, def::ok};

    auto code = [](def::error_code _code) { return std::pair<bool, def::error_code>(false, _code); };

    if (!move_is_pseudo_legal(from, to))
        return code(def::move_not_pseudo_legal);


    return _true;
}

void Board::make_move(Square from, Square to)
{
    // TODO
    // implement castling
    // implement en passant
    // check game state
    // display board correctly. implement mirroring.

    auto legal = move_is_legal(from, to);

    if (legal.first)
    {
        move_piece(from, to);
    }
    else switch(legal.second)
    {
    case def::move_not_pseudo_legal: throw std::invalid_argument("Move is not pseudolegal: ");
    case def::square_not_empty: throw std::invalid_argument("Destination square is not empty");
    case def::king_capture: throw std::invalid_argument("Move captures a king");
    case def::king_passing_through_check: throw std::invalid_argument("King passing throw check");
    case def::cant_castle: throw std::invalid_argument("Can't castle");
    case def::pawn_capturing_empty_square: throw std::invalid_argument("Pawn capturing empty square");
    case def::ok: break;
    }
}


