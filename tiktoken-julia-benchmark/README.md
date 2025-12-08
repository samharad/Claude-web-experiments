# Tiktoken Julia-Python Benchmarking

## Goal

Understand the performance characteristics of calling Python's Tiktoken library from Julia code, compared to native Python execution.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Julia (optional - for full comparison)
# Download from https://julialang.org/downloads/

# 3. Run benchmarks
bash run_benchmarks.sh

# Or run individually:
python benchmark_python.py           # Python baseline
julia --project=. benchmark_julia.jl # Julia→Python (requires Julia)
python compare_results.py            # Compare results
```

**Note**: Requires internet access on first run to download tokenizer encoding files from OpenAI.

## Research Questions

1. **What is the overhead of the Julia→Python bridge?**
   - How much slower is calling Tiktoken from Julia vs native Python?
   - Is the overhead constant or does it scale with input size?

2. **When does the bridge overhead become negligible?**
   - For large text tokenization, does the actual computation dominate?
   - What's the break-even point where bridge overhead is <5%?

3. **Does call frequency matter?**
   - Single call with large text vs many calls with small texts
   - Are there optimal batching strategies?

## Benchmarking Approach

We test the following scenarios:

### Text Sizes
- Small: ~100 tokens
- Medium: ~1,000 tokens
- Large: ~10,000 tokens
- Very Large: ~100,000 tokens

### Call Patterns
- **Single call**: One large text (minimizes bridge overhead)
- **Multiple calls**: Many small texts totaling the same token count (amplifies bridge overhead)

### Implementations
- **Pure Python**: Baseline performance using Tiktoken natively
- **Julia→Python**: Using PythonCall.jl to invoke Tiktoken

### Metrics
- Wall-clock time (mean, median, std dev)
- Throughput (tokens/second)
- Overhead percentage: `(Julia_time - Python_time) / Python_time × 100%`

## Technical Details

- **Tokenizer**: GPT-2 encoding (fallback to p50k_base if unavailable)
- **Julia-Python Bridge**: PythonCall.jl
- **Statistical rigor**: Multiple runs with warmup iterations

## Files

- `benchmark_python.py` - Pure Python benchmark
- `benchmark_julia.jl` - Julia calling Python benchmark
- `compare_results.py` - Analyzes and compares benchmark results
- `run_benchmarks.sh` - Automated script to run all benchmarks
- `requirements.txt` - Python dependencies
- `Project.toml` - Julia dependencies
- `SETUP.md` - Detailed setup instructions
- `results_python.json` - Python benchmark output
- `results_julia.json` - Julia benchmark output
