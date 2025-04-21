import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import os
import time

# Range to test
lower_bound = 2
upper_bound = 100000000

# Programs to test
programs = ["k2.o", "k4.o", "k4a.o"]

# Block sizes to test (powers of 2 from 16 to 8192)
block_sizes = [2**i for i in range(4, 28)]  # 16, 32, 64, 128, ..., 8192

# Regular expression to extract execution time
time_pattern = re.compile(r'Czas przetwarzania: (\d+\.\d+) sekund')

# Function to run a test and return execution time
def run_test(program, lower, upper, chunk_size=None):
    if chunk_size == "dynamic":
        cmd = f"./{program} {lower} {upper} dynamic"
    else:
        cmd = f"./{program} {lower} {upper} {chunk_size}"
    
    #print(f"Running: {cmd}")
    
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
results = {program: [] for program in programs}
dynamic_results = {program: None for program in programs}

# First, test dynamic scheduling for each program
print(f"\nTesting DYNAMIC scheduling with range {lower_bound} to {upper_bound}:")
print("-" * 60)
print(f"{'Program':<10} | {'Dynamic Scheduling Time (s)':<25}")
print("-" * 60)

for program in programs:
    # Run test with dynamic scheduling
    time_dynamic = run_test(program, lower_bound, upper_bound, "dynamic")
    
    # Store result
    dynamic_results[program] = time_dynamic
    
    # Print result
    print(f"{program:<10} | {time_dynamic if time_dynamic else 'Error':<25.6f}")
    
    # Short delay between tests
    time.sleep(1)

# Now test static scheduling with different block sizes
print(f"\nTesting STATIC scheduling with range {lower_bound} to {upper_bound}:")
print("-" * 80)
header = f"{'Block Size':<10}"
for program in programs:
    header += f" | {program + ' Time (s)':<15}"
print(header)
print("-" * 80)

for block_size in block_sizes:
    row = f"{block_size:<10}"
    
    for program in programs:
        # Run test
        time_static = run_test(program, lower_bound, upper_bound, block_size)
        
        # Store results
        if time_static is not None:
            results[program].append((block_size, time_static))
        
        # Add to output row
        row += f" | {time_static if time_static else 'Error':<15.6f}"
        
        # Short delay between tests
        time.sleep(0.5)
    
    print(row)
    
    # Slightly longer delay between block sizes
    time.sleep(0.5)

# Find optimal block size for each program
best_static = {}
for program in programs:
    if results[program]:
        best_static[program] = min(results[program], key=lambda x: x[1])
        print(f"\nBest static block size for {program}: {best_static[program][0]} with time {best_static[program][1]:.6f} seconds")
        
        # Compare with dynamic
        if dynamic_results[program] is not None:
            dynamic_time = dynamic_results[program]
            static_time = best_static[program][1]
            diff_percent = ((dynamic_time - static_time) / static_time) * 100
            
            if diff_percent > 0:
                print(f"Static is faster by {abs(diff_percent):.2f}%")
            else:
                print(f"Dynamic is faster by {abs(diff_percent):.2f}%")

# Plot results
plt.figure(figsize=(14, 8))

# Prepare color cycle
colors = ['blue', 'green', 'red']
markers = ['o', 's', '^']

# Create plots for static scheduling
for i, program in enumerate(programs):
    if results[program]:
        block_sizes_prog, times_prog = zip(*results[program])
        plt.plot(block_sizes_prog, times_prog, f"{markers[i]}-", color=colors[i], label=f'{program} (Static)')
        
        # Mark the best block size
        if program in best_static:
            plt.scatter([best_static[program][0]], [best_static[program][1]], 
                      color=colors[i], s=150, edgecolor='black', 
                      label=f'Best {program}: {best_static[program][0]}')

# Add horizontal lines for dynamic scheduling
for i, program in enumerate(programs):
    if dynamic_results[program] is not None:
        plt.axhline(y=dynamic_results[program], color=colors[i], linestyle='--', 
                   label=f'{program} (Dynamic): {dynamic_results[program]:.6f}s')

# Labels and title
plt.xlabel('Block Size (Static Scheduling)')
plt.ylabel('Execution Time (seconds)')
plt.title(f'Prime Finder Performance: Range {lower_bound}-{upper_bound}')
plt.grid(True)
plt.legend(loc='best')
plt.xscale('log')  # Use log scale for x-axis
plt.tight_layout()

# Save the plot to a file
plt.savefig('prime_finder_performance.png')
print("\nPerformance plot saved as prime_finder_performance.png")

# Show the plot
plt.show()

# Save the data to a CSV file
with open('prime_finder_results.csv', 'w') as f:
    # Header
    f.write("Block Size," + ",".join([f"{prog} Static Time (s)" for prog in programs]) + 
            "," + ",".join([f"{prog} Dynamic Time (s)" for prog in programs]) + "\n")
    
    # Data for static scheduling
    for block_size in block_sizes:
        row = f"{block_size}"
        
        # Static times
        for program in programs:
            time_val = next((t for bs, t in results[program] if bs == block_size), "N/A")
            row += f",{time_val}"
        
        # Dynamic times (same for all block sizes)
        for program in programs:
            row += f",{dynamic_results[program] if dynamic_results[program] is not None else 'N/A'}"
        
        f.write(row + "\n")

print("Results saved to prime_finder_results.csv")

# Generate summary table
print("\nSUMMARY TABLE:")
print("-" * 80)
print(f"{'Program':<10} | {'Best Static Size':<15} | {'Best Static Time':<15} | {'Dynamic Time':<15} | {'Faster Option':<15}")
print("-" * 80)

for program in programs:
    if program in best_static and dynamic_results[program] is not None:
        best_size = best_static[program][0]
        static_time = best_static[program][1]
        dynamic_time = dynamic_results[program]
        
        if static_time < dynamic_time:
            faster = "Static"
            diff = ((dynamic_time - static_time) / static_time) * 100
        else:
            faster = "Dynamic"
            diff = ((static_time - dynamic_time) / dynamic_time) * 100
            
        print(f"{program:<10} | {best_size:<15} | {static_time:<15.6f} | {dynamic_time:<15.6f} | {faster} by {diff:.2f}%")
    else:
        print(f"{program:<10} | {'N/A':<15} | {'N/A':<15} | {'N/A':<15} | {'N/A':<15}")