#!/usr/bin/env python3
"""
Pure Python benchmark for Tiktoken tokenization.
Tests various text sizes and call patterns to establish baseline performance.
"""

import time
import statistics
import json
from typing import List, Dict, Any
import tiktoken

# Try GPT-2, fallback to p50k_base (GPT-3)
try:
    ENCODING_NAME = "gpt2"
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    print(f"Using encoding: {ENCODING_NAME}")
except Exception:
    ENCODING_NAME = "p50k_base"
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    print(f"Using encoding: {ENCODING_NAME} (GPT-2 not available)")


def generate_text(target_tokens: int) -> str:
    """Generate text that will tokenize to approximately target_tokens."""
    # Using a sample paragraph; ~1 token per 4 characters on average
    base_text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is a sample text used for benchmarking tokenization performance. "
        "It contains various words and punctuation marks to represent typical text. "
        "We repeat this text multiple times to reach the desired token count. "
    )

    # Estimate how many repetitions we need
    base_tokens = len(encoding.encode(base_text))
    repetitions = max(1, target_tokens // base_tokens)

    return base_text * repetitions


def benchmark_single_call(text: str, warmup: int = 5, iterations: int = 20) -> Dict[str, Any]:
    """Benchmark tokenizing a single text multiple times."""
    # Warmup
    for _ in range(warmup):
        encoding.encode(text)

    # Actual benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        tokens = encoding.encode(text)
        end = time.perf_counter()
        times.append(end - start)

    token_count = len(tokens)
    mean_time = statistics.mean(times)

    return {
        "token_count": token_count,
        "times_seconds": times,
        "mean_time": mean_time,
        "median_time": statistics.median(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "throughput_tokens_per_sec": token_count / mean_time if mean_time > 0 else 0,
    }


def benchmark_multiple_calls(texts: List[str], warmup: int = 5, iterations: int = 20) -> Dict[str, Any]:
    """Benchmark tokenizing multiple texts (amplifies bridge overhead)."""
    # Warmup
    for _ in range(warmup):
        for text in texts:
            encoding.encode(text)

    # Actual benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        all_tokens = [encoding.encode(text) for text in texts]
        end = time.perf_counter()
        times.append(end - start)

    total_tokens = sum(len(tokens) for tokens in all_tokens)
    mean_time = statistics.mean(times)

    return {
        "num_calls": len(texts),
        "total_tokens": total_tokens,
        "times_seconds": times,
        "mean_time": mean_time,
        "median_time": statistics.median(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "throughput_tokens_per_sec": total_tokens / mean_time if mean_time > 0 else 0,
    }


def run_benchmarks():
    """Run comprehensive benchmark suite."""
    results = {
        "encoding": ENCODING_NAME,
        "benchmarks": {}
    }

    # Test configurations: (name, target_tokens, num_chunks)
    configs = [
        ("small_single", 100, 1),
        ("small_multiple", 100, 10),
        ("medium_single", 1000, 1),
        ("medium_multiple", 1000, 10),
        ("large_single", 10000, 1),
        ("large_multiple", 10000, 10),
        ("very_large_single", 100000, 1),
        ("very_large_multiple", 100000, 10),
    ]

    for name, target_tokens, num_chunks in configs:
        print(f"\nRunning benchmark: {name} (target={target_tokens} tokens, chunks={num_chunks})")

        if num_chunks == 1:
            text = generate_text(target_tokens)
            result = benchmark_single_call(text)
            result["config"] = {
                "target_tokens": target_tokens,
                "num_chunks": num_chunks,
                "type": "single_call"
            }
        else:
            chunk_size = target_tokens // num_chunks
            texts = [generate_text(chunk_size) for _ in range(num_chunks)]
            result = benchmark_multiple_calls(texts)
            result["config"] = {
                "target_tokens": target_tokens,
                "num_chunks": num_chunks,
                "type": "multiple_calls"
            }

        results["benchmarks"][name] = result

        # Print summary
        if "token_count" in result:
            print(f"  Tokens: {result['token_count']}")
        else:
            print(f"  Total tokens: {result['total_tokens']} across {result['num_calls']} calls")
        print(f"  Mean time: {result['mean_time']*1000:.3f} ms")
        print(f"  Throughput: {result['throughput_tokens_per_sec']:.0f} tokens/sec")

    # Save results
    output_file = "results_python.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_file}")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Python Tiktoken Benchmark")
    print("=" * 60)
    run_benchmarks()
