// Synthetic CPU admission fixtures only; no model/GPU measurements.
#include "mr09_quota.hpp"
#include <cassert>
#include <atomic>
#include <cstdio>
#include <limits>
#include <thread>
#include <vector>
int main() {
    mr09_quota q(64);
    assert(q.reserve(64));
    assert(!q.reserve(1));
    q.release(64);
    assert(!q.reserve(std::numeric_limits<std::size_t>::max()));
    assert(q.snapshot().current == 0);
    assert(q.reserve(32)); // simulate failed allocator: reservation rolls back
    q.release(32);
    bool underflow=false;
    try { q.release(1); } catch(const std::logic_error&) { underflow=true; }
    assert(underflow && q.snapshot().current == 0);
    std::atomic<int> successes{0};
    std::vector<std::thread> workers;
    for(int t=0;t<8;++t) workers.emplace_back([&]{
        for(int n=0;n<2000;++n) if(q.reserve(8)) {
            successes.fetch_add(1); q.release(8);
        }
    });
    for(auto & t:workers) t.join();
    auto s=q.snapshot();
    assert(successes == 16000 && s.current == 0 && s.peak == 64 && s.denied == 2);
    std::puts("{\"classification\":\"synthetic CPU quota selftest\",\"status\":\"passed\",\"threads\":8,\"concurrent_admissions\":16000,\"boundary_denials\":2,\"final_live_bytes\":0}");
}
