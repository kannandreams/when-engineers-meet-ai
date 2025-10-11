# eParallel CPU-bound Benchmark (Prime Computation)
# This script measures how Python performs in CPU-intensive tasks like
# counting prime numbers — both single-threaded and multi-threaded.
# In traditional Python (with GIL), threads can't truly run in parallel,
# but in Python 3.14's no-GIL (free-threaded) build, each thread can
# utilize a separate CPU core, allowing real parallelism.

import threading
import time

def is_prime(n):
    """Return True if n is a prime number."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def count_primes(start, end):
    """Count primes in the range [start, end)."""
    return sum(1 for i in range(start, end) if is_prime(i))


# Benchmark parameters
N = 20000   # Upper limit
NUM_THREADS = 4


# --- Single-threaded benchmark ---
start = time.time()
single_count = count_primes(0, N)
single_time = time.time() - start

print(f"Number of primes up to {N}: {single_count}")
print(f"Single-threaded: {single_time:.3f}s")


# --- Multi-threaded benchmark ---
threads = []
results = [0] * NUM_THREADS
step = N // NUM_THREADS

def worker(tid, start, end):
    results[tid] = count_primes(start, end)

start = time.time()
for i in range(NUM_THREADS):
    s = i * step
    e = N if i == NUM_THREADS - 1 else (i + 1) * step
    t = threading.Thread(target=worker, args=(i, s, e))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

multi_time = time.time() - start
multi_count = sum(results)

print(f"Number of primes up to {N}: {multi_count}")
print(f"Multi-threaded ({NUM_THREADS} threads): {multi_time:.3f}s")
print(f"Speed-up: {single_time / multi_time:.2f}×")
