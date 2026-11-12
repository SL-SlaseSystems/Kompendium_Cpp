#pragma once
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace kompendium {
// Ograniczenie upraszcza gwarancje wyjątków przy pobieraniu elementu.
template<class T>
requires (std::is_nothrow_move_constructible_v<T> && std::is_nothrow_destructible_v<T>)
class BoundedQueue {
    const std::size_t capacity_;
    std::deque<T> items_;
    bool closed_ = false;
    std::mutex mutex_;
    std::condition_variable readable_;
    std::condition_variable writable_;
public:
    explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {
        if (capacity == 0) throw std::invalid_argument("capacity must be positive");
    }
    BoundedQueue(const BoundedQueue&) = delete;
    BoundedQueue& operator=(const BoundedQueue&) = delete;

    bool push(T value) {
        std::unique_lock lock(mutex_);
        writable_.wait(lock, [&] { return closed_ || items_.size() < capacity_; });
        if (closed_) return false;
        try {
            items_.push_back(std::move(value));
        } catch (...) {
            // Powiadomienie z pop mogło trafić tylko do tego producenta.
            // Wolne miejsce nadal istnieje: pozwól spróbować następnemu.
            lock.unlock();
            writable_.notify_one();
            throw;
        }
        lock.unlock();
        readable_.notify_one();
        return true;
    }

    std::optional<T> pop() {
        std::unique_lock lock(mutex_);
        readable_.wait(lock, [&] { return closed_ || !items_.empty(); });
        if (items_.empty()) return std::nullopt;
        std::optional<T> result{std::in_place, std::move(items_.front())};
        items_.pop_front();
        lock.unlock();
        writable_.notify_one();
        return result;
    }

    void close() {
        {
            std::lock_guard lock(mutex_);
            closed_ = true;
        }
        readable_.notify_all();
        writable_.notify_all();
    }
    // Przed destrukcją właściciel musi close() i dołączyć wszystkie wątki.
};
} // namespace kompendium
