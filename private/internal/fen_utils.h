#ifndef UTILITY_H
#define UTILITY_H

#include <string>
#include <vector>
#include "public_utils/definitions.h"

namespace utility
{
[[nodiscard]]
std::string bitboard_to_string(chess::Bitboard bb);
[[nodiscard]]
std::vector<std::string> validate_and_split_board_fen(const std::string &_board_fen);
[[nodiscard]]
std::array<std::array<chess::Bitboard, 7>, 2> parse_board_fen_from_rows(std::vector<std::string> crows, const std::string &_board_fen);
}

#endif // UTILITY_H
