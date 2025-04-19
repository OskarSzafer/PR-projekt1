#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <omp.h>

// gcc k3a.c -o k3a.o -fopenmp -lm -O3

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Użycie: %s <dolny_zakres> <gorny_zakres>\n", argv[0]);
        return 1;
    }

    int m = atoi(argv[1]);
    int n = atoi(argv[2]);

    if (m > n || m < 2) {
        printf("Zakres nieprawidłowy. Upewnij się, że m >= 2 i m <= n.\n");
        return 1;
    }

    double start_time = omp_get_wtime();

    int range = n - m + 1;
    bool* result = (bool*)malloc(range * sizeof(bool));
    memset(result, true, range * sizeof(bool));

    bool* primeArray = (bool*)malloc((int)sqrt(n) + 1 * sizeof(bool));
    memset(primeArray, true, ((int)sqrt(n) + 1) * sizeof(bool));

    // Generate primes up to sqrt(n)
    for (int i = 2; i * i <= (int)sqrt(n); i++) {
        if (primeArray[i]) {
            for (int j = i * i; j <= (int)sqrt(n); j += i) {
                primeArray[j] = false;
            }
        }
    }

    // Define block size for better cache locality
    // A good block size is often related to cache size, 
    // but a few thousand elements usually works well
    const int BLOCK_SIZE = 8192;
    
    // Calculate number of blocks needed
    int num_blocks = (range + BLOCK_SIZE - 1) / BLOCK_SIZE;
    
    // Process each block
    for (int block = 0; block < num_blocks; block++) {
        // Determine start and end of current block
        int block_start = m + block * BLOCK_SIZE;
        int block_end = block_start + BLOCK_SIZE - 1;
        if (block_end > n) block_end = n;
        
        // Process each prime number for the current block
        for (int i = 2; i * i <= n; i++) {
            if (primeArray[i]) {
                // Find the first multiple of i in the current block
                int firstMultiple = (block_start / i) * i;
                if (firstMultiple < block_start) {
                    firstMultiple += i;
                }
                
                // Mark all multiples of i in the current block as non-prime
                for (int j = firstMultiple; j <= block_end; j += i) {
                    if (j >= m) {  // Ensure we're within the requested range
                        result[j - m] = false;
                    }
                }
            }
        }
    }

    // Special case for 1 if it's in the range
    if (m == 1) {
        result[0] = false;  // 1 is not a prime
    }

    // Uncomment to print the prime numbers
    // printf("Liczby pierwsze w zakresie [%d, %d]:\n", m, n);
    // for (int i = 0; i < range; i++) {
    //     if (result[i]) {
    //         printf("%d ", i + m);
    //     }
    // }
    // printf("\n");

    double end_time = omp_get_wtime();
    printf("Czas przetwarzania: %.6f sekund\n", end_time - start_time);

    free(result);
    free(primeArray);

    return 0;
}