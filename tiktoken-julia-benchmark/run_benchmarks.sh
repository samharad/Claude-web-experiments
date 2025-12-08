#!/bin/bash
# Run both Python and Julia benchmarks, then compare results

set -e

echo "============================================================"
echo "Tiktoken Julia-Python Benchmarking Suite"
echo "============================================================"
echo

# Check Python
if ! command -v python &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8+."
    exit 1
fi

# Check tiktoken
if ! python -c "import tiktoken" 2>/dev/null; then
    echo "Error: tiktoken not installed. Run: pip install -r requirements.txt"
    exit 1
fi

# Check Julia (optional, continue if not available)
JULIA_AVAILABLE=false
if command -v julia &> /dev/null; then
    JULIA_AVAILABLE=true
else
    echo "Warning: Julia not found. Only Python baseline will be run."
    echo "Install Julia from https://julialang.org/downloads/ to run full comparison."
    echo
fi

# Run Python benchmark
echo "Running Python baseline benchmark..."
echo "------------------------------------------------------------"
python benchmark_python.py
echo
echo "✓ Python benchmark complete"
echo

# Run Julia benchmark if available
if [ "$JULIA_AVAILABLE" = true ]; then
    echo "Running Julia→Python benchmark..."
    echo "------------------------------------------------------------"

    # Check if Julia packages are installed
    if ! julia --project=. -e 'using PythonCall' 2>/dev/null; then
        echo "Installing Julia dependencies..."
        julia --project=. -e 'using Pkg; Pkg.instantiate()'
    fi

    julia --project=. benchmark_julia.jl
    echo
    echo "✓ Julia benchmark complete"
    echo
fi

# Compare results
echo "Generating comparison report..."
echo "------------------------------------------------------------"
python compare_results.py
echo

echo "============================================================"
echo "Benchmarking complete!"
echo "Results saved in results_python.json and results_julia.json"
echo "============================================================"
