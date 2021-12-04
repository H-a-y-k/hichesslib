#include "chessplusplus/chessplusplus.h"
#include <iostream>

using namespace chess;

namespace
{
namespace pvt
{
bool is_valid_square(Square square)
{
    return 0 <= square && square <= 63;
}

uint64_t combine_squares_impl(Square val)
{
    return square_bb(val);
}

template <typename... Squares>
uint64_t combine_squares(Squares... squares)
{
    uint64_t result = 0;

    auto a = {(result |= combine_squares_impl(squares))...}; // throwaway object

    return result;
}

uint64_t combine_squares_if_impl(const std::function<bool(Square)> &callback, Square val)
{
    uint64_t result = 0;

    if (callback(val))
        result |= square_bb(val);

    return result;
}

template <typename... Squares>
uint64_t combine_squares_if(const std::function<bool(Square)> &callback, Squares... squares)
{
    uint64_t result = 0;

    auto _ = {(result |= combine_squares_if_impl(callback, squares))...}; // throwaway object
    (void)_;

    return result;
}

std::function<bool(Square)> conjunction(const std::function<bool(Square)> &f1, const std::function<bool(Square)> &f2)
{
    return [f1, f2](Square sq) { return f1(sq) && f2(sq); };
}

}
}


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


uint64_t chess::square_bb(Square square)
{
    return uint64_t(1) << square;
}

Square chess::square_at(int rank, int file)
{
    return rank * 8 + file;
}

Square chess::shift_square(Square square, def::directions direction, int step)
{
    // avoid changing rank/file. in this way you can loop easier

    switch(direction)
    {
    case def::up:
        return square + step * 8;
    case def::down:
        return square - step * 8;
    case def::right:
        return square + step;
    case def::left:
        return square - step;
    case def::up_right:
        return square + step + step * 8;
    case def::up_left:
        return square - step + step * 8;
    case def::down_right:
        return square + step - step * 8;
    case def::down_left:
        return square - step - step * 8;
    case def::null: break;
    }

    return square;
}

int chess::square_rank(Square square)
{
    return square / 8;
}

int chess::square_file(Square square)
{
    return square % 8;
}

uint64_t chess::diagonals_at(Square square)
{
    uint64_t result = 0;

    for (Square i = square; pvt::is_valid_square(i); i = shift_square(square, def::up_left))
        result |= i;

    for (Square i = square; pvt::is_valid_square(i); i = shift_square(square, def::up_right))
        result |= i;

    for (Square i = square; pvt::is_valid_square(i); i = shift_square(square, def::down_left))
        result |= i;

    for (Square i = square; pvt::is_valid_square(i); i = shift_square(square, def::down_right))
        result |= i;

    return result;
}

// defaults

char def::piece_symbol(PieceType type)
{
    return def::piece_symbols[type];
}

const char* def::piece_name(PieceType type)
{
    return def::piece_names[type];
}


Move::Move(Square from, Square to)
    : from(from)
    , to(to)
{ }


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
    if (_board_fen.empty())
        throw std::invalid_argument("fen is empty");

    if (_board_fen.find(' ') != std::string::npos)
        throw std::invalid_argument(std::string("expected position part, got multiple parts: ") + _board_fen);

    std::istringstream split(_board_fen);
    std::vector<std::string> rows;

    for (std::string row; std::getline(split, row, '/'); rows.push_back(row)) { }

    if (rows.empty())
        throw std::invalid_argument("rows aren't separated with slashes('/') in the fen: " + _board_fen);
    else if (rows.size() != 8)
        throw std::invalid_argument("the fen has to contain 8 rows and not" + std::to_string(rows.size()) + ": " + _board_fen);

    clear();

    std::array<std::array<uint64_t, 6>, 2> tmp_bb_board {{{0,0,0,0,0,0},{0,0,0,0,0,0}}};

    const auto crows = rows;

    for (auto row_it = crows.crbegin(); row_it != crows.crend(); row_it++)
    {
        if (row_it->empty())
            throw std::invalid_argument("rows in fen cannot be empty: " + _board_fen);

        int empty_cells = 0;
        int occupied_cells = 0;

        for (auto symbol_it = row_it->cbegin(); symbol_it != row_it->cend(); symbol_it++)
        {
            bool previous_was_digit = false;

            if (isdigit(*symbol_it))
            {
                empty_cells += *symbol_it - '0';

                if (previous_was_digit)
                    throw std::invalid_argument("a row in the fen shouldn't contain two digits next to each other: " + _board_fen);

                previous_was_digit = true;
            }
            else
            {
                auto found = std::find(def::piece_symbols.begin(), def::piece_symbols.end(),
                                       std::tolower(*symbol_it));
                if (found != def::piece_symbols.end())
                {
                    int rank = std::abs(std::distance(row_it, rows.crbegin()))-1;
                    int file = std::abs(std::distance(symbol_it, row_it->cbegin()));

                    if (previous_was_digit)
                        file += *(symbol_it-1) - '0';

                    Color color = std::islower(*symbol_it);
                    PieceType piece = static_cast<PieceType>(found - def::piece_symbols.cbegin());
                    tmp_bb_board[color][piece] |= square_bb(square_at(rank, file));
//                    std::cout << "(" << rank << ", " << file << ") ";
                    previous_was_digit = false;
                    occupied_cells++;
                }
                else throw std::invalid_argument("invalid character(s)('" +
                                                 std::string(1, *symbol_it) +
                                                 "') in the fen: " + _board_fen);
            }
        }

        if (empty_cells + occupied_cells != 8)
            throw std::invalid_argument("a fen row has to occupy exactly 8 cells: " + _board_fen);
    }

    bb_board = tmp_bb_board;
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

PieceType Board::piece_type_at(Square square)
{
    for (auto piece_bb = bb_board[def::white].begin(); piece_bb != bb_board[def::white].end(); piece_bb++)
    {
        if (*piece_bb & square_bb(square))
            return std::abs(std::distance(piece_bb, bb_board[def::white].begin()));
    }
    for (auto piece_bb = bb_board[def::black].begin(); piece_bb != bb_board[def::black].end(); piece_bb++)
    {
        if (*piece_bb & square_bb(square))
            return std::abs(std::distance(piece_bb, bb_board[def::black].begin()));
    }

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
            return (piece_type_at(def::E1) == def::king
                    && piece_type_at(def::H1) == def::rook
                    && square_is_empty(def::G1) && square_is_empty(def::H1));
        else
            return (piece_type_at(def::E8) == def::king
                    && piece_type_at(def::H8) == def::rook
                    && square_is_empty(def::G8) && square_is_empty(def::H8));
    }

    return false;
}

bool Board::can_castle_queenside(Color side)
{
    if (castling_rights.find(side ? "Q" : "q") != std::string::npos)
    {
        if (side == def::white)
            return (piece_type_at(def::E1) == def::king
                    && piece_type_at(def::A1) == def::rook
                    && square_is_empty(def::B1)
                    && square_is_empty(def::C1)
                    && square_is_empty(def::D1));
        else
            return (piece_type_at(def::E8) == def::king
                    && piece_type_at(def::A8) == def::rook
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
    Piece piece = piece_at(from);

    if (piece == Piece::empty_square())
        throw std::invalid_argument("square " + std::to_string(from) +
                                    " is empty, there is no piece to move.");

    bb_board[piece.color][piece.piece_type] &= ~square_bb(from);
    bb_board[piece.color][piece.piece_type] |= square_bb(to);
}

uint64_t Board::pseudo_legal_moves_on_square(Square square, std::function<bool(Square)> callback)
{
    PieceType piece = piece_type_at(square);
    std::function<bool(Square)> condition = pvt::conjunction(callback, pvt::is_valid_square);

    uint64_t knight_dirs = pvt::combine_squares_if(condition,
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
        uint64_t pawn_dirs = pvt::combine_squares_if(condition,
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
        uint64_t king_dirs = pvt::combine_squares_if(condition,
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
    if (move_is_pseudo_legal(from, to))
    {
        if (piece_type_at(from) == def::pawn)
            if (square_file(from) != square_file(to))
                return true;
        return true;
    }

    return false;
}

bool Board::is_capture(Square from, Square to)
{
    if (is_attacking_square(from, to))
        if (piece_type_at(to) != def::king)
            return true;

    return false;
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
                        square_is_empty(shift_square(to, def::up)) ? _true : code(def::empty_capture);
        }
        else if (is_capture(from, to))
        {
            if (piece_type_at(to) != def::king)
                return _true;
            return code(def::king_capture);
        }
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
    if (move_is_legal(from, to).first)
        move_piece(from, to);
//    else throw something
}

std::string Board::board_fen()
{
    std::string board_fen;

    constexpr int max_fen_length = 90;
    board_fen.reserve(max_fen_length);

    // iterate over each line

    for (int rank_i = 0; rank_i < 8; rank_i++)
    {
        int empty_square_counter = 0;
        for (Square square = 8*rank_i; square_rank(square) == rank_i; square = shift_square(square, def::right))
        {
            Piece piece = piece_at(square);

            if (piece != Piece::empty_square())
            {
                if (empty_square_counter != 0)
                {
                    board_fen.push_back(empty_square_counter + '0');
                    empty_square_counter = 0;
                }

                char symbol = def::piece_symbol(piece.piece_type);
                if (piece.color == def::white)
                    symbol = std::toupper(symbol);
//                std::cout << "<<<" << piece.piece_type << ">>> ";
                board_fen.push_back(symbol);
            }
            else empty_square_counter++;
        }

        if (empty_square_counter != 0)
            board_fen.push_back(empty_square_counter + '0');

        if (rank_i != 7)
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

    for (auto it = b_fen.rbegin(); it != b_fen.rend(); it++)
    {
        if (std::isalpha(*it))
            board.push_back(*it);

        if (std::isdigit(*it))
            board.append(std::string(*it - '0', '.'));

        if (*it == '/')
            board.push_back('\n');
    }

    return board;
}
