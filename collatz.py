"""The 3x+1 (Collatz) problem.

Start with a positive integer n. If n is even, divide it by 2; if odd,
replace it with 3n + 1. Repeat. The Collatz conjecture says every starting
value eventually reaches 1.

Usage:
    python collatz.py 27            # print the sequence for 27
    python collatz.py --max 1000000 # find the longest chain below a limit
"""

import argparse


def collatz_step(n: int) -> int:
    """Return the next value in the 3x+1 sequence."""
    return n // 2 if n % 2 == 0 else 3 * n + 1


def collatz_sequence(n: int) -> list[int]:
    """Return the full sequence from n down to 1, inclusive."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    seq = [n]
    while n != 1:
        n = collatz_step(n)
        seq.append(n)
    return seq


def stopping_time(n: int, cache: dict[int, int] | None = None) -> int:
    """Return the number of steps for n to reach 1, memoized via cache."""
    if n < 1:
        raise ValueError("n must be a positive integer")
    if cache is None:
        cache = {}
    cache.setdefault(1, 0)
    path = []
    while n not in cache:
        path.append(n)
        n = collatz_step(n)
    steps = cache[n]
    for value in reversed(path):
        steps += 1
        cache[value] = steps
    return steps


def longest_chain(limit: int) -> tuple[int, int]:
    """Return (start, steps) for the start value below limit with the most steps."""
    if limit < 2:
        raise ValueError("limit must be at least 2")
    cache: dict[int, int] = {1: 0}
    best_start, best_steps = 1, 0
    for start in range(1, limit):
        steps = stopping_time(start, cache)
        if steps > best_steps:
            best_start, best_steps = start, steps
    return best_start, best_steps


def main() -> None:
    parser = argparse.ArgumentParser(description="Explore the 3x+1 (Collatz) problem.")
    parser.add_argument("n", nargs="?", type=int, help="starting value")
    parser.add_argument("--max", type=int, metavar="LIMIT",
                        help="find the start below LIMIT with the longest chain")
    args = parser.parse_args()

    if args.max is not None:
        start, steps = longest_chain(args.max)
        print(f"Longest chain below {args.max}: start={start}, steps={steps}")
    elif args.n is not None:
        seq = collatz_sequence(args.n)
        print(" -> ".join(map(str, seq)))
        print(f"Steps: {len(seq) - 1}, peak: {max(seq)}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
