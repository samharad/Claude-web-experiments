#!/usr/bin/env julia
"""
Julia benchmark for Tiktoken tokenization via PythonCall.jl.
Tests the overhead of calling Python code from Julia.
"""

using PythonCall
using Statistics
using JSON

# Import tiktoken
const tiktoken = pyimport("tiktoken")

# Try GPT-2, fallback to p50k_base (GPT-3)
ENCODING_NAME = "gpt2"
encoding = nothing
try
    global encoding = tiktoken.get_encoding(ENCODING_NAME)
    println("Using encoding: ", ENCODING_NAME)
catch
    global ENCODING_NAME = "p50k_base"
    global encoding = tiktoken.get_encoding(ENCODING_NAME)
    println("Using encoding: ", ENCODING_NAME, " (GPT-2 not available)")
end


"""Generate text that will tokenize to approximately target_tokens."""
function generate_text(target_tokens::Int)::String
    # Using a sample paragraph; ~1 token per 4 characters on average
    base_text = (
        "The quick brown fox jumps over the lazy dog. " *
        "This is a sample text used for benchmarking tokenization performance. " *
        "It contains various words and punctuation marks to represent typical text. " *
        "We repeat this text multiple times to reach the desired token count. "
    )

    # Estimate how many repetitions we need
    base_tokens = length(pyconvert(Vector, encoding.encode(base_text)))
    repetitions = max(1, target_tokens ÷ base_tokens)

    return base_text ^ repetitions
end


"""Benchmark tokenizing a single text multiple times."""
function benchmark_single_call(text::String; warmup::Int=5, iterations::Int=20)
    # Warmup
    for _ in 1:warmup
        encoding.encode(text)
    end

    # Actual benchmark
    times = Float64[]
    tokens = nothing
    for _ in 1:iterations
        start = time()
        tokens = encoding.encode(text)
        elapsed = time() - start
        push!(times, elapsed)
    end

    token_count = length(pyconvert(Vector, tokens))
    mean_time = mean(times)

    return Dict(
        "token_count" => token_count,
        "times_seconds" => times,
        "mean_time" => mean_time,
        "median_time" => median(times),
        "std_dev" => length(times) > 1 ? std(times) : 0.0,
        "throughput_tokens_per_sec" => mean_time > 0 ? token_count / mean_time : 0.0,
    )
end


"""Benchmark tokenizing multiple texts (amplifies bridge overhead)."""
function benchmark_multiple_calls(texts::Vector{String}; warmup::Int=5, iterations::Int=20)
    # Warmup
    for _ in 1:warmup
        for text in texts
            encoding.encode(text)
        end
    end

    # Actual benchmark
    times = Float64[]
    all_tokens = nothing
    for _ in 1:iterations
        start = time()
        all_tokens = [encoding.encode(text) for text in texts]
        elapsed = time() - start
        push!(times, elapsed)
    end

    total_tokens = sum(length(pyconvert(Vector, tokens)) for tokens in all_tokens)
    mean_time = mean(times)

    return Dict(
        "num_calls" => length(texts),
        "total_tokens" => total_tokens,
        "times_seconds" => times,
        "mean_time" => mean_time,
        "median_time" => median(times),
        "std_dev" => length(times) > 1 ? std(times) : 0.0,
        "throughput_tokens_per_sec" => mean_time > 0 ? total_tokens / mean_time : 0.0,
    )
end


"""Run comprehensive benchmark suite."""
function run_benchmarks()
    results = Dict(
        "encoding" => ENCODING_NAME,
        "benchmarks" => Dict()
    )

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

    for (name, target_tokens, num_chunks) in configs
        println("\nRunning benchmark: ", name, " (target=", target_tokens, " tokens, chunks=", num_chunks, ")")

        if num_chunks == 1
            text = generate_text(target_tokens)
            result = benchmark_single_call(text)
            result["config"] = Dict(
                "target_tokens" => target_tokens,
                "num_chunks" => num_chunks,
                "type" => "single_call"
            )
        else
            chunk_size = target_tokens ÷ num_chunks
            texts = [generate_text(chunk_size) for _ in 1:num_chunks]
            result = benchmark_multiple_calls(texts)
            result["config"] = Dict(
                "target_tokens" => target_tokens,
                "num_chunks" => num_chunks,
                "type" => "multiple_calls"
            )
        end

        results["benchmarks"][name] = result

        # Print summary
        if haskey(result, "token_count")
            println("  Tokens: ", result["token_count"])
        else
            println("  Total tokens: ", result["total_tokens"], " across ", result["num_calls"], " calls")
        end
        println("  Mean time: ", round(result["mean_time"] * 1000, digits=3), " ms")
        println("  Throughput: ", round(Int, result["throughput_tokens_per_sec"]), " tokens/sec")
    end

    # Save results
    output_file = "results_julia.json"
    open(output_file, "w") do f
        JSON.print(f, results, 2)
    end

    println("\n✓ Results saved to ", output_file)
    return results
end


if abspath(PROGRAM_FILE) == @__FILE__
    println("=" ^ 60)
    println("Julia→Python Tiktoken Benchmark")
    println("=" ^ 60)
    run_benchmarks()
end
