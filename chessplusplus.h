#ifndef CHESSPLUSPLUS_H
#define CHESSPLUSPLUS_H

#include "chessplusplus_global.h"
#include <array>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <iterator>

namespace chess
{
using Color = bool;

constexpr Color _white = true;
constexpr Color _black = false;

std::array<char, 8> _filenames = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'};
std::array<int, 8> _ranknames = {'1', '2', '3', '4', '5', '6', '7', '8'};

using PieceType = int;

enum _piecetypes: PieceType
{
    _pawn = 0,
    _knight,
    _bishop,
    _rook,
    _queen,
    _king
};

constexpr std::array<char, 6> _piecesymbols = {'p', 'n', 'b', 'r', 'q', 'k'};
constexpr std::array<const char*, 6> _piecenames = {"pawn", "knight", "bishop", "rook", "queen", "knight"};

char _piecesymbol(PieceType t)
{
    return _piecesymbols[t];
}

const char* _piecename(PieceType t)
{
    return _piecenames[t];
}

constexpr const char* _starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
constexpr const char* _starting_board_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR";

using Square = int;

enum _squares: Square
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

constexpr std::array<const char*, 64> _square_names =
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

// TODO
// Create basic board

#define BB_SQUARE(sq) (uint64_t(1) << sq)

#define BB BB_SQUARE
constexpr std::array<uint64_t, 8> _bb_ranks =
{
    BB(A1) & BB(A2) & BB(A3) & BB(A4) & BB(A5) & BB(A6) & BB(A7) & BB(A8),
    BB(B1) & BB(B2) & BB(B3) & BB(B4) & BB(B5) & BB(B6) & BB(B7) & BB(B8),
    BB(C1) & BB(C2) & BB(C3) & BB(C4) & BB(C5) & BB(C6) & BB(C7) & BB(C8),
    BB(D1) & BB(D2) & BB(D3) & BB(D4) & BB(D5) & BB(D6) & BB(D7) & BB(D8),
    BB(E1) & BB(E2) & BB(E3) & BB(E4) & BB(E5) & BB(E6) & BB(E7) & BB(E8),
    BB(F1) & BB(F2) & BB(F3) & BB(F4) & BB(F5) & BB(F6) & BB(F7) & BB(F8),
    BB(G1) & BB(G2) & BB(G3) & BB(G4) & BB(G5) & BB(G6) & BB(G7) & BB(G8),
    BB(H1) & BB(H2) & BB(H3) & BB(H4) & BB(H5) & BB(H6) & BB(H7) & BB(H8)
};
#undef BB

constexpr uint64_t _bb_empty = 0;
constexpr uint64_t _bb_full = 0xffffffffffffffff;


Square square_at(int rank, int file)
{
    return rank * 8 + file;
}


class Board
{
    std::array<std::array<uint64_t, 6>, 2> bb_board {};
    std::string board_fen = "";

public:
    Board(const std::string &fen = _starting_board_fen)
        : board_fen(fen)
    {
        if (fen.empty())
            clear();
        else if (fen == _starting_board_fen)
            reset_board();
        else
            set_board_fen(fen);
    }

    auto reset_board() -> void
    {
        board_fen = _starting_board_fen;

        bb_board[_white][_pawn] = _bb_ranks[1];
        bb_board[_white][_knight] = BB_SQUARE(B1) & BB_SQUARE(G1);
        bb_board[_white][_bishop] = BB_SQUARE(C1) & BB_SQUARE(F1);
        bb_board[_white][_rook] = BB_SQUARE(A1) & BB_SQUARE(H1);
        bb_board[_white][_queen] = BB_SQUARE(D1);
        bb_board[_white][_king] = BB_SQUARE(E1);

        bb_board[_black][_pawn] = _bb_ranks[7];
        bb_board[_black][_knight] = BB_SQUARE(B8) & BB_SQUARE(G8);
        bb_board[_black][_bishop] = BB_SQUARE(C8) & BB_SQUARE(F8);
        bb_board[_black][_rook] = BB_SQUARE(A8) & BB_SQUARE(H8);
        bb_board[_black][_queen] = BB_SQUARE(D8);
        bb_board[_black][_king] = BB_SQUARE(E8);
    }

    void clear()
    {
        board_fen = std::string(8, '/');
        bb_board[_white] = {0,0,0,0,0,0};
        bb_board[_black] = {0,0,0,0,0,0};
    }

    void set_board_fen(const std::string &fen)
    {
        board_fen = fen;

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
                    auto found = std::find(_piecesymbols.begin(), _piecesymbols.end(),
                                           std::tolower(*symbol_it));
                    if (found != _piecesymbols.end())
                    {
                        int rank = std::distance(row_it, rows.rbegin());
                        int file = std::distance(symbol_it, row_it->begin());

                        if (previous_was_digit)
                            file += *(symbol_it - 1) - '0';

                        Color color = std::islower(*symbol_it);
                        PieceType piece = static_cast<PieceType>(std::distance(found, _piecesymbols.begin()));

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


};

// TODO
// create move system
}

#endif // CHESSPLUSPLUS_H
