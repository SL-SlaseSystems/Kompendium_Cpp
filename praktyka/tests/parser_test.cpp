#include "strict_integer.hpp"
#include "check.hpp"
#include <limits>
#include <string>
#include <variant>

int main() {
    using namespace kompendium;
    check(std::get<int>(parse_integer("42")) == 42, "positive");
    check(std::get<int>(parse_integer("-17")) == -17, "negative");
    check(std::get<int>(parse_integer("0")) == 0, "zero");
    check(std::get<int>(parse_integer(std::to_string(std::numeric_limits<int>::max())))
          == std::numeric_limits<int>::max(), "max boundary");
    check(std::get<int>(parse_integer(std::to_string(std::numeric_limits<int>::min())))
          == std::numeric_limits<int>::min(), "min boundary");
    for (const auto input : {"", "+2", " 2", "-", "abc"})
        check(std::get<ParseError>(parse_integer(input)) == ParseError::invalid,
              "invalid input must not become zero");
    for (const auto input : {"2x", "2 ", "0x10", "12\n"})
        check(std::get<ParseError>(parse_integer(input)) == ParseError::trailing,
              "whole input must be consumed");
    check(std::get<ParseError>(parse_integer("999999999999999999999999999999999999"))
          == ParseError::out_of_range, "overflow");
    const std::string embedded{"12\0x", 4};
    check(std::get<ParseError>(parse_integer(embedded)) == ParseError::trailing,
          "embedded nul is input, not terminator");
}
