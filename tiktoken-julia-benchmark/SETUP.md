# Setup Instructions

## Prerequisites

### Python Setup
```bash
pip install -r requirements.txt
```

### Julia Setup

1. **Install Julia** (version 1.10 or later recommended)

   Download from: https://julialang.org/downloads/

   Or use juliaup (recommended):
   ```bash
   curl -fsSL https://install.julialang.org | sh
   ```

2. **Install Julia dependencies**
   ```bash
   cd tiktoken-julia-benchmark
   julia --project=. -e 'using Pkg; Pkg.instantiate()'
   ```

   This will install:
   - PythonCall.jl (Julia-Python bridge)
   - JSON.jl (for saving results)
   - Statistics.jl (built-in, for statistical analysis)

## Running Benchmarks

### Python Benchmark (Baseline)
```bash
cd tiktoken-julia-benchmark
python benchmark_python.py
```

This will create `results_python.json` with baseline performance metrics.

### Julia Benchmark (Julia→Python)
```bash
cd tiktoken-julia-benchmark
julia --project=. benchmark_julia.jl
```

This will create `results_julia.json` with Julia-calling-Python performance metrics.

### Compare Results
```bash
python compare_results.py
```

This will read both JSON files and generate a comparison report showing:
- Overhead percentages for each test case
- Performance differences across text sizes
- Impact of call frequency on overhead

## Troubleshooting

### PythonCall.jl not finding tiktoken
Make sure tiktoken is installed in the Python environment that PythonCall.jl uses:
```bash
julia --project=. -e 'using PythonCall; run(`$(PythonCall.python_executable()) -m pip install tiktoken`)'
```

### Julia compilation time
The first run will be slower due to Julia's JIT compilation. Run the benchmark twice and use the second run's results for accurate measurements.
