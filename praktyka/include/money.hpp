#pragma once
#include <compare>
#include <cstdint>
#include <limits>
#include <optional>

namespace kompendium {
struct PLN {};
struct EUR {};

template<class Currency>
class Money {
    std::int64_t cents_;
public:
    explicit constexpr Money(std::int64_t cents) : cents_(cents) {}
    constexpr std::int64_t cents() const { return cents_; }
    constexpr auto operator<=>(const Money&) const = default;

    constexpr std::optional<Money> add(Money other) const {
        constexpr auto hi = std::numeric_limits<std::int64_t>::max();
        constexpr auto lo = std::numeric_limits<std::int64_t>::min();
        const auto b = other.cents_;
        if ((b > 0 && cents_ > hi - b) || (b < 0 && cents_ < lo - b))
            return std::nullopt;
        return Money{cents_ + b};
    }
};
} // namespace kompendium
