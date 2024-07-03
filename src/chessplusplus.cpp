#include <iostream>
#include <cassert>
#include <algorithm>
#include <numeric>
#include "chessplusplus/chessplusplus.h"
#include "internal/chess_utils.h"
#include "internal/fen_utils.h"

using namespace chess;

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

    bb_board[white][pawn] = bb_ranks[1];
    bb_board[white][knight] = square_bb(B1) | square_bb(G1);
    bb_board[white][bishop] = square_bb(C1) | square_bb(F1);
    bb_board[white][rook] = square_bb(A1) | square_bb(H1);
    bb_board[white][queen] = square_bb(D1);
    bb_board[white][def::king] = square_bb(E1);

    bb_board[black][pawn] = bb_ranks[6];
    bb_board[black][knight] = square_bb(B8) | square_bb(G8);
    bb_board[black][bishop] = square_bb(C8) | square_bb(F8);
    bb_board[black][rook] = square_bb(A8) | square_bb(H8);
    bb_board[black][queen] = square_bb(D8);
    bb_board[black][def::king] = square_bb(E8);
}

void Board::clear()
{
    bb_board[def::white] = {0,0,0,0,0,0};
    bb_board[def::black] = {0,0,0,0,0,0};
}

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
    std::getline(split, turn, ' ');
    std::getline(split, _castling_rights, ' ');
    std::getline(split, en_passant, ' ');
    std::getline(split, halfmove_clock, ' ');
    std::getline(split, fullmove_num, ' ');
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
        {
            board_fen.push_back(empty_square_counter + '0');
            empty_square_counter = 0;
        }

        if (file_i != 0)
            board_fen.push_back('/');
    }

    return board_fen;
}

std::string Board::fen()
{
    std::string fen = board_fen();

    return fen;
}

std::string Board::board()
{
    std::string board;
    std::string b_fen = board_fen();

    std::istringstream split(b_fen);
    std::vector<std::string> rows;

    for (std::string row; std::getline(split, row, '/'); rows.push_back(row)) { }

    for (auto row_it = rows.begin(); row_it != rows.end(); row_it++)
    {
        for (auto symbol_it = row_it->begin(); symbol_it != row_it->end(); symbol_it++)
        {
            if (std::isalpha(*symbol_it))
                board.push_back(*symbol_it);
            else if (std::isdigit(*symbol_it))
            {
                board.append(std::string(*symbol_it - '0', '.'));
            }
        }
        board.push_back('\n');
    }
    return board;
}

std::string Board::bitboard_str()
{
    uint64_t bb = 0;

    // accumulate over the white pieces
    bb = std::accumulate(bb_board[def::white].begin(), bb_board[def::white].end(), bb,
                              [](uint64_t acc, auto piece_bb) { return acc | piece_bb; });

    // accumulate over the black pieces
    bb = std::accumulate(bb_board[def::white].begin(), bb_board[def::black].end(), bb,
                         [](uint64_t acc, auto piece_bb) { return acc | piece_bb; });

    return utility::bitboard_to_string(bb);
}

PieceType Board::piece_type_at(Square square)
{
    auto pred = [square](const auto piece_bb) {
        return piece_bb & square_bb(square);
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

    if (bb_board[def::white][piece_type] & square_bb(square))
        return Piece(piece_type, def::white);
    else if (bb_board[def::black][piece_type] & square_bb(square))
        return Piece(piece_type, def::black);

    return Piece::empty_square();
}

Color Board::color_at(Square square)
{
    return bb_board[def::white][piece_type_at(square)] & square_bb(square);
}

Square Board::king(Color side)
{
    uint64_t bb_king = bb_board[side][def::king];
    Square square_i = 0;
    for (; bb_king != 1; bb_king >>= 2)
        square_i++;

    return square_i;
}

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

bool Board::square_is_empty(Square square)
{
    return (piece_type_at(square) == def::no_piece);
}

void Board::move_piece(Square from, Square to)
{
    Piece piece_from = piece_at(from);
    Piece piece_to = piece_at(to);

    if (piece_from == Piece::empty_square())
        throw std::invalid_argument("square " + std::to_string(from) +
                                    " is empty, there is no piece to move.");

    bb_board[piece_from.color][piece_from.piece_type] &= ~square_bb(from);
    if (piece_to != Piece::empty_square())
        bb_board[piece_to.color][piece_to.piece_type] &= ~square_bb(to);

    bb_board[piece_from.color][piece_from.piece_type] |= square_bb(to);
}

uint64_t Board::pseudo_legal_moves_on_square(Square square, std::function<bool(Square)> callback)
{
    PieceType piece = piece_type_at(square);

    if (piece == def::no_piece)
        return 0;

    Color piece_color = piece_at(square).color;

    std::function<bool(Square)> condition = utility::conjunction(callback, is_valid_square);

    uint64_t knight_dirs = utility::combine_squares_if(condition,
                                                   shift_square(shift_square(square, def::up, 2), def::left),
                                                   shift_square(shift_square(square, def::up, 2), def::right),
                                                   shift_square(shift_square(square, def::down, 2), def::left),
                                                   shift_square(shift_square(square, def::down, 2), def::right),
                                                   shift_square(shift_square(square, def::left, 2), def::up),
                                                   shift_square(shift_square(square, def::left, 2), def::down),
                                                   shift_square(shift_square(square, def::right, 2), def::up),
                                                   shift_square(shift_square(square, def::right, 2), def::down));

    uint64_t rook_dirs = def::bb_ranks[square_rank(square)] | def::bb_files[square_file(square)];
    uint64_t bishop_dirs = chess::diagonals_at(square);

    switch(piece)
    {
    case def::pawn: {
        uint64_t pawn_dirs = utility::combine_squares_if(condition,
                                                     shift_square(square, def::up),
                                                     shift_square(square, def::up_left),
                                                     shift_square(square, def::up_right));

        if (square_rank(square) == 1 && square_rank(square) == 7)
            return pawn_dirs | square_bb(shift_square(square, def::up, 2));
        return pawn_dirs;
    }
    case def::knight:
        return knight_dirs;
    case def::bishop:
        return bishop_dirs;
    case def::rook:
        return rook_dirs;
    case def::queen:
        return knight_dirs | bishop_dirs | rook_dirs;
    case def::king:
    {
        uint64_t king_dirs = utility::combine_squares_if(condition,
                                                     shift_square(square, def::up),
                                                     shift_square(square, def::down),
                                                     shift_square(square, def::left),
                                                     shift_square(square, def::right));
        if (can_castle_kingside(color_at(square)))
            king_dirs |= shift_square(square, def::right, 2);
        if (can_castle_queenside(color_at(square)))
            king_dirs |= shift_square(square, def::left, 2);

        return king_dirs;
    }
    }

    return 0;
}

bool Board::move_is_pseudo_legal(Square from, Square to)
{
    return square_bb(to) & pseudo_legal_moves_on_square(from);
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

    if (king_under_check)
    {
        Board tmp = *this;
        tmp.move_piece(from, to);
        if (tmp.king_under_check)
            return code(def::king_passing_through_check);
    }
    else switch(piece_type_at(from))
    {
    case def::pawn: {
        if (square_rank(from) == square_rank(to))
        {
            if (square_file(to) - square_file(from) == 1)
                return square_is_empty(to) ? _true : code(def::square_not_empty);
            else return square_is_empty(to) &&
                        square_is_empty(shift_square(to, def::up)) ? _true : code(def::square_not_empty);
        }
        else if (is_capture(from, to))
            return _true;
        else if (piece_type_at(to) == def::no_piece)
            return code(def::pawn_capturing_empty_square);
    }
    case def::knight:
        return _true;
    case def::bishop: {
        def::directions x = def::null, y = def::null;

        x = (square_file(to) - square_file(from) > 0) ? def::right
                                                      : def::left;
        y = (square_rank(to) - square_rank(from) > 0) ? def::up
                                                      : def::down;

        def::directions dir = static_cast<def::directions>(4 + (x-2) + y);

        for (Square i = shift_square(from, dir); i != to; i = shift_square(i, dir))
        {
            if (!square_is_empty(i))
                return code(def::square_not_empty);
        }

        return _true;
    }
    case def::rook: {
        def::directions dir = def::null;

        if (square_file(to) - square_file(from) > 0)
            dir = def::right;
        else if (square_file(to) - square_file(from) < 0)
            dir = def::left;
        else if (square_rank(to) - square_rank(from) > 0)
            dir = def::up;
        else if (square_rank(to) - square_rank(from) < 0)
            dir = def::down;

        for (Square i = shift_square(from, dir); i != to; i = shift_square(i, dir))
        {
            if (!square_is_empty(i))
                return code(def::square_not_empty);
        }

        return _true;
    }
    case def::queen: {
        def::directions x = def::null, y = def::null;

        x = (square_file(to) - square_file(from) >= 0) ? def::right
                                                      : def::left;
        y = (square_rank(to) - square_rank(from) >= 0) ? def::up
                                                      : def::down;

        def::directions dir = static_cast<def::directions>(4 + (x-2) + y);

        for (Square i = shift_square(from, dir); i != to; i = shift_square(i, dir))
        {
            if (!square_is_empty(i))
                return code(def::square_not_empty);
        }

        return _true;
    }
    case def::king: {
        Board tmp = *this;
        tmp.move_piece(from, to);

        if (!tmp.king_under_check)
        {
            int diff_x = abs(square_file(to) - square_file(from));
            int diff_y = abs(square_rank(to) - square_rank(from));

            if (diff_x <= 1 && diff_y <= 1)
                return _true;
            else if (can_castle_kingside(color_at(from)) || can_castle_queenside(from))
            {
                return _true;
            }
            else return code(def::cant_castle);
        }
        else return code(def::king_passing_through_check);
    }
    }

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


