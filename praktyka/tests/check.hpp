#pragma once
#include <stdexcept>
#include <string>

inline void check(bool condition, const char* message) {
    if (!condition) throw std::runtime_error(message);
}
