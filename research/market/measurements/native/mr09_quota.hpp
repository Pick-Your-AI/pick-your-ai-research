#pragma once
// Project-owned native admission counter. No CUDA or third-party code copied.
#include <cstddef>
#include <mutex>
#include <stdexcept>

class mr09_quota {
    std::mutex mutex_;
    std::size_t limit_, current_ = 0, peak_ = 0, denied_ = 0, granted_ = 0;
public:
    explicit mr09_quota(std::size_t limit) : limit_(limit) {
        if (!limit) throw std::invalid_argument("zero cap");
    }
    bool reserve(std::size_t bytes) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (bytes > limit_ - current_) { ++denied_; return false; }
        current_ += bytes;
        if (current_ > peak_) peak_ = current_;
        ++granted_;
        return true;
    }
    void release(std::size_t bytes) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (bytes > current_) throw std::logic_error("counter underflow");
        current_ -= bytes;
    }
    struct state { std::size_t limit, current, peak, denied, granted; };
    state snapshot() {
        std::lock_guard<std::mutex> lock(mutex_);
        return {limit_,current_,peak_,denied_,granted_};
    }
};
