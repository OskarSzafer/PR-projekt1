import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime

# Programs to test
programs = ["k1.o", "k2.o", "k3.o", "k3a.o", "k4.o", "k4a.o", "k5.o"]

# Ranges to test
ranges = [
    (2, 10**8),
    (2, 5*10**7),
    (5*10**7, 10**8)
]

# Regex to extract execution time
time_pattern = re.compile(r'Czas przetwarzania: (\d+\.\d+) sekund')

# Run a test and return execution time
def run_test(program, lower, upper):
    if program == "k1.o":
        cmd = f"./{program} {lower} {upper}"
    if program == "k2.o":
        cmd = f"./{program} {lower} {upper} dynamic"
    if program == "k3.o":
        cmd = f"./{program} {lower} {upper} "
    if program == "k3a.o":
        cmd = f"./{program} {lower} {upper} 524288"
    if program == "k4.o":
        cmd = f"./{program} {lower} {upper} dynamic"
    if program == "k4a.o":
        cmd = f"./{program} {lower} {upper} dynamic"
    if program == "k5.o":
        cmd = f"./{program} {lower} {upper} 131072"

    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error running {cmd}:\n{result.stderr}")
        return None

    match = time_pattern.search(result.stdout)
    if match:
        return float(match.group(1))
    else:
        print(f"Could not parse execution time from output:\n{result.stdout}")
        return None

# Timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Results dictionary
dynamic_results = {program: [] for program in programs}

# Run tests
for lower, upper in ranges:
    range_str = f"{lower}-{upper}"
    print(f"\n{'=' * 80}\nTesting range: {range_str}\n{'=' * 80}")
    print(f"{'Program':<10} | {'Dynamic Time (s)':<15}")
    print("-" * 60)

    for program in programs:
        time_dynamic = run_test(program, lower, upper)
        if time_dynamic is not None:
            dynamic_results[program].append((upper, time_dynamic))
            print(f"{program:<10} | {time_dynamic:<15.6f}")
        else:
            print(f"{program:<10} | {'Error':<15}")
        time.sleep(1)

# Plot results
plt.figure(figsize=(12, 6))
plt.title('Execution Time vs Range Size (Dynamic Scheduling Only)')
plt.xlabel('Upper Bound of Range')
plt.ylabel('Execution Time (seconds)')
plt.grid(True)
plt.xscale('log')

styles = ['b-o', 'g-s', 'r-^', 'c-*', 'm-d', 'y-x', 'k-p']
for i, program in enumerate(programs):
    if dynamic_results[program]:
        upper_bounds, times = zip(*sorted(dynamic_results[program]))
        plt.plot(upper_bounds, times, styles[i % len(styles)], label=program)

plt.legend()
plt.tight_layout()
plt.savefig(f'dynamic_only_results_{timestamp}.png')
print(f"\nPlot saved as dynamic_only_results_{timestamp}.png")

# Save CSV
with open(f'dynamic_only_results_{timestamp}.csv', 'w') as f:
    f.write("Range,")
    f.write(",".join([f"{p} Dynamic" for p in programs]))
    f.write("\n")
    for lower, upper in ranges:
        f.write(f"{lower}-{upper},")
        for program in programs:
            t = next((t for r, t in dynamic_results[program] if r == upper), "N/A")
            f.write(f"{t if t is not None else 'N/A'},")
        f.write("\n")

print(f"Results saved to dynamic_only_results_{timestamp}.csv")
