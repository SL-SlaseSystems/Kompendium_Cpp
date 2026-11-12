#pragma once
#include <charconv>
#include <string_view>
#include <system_error>
#include <variant>

namespace kompendium {
enum class ParseError { invalid, out_of_range, trailing };
using ParseResult = std::variant<int, ParseError>;

// Dziesiętne int; bez plusa, białych znaków, prefiksów i sufiksów.
// Priorytet błędów: invalid, out_of_range, trailing.
inline ParseResult parse_integer(std::string_view input) {
    if (input.empty()) return ParseError::invalid;
    int value{};
    const char* end = input.data() + input.size();
    const auto [ptr, ec] = std::from_chars(input.data(), end, value, 10);
    if (ec == std::errc::invalid_argument) return ParseError::invalid;
    if (ec == std::errc::result_out_of_range) return ParseError::out_of_range;
    if (ptr != end) return ParseError::trailing;
    return value;
}
} // namespace kompendium
