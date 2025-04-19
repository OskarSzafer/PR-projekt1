#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <omp.h>

// gcc k3a.c -o k3a.o -fopenmp -lm -O3

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("Użycie: %s <dolny_zakres> <gorny_zakres> <rozmiar_bloku>\n", argv[0]);
        return 1;
    }

    int m = atoi(argv[1]);
    int n = atoi(argv[2]);
    int BLOCK_SIZE = atoi(argv[3]);

    if (m > n || m < 2) {
        printf("Zakres nieprawidłowy. Upewnij się, że m >= 2 i m <= n.\n");
        return 1;
    }

    if (BLOCK_SIZE <= 0) {
        printf("Rozmiar bloku musi być większy od zera.\n");
        return 1;
    }

    double start_time = omp_get_wtime();

    int range = n - m + 1;
    bool* result = (bool*)malloc(range * sizeof(bool));
    memset(result, true, range * sizeof(bool));

    // Initialize all numbers in range as potential primes
    // (we'll mark non-primes later)
    for (int i = 0; i < range; i++) {
        result[i] = true;
    }

    // Special case for 1 if it's in the range
    if (m == 1) {
        result[0] = false;  // 1 is not a prime
    }

    // Generate primes up to sqrt(n) using sieve
    int sqrt_n = (int)sqrt(n);
    bool* primeArray = (bool*)malloc((sqrt_n + 1) * sizeof(bool));
    for (int i = 0; i <= sqrt_n; i++) {
        primeArray[i] = true;
    }
    
    // Mark non-primes in the primeArray (standard sieve of Eratosthenes)
    primeArray[0] = primeArray[1] = false;
    for (int i = 2; i * i <= sqrt_n; i++) {
        if (primeArray[i]) {
            for (int j = i * i; j <= sqrt_n; j += i) {
                primeArray[j] = false;
            }
        }
    }

    // Calculate number of blocks needed
    int num_blocks = (range + BLOCK_SIZE - 1) / BLOCK_SIZE;
    
    // Process each block
    for (int block = 0; block < num_blocks; block++) {
        // Determine start and end of current block
        int block_start = m + block * BLOCK_SIZE;
        int block_end = block_start + BLOCK_SIZE - 1;
        if (block_end > n) block_end = n;
        
        // Process each prime number for the current block
        for (int i = 2; i <= sqrt_n; i++) {
            if (primeArray[i]) {
                // Find the first multiple of i in the current block
                int firstMultiple = (block_start / i) * i;
                if (firstMultiple < block_start) {
                    firstMultiple += i;
                }
                if (firstMultiple == i) {
                    firstMultiple += i;  // Skip the prime itself
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