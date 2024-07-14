#include "public_utils/piece_utils.h"
#include <cctype>
#include <algorithm>

using namespace chess;

char chess::piece_symbol(PieceType type)
{
    return def::piece_symbols[type];
}

char chess::piece_symbol_from_piece(PieceType type, Color color)
{
    return (color == def::white) ? std::toupper(def::piece_symbols[type])
                                 : def::piece_symbols[type];
}

chess::PieceType chess::piece_type_from_symbol(char c)
{
    if (!c) return def::no_piece;

    auto found = std::find(def::piece_symbols.begin(), def::piece_symbols.end(), std::tolower(c));
    if (found == def::piece_symbols.end())
        return def::no_piece;
    return static_cast<PieceType>(std::abs(std::distance(found, def::piece_symbols.begin())));
}

const char* chess::piece_name(PieceType type)
{
    return def::piece_names[type];
}

