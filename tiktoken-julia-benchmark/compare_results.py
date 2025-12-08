#!/usr/bin/env python3
"""
Compare results from Python and Julia benchmarks.
Analyzes overhead and performance differences.
"""

import json
import sys
from pathlib import Path


def load_results(filename):
    """Load benchmark results from JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def format_time(seconds):
    """Format time in appropriate units."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


def format_throughput(tokens_per_sec):
    """Format throughput with appropriate units."""
    if tokens_per_sec >= 1_000_000:
        return f"{tokens_per_sec / 1_000_000:.2f} M tokens/s"
    elif tokens_per_sec >= 1_000:
        return f"{tokens_per_sec / 1_000:.2f} K tokens/s"
    else:
        return f"{tokens_per_sec:.0f} tokens/s"


def compare_benchmarks(python_results, julia_results):
    """Generate comparison report."""
    print("=" * 80)
    print("TIKTOKEN BENCHMARK COMPARISON: Python vs Julia→Python")
    print("=" * 80)
    print()

    # Encoding info
    py_encoding = python_results.get("encoding", "unknown")
    jl_encoding = julia_results.get("encoding", "unknown") if julia_results else "N/A"
    print(f"Encoding: {py_encoding} (Python), {jl_encoding} (Julia)")
    print()

    # Compare each benchmark
    py_benchmarks = python_results.get("benchmarks", {})
    jl_benchmarks = julia_results.get("benchmarks", {}) if julia_results else {}

    print("-" * 80)
    print(f"{'Benchmark':<25} {'Python':<15} {'Julia':<15} {'Overhead':<15} {'Notes'}")
    print("-" * 80)

    for name in sorted(py_benchmarks.keys()):
        py_result = py_benchmarks[name]
        jl_result = jl_benchmarks.get(name)

        py_time = py_result["mean_time"]
        py_throughput = py_result["throughput_tokens_per_sec"]

        if jl_result:
            jl_time = jl_result["mean_time"]
            jl_throughput = jl_result["throughput_tokens_per_sec"]
            overhead_pct = ((jl_time - py_time) / py_time) * 100

            # Determine note
            if overhead_pct < 5:
                note = "negligible"
            elif overhead_pct < 20:
                note = "small"
            elif overhead_pct < 50:
                note = "moderate"
            else:
                note = "significant"

            print(f"{name:<25} {format_time(py_time):<15} {format_time(jl_time):<15} "
                  f"{overhead_pct:>6.1f}%{'':<8} {note}")
        else:
            print(f"{name:<25} {format_time(py_time):<15} {'N/A':<15} {'N/A':<15}")

    print("-" * 80)
    print()

    # Detailed analysis
    if julia_results:
        print("DETAILED ANALYSIS")
        print("=" * 80)
        print()

        # Group by size
        for size in ["small", "medium", "large", "very_large"]:
            single_name = f"{size}_single"
            multiple_name = f"{size}_multiple"

            if single_name in py_benchmarks and single_name in jl_benchmarks:
                print(f"{size.upper()} TEXT SIZE:")

                # Single call
                py_single = py_benchmarks[single_name]
                jl_single = jl_benchmarks[single_name]
                overhead_single = ((jl_single["mean_time"] - py_single["mean_time"])
                                   / py_single["mean_time"]) * 100

                tokens = py_single.get("token_count", jl_single.get("total_tokens", "?"))
                print(f"  Single call ({tokens} tokens):")
                print(f"    Python:   {format_time(py_single['mean_time'])} "
                      f"({format_throughput(py_single['throughput_tokens_per_sec'])})")
                print(f"    Julia:    {format_time(jl_single['mean_time'])} "
                      f"({format_throughput(jl_single['throughput_tokens_per_sec'])})")
                print(f"    Overhead: {overhead_single:.1f}%")

                # Multiple calls
                if multiple_name in py_benchmarks and multiple_name in jl_benchmarks:
                    py_multi = py_benchmarks[multiple_name]
                    jl_multi = jl_benchmarks[multiple_name]
                    overhead_multi = ((jl_multi["mean_time"] - py_multi["mean_time"])
                                      / py_multi["mean_time"]) * 100

                    num_calls = py_multi["num_calls"]
                    print(f"  Multiple calls ({num_calls} calls):")
                    print(f"    Python:   {format_time(py_multi['mean_time'])} "
                          f"({format_throughput(py_multi['throughput_tokens_per_sec'])})")
                    print(f"    Julia:    {format_time(jl_multi['mean_time'])} "
                          f"({format_throughput(jl_multi['throughput_tokens_per_sec'])})")
                    print(f"    Overhead: {overhead_multi:.1f}%")

                    # Compare single vs multiple overhead
                    overhead_delta = ((jl_multi['mean_time'] - py_multi['mean_time']) -
                                     (jl_single['mean_time'] - py_single['mean_time'])) * 1000
                    print(f"  Bridge overhead impact: {overhead_multi - overhead_single:.1f}% "
                          f"(+{overhead_delta:.2f} ms)")

                print()

        # Summary insights
        print("KEY INSIGHTS")
        print("=" * 80)

        all_overheads = []
        for name in py_benchmarks.keys():
            if name in jl_benchmarks:
                py_time = py_benchmarks[name]["mean_time"]
                jl_time = jl_benchmarks[name]["mean_time"]
                overhead = ((jl_time - py_time) / py_time) * 100
                all_overheads.append((name, overhead))

        if all_overheads:
            min_overhead = min(all_overheads, key=lambda x: x[1])
            max_overhead = max(all_overheads, key=lambda x: x[1])
            avg_overhead = sum(x[1] for x in all_overheads) / len(all_overheads)

            print(f"• Average overhead: {avg_overhead:.1f}%")
            print(f"• Minimum overhead: {min_overhead[1]:.1f}% ({min_overhead[0]})")
            print(f"• Maximum overhead: {max_overhead[1]:.1f}% ({max_overhead[0]})")
            print()

            # Recommendations
            print("RECOMMENDATIONS")
            print("-" * 80)
            if avg_overhead < 10:
                print("✓ Julia→Python bridge overhead is minimal for this workload")
                print("  Safe to use Tiktoken from Julia for most use cases")
            elif avg_overhead < 30:
                print("• Moderate overhead detected")
                print("  Consider batching multiple tokenization calls when possible")
            else:
                print("⚠ Significant overhead detected")
                print("  For performance-critical code, consider:")
                print("  - Running tokenization in pure Python")
                print("  - Batching many small calls into fewer large calls")
                print("  - Caching tokenization results")


def main():
    # Load results
    python_results = load_results("results_python.json")
    julia_results = load_results("results_julia.json")

    if not python_results:
        print("Error: results_python.json not found. Run benchmark_python.py first.")
        sys.exit(1)

    if not julia_results:
        print("Warning: results_julia.json not found. Showing Python results only.")
        print("Run benchmark_julia.jl to generate comparison data.")
        print()

    # Generate comparison
    compare_benchmarks(python_results, julia_results)


if __name__ == "__main__":
    main()
