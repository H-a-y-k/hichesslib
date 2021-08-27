#include "chessplusplus.h"

using namespace chess;

Piece::Piece(PieceType _piece_type, Color _color)
    : piece_type(_piece_type)
    , color(_color)
{  }

Piece Piece::empty_square()
{
    return Piece(def::no_piece, def::white);
}

uint64_t square_bb(Square square)
{
    return uint64_t(1) << square;
}


Square square_at(int rank, int file)
{
    return rank * 8 + file;
}

// defaults

char def::piece_symbol(PieceType type)
{
    return def::piece_symbols[type];
}

const char* piece_name(PieceType t)
{
    return def::piece_names[t];
}


Board::Board(const std::string &fen)
{
    if (fen.empty())
        clear();
    else if (fen == def::starting_board_fen)
        reset_board();
    else
        set_board_fen(fen);
}

void Board::reset_board()
{
    using namespace def;

    bb_board[white][pawn] = bb_ranks[1];
    bb_board[white][knight] = square_bb(B1) & square_bb(G1);
    bb_board[white][bishop] = square_bb(C1) & square_bb(F1);
    bb_board[white][rook] = square_bb(A1) & square_bb(H1);
    bb_board[white][queen] = square_bb(D1);
    bb_board[white][king] = square_bb(E1);

    bb_board[black][pawn] = bb_ranks[7];
    bb_board[black][knight] = square_bb(B8) & square_bb(G8);
    bb_board[black][bishop] = square_bb(C8) & square_bb(F8);
    bb_board[black][rook] = square_bb(A8) & square_bb(H8);
    bb_board[black][queen] = square_bb(D8);
    bb_board[black][king] = square_bb(E8);
}

void Board::clear()
{
    bb_board[def::white] = {0,0,0,0,0,0};
    bb_board[def::black] = {0,0,0,0,0,0};
}

void Board::set_board_fen(const std::string &board_fen)
{
    if (board_fen.empty())
        throw std::invalid_argument("fen is empty");

    if (board_fen.find(' ') != std::string::npos)
        throw std::invalid_argument(std::string("expected position part, got multiple parts: ") + board_fen);

    std::istringstream split(board_fen);
    std::vector<std::string> rows;

    for (std::string row; std::getline(split, row, '/');)
        rows.push_back(row);

    if (rows.empty())
        throw std::invalid_argument("rows aren't separated with slashes('/') in the fen: " + board_fen);
    else if (rows.size() != 8)
        throw std::invalid_argument("the fen has to contain 8 rows and not" + std::to_string(rows.size()) + ": " + board_fen);

    clear();

    std::array<std::array<uint64_t, 6>, 2> tmp_bb_board {};

    for (auto row_it = rows.rbegin(); row_it != rows.rend(); row_it++)
    {
        if (row_it->empty())
            throw std::invalid_argument("rows in fen cannot be empty: " + board_fen);

        int empty_cells = 0;
        int occupied_cells = 0;
        for (auto symbol_it = row_it->begin(); symbol_it < row_it->end(); symbol_it++)
        {
            bool previous_was_digit = false;

            if (isdigit(*symbol_it))
            {
                empty_cells += *symbol_it - '0';

                if (previous_was_digit)
                    throw std::invalid_argument("a row in the fen shouldn't contain two digits next to each other: " + board_fen);

                previous_was_digit = true;
            }
            else
            {
                auto found = std::find(def::piece_symbols.begin(), def::piece_symbols.end(),
                                       std::tolower(*symbol_it));
                if (found != def::piece_symbols.end())
                {
                    int rank = std::distance(row_it, rows.rbegin());
                    int file = std::distance(symbol_it, row_it->begin());

                    if (previous_was_digit)
                        file += *(symbol_it - 1) - '0';

                    Color color = std::islower(*symbol_it);
                    PieceType piece = static_cast<PieceType>(std::distance(found, def::piece_symbols.begin()));

                    tmp_bb_board[color][piece] |= square_at(rank, file);

                    previous_was_digit = false;
                }
                else throw std::invalid_argument("invalid character(s)('" +
                                                 std::string(1, *symbol_it) +
                                                 "') in the fen: " + board_fen);
            }
        }

        if (empty_cells + occupied_cells != 8)
            throw std::invalid_argument("a fen row has to occupy exactly 8 cells: " + board_fen);
    }

    bb_board = tmp_bb_board;
}

PieceType Board::piece_type_at(Square square)
{
    for (auto piece_bb = bb_board[def::white].begin(); piece_bb != bb_board[def::white].end(); piece_bb++)
    {
        if (*piece_bb & square_bb(square))
            return std::distance(piece_bb, bb_board[def::white].begin());
    }
    for (auto piece_bb = bb_board[def::black].begin(); piece_bb != bb_board[def::black].end(); piece_bb++)
    {
        if (*piece_bb & square_bb(square))
            return std::distance(piece_bb, bb_board[def::black].begin());
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

    bb_board[piece.color][piece.piece_type] &= square_bb(from);
    bb_board[piece.color][piece.piece_type] |= square_bb(to);
}

void Board::make_move(Square from, Square to)
{
}
