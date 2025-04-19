import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import os
import time

# Range to test
lower_bound = 2
upper_bound = 100000000

# Block sizes to test (powers of 2 from 16 to 8192(14 pow))
block_sizes = [2**i for i in range(4, 28)]  # 16, 32, 64, 128, ..., 8192

# Regular expression to extract execution time
time_pattern = re.compile(r'Czas przetwarzania: (\d+\.\d+) sekund')

# Function to run a test and return execution time
def run_test(program, lower, upper, block_size):
    cmd = f"./{program} {lower} {upper} {block_size}"
    # print(f"Running: {cmd}") # ----------------------------------------------------------
    
    # Run the process and capture output
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Error running {cmd}:")
        print(result.stderr)
        return None
    
    # Parse the output to get the execution time
    match = time_pattern.search(result.stdout)
    if match:
        return float(match.group(1))
    else:
        print(f"Could not parse execution time from output: {result.stdout}")
        return None

# Results will be stored here
results_k3a = []
results_k5 = []

# Run tests for each block size
print(f"\nTesting with range {lower_bound} to {upper_bound}:")
print("-" * 50)
print(f"{'Block Size':<10} | {'k3a.o Time (s)':<15} | {'k5.o Time (s)':<15}")
print("-" * 50)

for block_size in block_sizes:
    # Run k3a test
    time_k3a = run_test("k3a.o", lower_bound, upper_bound, block_size)
    
    # Small delay to ensure system resources are free
    time.sleep(0.5)
    
    # Run k5 test
    time_k5 = run_test("k5.o", lower_bound, upper_bound, block_size)
    
    # Store results
    results_k3a.append((block_size, time_k3a))
    results_k5.append((block_size, time_k5))
    
    # Print results for this block size
    print(f"{block_size:<10} | {time_k3a if time_k3a else 'Error':<15.6f} | {time_k5 if time_k5 else 'Error':<15.6f}")
    
    # Short delay between tests
    time.sleep(0.5)

# Filter out any failed tests
results_k3a = [(bs, t) for bs, t in results_k3a if t is not None]
results_k5 = [(bs, t) for bs, t in results_k5 if t is not None]

# Find optimal block size
if results_k3a:
    best_k3a = min(results_k3a, key=lambda x: x[1])
    print(f"\nBest block size for k3a: {best_k3a[0]} with time {best_k3a[1]:.6f} seconds")

if results_k5:
    best_k5 = min(results_k5, key=lambda x: x[1])
    print(f"Best block size for k5: {best_k5[0]} with time {best_k5[1]:.6f} seconds")

# Plot results
plt.figure(figsize=(12, 6))

# Extract data for plotting
block_sizes_k3a, times_k3a = zip(*results_k3a) if results_k3a else ([], [])
block_sizes_k5, times_k5 = zip(*results_k5) if results_k5 else ([], [])

# Create plots
plt.plot(block_sizes_k3a, times_k3a, 'o-', label='k3a.o')
plt.plot(block_sizes_k5, times_k5, 's-', label='k5.o')

# Mark the best block sizes
if results_k3a:
    plt.scatter([best_k3a[0]], [best_k3a[1]], color='red', s=100, label=f'Best k3a: {best_k3a[0]}')
if results_k5:
    plt.scatter([best_k5[0]], [best_k5[1]], color='green', s=100, label=f'Best k5: {best_k5[0]}')

# Labels and title
plt.xlabel('Block Size')
plt.ylabel('Execution Time (seconds)')
plt.title(f'Prime Sieve Performance: Range {lower_bound}-{upper_bound}')
plt.grid(True)
plt.legend()
plt.xscale('log')  # Use log scale for x-axis
plt.tight_layout()

# Save the plot to a file
plt.savefig('prime_sieve_performance.png')
print("\nPerformance plot saved as prime_sieve_performance.png")

# Show the plot
plt.show()

# Save the data to a CSV file
with open('prime_sieve_results.csv', 'w') as f:
    f.write("Block Size,k3a Time (s),k5 Time (s)\n")
    for i in range(len(block_sizes)):
        k3a_time = results_k3a[i][1] if i < len(results_k3a) else "N/A"
        k5_time = results_k5[i][1] if i < len(results_k5) else "N/A"
        f.write(f"{block_sizes[i]},{k3a_time},{k5_time}\n")

print("Results saved to prime_sieve_results.csv")