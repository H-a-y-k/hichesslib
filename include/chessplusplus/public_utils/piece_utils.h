#include "definitions.h"

namespace chess
{
[[nodiscard]]
char piece_symbol(PieceType t);
[[nodiscard]]
char piece_symbol_from_piece(PieceType t, Color c);
[[nodiscard]]
PieceType piece_type_from_symbol(char c);
[[nodiscard]]
const char* piece_name(PieceType t);
}
