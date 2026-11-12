#include "money.hpp"
#include "check.hpp"
#include <limits>
#include <type_traits>

template<class A, class B>
concept CanAdd = requires(A a, B b) { a.add(b); };

int main() {
    using namespace kompendium;
    using Zloty = Money<PLN>;
    using Euro = Money<EUR>;
    static_assert(!std::is_convertible_v<std::int64_t, Zloty>);
    static_assert(!CanAdd<Zloty, Euro>);
    check(Zloty{199}.add(Zloty{1})->cents() == 200, "exact sum");
    check(Zloty{-300}.add(Zloty{100})->cents() == -200, "negative balance");
    constexpr auto hi = std::numeric_limits<std::int64_t>::max();
    constexpr auto lo = std::numeric_limits<std::int64_t>::min();
    check(!Zloty{hi}.add(Zloty{1}), "positive overflow");
    check(!Zloty{lo}.add(Zloty{-1}), "negative overflow");
    check(Zloty{hi}.add(Zloty{lo})->cents() == -1, "opposite extremes");
    check(Zloty{lo}.add(Zloty{0})->cents() == lo, "minimum plus zero");
    check(Zloty{1} < Zloty{2}, "ordering follows cents");
    check(Zloty{10} == Zloty{10}, "equality");
    static_assert(Zloty{10}.add(Zloty{20})->cents() == 30);
}
