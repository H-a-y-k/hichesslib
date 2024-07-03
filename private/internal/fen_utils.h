#ifndef UTILITY_H
#define UTILITY_H

#include "internal/chess_utils.h"

namespace chess
{
namespace utility
{
inline
uint64_t combine_squares_impl(Square val)
{
    return square_bb(val);
}

template <typename... Squares>
[[nodiscard]]
uint64_t combine_squares(Squares... squares)
{
    uint64_t result = 0;

    auto _ = {(result |= combine_squares_impl(squares))...}; // throwaway object

    return result;
}

[[nodiscard]]
inline
uint64_t combine_squares_if_impl(const std::function<bool(Square)> &callback, Square val)
{
    uint64_t result = 0;

    if (callback(val))
        result |= square_bb(val);

    return result;
}

template <typename... Squares>
[[nodiscard]]
uint64_t combine_squares_if(const std::function<bool(Square)> &callback, Squares... squares)
{
    uint64_t result = 0;

    auto _ = {(result |= combine_squares_if_impl(callback, squares))...}; // throwaway object
    (void)_;

    return result;
}

[[nodiscard]]
inline
std::function<bool(Square)> conjunction(const std::function<bool(Square)> &f1, const std::function<bool(Square)> &f2)
{
    return [f1, f2](Square sq) { return f1(sq) && f2(sq); };
}

[[nodiscard]]
std::string bitboard_to_string(uint64_t bb);
[[nodiscard]]
std::vector<std::string> validate_and_split_board_fen(const std::string &_board_fen);
[[nodiscard]]
std::array<std::array<uint64_t, 6>, 2> parse_board_fen_from_rows(std::vector<std::string> crows, const std::string &_board_fen);

}
}
#endif // UTILITY_H
