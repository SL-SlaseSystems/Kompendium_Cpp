#include "strict_integer.hpp"
#include <algorithm>
#include <iostream>
#include <limits>
#include <variant>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: stats INTEGER [INTEGER ...]\n";
        return 2;
    }
    long long sum = 0;
    int minimum = std::numeric_limits<int>::max();
    int maximum = std::numeric_limits<int>::min();
    for (int i = 1; i < argc; ++i) {
        const auto result = kompendium::parse_integer(argv[i]);
        const auto* value = std::get_if<int>(&result);
        if (!value) {
            std::cerr << "invalid integer at argument " << i << '\n';
            return 2;
        }
        const long long v = *value;
        if ((v > 0 && sum > std::numeric_limits<long long>::max() - v) ||
            (v < 0 && sum < std::numeric_limits<long long>::min() - v)) {
            std::cerr << "sum out of range at argument " << i << '\n';
            return 2;
        }
        sum += v;
        minimum = std::min(minimum, *value);
        maximum = std::max(maximum, *value);
    }
    std::cout << "count=" << argc - 1 << " sum=" << sum
              << " min=" << minimum << " max=" << maximum << '\n';
}
