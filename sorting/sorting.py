import random
import time
import sys

"""
Various sorting algorithms benchmarked on the same list of 1000 words.

Source of the words is:
https://nl.wiktionary.org/wiki/WikiWoordenboek:Lijst_met_1000_basiswoorden
"""

SEED = 0
RECURSIONLIMIT = 1000
random.seed(SEED)
sys.setrecursionlimit(RECURSIONLIMIT)


def prepare_data(iter):
    """
    Returns a sorted and shuffled lists after loading the list.
    Iter different number of permutations are sampled.
    """
    with open("woordenlijst.txt", 'r') as f:
        line = f.read()
    
    double_line = line + " " + line
    SORTED_LIST = sorted(double_line.replace(',', '').split())
    length = len(SORTED_LIST)
    UNSORTED_LISTS = [random.sample(SORTED_LIST, length)]
    for idx in range(iter - 1):
        UNSORTED_LISTS.append(random.sample(UNSORTED_LISTS[idx], length)) 
    
    return SORTED_LIST, UNSORTED_LISTS


def verify(func, iter):
    """
    Verifies if func sorts correctly on iter number of different permutations.
    """
    for idx in range(iter):
        if func(UNSORTED_LISTS[idx].copy()) != SORTED_LIST:
            print(f"The function {func.__name__} does not sort correctly.")
            print_summary(func, UNSORTED_LISTS[idx].copy())
            print()
            return False
    return True


def benchmark(func, iter):
    """
    Calls func iter number of times on as many different permutations.
    Returns the average elapsed time.
    """
    start_time = time.perf_counter()
    for idx in range(iter):
        func(UNSORTED_LISTS[idx].copy())
    end_time = time.perf_counter()
    return (end_time - start_time) / iter


def get_unsorted_list(*args):
    """Test function with predictable behaviour."""
    return UNSORTED_LISTS[0]


def get_sorted_list(*args):
    """Test function with predictable behaviour."""
    return SORTED_LIST


def built_in_sort(words):
    """Built-in function for reference speed."""
    return sorted(words)


def bubble_sort(words):
    """Bubble sort algorithm."""
    length = len(words) - 1
    while length > 0: 
        for idx in range(length):
            if words[idx] > words[idx+1]:
                words[idx], words[idx+1] = words[idx+1], words[idx]
        length -= 1
    return words


def selection_sort(words):
    """Selection sort algorithm."""
    for idx in range(len(words)):
        min_idx = idx + words[idx:].index(min(words[idx:]))
        words[idx], words[min_idx] = words[min_idx], words[idx]
    return words


def quick_sort_bad_memory(words):
    """
    Quick sort algorithm using first value as pivot.
    Naive implementation without in-place partitioning,
    thus having inefficient memory usage.
    """
    pivot = words[0]
    lower = []
    upper = []
    count = 1
    for word in words[1:]:
        if word < pivot:
            lower.append(word)
        elif word > pivot:
            upper.append(word)
        else:
            count += 1
    if len(lower) > 1:
        lower = quick_sort_bad_memory(lower)
    if len(upper) > 1:
        upper = quick_sort_bad_memory(upper)
    return lower + count * [pivot] + upper


def quick_sort_naive(words, start=0, end=None):
    """
    Quick sort algorithm using first value as pivot.
    Naive implementation without in-place partitioning,
    but with memory cleanup.
    """
    if end is None:
        end = len(words)
    pivot = words[start]
    lower = []
    upper = []
    for word in words[start+1:end]:
        if word < pivot:
            lower.append(word)
        elif word > pivot:
            upper.append(word)
    lower_bound = start + len(lower)
    upper_bound = end - len(upper)
    words[start: lower_bound] = lower
    words[lower_bound:upper_bound] = [pivot] * (upper_bound - lower_bound)
    words[upper_bound: end] = upper
    del lower, upper
    if lower_bound - start > 1:
        quick_sort_naive(words, start, lower_bound)
    if end - upper_bound > 1:
        quick_sort_naive(words, upper_bound, end)
    return words


def quick_sort_lomuta(words, start=0, end=None):
    """
    Quick sort algorithm using the lomuta partition with last value as pivot.
    """
    if end is None:
        end = len(words)
    pivot = words[end-1]
    boundary = start
    for idx in range(start, end - 1):
        if words[idx] < pivot:
            words[boundary], words[idx] = words[idx], words[boundary]
            boundary += 1
    words[boundary], words[end-1] = words[end-1], words[boundary]
    if boundary - start > 1:
        quick_sort_lomuta(words, start, boundary)
    if end - boundary > 2:
        quick_sort_lomuta(words, boundary + 1, end)
    return words


def quick_sort_hoare(words, start=0, end=None):
    """
    Quick sort algorithm using the hoare partition with first value as pivot.
    """
    if end is None:
        end = len(words)
    pivot = words[start] 
    lower = start + 1
    upper = end - 1
    while True:
        while words[upper] >= pivot and upper > start:
            upper -= 1
        while words[lower] < pivot:
            lower += 1
            if lower == end:
                break
        if lower > upper:
            break
        words[lower], words[upper] = words[upper], words[lower]
    words[start], words[lower-1] = words[lower-1], words[start]
    if lower - start > 2:
        quick_sort_hoare(words, start, lower - 1)
    if end - lower > 1:
        quick_sort_hoare(words, lower, end)
    return words


def print_summary(func, UNSORTED_LISTS, head=5, tail=5):
    """Prints an overview of first and last n items in list returned by func."""
    words = func(UNSORTED_LISTS)
    print(f"{func.__name__:18}SORTED_LIST       UNSORTED_LISTS")
    for idx in range(head):
        print(f"{words[idx]:18}{SORTED_LIST[idx]:18}{UNSORTED_LISTS[idx]:18}")
    print("⋮                 ⋮                 ⋮")
    for idx in range(- tail - 1, 0):
        print(f"{words[idx]:18}{SORTED_LIST[idx]:18}{UNSORTED_LISTS[idx]:18}")


if __name__ == "__main__":
    ITERATIONS = 10
    SORTED_LIST, UNSORTED_LISTS = prepare_data(ITERATIONS)

    sorting_functions = (
        get_unsorted_list,
        get_sorted_list,
        built_in_sort,
        bubble_sort,
        selection_sort,
        quick_sort_bad_memory,
        quick_sort_naive,
        quick_sort_lomuta,
        quick_sort_hoare,
    )

    algorithm_benchmarks = {}
    for func in sorting_functions:
        if verify(func, ITERATIONS):
            algorithm_benchmarks[func.__name__] = benchmark(func, ITERATIONS)
    
    message = (
        "Performance of sorting algorithms on a collection of "
        f"{len(SORTED_LIST)} words.\n"
        f"Benchmarks are averaged over {ITERATIONS} function calls "
        "on different permutations.\n"
        "Each algorithm is tested on the same set of permutations.\n\n"
        "Algorithm                Time (µs)"
    )
    print(message)
    micro = 1e-6
    for key, value in algorithm_benchmarks.items():
        print(f"{key:24}{value/micro:>10.2f}")
