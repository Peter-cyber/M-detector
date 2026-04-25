#include <algorithm>
#include <cassert>
#include <atomic>
#include <numeric>
#include <vector>

#include <m-detector/parallel_utils.h>

#ifdef _OPENMP
#include <omp.h>
#endif

int main()
{
    std::vector<int> index(4096);
    std::iota(index.begin(), index.end(), 0);

    std::vector<int> output(index.size(), 0);
#ifdef _OPENMP
    std::vector<std::atomic<int>> thread_seen(omp_get_max_threads());
#endif
    m_detector::parallel_for_each(index.begin(), index.end(), [&](const int &i) {
#ifdef _OPENMP
        thread_seen[omp_get_thread_num()].store(1, std::memory_order_relaxed);
#endif
        output[i] = i * 3 + 7;
    });

    for (int i = 0; i < static_cast<int>(output.size()); ++i)
    {
        assert(output[i] == i * 3 + 7);
    }

#ifdef _OPENMP
    int used_threads = 0;
    for (const auto &seen : thread_seen)
    {
        used_threads += seen.load(std::memory_order_relaxed);
    }
    assert(used_threads > 1 || omp_get_max_threads() == 1);
#endif

    std::vector<int> empty;
    m_detector::parallel_for_each(empty.begin(), empty.end(), [](const int &) {
        assert(false && "empty ranges must not invoke the callback");
    });

    return 0;
}
