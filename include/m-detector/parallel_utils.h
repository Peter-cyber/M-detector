#ifndef M_DETECTOR_PARALLEL_UTILS_H
#define M_DETECTOR_PARALLEL_UTILS_H

#include <iterator>

namespace m_detector
{

template <typename RandomAccessIterator, typename Function>
inline void parallel_for_each(RandomAccessIterator first, RandomAccessIterator last, Function function)
{
    using Difference = typename std::iterator_traits<RandomAccessIterator>::difference_type;
    const Difference count = last - first;
    if (count <= 0)
    {
        return;
    }

#if defined(_OPENMP)
#pragma omp parallel for schedule(static) if(count > 1)
    for (Difference offset = 0; offset < count; ++offset)
    {
        function(*(first + offset));
    }
#else
    for (Difference offset = 0; offset < count; ++offset)
    {
        function(*(first + offset));
    }
#endif
}

} // namespace m_detector

#endif
