#include "bounded_queue.hpp"
#include "check.hpp"
#include <atomic>
#include <future>
#include <latch>
#include <memory>
#include <thread>
#include <vector>

int main() {
    using kompendium::BoundedQueue;
    bool rejected = false;
    try { BoundedQueue<int> invalid{0}; }
    catch (const std::invalid_argument&) { rejected = true; }
    check(rejected, "zero capacity must be rejected");
    {
        BoundedQueue<int> q{2};
        check(q.push(7) && q.push(9), "fill");
        q.close(); q.close();
        check(!q.push(11), "closed queue rejects producer");
        check(q.pop() == 7 && q.pop() == 9, "close drains FIFO");
        check(!q.pop(), "closed and empty means end");
    }
    {
        BoundedQueue<int> q{1};
        std::latch started{1};
        auto consumer = std::async(std::launch::async, [&] {
            started.count_down(); return q.pop();
        });
        started.wait(); q.close();
        check(!consumer.get(), "close releases consumer");
    }
    {
        BoundedQueue<int> q{1};
        check(q.push(1), "fill capacity one");
        std::latch started{1};
        auto producer = std::async(std::launch::async, [&] {
            started.count_down(); return q.push(2);
        });
        started.wait(); q.close();
        check(!producer.get(), "close releases producer");
        check(q.pop() == 1 && !q.pop(), "rejected item never appears");
    }
    {
        BoundedQueue<std::unique_ptr<int>> q{1};
        check(q.push(std::make_unique<int>(8)), "move-only element");
        auto result = q.pop();
        check(result && **result == 8, "ownership transferred");
        q.close();
    }
    {
        BoundedQueue<int> q{3};
        std::vector<std::atomic<int>> seen(200);
        for (auto& count : seen) count.store(0);
        std::vector<std::jthread> consumers;
        for (int c = 0; c != 3; ++c) consumers.emplace_back([&] {
            while (auto value = q.pop()) {
                check(*value >= 0 && *value < 200, "valid value");
                seen[static_cast<std::size_t>(*value)].fetch_add(1);
            }
        });
        std::vector<std::jthread> producers;
        for (int p = 0; p != 2; ++p) producers.emplace_back([&, p] {
            for (int n = p * 100; n != (p + 1) * 100; ++n)
                check(q.push(n), "open queue accepts all values");
        });
        producers.clear(); // join before closing
        q.close();
        consumers.clear(); // join before queue destruction
        for (const auto& count : seen)
            check(count.load() == 1, "each item delivered exactly once");
    }
}
